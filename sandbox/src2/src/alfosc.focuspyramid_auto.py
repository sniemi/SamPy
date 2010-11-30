#!/usr/bin/python -O

# (The -O option suppresses the output from __debug__)

# Output file path for log
logpath = '/home/postprocess/alfosc/focuspyr/logs' 

# File path for additional modules
pymodules = '/home/postprocess/python_modules'
sexmodules = '/home/postprocess/seeing_mon/src'

import sys
sys.path.append('/home/fies-pipe/local/lib/python2.3/site-packages')
sys.path.append(pymodules)
sys.path.append(sexmodules)
import os
import time
import re
import stats
from pyfits import getheader
from sexmachine import *
from postprocess import *
import dbhandle
from math import sqrt

bs                    = 10    # (Radius of search box)
refdistance           = 44.57
pyramidscalefactor    = 28.00

#Open a MySQL connection
dh = dbhandle.MySQLhandler()

# Loop over fits files on command line
for file in sys.argv[1:]:
  
  # Initialize lists holding result data for every frame
  offset  = []
  pyrobjects = []

  # If file does not exist, do not go further
  if not os.path.exists(file): 
    writeLog(logpath,file,'does not exist')    
    sys.exit(1)

  # Get fits file name from stdin
  # file path + file name 
  fits_file = str(file)

  # filename
  fits_nm = str(os.path.basename(file))

  # Check file extention corresponds to a fits file
  if not (fits_nm[-5:] == '.fits'): 
    writeLog(logpath,file,'not .fits ext')
    sys.exit(1)

  # file name prefix (night identifier)
  night_nm = fits_nm[:-9]
    
  # Extract fits header values using pyfits
  try:
    h0 = getheader(fits_file,0)
  except IndexError:
    writeLog(logpath,file,'Missing Primary HDU')
    sys.exit(1)

  # Skip any images except Focus Pyramid images
  try:
    if (h0['ALGRNM'] != 'Focus_Pyr'):
      writeLog(logpath,file,'WRONG ALGRNM Keyword')
      sys.exit(1)
  except KeyError:
    writeLog(logpath,file,'Missing ALGRNM Keyword')
    sys.exit(1)
    
  # Extract primary image extention fits header  
  try:
    h1 = getheader(fits_file,1)
  except IndexError:
    writeLog(logpath,file,'Missing Image HDU')
    sys.exit(1)

  # Create header dictionary
  h = {}
  try:
   h['filename'] = fits_nm[:-5]
   h['dateobs']  = h0['DATE-OBS']
   h['tcstgt']   = h0['TCSTGT']
   h['ra']       = h0['RA']
   h['decl']     = h0['DEC']
   h['exptime']  = h0['EXPTIME']
   h['detector'] = h0['DETNAME']
   h['apartur']  = h0['ALAPRTNM']
   h['polariza'] = h0['FARETARD']
   h['telalt']   = h0['TELALT']
   h['azimuth']  = h0['AZIMUTH']
   h['rotpos']   = h0['ROTPOS']
   h['austatus'] = h0['AUSTATUS']
   h['afltid']   = h0['ALFLTID']
   h['afltnm']   = h0['ALFLTNM']
   h['fafltid']  = h0['FAFLTID']
   h['fafltnm']  = h0['FAFLTNM']
   h['fbfltid']  = h0['FBFLTID']
   h['fbfltnm']  = h0['FBFLTNM']
   h['gain']     = str(h1['GAIN'])
   cd1_1  	 = h1['CD1_1'] 
   cd1_2  	 = h1['CD1_2']
   h['pscale']   = '%.3f' % (sqrt(pow(cd1_1,2)+pow(cd1_2,2))*3600)
   h['telfocus'] = h0['TELFOCUS']
   h['alfocus']  = h0['ALFOCUS']     
  except KeyError:
   writeLog(logpath,file,'Missing Keywords')
   sys.exit(1)

  # If the directory containing the nightly data does not exist,
  # create it and set 777 permissions
  dirname = "%s/%s" % (logpath, night_nm)
  try:
    os.stat(dirname)
  except OSError:
    os.mkdir(dirname)
    os.chmod(dirname,0777)

  # Define output filenames for individual images,
  # nightly log and ds9 input file. 
  logfile_nm = "%s/%s.log" % (dirname, night_nm)  
  analysi_nm = "%s/%s.sex" % (dirname, fits_nm[:-5]) 

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

  # Initialize a sextractor object
  sex = Sextractor()

  # Run sextractor on a single fits file
  sex.dosex(fits_file,analysi_nm,GAIN=h['gain'],PIXEL_SCALE=h['pscale'])

  # Read the sextractor output catalog into a list of list
  objects = sex.readsex(analysi_nm)

  # Apply filter rules to the source catalog
  objects = sex.filtersex(objects,analysi_nm,MinAxisRMS=1,MinFWHM=2)

  if not objects: 
    writeLog(logpath,file,'1.filter - no objects')
    sys.exit(1)

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
        distance = sqrt( (x1 - 1000)**2 + (y1 - 1000)**2 )

	if distance < 200: 
		offset.append(teloff)
		offset.append(teloff)
        elif distance < 600:
		offset.append(teloff) # The average focus offset should be 
		offset.append(teloff) # weighted toward the value a few hundred pixels away from the center.
		offset.append(teloff) # pixels away from the center. (action 07.10.04)
	elif distance < 800:
		offset.append(teloff)
		offset.append(teloff)
	else:
		offset.append(teloff)

	writeLog(logpath,file,"FocusPyr: teloffset= %d" % teloff)  
	#print "FocusPyr: teloffset= %d distance=(%f,%f) (%f,%f) %s" % (teloff,xdist,ydist,x1,y1,o[11]) 	

	# Append to a list to be inserted into Objects table
	pyrobjects.append((teloff,xdist,ydist,x1,y1,o[11]))        


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
	if float(off) <= clipHighLimit and float(off) >= clipLowLimit ]	

    # Determine stats on sigma clipped data 
    h['meanFocusOffset']   = stats.mean(offset) 
    h['medianFocusOffset'] = stats.median(offset) 
    try:	
      h['stdevFocusOffset'] = stats.stdev(offset)
    except ZeroDivisionError:
      h['stdevFocusOffset'] = 0.0;
    h['NumFocusOffset'] = len(pyrobjects)
    
    # Write median Focus Offset on STDOUT
    print "%.0f" % h['medianFocusOffset']	

    writeLog(logpath,file,"Mean,Median,Stdev: %.0f,%.0f,%.0f" % (h['meanFocusOffset'],h['medianFocusOffset'],h['stdevFocusOffset']))

    msg = "[NOTE]: %s: Required telescope focus change: %d" % (h['filename'], h['medianFocusOffset'])
    #writeTalker('postproc.seeingmon',msg)
      
    # Delete any existing entries in the database tables
    # for this image
    dh.deleteObjectsDB(h['filename'])
    dh.deleteDataDB(h['filename'])

    # Insert header and statistics data into database 
    dh.insertDataDB(h)
    dh.insertObjectsDB(h['filename'],pyrobjects)        

  else:

    writeLog(logpath,file,'No Objects')
    sys.exit(1)

# End file loop

# Close database connection
dh.close()

