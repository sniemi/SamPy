#!/usr/bin/python

###################################################################
#
# invocation: 
#
#      countcheck FIpj190003
#
# purpose:
#   Estimates the highest countlevels on a FIES (flatfield) image.
#
#   The algoritm is quick and dirty:
#   - bias level is not accounted for,
#   - should NOT be used for emission line spectra, or arc spectra,
#   - note that for long exposures of faint targets cosmics will up the
#     resulting countlevel estimate.
#
# description:
#   Uses IRAF imhist to make a histogram.
#   The highest of the bins with more than xsize*ysize/100000 pixels
#   will be used as an estimator of the highest count level on the image.
#
# FIES setup:
#   Any
#
#
# modifications:
#
#   Jan 08 -  JHT
#
###################################################################


import sys
from os       import path, system, environ, getenv

# Start IRAF, but first set TERM environment if it is not set,
# to suppress stupid error message....
if getenv("TERM") == None:
  environ["TERM"] = 'xterm'

from pyraf    import iraf


############# main part of script starts here ##########

# Check syntax

if len(sys.argv) != 2:
  print "\n CountCheck usage: this script needs only 1 argument, which is",\
     "the FIES image. \n"
  print " Examples:  ./countcheck.py  FIpk110123"
  print "            ./countcheck.py  FIpk110123_cal.fits\n"
  sys.exit(1)

datadir="/raid1/data/fies/"
#datadir="/raid1/data/fies/FIra14/"


# Determine filename, and strip ".fits" if present
arglist=sys.argv[1]

spos = arglist.rfind(".fits")
if spos == -1: spos=len(arglist)

spos2 = arglist[0:spos].rfind("_cal")
calsize = 4
calstring = "_cal"
if spos2 == -1: 
   calsize=0
   calstring = ""

image1 = arglist[0:spos]
imagebase = image1[:len(image1)-4-calsize]
image1nr = int(image1[len(image1)-4-calsize:len(image1)-calsize])
image1 = image1+".fits"

# Quit if the file does not exist
if not path.exists(datadir+image1): 
  print " CountCheck:  image "+datadir+image1+" not found!"
  sys.exit(1)


#iraf.images()
#iraf.images.imutil()

# Collect some data from keywords of the image.
iraf.images.imutil.imgets(datadir+image1+"[1]", "FILMP7")
topthar = int(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(datadir+image1+"[1]", "FILMP4")
botthar = int(iraf.images.imutil.imgets.value)

if topthar==1 | botthar==1 :
  print "\n CountCheck warning: one of the ThAr lamps was on during the FIES exposure."
  print " The highest countlevel CountCheck finds might not be accurate.....\n\n"

xsize = int(iraf.images.imutil.hselect(datadir+image1+"[1]", "NAXIS1", "yes", Stdout=1)[0])
ysize = int(iraf.images.imutil.hselect(datadir+image1+"[1]", "NAXIS2", "yes", Stdout=1)[0])
print " CountCheck:  file "+image1+"        X size ",xsize,"     Y size ",ysize

#image1 = datadir+image1+"[1]"

lines=iraf.images.imutil.imhist(datadir+image1+"[1]", z1=12., z2=66012., nbins=2640, listout='yes', autoscale='no', top_closed='no', hist_type='normal', Stdout=1)

jj=len(lines)
ii=0
highbin=0
while ( ii <= jj-1 ):
#  if int(lines[ii].split()[1]) > 0:
#     print ii, lines[ii]
   if int(lines[ii].split()[1]) > xsize*ysize/100000 :
      highbin=ii
   ii = ii+1

print " CountCheck:  high countlevel estimate (histogram bins of 25 counts):"
print " ",int(float(lines[highbin].split()[0])+0.5)

