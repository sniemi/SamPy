#!/usr/bin/python2.4

DEBUG = 1

datadir     = "/raid1/data/alfosc"
mergedir    = "/raid1/data/tempdata/"
fifopath    = "/home/postprocess/alfosc/"            
pymodules   = "/home/postprocess/python_modules/"
ds9_title   = "ALFOSC"     	    	    
ds9geometry = "+100+0"                         

import sys
import os
sys.path.append(pymodules)
from ds9 import *
from pyfits import getval
from postprocess import writeTalker
from postprocess import getLatestImage
from postprocess import mergeALFOSC
from shutil import copy

# Default arguments
par = {
  'im'	: '',
  'zscale' : '',
  'zoom'   : ''
}


#####################
####### MAIN ########
#####################

#
# Go through commandline arguments
#
for arg in sys.argv[1:]:
   try:
      parname, value = arg.split('=')
      if parname in par:
         t = type(par[parname])
         par[parname] = t(value)
   except ValueError:
      print "Usage:"
      print "displayALFOSC [OPTION]..."
      print "Options:"
      print "  im=<image>   Default image: Last image in default path"
      print "  zscale=<on|off>  Default scale: Off"
      print "  zoom=<fit|off>   Default zoom: Off"
      sys.exit()

if DEBUG: print par

#
# If no image name has been specified, choose the one with latest timestamp.
#
if (par['im'] == ''):
   try:
     par['im'] = getLatestImage(datadir,'AL')
     print "Using image " + datadir + "/" + par['im'] 
   except: # If the image does not exist, we will be told ...
     pass   

path,filenm = os.path.split(par['im'])
if path == '': path = datadir
basenm,ext = os.path.splitext(filenm)
if ext == '': ext = '.fits'

fits_nm   = basenm + ext  	       # full image path
fits_file = os.path.join(path,fits_nm) # filename with extention

#
# Check if the FITS file exists
#
if not os.path.exists(fits_file): 
   print "ALFOSC image %s not found! Exiting ..." % fits_file
   sys.exit()

#
# Start a DS9 display
#

display = DS9(fifopath)

if (display.ds9_exists(ds9_title) == 0):
   display.start_ds9(ds9_title,ds9geometry,fifopath)


#
# Display image in DS9
#
if (getval(fits_file,'AMPLMODE',0) == 'AB'):   
   outfile = os.path.join(mergedir, fits_nm)
   if not os.path.isfile(outfile):
     mergeALFOSC(fits_file,outfile)  
   fits_file = outfile

display.loadSingleFits(ds9_title,fits_file,1)  
display.loadSingleFits(ds9_title,fits_file,2)  

#
# Write to Talker
#
msg = "[DEBUG]: %s: Display started" % fits_nm
#writeTalker('postprocess.display',msg)

#sleep(5)

# Overlay the DS9 display with information from 
# the automatic seeing analysis if exists

seeing_fn = "/home/postprocess/seeing_mon/logs/ALFOSC/%s/%s.ds9" % (fits_nm[:-9],basenm)
print seeing_fn
if os.path.exists(seeing_fn):
  display.overlayRegions(ds9_title,seeing_fn,1)
  writeTalker('postprocess.display',"[DEBUG]: %s: Overlaying Seeing Analysis Regions" % fits_nm)
else:
  writeTalker('postprocess.display',"[DEBUG]: %s: No regions to overlay" % fits_nm)
