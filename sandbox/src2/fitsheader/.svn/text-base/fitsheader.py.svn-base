from pyfits import getheader
import pyfits
import os

class HeaderException(Exception):
  pass


##############
### ALFOSC ###
##############

def extractALFOSCHeader(file):

  """ Extract ALFOSC keywords from a fits file """

  try:

    hdulist = pyfits.open(file)
    hdulist.close()  

    if len(hdulist) == 2:
      prihdr = hdulist[0].header  
      im1hdr = hdulist[1].header
      return ['alfosc','AL',prihdr,im1hdr]
    elif len(hdulist) == 3:
      prihdr = hdulist[0].header  
      im1hdr = hdulist[1].header
      im2hdr = hdulist[2].header
      return ['alfosc','AL',prihdr,im1hdr,im2hdr]     
    else:
      return ['ERROR']

  # Error

  except Exception, e:
    raise HeaderException(e)



##############
### NOTCAM ###
##############

def extractNOTCAMHeader(file):

  """ Extract NOTCAM keywords from a fits file """

  try:

    hdulist = pyfits.open(file)
    hdulist.close()  
        
    if len(hdulist) > 0:
      prihdr = hdulist[0].header
      a = ['notcam','NC',prihdr]
      for i in range(1, len(hdulist)):
        a.append(hdulist[i].header)	
      return a     
    else:
      return ['ERROR']

  # Error

  except Exception, e:
    raise HeaderException(e)


#############
### MOSCA ###
#############

def extractMOSCAHeader(file):

  """ Extract MOSCA keywords from fits header """


  try:

    hdulist = pyfits.open(file)
    hdulist.close()  
        
    if len(hdulist) > 0:
      prihdr = hdulist[0].header
      a = ['mosca','MO',prihdr]
      for i in range(1, len(hdulist)):
        a.append(hdulist[i].header)	
      return a     
    else:
      return ['ERROR']

  # Error

  except Exception, e:
    raise HeaderException(e)


###############
### STANCAM ###
###############

def extractSTANCAMHeader(file):

  """ Extract StanCam keywords from fits header """


  try:

    hdulist = pyfits.open(file)
    hdulist.close()  
        
    if len(hdulist) > 0:
      prihdr = hdulist[0].header
      a = ['stancam','ST',prihdr]
      for i in range(1, len(hdulist)):
        a.append(hdulist[i].header)	
      return a     
    else:
      return ['ERROR']

  # Error

  except Exception, e:
    raise HeaderException(e)


############
### FIES ###
############

def extractFIESHeader(file):

  """ Extract FIES keywords from fits header """

  try:

    hdulist = pyfits.open(file)
    hdulist.close()

    if len(hdulist) > 0:
      prihdr = hdulist[0].header
      a = ['fies','FI',prihdr]
      for i in range(1, len(hdulist)):
        a.append(hdulist[i].header)
      return a
    else:
      return ['ERROR']

  # Error

  except Exception, e:
    raise HeaderException(e)



##################
### OLD ALFOSC ###
##################

def extractOldALFOSCHeader(file):

  """ Extract headers for non-MEF ALFOSC Images """

  try:

    hdulist = pyfits.open(file)
    hdulist.close()  

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
    return ['ERROR']


  return fitsheader


### SUB ROUTINES ###

def extractHeader(file) :

   """
     Pseudo method for extracting fitsheader keywords. Will call an	
     apropriate method, depending on filename (instrument)	 
   """

   headerDispatching = {
   	'AL': extractALFOSCHeader,
   	'NC': extractNOTCAMHeader,
   	'MO': extractMOSCAHeader,
   	'ST': extractSTANCAMHeader,	
	'FI': extractFIESHeader
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
