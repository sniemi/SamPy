#!/usr/bin/python

###################################################################
#
# invocation: 
#
#      countcheck-emission FIpj190003
#
# purpose:
#   Estimates the highest countlevels on a FIES ThAr spectrum image.
#
#   The algorithm is quick and dirty:
#   - bias level is not accounted for,
#   - should NOT be used for continuum spectra.
#
# description:
#   Uses IRAF daofind to find the highest peak.
#   Then uses IRAF imstat to find the MAX value in a 21x21 pixel
#   area centered around the peak.
#
# FIES setup:
#   Any
#
#
# modifications:
#
#   Jan 08 - JHT
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
  print " Examples:  ./countcheck-emission.py  FIpk110123"
  print "            ./countcheck-emission.py  FIpk110123_cal.fits\n"
  sys.exit(1)

datadir="/raid1/data/fies/"


# Determine filename, and add ".fits" if needed
arg1 = sys.argv[1]

spos = arg1.rfind(".fits")
if spos == -1: spos=len(arg1)

image1 = arg1[0:spos]+".fits"


# Quit if the file does not exist
if not path.exists(datadir+image1): 
  print " CountCheck:  image "+datadir+image1+" not found!"
  sys.exit(1)


# Load IRAF packages
#iraf.images()
#iraf.images.imutil()


# Check FITS headers to see if the wrong lamp was on.
iraf.images.imutil.imgets(datadir+image1+"[1]", "FILMP6")
tophalo = int(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(datadir+image1+"[1]", "FILMP1")
bothalo = int(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(datadir+image1+"[1]", "FILMP4")
botthar = int(iraf.images.imutil.imgets.value)

if tophalo==1 | bothalo==1 :
  print "\n CountCheck-Emission warning: one of the halogen lamps was on during the FIES exposure."
  print " The highest countlevel found might not be accurate.....\n\n"


# Check FITS headers to see which fiber was used
iraf.images.imutil.imgets(datadir+image1+"[1]", "FIFMSKNM")
fiber = iraf.images.imutil.imgets.value.split()[0]


# Set estimate of PSF FWHM:  3 pixels for fib#4 and #5, more for the other fibers
# This is needed for DAOphot
fwhm = 4.0                     # med/high res 
if fiber == "F1": fwhm=7.0     # low res
if botthar == 1 : fwhm=4.0     # F5 ThAr

# Set axis ratio of PSF:  0.5  for fib#4 and #5, and  1.0  for fib#1 and #3, 
# This is needed for DAOphot
ratio = 1.0                                         # low/med res 
if (fiber == "F4") | (botthar == 1):  ratio=0.5     # F4/F5

print fiber, fwhm, ratio

#### todo: handle  BINNING


# Check FITS headers to determine the image X,Y size
xsize = int(iraf.images.imutil.hselect(datadir+image1+"[1]", "NAXIS1", "yes", Stdout=1)[0])
ysize = int(iraf.images.imutil.hselect(datadir+image1+"[1]", "NAXIS2", "yes", Stdout=1)[0])
print " CountCheck-Emission:  file "+image1+"        X size ",xsize,"     Y size ",ysize


# Load more IRAF packages and set the crucial variables
iraf.noao.digiphot(_doprint=0)
iraf.noao.digiphot.daophot(_doprint=0)
iraf.noao.digiphot.daophot.verify='n'
iraf.noao.digiphot.daophot.datapars.sigma=3
iraf.noao.digiphot.daophot.datapars.readnoise=3
iraf.noao.digiphot.daophot.datapars.fwhmpsf=fwhm
iraf.noao.digiphot.daophot.findpars.ratio=ratio
iraf.noao.digiphot.daophot.datapars.ccdread=""


# Let DAOfind find emission lines
lines=iraf.noao.digiphot.daophot.daofind(datadir+image1+"[1]", " ", Stdout=1)


# print DAOfind output on STDOUT
#jj=0
#while jj < (len(lines)):
#  print jj, lines[jj]
#  jj=jj+1


# Find 'object' with highest peak value in all 'objects' that are returned by DAOfind
maxbright=0.0
jj=3
while jj < (len(lines) - 3):
# print jj, lines[jj]
  if float(lines[jj].split()[2]) < maxbright:
     maxbright =float(lines[jj].split()[2])
     xpos=float(lines[jj].split()[0])
     ypos=float(lines[jj].split()[1])
     mbjj=jj
  jj=jj+1

#print "len = ", len(lines)
#print 0,lines[0]
#print 1,lines[1]
#print 2,lines[2]
#print 3,lines[3],lines[3].split()[2]
#print -4,lines[-4]
#print -3,lines[-3]
#print -2,lines[-2]
#print -1,lines[-1]

#print lines[mbjj]
#print xpos, ypos, maxbright
print " CountCheck-Emission:  DAOphot X,Y position of brightest line     ", xpos, ",", ypos


# Round X,Y position to integers and set start and end coordinates of examination box 
xpos=int(0.5+xpos)
ypos=int(0.5+ypos)
x1=xpos-10
x2=xpos+10
y1=ypos-10
y2=ypos+10

if x1<1     : x1=1
if x2>xsize : x2=xsize
if y1<1     : y1=1
if y2>ysize : y2=ysize

xyrange="["+str(x1)+":"+str(x2)+","+str(y1)+":"+str(y2)+"]"


# Use IMSTAT to find maximum value in examination box
lines=iraf.images.imutil.imstat(datadir+image1+"[1]"+xyrange, fields='max', Stdout=1)


# print IMSTAT output on STDOUT
#jj=0
#while jj < len(lines):
#  print jj,lines[jj]
#  jj=jj+1

print " CountCheck-Emission:  high countlevel estimate ( MAX pixel value in section",xyrange,"):"
print " ",int(0.5+float(lines[1]))

