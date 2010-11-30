#!/usr/bin/python2.4

DEBUG = 1

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
from postprocess import flattenImageALFOSC
from shutil import copy

# Default arguments
par = {
  'path': '/raid1/data/alfosc',
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
      print "  path=<path>  Default path: /raid1/data/alfosc/"
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
     par['im'] = getLatestImage(par['path'],'AL')
     print "Using image " + par['path'] + "/" + par['im'] 
   except: # If the image does not exist, we will be told ...
     pass   

#
# Define absolute filename, with and without the .fits extention
#

rootnm,ext = os.path.splitext(par['im'])
image  	= os.path.join(par['path'], rootnm)
imagef 	= image + '.fits'

#
# Check if the FITS file exists
#
if not os.path.exists(imagef): 
   print "ALFOSC image %s not found! Exiting ..." % imagef
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
if (getval(imagef,'AMPLMODE',0) == 'AB'):   
   flattenImageALFOSC(imagef,'/tmp/alfosc.fits')  
   imagef = '/tmp/alfosc.fits'

display.loadSingleFits(ds9_title,imagef,1)  
display.loadSingleFits(ds9_title,imagef,2)  

#
# Write to Talker
#
msg = "[DEBUG]: %s: Display started" % par['im']
writeTalker('postprocess.display',msg)

sleep(5)

# Overlay the DS9 display with information from 
# the automatic seeing analysis if exists

seeing_fn = "/home/postprocess/seeing_mon/logs/alfosc/%s/%s.ds9" % (par['im'][:-4],par['im'])
if os.path.exists(seeing_fn):
  display.overlayRegions(ds9_title,seeing_fn,1)
  writeTalker('postprocess.display',"[DEBUG]: %s: Overlaying Seeing Analysis Regions" % par['im'])
else:
  writeTalker('postprocess.display',"[DEBUG]: %s: No regions to overlay" % par['im'])
