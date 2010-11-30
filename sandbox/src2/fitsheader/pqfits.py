#!/usr/bin/python -O

# (The -O option suppresses the output from __debug__)


def MainWork():

  # Open a MySQL connection
  try: 
    dh = dbhandler.PostgreSQLhandler()
  except dbhandler.DBException, e: 
    WriteLog('',str(e))
    sys.exit(1)
    
  # Loop over fits files on command line
  for file in sys.argv[1:]:

    print file

    # If file does not exist, do not go further
    if not os.path.exists(file): 
      WriteLog(file,'does not exist')	
      continue

    # Extract fits header values using pyfits
    # header = [<instrument>,<tbl_prefix>,primaryHDU,ext1HDU,ext2HDU,..,extNHDU]
    try:
      header = extractHeader(str(file))
    except HeaderException, e:
      WriteLog(file,str(e))
      continue

    # Pyfits do not recognize this a a fits file. Make a note and skip file.
    if header[0] == 'ERROR':
      WriteLog(file,'not a valid fits file')	
      continue

    instrument = header[0]
    tbl_prefix = header[1]
   
    # filename (stripped of .fits extension)
    fits_nm = str(os.path.basename(file))[:-5]

    # Delete any existing data for the Fits Header 
    #dh.deleteFitsHeader(tbl_prefix,fits_nm)

    # Insert the Fits Header into Database   
    try:
      dh.insertFitsHeader(header[1:],fits_nm)	
    except dbhandler.DBException, e:
      WriteLog(file,str(e))
      continue    

    # Write firsheader to file
    WriteHeader(fits_nm, instrument, header[2:])

    # End file loop

  # Close database connection
  dh.close()


# Logfile functionality
def WriteLog(fn,str):
  timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
  debugfile = open(OUTFILEPATH + '/debug.log', 'a')
  debugfile.write(timestamp + ' ' + fn + ':' + str)
  debugfile.write('\n')
  debugfile.close()


def WriteHeader(filename, instrument, header):

  # If the directory containing the nightly data does not exist,
  # create it and set 777 permissions

  dirname = "%s/%s/%s" % (OUTFILEPATH, instrument, filename[:6])
  try:
    os.stat(dirname)
  except OSError:
    os.mkdir(dirname)
    os.chmod(dirname,0777)

  # Define output filenames for individual images 

  fn = "%s/%s.fits" % (dirname, filename) 

  # Delete any existing fitsheader file for this image 

  try:
    os.unlink(fn)
  except OSError:
    pass

  # Now write all HDUs to file

  fh = open(fn, 'w')
  #os.chmod(fn, 0666)
  fh.write(str(header[0]))
  fh.write('\n')

  for exthdu in header[1:]:
    fh.write('\n')
    fh.write(str(exthdu))
    fh.write('\n')

  # Close filehandler

  fh.close() 


if __name__ == "__main__":
 
  import sys, os, time 
  import pqhandler as dbhandler
  from fitsheader import extractHeader, HeaderException

  # Output file path for log
  OUTFILEPATH = '/home/postprocess/fitsheader/logs' 

  MainWork()  
