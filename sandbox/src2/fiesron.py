#!/usr/bin/python

import sys
from os import path, remove, chdir
from pyraf import iraf


###################################################################
#
# invocation: 
#
#      fiesron FIpj190003 
#
# purpose:
#
# calculates and returns the RON [in ADU] of the CCD on FIES.
#
# description:
#
# This script calculates the read noise from a bias exposure. 
# This script splits the frame up in sections and determines the RON
# on each section. Then the median is determined as the final RON
# value.
#
# The script uses IRAF imstat to get the statistics,
# with one sigma-clipping iteration.
#
# Full frame readout, binning allowed.
#
#    nov 06 -  JHT: pyraf version (fiesron.py)
#
###################################################################


# Check syntax

if len(sys.argv) != 2:
  print "\nUsage: this script needs (only) 1 argument, which is \
     the first of four FIES images. \nThe correct order of the \
     images: two bias, two flats."
  print "Examples:  ./fiesron.py  FIpk110123"
  print "           ./fiesron.py  FIpk110123.fits\n"
  exit(1)


workdir="/home/qc-user/fies/gainron/"
chdir(workdir)

#datadir="/raid1/data/fies/FIpj19/"
datadir="/raid1/data/fies/"
#datadir="/mnt/usbdisk2/obs/FIESgainron/"


# Determine filename of first bias, and strip ".fits" if present
arglist=sys.argv[1]

spos = arglist.rfind(".fits")
if spos == -1: spos=len(arglist)
image1 = arglist[0:spos]
image1 = image1+".fits"
#print (image1)
bias1 = datadir+image1+"[1]"

# Quit if one of the files does not exist

doexit= 0
if not path.exists(datadir+image1): 
  print "Bias image "+datadir+image1+" not found!"
  doexit= 1

if doexit==1:  
  print "Ciao!\n"
  exit(1)


# Check if first images are bias frames

#iraf.images()
#iraf.images.imutil()

iraf.images.imutil.imgets(bias1,"EXPTIME")
exptime=int(float(iraf.images.imutil.imgets.value))
if exptime!=0: 
  print "Bias image "+datadir+image1+" has non-zero exposure time!"
  print "Exposure time = ",exptime
  doexit= 1

if doexit==1:  
  print "Ciao!\n"
  exit(1)




# Collect data from keywords of first flat image.
# Other images are assumed to have an identical format,
# and detector settings.

print  "\nCollecting data from keywords... \n" 

iraf.images.imutil.imgets(bias1, "CCDNAME")
detector = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(bias1, "GAINM")
gainmode = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(bias1, "AMPLM")
amplmode = iraf.images.imutil.imgets.value

xsize = int(iraf.images.imutil.hselect(bias1, "NAXIS1", "yes", Stdout=1)[0])
ysize = int(iraf.images.imutil.hselect(bias1, "NAXIS2", "yes", Stdout=1)[0])
print "X size ",xsize,"   Y size ",ysize

iraf.images.imutil.imgets(bias1, "DETXBIN")
xbin = int(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(bias1, "DETYBIN")
ybin = int(iraf.images.imutil.imgets.value)
print "X binning ",xbin,"   Y binning ",ybin
print " " 

if (xsize != 2148/xbin) | (ysize != 2052/ybin):
  print "\nUse full-frame readout: no windowing !\n"
  doexit= 1

if doexit==1:  
  print "\nCiao!\n"
  exit(1)

# This sets the box size!!
nXpix = int(100/xbin)
nYpix = 2*int(100/ybin)


# xbegin, xend : begin and end value in x within the digitized frame
#                where gain can be measured.
# ybegin, yend : begin and end value in y within the digitized frame
#                where gain can be measured.


loop=0

while (loop<2):

   loop=loop+1

   if loop==1 :
     xbegin=1+int(100/xbin)
     xend  =int(1000/xbin)
   
   if loop==2 :
     xbegin=1001+int(100/xbin)
     xend  =int(2000/xbin)
   
   ybegin=1+int(20/ybin)
   yend  =int(2020/ybin)
      
#  print "\n\nX  %d-%d    Y %d-%d" % (xbegin, xend, ybegin, yend)
   
   
   print "Removing old temporary files ...."
   if path.exists("frb1.fits"):      remove ("frb1.fits")
   
   print ("Making local clipped copy ...")   
   bias1 = datadir+image1+"[1]"

   
   xyrange="["+str(xbegin)+":"+str(xend)+","+str(ybegin)+":"+str(yend)+"]"
   iraf.images.imutil.imcopy(bias1+xyrange, "frb1")
   
   bias1="frb1"
   
   xbegin2=xbegin
   xend2  =xend  
   ybegin2=ybegin
   yend2  =yend  
   
   xend  = xend - xbegin +1
   xbegin=1
   yend  = yend - ybegin +1
   ybegin=1
   
#   print "\nX range   %4d-%4d" % (xbegin,xend)
#   print "Y range   %4d-%4d" % (ybegin,yend)


#  Determine the number of boxes of size npix square that will fit
#  in the useful image area.
   
   nx   = int((xend-xbegin)/(nXpix-1))         # for FIES use boxes of width 1
   ny   = int((yend-ybegin)/(nYpix-1))
   
   print "\nX,Y boxsize %3d,%3d     Number of boxes:  nX=%d   nY=%d   total=%d" % (nXpix,nYpix, nx,ny,nx*ny)
   
   if (nx <= 0) | (ny <= 0):
      print "CCD readout window too small" 
      print "Decrease box size !" 
      doexit=1
   
   

#  Now cycle through all sub-windows and determine read noise

#  print "Working on box ...  ",
#  sys.stdout.flush()
   
   datalist = []
   nout = 0
   nbox = 0
   j = 1
   
   while ( j <= ny ):
      i = 1
      while ( i <= nx ):
         nbox = nbox+1
         nboxdum = nbox/50.0
         nboxdum = nboxdum - int(nboxdum)
#        if nboxdum == 0 : print "%d" % nbox,
#        sys.stdout.flush()
         x1 = xbegin-1+(i-1)*nXpix+1      
         x2 = x1+nXpix-1    
         y1 = ybegin-1+(j-1)*nYpix+1
         y2 = y1+nYpix-1
         xyrange="["+str(x1)+":"+str(x2)+","+str(y1)+":"+str(y2)+"]"
   
         dummy=iraf.images.imutil.imstat(bias1+xyrange, fields="stddev", nclip=1, lsigma=4, usigma=4, format="no", Stdout=1)[0]
         if dummy.split()[0] == "INDEF":
           tmpstd=float(0)
         else:
           tmpstd=float(dummy.split()[0])
#        print xyrange, tmpstd

         datalist.append(tmpstd)
         nout = nout+1
         i = i+1
      j = j+1
   
   
   datalist.sort()
#  ii=1
#  for xx in datalist: 
#     ii=ii+1
#     print "%d %5.2f" %  (ii,xx)

#  Determine median, min and max values.
#  discard the absolute low and high, when determining min and max values
   
   k = int((nout / 2) + 1)
   print "\nUsing entry %d of the sorted RON values as median" % k
   print "Using entry 3 and N-3 for min and max median values\n"
   
   ronmin=datalist[2]
   ronmed=datalist[k]
   ronmax=datalist[-3]
   
   
   print "Results for " + detector + ", amplifier " + \
           amplmode + " in " + gainmode + " gain mode, " + \
           str(xbin) + "x"+str(ybin)+" binning :"
   print "  pixel range    X %d-%d    Y %d-%d" % \
           (xbegin2, xend2, ybegin2, yend2)
   
   print "  median read noise is %4.2f ADU   \
          ranging from %4.2f to %4.2f ADU\n\n" % (ronmed, ronmin, ronmax)


#  Clean up the temporary files

   if path.exists("frb1.fits"):      remove ("frb1.fits")


print "Ciao!"   
