from pyfits import getheader
from math import asin,degrees,pow,sqrt,pi
import os

class HeaderException(Exception):
  pass


##############
### ALFOSC ###
##############

def extractALFOSCHeader(file):

  """ Extract ALFOSC keywords from a fits file """

  try:
    # extract primary and first HDU
    ph = extractHDU(file,0) 
    im1hdr = extractHDU(file,1)
    
    # Extract keywords common for all instruments
    fitsheader = extractCommonKeywords(ph,im1hdr)

    # Imaging Check: Shutter open 
    if 	(requireValidString('SHSTAT', ph) == 'OPEN'):
      fitsheader['imaging'] = 1
    else:
      fitsheader['imaging'] = 0	
      return fitsheader

    # The ALFOSC grism wheel position (ALGRNM) determines the mode of analysis to follow:
    # - 'Open (Lyot)' : Direct imaging  
    # - 'Focus_Pyr'   : Focus Pyramid image
    # - Any other wheel content is related to spectroscopy
    algrnm = requireValidString('ALGRNM', ph)
    if (algrnm == 'Focus_Pyr'):
      fitsheader['mode'] = 'FOCUS'	    
    elif (algrnm == 'Open (Lyot)'):
      fitsheader['mode'] = 'IMAGING'
    else:	
      fitsheader['mode'] = 'SPECTROSCOPY'
      return fitsheader

    # Add instrument specific keywords
    fitsheader['instrume'] = 'alfosc'
    fitsheader['alfocus']  = requireValidInt('ALFOCUS', ph)	
    fitsheader['alfltid']  = requireValidInt('ALFLTID', ph)
    fitsheader['alfltnm']  = requireValidString('ALFLTNM', ph)
    fitsheader['fafltid']  = requireValidInt('FAFLTID', ph)
    fitsheader['fafltnm']  = requireValidString('FAFLTNM', ph)
    fitsheader['fbfltid']  = requireValidInt('FBFLTID', ph)
    fitsheader['fbfltnm']  = requireValidString('FBFLTNM', ph)
    fitsheader['apertur']  = requireValidString('ALAPRTNM', ph)
    fitsheader['pscale']   = calculatePixelScale(im1hdr)
  
    # Define the list of keywords that will be added to logfile
    fitsheader['keys'] = ['dateobs','telalt','azimuth','rotpos','ra','decl','telfocus','pscale','gain',
		'apertur','alfltid','alfltnm','fafltid','fafltnm','fbfltid','fbfltnm',
		'imagetyp','exptime','austatus']

  # A keyword is missing, flag this image to be skipped
  except HeaderException, e:
    fitsheader = { 'imaging': 0 }
    print e

  # Return the fitsheader dictionary
  return fitsheader


#############
### MOSCA ###
#############

def extractMOSCAHeader(file):

  """ Extract MOSCA keywords from fits header """

  try:
    # extract primary and first HDU
    ph = extractHDU(file,0) 
    im1hdr = extractHDU(file,1)

    # Extract keywords common for all instruments
    fitsheader = extractCommonKeywords(ph,im1hdr)

    # Imaging Check: Shutter open 
    if 	(requireValidString('SHSTAT', ph) == 'OPEN'):
      fitsheader['imaging'] = 1
    else:
      fitsheader['imaging'] = 0	
      return fitsheader

    # Add instrument specific keywords
    fitsheader['instrume'] = 'mosca'
    fitsheader['fafltid']  = requireValidInt('FAFLTID', ph)
    fitsheader['fafltnm']  = requireValidString('FAFLTNM', ph)
    fitsheader['fbfltid']  = requireValidInt('FBFLTID', ph)
    fitsheader['fbfltnm']  = requireValidString('FBFLTNM', ph)
    fitsheader['pscale']   = calculatePixelScale(im1hdr)
    fitsheader['mode'] 	   = 'IMAGING'

    # Define the list of keywords that will be added to logfile
    fitsheader['keys'] = ['dateobs','telalt','azimuth','rotpos','ra','decl','telfocus','pscale','gain',
		'fafltid','fafltnm','fbfltid','fbfltnm','imagetyp','exptime','austatus']

  # A keyword is missing, flag this image to be skipped
  except HeaderException, e:
    fitsheader = { 'imaging': 0 }
    print e
  return fitsheader


###############
### STANCAM ###
###############

def extractSTANCAMHeader(file):

  """ Extract StanCam keywords from fits header """

  try:
    # extract primary and first HDU
    ph = extractHDU(file,0) 
    im1hdr = extractHDU(file,1)

    # Extract keywords common for all instruments
    fitsheader = extractCommonKeywords(ph,im1hdr)

    # Imaging Check: Shutter open 
    if 	(requireValidString('SHSTAT', ph) == 'OPEN'):
      fitsheader['imaging'] = 1
    else:
      fitsheader['imaging'] = 0	
      return fitsheader

    # Add instrument specific keywords
    fitsheader['instrume'] = 'stancam'
    fitsheader['stfltid']  = requireValidInt('STFLTID', ph)
    fitsheader['stfltnm']  = requireValidString('STFLTNM', ph)
    fitsheader['pscale']   = calculatePixelScale(im1hdr)
    fitsheader['mode']     = 'IMAGING'

    # Define the list of keywords that will be added to logfile
    fitsheader['keys'] = ['dateobs','telalt','azimuth','rotpos','ra','decl','telfocus','pscale','gain',
		'stfltid','stfltnm','imagetyp','exptime','austatus']

  # A keyword is missing, flag this image to be skipped
  except HeaderException, e:
    fitsheader = { 'imaging': 0 }
    print e
  return fitsheader


##################
### OLD ALFOSC ###
##################

def extractOldALFOSCHeader(file):

  """ Extract headers for non-MEF ALFOSC Images """

  try:
    # Extract primary header unit
    ph = extractHDU(file,0)

    # Form a proper timestamp from a float type UT 
    ut = requireValidFloat('UT',ph)    
    hh = int(ut)
    mm = int((ut-hh)*60)
    ss = int((((ut-hh)*60)-mm)*60)
    timestamp = "%02d:%02d:%02d" % (hh,mm,ss)
    date_obs = requireValidString('DATE-OBS', ph)

    fitsheader = {
      'imagetyp': ph.get('IMAGETYP', 'na').strip() or 'na',
      'exptime'	: requireValidFloat('EXPTIME',ph),			
      'azimuth'	: '0.00', 	
      'austatus': 'na',	
      'telfocus': requireValidInt('TELFOCUS', ph),
      'gain'	: '0.726',
      'alfltid'	: requireValidInt('FILTID', ph),
      'alfltnm'	: requireValidString('FILTER', ph),	  	
      'fafltid'	: requireValidInt('AFILTID', ph),
      'fafltnm'	: requireValidString('AFILTER', ph),
      'fbfltid'	: requireValidInt('BFILTID', ph),
      'fbfltnm'	: requireValidString('BFILTER', ph),		
      'rotpos'  : requireValidFloat('ROTPOS',ph),
      'apertur' : requireValidString('APERTUR', ph),
      'ra'      : '%.2f' % requireValidFloat('RA',ph),
      'decl'    : '%.2f' % requireValidFloat('DEC',ph) 
	
    }
  
    fitsheader['dateobs'] = "%sT%s" % (date_obs, timestamp)

    # Calculate telescope altitude from airmass
    airmass = requireValidFloat('AIRMASS',ph)
    fitsheader['telalt'] = '%.2f' % (90 - degrees(pi/2 - asin(1/airmass))) 

    # Calculate pixel scale
    cd1_1 = requireValidInt('CDELT1', ph)
    fitsheader['pscale'] = str(cd1_1 * 0.19)

    fitsheader['instrume'] = 'alfosc'

    if (fitsheader['exptime'] > 1.0) and (requireValidString('GRISM', ph) == 'Open_(Lyot)'):
      fitsheader['imaging'] = 1
    else:
      fitsheader['imaging'] = 0	

    fitsheader['keys'] = ['dateobs','telalt','azimuth','rotpos','ra','decl','telfocus','pscale','gain',
		'apertur','alfltid','alfltnm','fafltid','fafltnm','fbfltid','fbfltnm',
		'imagetyp','exptime','austatus']

  except HeaderException, e:
    fitsheader = { 'imaging': 0 }

  return fitsheader

###################
### NON IMAGING ###
###################

def returnNoImaging(file):
  
  """
    Return a dummy fitsheader where imaging is set to false
    Used for non-imaging instruments (FIES etc.) 
  """
  fitsheader={'imaging':0}
  return fitsheader


### SUB ROUTINES ###

def extractHeader(file) :

   """
     Pseudo method for extracting fitsheader keywords. Will call an	
     apropriate method, depending on filename (instrument)	 
   """

   headerDispatching = {
   	'AL': extractALFOSCHeader,
   	'MO': extractMOSCAHeader,
   	'ST': extractSTANCAMHeader,	
   	'FI': returnNoImaging,
   	'NC': returnNoImaging
   }

   fn = headerDispatching.get(os.path.basename(file)[:2], extractOldALFOSCHeader)
   return fn(file)

def extractHDU(file,unit):

  """ Return a header unit """

  try:
    return getheader(file, unit)
  except IndexError:
    pass
  raise HeaderException("No such HDU: %s" % unit)

def extractCommonKeywords(ph,im1hdr):

  """ Extract mandatory keywords common for all MEF files """

  fitsheader = {
      'dateobs' : requireValidString('DATE-OBS',ph),
      'imagetyp': ph.get('IMAGETYP', 'na').strip() or 'na',
      'exptime'	: requireValidFloat('EXPTIME', ph),			
      'telalt'	: '%.2f' % requireValidFloat('TELALT', ph),
      'azimuth'	: '%.2f' % requireValidFloat('AZIMUTH', ph), 
      'rotpos'  : requireValidFloat('ROTPOS', ph),		
      'austatus': requireValidString('AUSTATUS', ph),
      'telfocus': requireValidInt('TELFOCUS', ph),
      'gain'	: str(requireValidFloat('GAIN', im1hdr)),
      'ra'      : '%.2f' % requireValidFloat('RA',ph),
      'decl'    : '%.2f' % requireValidFloat('DEC',ph)	
    }

  return fitsheader

def requireValidString(key,hdr):

  """ Returns a header keyword if a valid string """

  val = hdr.get(key)
  try:
    if type(val) == str:
      val = val.strip()
      if val:
        return val
  except AttributeError,ValueError:
    pass
  raise HeaderException ("Invalid string at key %s" % key)

def requireValidFloat(key,hdr):

  """ Returns a header keyword if a valid float """

  val = hdr.get(key)
  try: 
    if type(val) == float:
      return val
  except AttributeError,ValueError:
    pass
  raise HeaderException ("Invalid float at key %s" % key)

def requireValidInt(key,hdr):

  """ Returns a header keyword if a valid integer """

  val = hdr.get(key)
  try: 
    if type(val) == int:
      return val
  except AttributeError,ValueError:
    pass
  raise HeaderException ("Invalid int at key %s" % key)

def calculatePixelScale(hdr):

   """
      Calculate the pixel scale based on the first image extention. We
      assume that the pixel scale is the same on all chips
   """
   cd1_1  = requireValidFloat('CD1_1',hdr) 
   cd1_2  = requireValidFloat('CD1_2',hdr)
   pscale = '%.3f' % (sqrt(pow(cd1_1,2)+pow(cd1_2,2))*3600)
   return pscale
