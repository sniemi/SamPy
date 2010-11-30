#!/usr/bin/python2.4

workdir     = "/home/postprocess/alfosc/focuspyr/"
fifopath    = "/home/postprocess/alfosc/"
irafdir     = "/home/postprocess/alfosc/" 	
pymodules   = "/home/postprocess/python_modules"
logfilenm   = "focuspyramid.log"		
ds9_title   = "ALFOSC"
ds9_frame   = "2"

import sys
import os
from math import sqrt
sys.path.append(pymodules)
from ds9 import *
from postprocess import *
from pyfits import getval


DEBUG = 1

##
## Define calibrated focus pyramid parameters for ALFOSC NO BINING
##
boxsize                 = 22.00
refdistance             = 44.57
pyramidscalefactor      = 28.00

#####################
####### MAIN ########
#####################

display = DS9(fifopath)

# Check we have a valid DS9 session 
if (display.ds9_exists(ds9_title) == 0):
  print "Error: No ALFOSC DS9 instance found!"
  writeTalker('postprocess.focuspyr',"[DEBUG]: No ALFOSC DS9 instance found!")
  sys.exit(1)

# Set focus on analysis frame
display.setFrame(ds9_title,ds9_frame)


# Get filename loaded in current frame
filename = display.getFile(ds9_title)
if DEBUG: print filename


# Check from fits header for valid focuspyramid image
if (getval(filename,'ALGRNM',0) != 'Focus_Pyr'):
   print "ERROR: No valid ALGRNM string (Focus_Pyr).  Put the pyramid in the beam!   EXITing ...."
   writeTalker('alfosc.focuspyramid', '[DEBUG]: No valid ALGRNM string (Focus_Pyr). Put the pyramid in the beam')
   sys.exit()

if (getval(filename,'CCDSUM',1) != '1 1'):
   print "ERROR: Please run the Focus Pyramid on an UNBINNED Image   EXITing ...."
   writeTalker('alfosc.focuspyramid', '[DEBUG]: Please run the Focus Pyramid on an UNBINNED Image')
   sys.exit()

# Show single frame if tiled
returnToTiledDisplay = 0
if (display.isTiled(ds9_title) == 'yes'):
  returnToTiledDisplay = 1
  display.setSingle(ds9_title)


#
# Show the focus correction value on STDOUT as determined by the automatic   
# focus pyramid routine. This serves mainly to ensure the results from this image being
# inserted into database. Also, the user might find it useful for comparison purposes.
#
command = "%s%s %s" % (workdir,'alfosc.focuspyramid_auto.py',filename)
cin, cout, cerr = os.popen3(command)
res = ''.join(cout.readlines())
print "Telescope focus offset estimated from automatic analysis procedure: " + res

#
# Start IRAF. This requires a valid login.cl in directory 'irafdir'
#
os.chdir(irafdir)
from pyraf import iraf
os.chdir(workdir)

print "Each star is imaged 4 times in a diamond shape."
print "Position the pointer on the top of a diamond, and press"
print "  --> Keystroke  a  to define star coordinates ..."  
print "Then, afterwards ..."
print "  --> Keystroke  q  to obtain the focus offset value ..."
print "Finally, Keystroke 'q' to exit this task .... "

while(1):

  # Delete any existing logfile.
  try:
    os.unlink(logfilenm)
  except OSError:
    pass

  # Start imexam with logfile output
  iraf.imexam(keeplog='yes', logfile=logfilenm, Stdout = 1)

  # Read logfile and remove comment lines
  file = open(logfilenm, 'rU').readlines()
  lines = [f for f in file if not f.startswith('#') ]

  # If logfile is empty, user has pressed 'q' with marking
  # any stars which means we want to exit task.
  if ( len(lines) < 1): 
    sys.exit()

  # Get (x,y) values for last two measurements
  (x1,y1,_) = lines[-1].split(None,2)

  # find other 3 stars and compute focus offset
  x1 = float(x1)
  y1 = float(y1)
  x2=x1
  y2=y1-refdistance
  x3=x1-refdistance/2
  x4=x1+refdistance/2
  y3=y1-refdistance/2
  y4=y3

  s1 = iraf.imcntr(filename+"[1]", x1, y1, cboxsize=boxsize, Stdout = 1)
  s2 = iraf.imcntr(filename+"[1]", x2, y2, cboxsize=boxsize, Stdout = 1)
  s3 = iraf.imcntr(filename+"[1]", x3, y3, cboxsize=boxsize, Stdout = 1)
  s4 = iraf.imcntr(filename+"[1]", x4, y4, cboxsize=boxsize, Stdout = 1)

  x1 = float(s1[0].split()[2])
  y1 = float(s1[0].split()[4])
  x2 = float(s2[0].split()[2])
  y2 = float(s2[0].split()[4])
  x3 = float(s3[0].split()[2])
  y3 = float(s3[0].split()[4])
  x4 = float(s4[0].split()[2])
  y4 = float(s4[0].split()[4])

  xdist = sqrt( (x4-x3)*(x4-x3) + (y4-y3)*(y4-y3) )
  ydist = sqrt( (y1-y2)*(y1-y2) + (x1-x2)*(x1-x2) )
  meandist = (xdist + ydist)/2
  teloff = (refdistance - meandist) * pyramidscalefactor

  if DEBUG: print "Top   %6.2f %6.2f    Bottom  %6.2f %6.2f   Y-distance %5.2f" % (x1,y1,x2,y2,ydist)
  if DEBUG: print "Left  %6.2f %6.2f    Right   %6.2f %6.2f   X-distance %5.2f" % (x3,y3,x4,y4,xdist)

  if (abs(xdist-ydist) > 10):
   print "WARNING: The two distances do not match."

  print "Mean distance  %5.2f pixels" % meandist
  print "Focus correction%5d telescope focus units" % teloff

  # Write results to Talker 
  msg = "[NOTE]: Telescope focus offset: %s Units" % teloff
  writeTalker('postprocess.focuspyr',msg)

# End loop

if (returnToTiledDisplay == 1):
  display.setTile(ds9_title)