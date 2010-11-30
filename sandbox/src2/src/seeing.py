#!/usr/bin/python -O

# (The -O option suppresses the output from __debug__)

# Output file path for log
logpath = '/home/postprocess/seeing_mon/logs' 

# File path for additional modules
pymodules = '/home/postprocess/python_modules'

import sys
sys.path.append('/home/fies-pipe/local/lib/python2.3/site-packages')
sys.path.append(pymodules)
import os
import time
import re
import MySQLdb
from sexmachine import *
from fitsheader import extractHeader
from postprocess import *
import dbhandler
from math import sqrt

# Open a MySQL connection
dh = dbhandler.MySQLhandler()

# Loop over fits files on command line
for file in sys.argv[1:]:

  # If file does not exist, do not go further
  if not os.path.exists(file): 
    writeLog(logpath,file,'does not exist')	
    continue

  # Get fits file name from stdin
  # file path + file name 
  fits_file = str(file)

  # filename
  fits_nm = str(os.path.basename(file))

  # Check file extention corresponds to a fits file
  if not (fits_nm[-5:] == '.fits'): 
    writeLog(logpath,file,'not .fits ext')
    continue

  # file name prefix (night identifier)
  night_nm = fits_nm[:-9]
    
  # Extract fits header values using pyfits
  header = extractHeader(fits_file)
  header['filename'] = fits_nm[:-5]


  # Either the ccd shutter is closed or some fits keywords
  # are missing. We skip this image.
  if not header['imaging']: 
    writeLog(logpath,file,'Shutter Closed')
    continue

  # Skip spectroscopy images
  if (header['mode'] == 'SPECTROSCOPY'): 
    writeLog(logpath,file,'Spectroscopy')
    continue

  # Execute an external fortran program that will return 
  # the string 'day' or 'night' depending whether the
  # timestamp given as input is refereing to before or after nautical twilight
  p = re.compile(r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(.*)$')
  li = p.search(header['dateobs'])
  if li:
    li.groups()
    cmdstr = '/usr/local/bin/nightday %s %s %s %s %s %s' % tuple(li.groups())
    try:
      nightday = os.popen(cmdstr).readlines()[0].strip()
    except OSError:
      nightday = 'day'            
  else:
    nightday = 'day'

  # Skip the image if the image is taken before twilight
  # or the evaluation of time (see above) failed. Focus Pyramid 
  # images can be taken in twillight.
  if (nightday == 'day') and (header['mode'] == 'IMAGING'): 
    writeLog(logpath,file,'Daytime')
    continue

  # If the directory containing the nightly data does not exist,
  # create it and set 777 permissions
  dirname = "%s/%s/%s" % (logpath, header['instrume'], night_nm)
  try:
    os.stat(dirname)
  except OSError:
    os.mkdir(dirname)
    os.chmod(dirname,0777)

  # Define output filenames for individual images,
  # nightly log and ds9 input file. 
  logfile_nm = "%s/%s.log" % (dirname, night_nm)  
  analysi_nm = "%s/%s.sex" % (dirname, fits_nm[:-5]) 
  ds9_nm     = "%s/%s.ds9" % (dirname, fits_nm[:-5])

  # If a nightly logfile does not exist, create it and make
  # it world-writable
  try:
    os.stat(logfile_nm)
  except OSError:
    open(logfile_nm, 'w')
    os.chmod(logfile_nm, 0666)

  # Delete any existing logfile for this image, then
  # create an empty logfile and make it world-writable
  try:
    os.unlink(analysi_nm)
  except OSError:
    pass
  open(analysi_nm, 'w')
  os.chmod(analysi_nm, 0666)

  # Delete any existing entries in the database tables 
  # for this image 
  dh.deleteObjectsDB(header['filename'])
  dh.deleteDataDB(header['filename']) 

  # Initialize a sextractor object
  sex = Sextractor()

  # Run sextractor on a single fits file
  sex.dosex(fits_file,analysi_nm,GAIN=header['gain'],PIXEL_SCALE=header['pscale'])

  # Read the sextractor output catalog into a list of list
  objects = sex.readsex(analysi_nm)

  # Use the unfiltered sextractor output catalogue to write a DS9 input file
  # with coloured circles
  sex.WriteDS9Regions(objects,ds9_nm)

  # Apply filter rules to the source catalog
  objects = sex.filtersex(objects,analysi_nm,ErrorFlag=0,MinAxisRMS=1,MinFWHM=2)

  if not objects: 
    writeLog(logpath,file,'1.filter - no objects')
    continue

  # Do not do the following steps for Focus Images
  if (header['mode'] == 'IMAGING'):

    # Do some statistics on the filtered sources
    s = sex.statsex(objects)

    # Calculate modal FWHM in arcsec
    ModalFWHM = str( float(s['modeFWHM']) * float(header['pscale']) )  

    # Rerun sextractor with Seeing estimate
    sex.dosex(fits_file,	analysi_nm,
			GAIN=header['gain'],
			PIXEL_SCALE=header['pscale'],
			SEEING_FWHM=ModalFWHM
	     )

    # Read the sextractor output catalog into a list of list
    objects = sex.readsex(analysi_nm)

    # Apply filter rules to the source catalog
    objects = sex.filtersex(objects,analysi_nm,ErrorFlag=0,MinAxisRMS=1,MinFWHM=2,StellaLike=0.7)

    if not objects: 
      writeLog(logpath,file,'2.filter - no objects')
      continue

    # Do some statistics on the filtered sources
    s = sex.statsex(objects)

    # Apply a sigma clipping filter to the list
    objects = sex.filtersex(objects,analysi_nm,Mean=s['meanFWHM'],Stdev=s['stdevFWHM'],SigmaClip=3)

    if not objects: 
      writeLog(logpath,file,'3.filter - no objects')
      continue

    # Do some statistics on the filtered sources
    s = sex.statsex(objects)

    # Apply another sigma clipping filter to the list based on new statistics
    objects = sex.filtersex(objects,analysi_nm,Mean=s['meanFWHM'],Stdev=s['stdevFWHM'],SigmaClip=1.5)
    if not objects: 
      writeLog(logpath,file,'4.filter - no objects')
      continue

  if (header['mode'] == 'IMAGING'): writeLog(logpath,file,str(len(objects)) + ' Objects')

  # Do final statistics
  s = sex.statsex(objects)

  if s: 

    #
    # For imaging data, print the results in a nightly logfile and 
    # insert measurements into the seeing database. 
    #

    if (header['mode'] == 'IMAGING'):
 
      logfile = open(logfile_nm, 'a')

      logfile.write(fits_nm)
      logfile.write(' ')	 

      for key in header['keys']:
         logfile.write(str(header[key]))
	 logfile.write(' ')

      s['medianFWHM'] = str("%.2f" % (float(s['medianFWHM'])*float(header['pscale'])))
      s['meanFWHM']   = str("%.2f" % (float(s['meanFWHM'])*float(header['pscale'])))
      s['stdevFWHM']  = str("%.2f" % (float(s['stdevFWHM'])*float(header['pscale'])))

      logfile.write(s['medianFWHM'])
      logfile.write(' ')
      logfile.write(s['meanFWHM'])
      logfile.write(' ')
      logfile.write(s['stdevFWHM'])
      logfile.write(' ')
      logfile.write(s['medianEL'])
      logfile.write(' ')
      logfile.write(s['meanEL'])
      logfile.write(' ')
      logfile.write(s['stdevEL'])
      logfile.write(' ')
      logfile.write(s['N']) 

      logfile.write('\n')
      logfile.close() 

      # Get current DIMM seeing and write values into Talker window
      dimm = getCurrentDimm()
      msg = "[NOTE]: %s: N=%s, FWHM=%s+-%s, EL=%s+-%s DIMM=%s" % (fits_nm,s['N'],
	s['meanFWHM'],s['stdevFWHM'],s['medianEL'],s['stdevEL'],dimm) 
      writeTalker('postprocess.seeingmon',msg)

      # Write Statistics in the DS9 input file
      sex.WriteDS9Stats(fits_nm,s,ds9_nm)

      # Do we need to refocus telescope?
      # 2007/08/13 : COMMENTED OUT	
      #if (float(s['medianEL']) > 0.14):
      #  msg = "[WARNING]: %s: High ellipticity detected. Refocus Telescope?" % fits_nm
      #	writeTalker('postproc.seeingmon',msg)

      # Insert header and statistics data into database 
      # after deleting some useless entries
      del (header['keys'],header['imaging'],header['mode'],s['modeFWHM'])		
      dh.insertDataDB(header,s)

      # Insert individual object data into database   
      dh.insertObjectsDB(header,objects)	


    #
    # For Focus Pyramid data, calculate the telescope focus offset
    #

    elif (header['mode'] == 'FOCUS'):

      import stats

      bs		 = 10  	# (Radius of search box)
      refdistance	 = 44.57
      pyramidscalefactor = 28.00	

      sum  = 0	
      wsum = 0.0	
      offset  = []
      woffset = [] 

      # Loop over every object identified in the field	
      for o in objects:

	# Define the other 3 nominal positions in the pyramid given the current object
	# would be the top point
	x1 = float(o[1])
        y1 = float(o[2])
        x2=x1
        y2=y1-refdistance
        x3=x1-refdistance/2
        x4=x1+refdistance/2
        y3=y1-refdistance/2
        y4=y3

	# If the current object do not correspond to the top point in the pyramid, 
        # continue to next object

        p2 = [obj for obj in objects if 
		(float(obj[1]) > x2 - bs) and (float(obj[1]) < x2 + bs) and
		(float(obj[2]) > y2 - bs) and (float(obj[2]) < y2 + bs)]

	if len(p2) != 1: continue

	p3 = [obj for obj in objects if 
		(float(obj[1]) > x3 - bs) and (float(obj[1]) < x3 + bs) and
		(float(obj[2]) > y3 - bs) and (float(obj[2]) < y3 + bs)]

	if len(p3) != 1: continue

	p4 = [obj for obj in objects if 
		(float(obj[1]) > x4 - bs) and (float(obj[1]) < x4 + bs) and
		(float(obj[2]) > y4 - bs) and (float(obj[2]) < y4 + bs)]

	if len(p4) != 1: continue


	x2 = float(p2[0][1])
	y2 = float(p2[0][2])
	x3 = float(p3[0][1])
	y3 = float(p3[0][2])
	x4 = float(p4[0][1])
	y4 = float(p4[0][2])

	xdist = sqrt( (x4-x3)*(x4-x3) + (y4-y3)*(y4-y3) )
        ydist = sqrt( (y1-y2)*(y1-y2) + (x1-x2)*(x1-x2) )

        meandist = (xdist + ydist)/2
	 
        teloff = (refdistance - meandist) * pyramidscalefactor

	# Weight function: distance from chip center. 
	# Add the teloff X times, depending on weight
	if (header['instrume'] == 'alfosc'):
          distance = sqrt( (x1 - 1000)**2 + (y1 - 1000)**2 )

	  if distance < 200: 
		offset.append(teloff)
		offset.append(teloff)
          elif distance < 600:
		offset.append(teloff) # The average focus offset should be 
		offset.append(teloff) # weighted toward the value a few hundred pixels away from the center.
		offset.append(teloff) # pixels away from the center. (07.10.04)
	  elif distance < 800:
		offset.append(teloff)
		offset.append(teloff)
	  else:
		offset.append(teloff)
        else:
          offset.append(teloff) 

	#writeLog(logpath,file,"FocusPyr: teloffset= %d" % offset)  
	#print "FocusPyr: teloffset= %d distance=%f (%f,%f)" % (teloff,distance,x1,y1) 	

      if len(offset) > 0:
        # Determine mean, median and stdev of unclipped offsets
        mean  = stats.mean(offset) 
        median = stats.median(offset) 
        try:	
          stdev = stats.stdev(offset)
        except ZeroDivisionError:
          stdev = '0.00';

        # Do a 1-sigma clipping
        clipLowLimit  =  float(mean) - 1 * float(stdev)
        clipHighLimit =  float(mean) + 1 * float(stdev)
        offset = [off for off in offset
		if float(off) < clipHighLimit and float(off) > clipLowLimit ]	

        # Determine stats on sigma clipped data 
        mean_c  = stats.mean(offset) 
        median_c = stats.median(offset) 
        try:	
          stdev_c = stats.stdev(offset)
        except ZeroDivisionError:
          stdev_c = '0.00';

        #print "FocusPyr Mean,Median,Stdev: %.0f,%.0f,%.0f" % (mean_c,median_c,stdev_c)	

        writeLog(logpath,file,"FocusPyr Mean,Median,Stdev: %.0f,%.0f,%.0f" % (mean_c,median_c,stdev_c))

        msg = "[NOTE]: %s: Required telescope focus change: %d" % (fits_nm, median_c)
        writeTalker('postproc.seeingmon',msg)
      
      else:

        writeLog(logpath,file,'No Objects')
        sys.exit(1)

# End file loop

# Close database connection
dh.close()

