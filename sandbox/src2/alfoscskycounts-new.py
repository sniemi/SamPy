#!/usr/bin/python

###################################################################
#
# Invocation: 
#
#      alfoscskycounts-new.py ALpj190003 
#
# Purpose:
#
# Calculates and returns the MEDIAN value of a (small) ALFOSC skytest
# image and an estimate of the BIAS level.  Expects full CCC X-range
# in order to have over/underscan for bias determination.
# This version also returns the 90%-percentile, which gives
# better estimate than median for vignetted filters.
#
# If X-windowing is detected, then set bias level to `defaultbias`
#
# Description:
#
# The script uses IRAF imstat to get the statistics,
# with one sigma-clipping iteration.
#
# Binning allowed, but a warning will be displayed.
# X-windowing allowed, but the bias level will be assumed from
# parameter`defaultbias` .
#
# Bugs:
# - is known to fail on AB-mode polarimetry flats
#
#
#    JHT, May 2007
#    updated JHT, Feb 2008
#    updated JHT, May 2008
#    updated JHT, Jul 2008  (for polarimetry flats)
#
###################################################################

defaultbias=350

###################################################################

import sys
from os import path, chdir, environ, getenv

# Start IRAF, but first set TERM environment if it is not set,
# to suppress stupid error message....
if getenv("TERM") == None:
  environ["TERM"] = 'xterm'

from pyraf import iraf


# Check syntax

if len(sys.argv) != 2:
  print "\nUsage: this script needs (only) 1 argument, which is \
     an ALFOSC image. "
  print "Examples:  ./alfoscskytest.py  ALpk110123"
  print "           ./alfoscskytest.py  ALpk110123.fits\n"
  sys.exit(1)


workdir="/home/qc-user/alfosc/skyflats/"
chdir(workdir)

datadir="/raid1/data/alfosc/"



# Determine filename of first bias, and strip ".fits" if present
arglist=sys.argv[1]

spos = arglist.rfind(".fits")
if spos == -1: spos=len(arglist)
image1 = arglist[0:spos]
image1 = image1+".fits"
#print (image1)
alfosc1 = datadir+image1+"[1]"

# Quit if one of the files does not exist

doexit= 0
if not path.exists(datadir+image1): 
  print "ALFOSC image "+datadir+image1+" not found!"
  doexit= 1

if doexit==1:  
  print "Ciao!\n"
  sys.exit(1)


# Collect data from keywords of the image.

xsiz = iraf.images.imutil.hselect(alfosc1, "NAXIS1", "yes", Stdout=1)[0]
iraf.images.imutil.imgets(alfosc1, "DETXBIN")
xbin = int(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(alfosc1, "DETYBIN")
ybin = int(iraf.images.imutil.imgets.value)

if not (xbin == 1 & ybin == 1):
   print "WARNING: binning ",xbin,",",ybin

iraf.images.imutil.imgets(alfosc1, "DETWIN1")
yw2 = iraf.images.imutil.imgets.value
xw1 = int(yw2[1:-1].split(',')[0].split(':')[0])
xw2 = int(yw2[1:-1].split(',')[0].split(':')[1])
yw1 = int(yw2[1:-1].split(',')[1].split(':')[0])
yw2 = int(yw2[1:-1].split(',')[1].split(':')[1])
#print 'Window: ',xw1,xw2,yw1,yw2

iraf.images.imutil.imgets(alfosc1, "ALAPRTNM")
apertureitem = iraf.images.imutil.imgets.value

#print apertureitem

#sys.exit(0)

# Determine the bias level.
# Use hardcoded value for windowed images.

if (str(xsiz) != str(2*int(2198/(xbin*2)))):
   print xsiz, 2*int(2198/(xbin*2))
   print "WARNING: windowed image, assuming bias=",defaultbias
   bias=float(defaultbias)
else:
   xl1=str(int(11/xbin))
   xl2=str(int(40/xbin))
   xr1=str(int(2111/xbin))
   xr2=str(int(2140/xbin))

   biasrange1="[" + xl1 + ":" + xl2 + ",*],"
   biasrange2="[" + xr1 + ":" + xr2 + ",*]"

   dummy=iraf.images.imutil.imstat(alfosc1+biasrange1+alfosc1+biasrange2, fields="midpt", nclip=1, lsigma=4, usigma=4, format="no", Stdout=1)
   #print dummy[0]
   #print dummy[1]
   if (dummy[0] == "INDEF") | (dummy[1] == "INDEF"):
      bias=float(0)
   else:
      bias=0.5 * (float(dummy[0]) + float(dummy[1]))


# Determine the median count level

imagesect='[*,*]'
if apertureitem=="Cal_90":
   print "Calcite in!"

   # define region to be used for calcite
   xc1= 751
   xc2=1500
   yc1= 651
   yc2=1400

   # find shared region between calcite and window
   x1=xc1
   x2=xc2
   y1=yc1
   y2=yc2

   if xw1>x1: x1=xw1
   if xw2<x2: x2=xw2
   if yw1>y1: y1=yw1
   if yw2<y2: y2=yw2

   if (x2-x1<2)  | (y2-y1<2) :
      print 'CCD window does not overlap Calcite region'
      sys.exit(1)

   # shift coordinates to absolute pixels numbers
   x1 = x1 + 1 - xw1 
   x2 = x2 + 1 - xw1 
   y1 = y1 + 1 - yw1 
   y2 = y2 + 1 - yw1 

   # scale coordinates to account for binning 
   x1=int(x1/xbin)
   x2=int(x2/xbin)
   y1=int(y1/ybin)
   y2=int(y2/ybin)

   imagesect="[" + str(x1) + ":" + str(x2) + "," + str(y1) + ":" + str(y2) + "]"
   #print imagesect

   # For percentile:
   xw1 = x1
   xw2 = x2
   yw1 = y1
   yw2 = y2



# Determine the median count level
dummy=iraf.images.imutil.imstat(alfosc1+imagesect, fields="midpt", nclip=1, lsigma=4, usigma=4, format="no", Stdout=1)[0]
#print dummy
if dummy == "INDEF":
   median=float(0)
else:
   median=float(dummy)



# Determine 90% percentile
dummy=iraf.images.imutil.imhist(alfosc1+imagesect, z1=5, z2=66000, nbins=13201, listout="yes", Stdout=1)
j = 0
threshold = 0.9*(xw2-xw1+1)*(yw2-yw1+1)
sum = 0.
while ( j < 12000 ):
   binpopul = float(dummy[j].split()[1])
   sum = sum + binpopul
   if ( binpopul > 0 ):
     print j, float(dummy[j].split()[0]), binpopul, sum, threshold
   if ( sum > threshold ):
      #print j
      break
   j = j + 1

#print j
# print results
print "    Bias           ", bias
print "    Median         ", median
print "    90%-percentile ", float(dummy[j].split()[0])

