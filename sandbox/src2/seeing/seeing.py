#!/usr/bin/python -O

# (The -O option suppresses the output from __debug__)

# Output file path for log
logpath = '/home/postprocess/seeing_mon/logs' 

# File path for additional modules
pymodules = '/home/postprocess/python_modules'

# Directory for flattened MEF images
mergedir = '/raid1/data/tempdata/'
 
import sys, os, time, re
import dbhandler
sys.path.append(pymodules)
from sexmachine import *
from postprocess import *
from math import sqrt


instrument = {'AL':'ALFOSC','MO':'MOSCA','NC':'NOTCAM','ST':'STANCAM'}

# Open a MySQL connection
dh = dbhandler.MySQLhandler()

# Loop over fits files on command line
for file in sys.argv[1:]:

  # If file does not exist, do not go further
  if not os.path.exists(file): 
    writeLog(logpath,file,'does not exist')	
    continue

  # --------------------------------------------------
  # Use the input filename to define useful variables 
  # --------------------------------------------------

  fits_file = str(file) 	            # image with full path
  fits_nm   = str(os.path.basename(file))   # Filename with extention

  # Check file extention corresponds to a fits file
  if not (fits_nm[-5:] == '.fits'): 
    writeLog(logpath,file,'not .fits ext')
    continue

  prefix    = fits_nm[:2]		    # Instrument prefix, i.e. AL,FI,ST,...
  instrum   = instrument[prefix]	    # Instrument name, i.e. ALFOSC, FIES, ..
  filename  = fits_nm[:-5]		    # Filename without extention
  night_nm  = fits_nm[:-9]                  # Night identifier, i.e. ALxxxx 

  # ---------------------------------------------- 
  # Retrieve fits header information from database
  # ----------------------------------------------
 
  try:
    header = dh.getFitsHeader(prefix,filename)
  except dbhandler.DBException, e:
    writeLog(logpath,file,str(e))
    continue

  if header is None:
    writeLog(logpath,file,'no fits header in database')
    continue

  headIDnm = "id%sprihdu" % prefix          # The PK name in the fits header table  
  id_Header = header[headIDnm]

  if instrum == 'MOSCA':
    header['DETWIN1'] = '[ 1:4096, 1:4096]'
  if instrum == 'NOTCAM':
    header['DETWIN1'] = '[ 1:1024, 1:1024]'  

  # Calculate the pixelscale based on CD1_1 and CD1_2 keywords
  cd1_1  = header['CD1_1'] 
  cd1_2  = header['CD1_2']
  try:
    PSCALE = '%.3f' % (sqrt(pow(cd1_1,2)+pow(cd1_2,2))*3600)
  except TypeError:
    writeLog(logpath,file,'Failed to calculate pixel scale')
    continue

  # Methods require str type parameters
  GAIN = str(header['GAIN'])
 
  # Get Binning and Window information from fits header
  # [ 1:1098, 1:1026]
  reg_win = re.compile(r'^\[\s*(\d+):\s*(\d+)\s*,\s*(\d+):\s*(\d+)\]$')

  # 2 2
  reg_bin    = re.compile(r'^(\d)\ (\d)$')

  ccd_win = reg_win.search(header['DETWIN1'])
  ccd_bin = reg_bin.search(header['CCDSUM'])

  if ccd_bin:
    XBIN = ccd_bin.groups()[0]
    YBIN = ccd_bin.groups()[0]
  else:
    XBIN = 1
    YBIN = 1

  if ccd_win:
    XBEG = ccd_win.groups()[0]
    YBEG = ccd_win.groups()[2]
  else:
    XBEG = 1
    YBEG = 1


  # ------------------------------------------------------ 	
  # Do not run Sextractor on images with shutter closed,
  # taken during daytime or with optics in the grism wheel	
  # (spectroscopy or focus pyramid for ALFOSC and NOTCAM)
  # ------------------------------------------------------

  # CCD shutter is closed
  if (header['SHSTAT'] == 'CLOSED'):  
    writeLog(logpath,file,'Shutter Closed')
    continue

  # For ALFOSC & NOTCAM, skip spectroscopy and focus pyramid images
  if (prefix == 'AL') and (header['ALGRNM'] != 'Open (Lyot)'): 
    writeLog(logpath,file,'ALFOSC Grism wheel optics')
    continue
  if (prefix == 'NC') and (header['GRISM'] != 'OPEN'): 
    writeLog(logpath,file,'NOTCAM Grism wheel optics')
    continue

  # Execute an external fortran program that will return 
  # the string 'day' or 'night' depending whether the
  # timestamp given as input is refereing to before or after civil twilight
  p = re.compile(r'^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(.*)$')
  li = p.search(header['DATE-OBS'])
  if li:
    li.groups()
    cmdstr = '/usr/local/bin/nightday_civil %s %s %s %s %s %s' % tuple(li.groups())
    try:	    
      nightday = os.popen(cmdstr).readlines()[0].strip()
    except OSError:
      nightday = 'day'            
  else:
    nightday = 'day'

  # Skip the image if the image is taken before civil twilight
  # or the evaluation of time (see above) failed. 
  if (nightday == 'day'): 
    writeLog(logpath,file,'Civil daytime')
    continue

  # -------------------------------------------------------- 
  # Define directories and filenames to hold log information
  # --------------------------------------------------------


  # If the directory containing the nightly data does not exist,
  # create it and set 777 permissions
  dirname = "%s/%s/%s" % (logpath, instrum, night_nm)
  try:
    os.stat(dirname)
  except OSError:
    os.mkdir(dirname)
    os.chmod(dirname,0777)

  # Define output filenames for individual images,
  # nightly log and ds9 region output file. 
  logfile_nm = "%s/%s.log" % (dirname, night_nm)  
  analysi_nm = "%s/%s.sex" % (dirname, filename) 
  ds9_nm     = "%s/%s.ds9" % (dirname, filename)

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


  # ------------------------------------------------------------------
  # SeXTractor looses track of the physical CCD coordinates  
  # on MEF images. We must flatten ALFOSC images taken with dual 
  # amplifier and MOSCA images. This is time consuming, we check if 
  # flattened images already exists before calling the merger routine.
  # ------------------------------------------------------------------
 
  if (prefix == 'AL') and (header['AMPLMODE'] == 'AB'): 
    outfile = os.path.join(mergedir, fits_nm)
    if not os.path.isfile(outfile):
       writeLog(logpath,file,'Flattening Image')
       mergeALFOSC(fits_file,outfile)  
    fits_file = outfile


  if (prefix == 'MO'):
    outfile = os.path.join(mergedir, fits_nm)
    if not os.path.isfile(outfile):
       writeLog(logpath,file,'Flattening Image')
       mergeMOSCA(fits_file,outfile)  
    fits_file = outfile


  # --------------------------------------------------
  # Delete any existing entries in the database tables 
  # for this image 
  # --------------------------------------------------
  try:
    dh.deleteDataDB(prefix,id_Header) 
  except dbhandler.DBException, e:
    writeLog(logpath,file,str(e))
    continue    


  # -----------------------------
  # Start the Sextractor analysis
  # -----------------------------

  # Initialize a sextractor object
  sex = Sextractor()

  # Run sextractor on a single fits file
  sex.dosex(fits_file,analysi_nm,GAIN=GAIN,PIXEL_SCALE=PSCALE)

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

  # Do some statistics on the filtered sources
  s = sex.statsex(objects)

  # Calculate modal FWHM in arcsec
  ModalFWHM = str( float(s['modeFWHM']) * float(PSCALE) )  

  # Rerun sextractor with Seeing estimate
  sex.dosex(fits_file,	analysi_nm,
			GAIN=GAIN,
			PIXEL_SCALE=PSCALE,
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

  writeLog(logpath,file,str(len(objects)) + ' Objects')
  
  # Transform ccd coordinates of each object into physical coordinates based
  # on binning and window information. Apply pixel scaling.
  for obj in objects:

   obj[1]  = str("%.3f" % (float(obj[1])*float(XBIN)+float(XBEG)-1)) 
   obj[2]  = str("%.3f" % (float(obj[2])*float(YBIN)+float(YBEG)-1)) 
   obj[3]  = str("%.3f" % (float(obj[3])*float(PSCALE)))
   obj[4]  = str("%.3f" % (float(obj[4])*float(PSCALE)))
   obj[7]  = str("%.2f" % (float(obj[7])*float(PSCALE)))


  # Do final statistics
  s = sex.statsex(objects)

  # Delete modeFWHM from stats to prevent going into database
  del s['modeFWHM']

  # Delete merged image, if any
  try:
    os.unlink(os.path.join(mergedir, fits_nm))
  except OSError:
    pass

  if s: 

    #
    # For imaging data, print the results in a nightly logfile and 
    # insert measurements into the seeing database. 
    #

    logfile = open(logfile_nm, 'a')
    logfile.write(filename)
    logfile.write(' ')	 
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
    #  writeTalker('postproc.seeingmon',msg)

    # Calculate airmass correction factor according to Kolmogolov atmosphere
    if not header['AIRMASS']: header['AIRMASS'] = 1 
    airmassC = float(header['AIRMASS'])**0.6

    # Calculate central wavelength correction (wrt 500nm) according to K atmosphere
    for f in ['ALFLTID','FAFLTID','FBFLTID','STFLTID','FILT1ID','FILT2ID']:
      try:
        # We assume first ID > 0 is the only filter in beam
        if header[f] > 0:
	  filterID = header[f] 
          break
      except KeyError:
        continue	

    # There may be no filter in the beam at all.
    if 'filterID' not in locals(): filterID = 0
    try:
      cenwave = dh.getFilterCenwave(filterID)[0]  
    except dbhandler.DBException, e:
      writeLog(logpath,file,str(e))
      cenwave = 600
    wavelenC = (500/float(cenwave))**0.2

    s['meanFWHMcor']   = "%.2f" % (float(s['meanFWHM'])/airmassC/wavelenC)
    s['medianFWHMcor'] = "%.2f" % (float(s['medianFWHM'])/airmassC/wavelenC)

    # Insert header and statistics data into database 
    try:
      dh.insertDataDB(prefix,id_Header,s,objects)
    except dbhandler.DBException, e:
      writeLog(logpath,file,str(e))
      continue    

# End file loop

# Close database connection
dh.close()

