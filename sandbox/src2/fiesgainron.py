#!/usr/bin/python

import sys
from math     import sqrt
from os       import path, remove, chdir, rmdir, system
from tempfile import mkdtemp
from pyraf    import iraf

###################################################################
#
# invocation: 
#
#      fiesgainron FIpj190003_cal 
#
# purpose:
#
# calculates and returns the gain and ron of the CCD on FIES.
#
# description:
#
# This script calculates the gain and read noise from two bias
# exposures and two flat fields. The exposures must be in consecutive
# FITS files, first 2 bias, then 2 flats, and the first of the 
# two bias frames should be passed as the only parameter to the script. 
#
# The files must have the same amplifier and gain mode. Also the flat
# field exposure times must be the same. This routine carves the part
# of the frame up in boxes and determines the gain on each box. Then
# the median value is determined as the final gain value.
#
# For the computation of the gain small vertical boxes of 1x25 pixes
# are used.  Two regions have been selected for computations: one on
# the Left and one on the Right part of the CCD.  This to have the
# distinction for AB amplifier mode.
#
# For the image statistics the IRAF task 'imstat' is used, with one
# 4-sigma clipping iteration.  The error biaslevel on the resulting
# bias level (in ADU !!) is the imstat stddev value.
#
# For the gain and RON this script computes median and stddev from the
# values found for all boxes.  For the computation of the stddev the
# median is used rather than the mean: sum of (X_i - median)**2 and
# the script outputs the error-in-mean computed as
# sttdev/sqrt(number-of-boxes).  The units are e-/ADU for gain,
# and e- for the RON values.
# 
# WARNINGS are sent by email to the address defined in
# the 'mailaddress' variable (see below).
# 
# required FIES setup:
# - make sure dome is dark
# - use 200-micron fiber
# - (defocus the spectrograph) <-- not necesary
# - take 2 bias frames and 2 equally illuminated flats
#
# Use boxsize=25 for FIES
#
# If you subtract a single number as bias level, the task runs faster!
# And this is what it does, now, avoiding 'findgain' .
#
# modifications:
#
#    nov 96 -  first created by RGMR (ccd_gain.cl)
#    dec 99 -  JHT: adapted for use with ues (ues_gain_ron.cl)
#    mar 00 -  JHT: adapted for use with wyffos (wyffos_gain_ron.cl)
#    nov 03 -  JHT: adapted for use with fies (fies_gain_ron.cl)
#    nov 06 -  JHT: pyraf version for automised qc (fiesgainron.py)
#
###################################################################


# Make exit procedure
def exitNow(code):

  if code==1:
    system ('echo fiesgainron.py '+image1+' data-not-found warning | /usr/bin/mail -s "FIES gainron Warning" '+mailaddress)   
  if code==2:
    system ('echo fiesgainron.py '+image1+' bias-expotime warning | /usr/bin/mail -s "FIES gainron Warning" '+mailaddress)   
  if code==3:
    system ('echo fiesgainron.py '+image1+' header-setup warning | /usr/bin/mail -s "FIES gainron Warning" '+mailaddress)   

  print "Ciao!\n"
  chdir(workdir)
  if code<=3: rmdir(tempdir)
  sys.exit(0)


############# main part of script starts here ##########

# Check syntax

if len(sys.argv) != 2:
  print "\nUsage: this script needs (only) 1 argument, which is",\
     "the first of four FIES images. \nThe correct order of the",\
     "images: two bias, two flats."
  print "Examples:  ./fiesgainron.py  FIpk110123"
  print "           ./fiesgainron.py  FIpk110123_cal.fits\n"
  sys.exit(0)

# Define who should receive the warning emails
#mailaddress="jht@not.iac.es,jclasen@not.iac.es"
mailaddress="jht@not.iac.es"

workdir="/home/qc-user/fies/gainron/"
tempdir=mkdtemp("","fgrtmp",workdir)
chdir(tempdir)

#datadir="/raid1/data/fies/FIpj19/"
datadir="/raid1/data/fies/FIESgainron/"
datadir="/mnt/usbdisk2/obs/FIESgainron/"


# Determine filename of first bias, and strip ".fits" if present
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


# Determine names of second bias, and the two flats, add ".fits"

imagebase = image1[:len(image1)-4-calsize]
image1nr = int(image1[len(image1)-4-calsize:len(image1)-calsize])
image2nr = image1nr+1
image3nr = image1nr+2
image4nr = image1nr+3
image1 = image1+".fits"
image2 = imagebase+("%04d%s.fits" % (image2nr,calstring))
image3 = imagebase+("%04d%s.fits" % (image3nr,calstring))
image4 = imagebase+("%04d%s.fits" % (image4nr,calstring))

print (image1, image2, image3, image4)

# Quit if one of the files does not exist

doexit= 0
if not path.exists(datadir+image1): 
  print "Bias image "+datadir+image1+" not found!"
  doexit= 1
if not path.exists(datadir+image2): 
  print "Bias image "+datadir+image2+" not found!"
  doexit= 1
if not path.exists(datadir+image3): 
  print "Flat image "+datadir+image3+" not found!"
  doexit= 1
if not path.exists(datadir+image4): 
  print "Flat image "+datadir+image4+" not found!"
  doexit= 1

if doexit==1:    exitNow(1)


# Check if first images are bias frames

#iraf.images()
#iraf.images.imutil()

iraf.images.imutil.imgets(datadir+image1+"[1]","EXPTIME")
exptime=int(float(iraf.images.imutil.imgets.value))
if exptime!=0: 
  print "Bias image "+datadir+image1+" has non-zero exposure time!"
  print "Exposure time = ",exptime
  doexit= 1

iraf.images.imutil.imgets(datadir+image2+"[1]","EXPTIME")
exptime=int(float(iraf.images.imutil.imgets.value))
if exptime!=0: 
  print "Bias image "+datadir+image2+" has non-zero exposure time!"
  print "Exposure time = ",exptime
  doexit= 1

if doexit==1:    exitNow(2)



bias1 = datadir+image1+"[1]"
bias2 = datadir+image2+"[1]"
flat1 = datadir+image3+"[1]"
flat2 = datadir+image4+"[1]"


# Collect data from keywords of first flat image.
# Other images are assumed to have an identical format,
# and detector settings.

print  "\nCollecting data from keywords... \n" 

iraf.images.imutil.imgets(bias1, "DATE-OBS")
obsdate = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(bias1, "CCDTEMP")
ccdtemp = float(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(bias1, "CHIPID")
chipid = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(bias1, "MPP")
mppmode = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(flat1,"EXPTIME")
flatexptime=float(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(flat1, "CCDNAME")
detector = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(flat1, "GAINM")
gainmode = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(flat1, "AMPLM")
amplmode = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(flat1, "FIFMSKNM")
maskpos = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(flat1, "FICARMNM")
armpos = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(flat1, "FILMP6")
halogen = iraf.images.imutil.imgets.value

print "Instrument setup:\nArm            ", armpos
print "Mask           ", maskpos
print "Halogen (0/1)  ", halogen


### Loosen this check because the big fibers' illumination is
#   problematic still.  

# if (maskpos!="F1 LowRes") | (armpos!="F1 LowRes Halogen") | (halogen!="1"):
#   print ("\nWrong instrument setup !\nUse Low-Res fiber with halogen.")
#   doexit= 1
if (halogen!="1"):
  print ("\nWrong instrument setup !\nUse halogen.")
  doexit= 1


xsize = int(iraf.images.imutil.hselect(flat1, "NAXIS1", "yes", Stdout=1)[0])
ysize = int(iraf.images.imutil.hselect(flat1, "NAXIS2", "yes", Stdout=1)[0])
print "X size ",xsize,"   Y size ",ysize

iraf.images.imutil.imgets(flat1, "DETXBIN")
xbin = int(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(flat1, "DETYBIN")
ybin = int(iraf.images.imutil.imgets.value)
print "X binning ",xbin,"   Y binning ",ybin
print " " 

#if (xsize != 2148/xbin) | (ysize != 2052/ybin):
if (xsize != 2198-(xbin-1)*1100) | (ysize != 2052/ybin):
  print "\nUse full-frame readout: no windowing !\n"
  doexit= 1

if doexit==1:    exitNow(3)


# This sets the box size!!
npix = int(24/ybin) + 1
#npix = 100



#
# xbegin, xend : begin and end value in x within the digitized frame
#                where gain can be measured.
# ybegin, yend : begin and end value in y within the digitized frame
#                where gain can be measured.
#


loop=0

while (loop<2):

   loop=loop+1

   if loop==1 :
     sortgainfile='../sortgainL'
     sortronfile='../sortronL'
     lowthreshold=3000
     xbegin=1+600/xbin
     xend  =xbegin+400/xbin -1
   
   if loop==2 :
     sortgainfile='../sortgainR'
     sortronfile='../sortronR'
     lowthreshold=10000
     xbegin=1+1300/xbin
     xend  =xbegin+400/xbin -1
   
   ybegin=1+ 700/ybin
   yend  =ybegin+600/ybin -1
      
#  print "\n\nX  %d-%d    Y %d-%d" % (xbegin, xend, ybegin, yend)
   
   
   print "Removing old temporary files ...."
   if path.exists("fgrb1.fits"):      remove ("fgrb1.fits")
   if path.exists("fgrb2.fits"):      remove ("fgrb2.fits")
   if path.exists("fgrf1.fits"):      remove ("fgrf1.fits")
   if path.exists("fgrf2.fits"):      remove ("fgrf2.fits")
   if path.exists("fgrbiasdif.fits"): remove ("fgrbiasdif.fits")
   if path.exists("fgrflatdif.fits"): remove ("fgrflatdif.fits")
   
   
   print ("Making local copies ...")
   
   bias1 = datadir+image1+"[1]"
   bias2 = datadir+image2+"[1]"
   flat1 = datadir+image3+"[1]"
   flat2 = datadir+image4+"[1]"
   
   xyrange="["+str(xbegin)+":"+str(xend)+","+str(ybegin)+":"+str(yend)+"]"
   iraf.images.imutil.imcopy(bias1+xyrange, "fgrb1")
   iraf.images.imutil.imcopy(bias2+xyrange, "fgrb2")
   iraf.images.imutil.imcopy(flat1+xyrange, "fgrf1")
   iraf.images.imutil.imcopy(flat2+xyrange, "fgrf2")
   
   bias1="fgrb1"
   bias2="fgrb2"
   flat1="fgrf1"
   flat2="fgrf2"
   
   iraf.images.imutil.imarith(flat1,"-",flat2,"fgrflatdif")
   iraf.images.imutil.imarith(bias1,"-",bias2,"fgrbiasdif")
   
   xbegin2=xbegin
   xend2  =xend  
   ybegin2=ybegin
   yend2  =yend  
   
   xbegin=1
   xend  =400/xbin
   ybegin=1
   yend  =600/ybin
   
#  print "\nX range   %4d-%4d" % (xbegin,xend)
#  print "Y range   %4d-%4d" % (ybegin,yend)


#  Determine the number of boxes of size npix square that will fit
#  in the useful image area.
   
   nx   = xend-xbegin+1          # for FIES use boxes of width 1
   ny   = int((yend-ybegin+1)/npix)
   
   print "\nY boxsize %3d     Number of boxes:  nX=%d   nY=%d   total=%d" % (npix, nx,ny,nx*ny)
   
   if ( nx <= 0) | (ny <= 0 ):
      print "CCD readout window too small" 
      print "Decrease box size !" 
   
   
#  Use only one value for the BIAS to speed things up!
   xyrange="["+str(xbegin)+":"+str(xend)+","+str(ybegin)+":"+str(yend)+"]"
   #tmpbias1 = float(iraf.images.imutil.imstat(bias1+xyrange, fields="midpt,stddev", format="no", Stdout=1)[0])
#  print "bias section ", bias1+xyrange
   bias1data = iraf.images.imutil.imstat(bias1+xyrange, fields="midpt,stddev", nclip=1, lsigma=4, usigma=4, format="no", Stdout=1)[0]
#  print "bias stats", bias1data
   tmpbias1 = float(bias1data.split()[0])
   tmpbias1err = float(bias1data.split()[1])
#  print "bias stats", bias1data, tmpbias1, tmpbias1err

#  Now cycle through all sub-windows and determine gain and read noise
#  *not* using the iraf findgain procedure
   
   
#  f4 = open('fgrtemp4','w')
   
   print "Working on box ...  ",
   sys.stdout.flush()
   
   maxflux = 0.0
   datalist = []
   nout = 0
   nbox = 0
   j = 1
   
   while ( j <= ny ):
      i = 1
      while ( i <= nx ):
         nbox = nbox+1
         nboxdum = nbox/100.0
         nboxdum = nboxdum - int(nboxdum)
         if nboxdum == 0 : print "%d" % nbox,
         sys.stdout.flush()
         x1 = xbegin-1+i          # for Wyffos/FIES
         x2 = x1                  # use boxes of width 1
         y1 = ybegin-1+(j-1)*npix+1
         y2 = y1+npix-1
         xyrange="["+str(x1)+":"+str(x2)+","+str(y1)+":"+str(y2)+"]"
   
         dummy=iraf.images.imutil.imstat(flat1+xyrange, fields="midpt,stddev", nclip=1, lsigma=4, usigma=4, format="no", Stdout=1)[0]
#        print dummy, xyrange
         if dummy.split()[0] == "INDEF":
           tmpflux1=66000
           tmpstd=0
         else:
           tmpflux1=float(dummy.split()[0])
           tmpstd=float(dummy.split()[1])
#        print dummy,dummy.split(),tmpflux1,tmpstd
   
         if (tmpflux1>lowthreshold) & (tmpflux1<45000):
               if tmpflux1>maxflux: maxflux=tmpflux1
               tmpflux2=float(iraf.images.imutil.imstat(flat2+xyrange, 
                  fields="midpt", format="no", Stdout=1)[0])
#              tmpbias1=float(iraf.images.imutil.imstat(bias1+xyrange, 
#                 fields="midpt", format="no", Stdout=1)[0])
#              tmpbias2=float(iraf.images.imutil.imstat(bias2+xyrange, 
#                 fields="midpt", format="no", Stdout=1)[0])
               tmpflatdifstddev=float(iraf.images.imutil.imstat("fgrflatdif"+xyrange, 
                  fields="stddev", nclip=1, lsigma=4, usigma=4, format="no", Stdout=1)[0])
               tmpbiasdifstddev=float(iraf.images.imutil.imstat("fgrbiasdif"+xyrange, 
                  fields="stddev", nclip=1, lsigma=4, usigma=4, format="no", Stdout=1)[0])
               tmpgain=(tmpflux1+tmpflux2-tmpbias1-tmpbias1)/ \
                  (tmpflatdifstddev*tmpflatdifstddev - tmpbiasdifstddev*tmpbiasdifstddev)
               tmpron=tmpgain*tmpbiasdifstddev/1.4142
   
#              print >> f4, "%5.2f %5.2f %5.2f %10.2f %10.2f" % (tmpgain,
#                       tmpron,tmpstd/tmpflux1,tmpflux1,tmpstd)  
   
               datalist.append([tmpgain,tmpron,tmpstd/tmpflux1,tmpflux1,tmpstd])
   
               nout = nout+1
         i = i+1
      j = j+1
   
#  f4.close()
   
   
#  for xx in datalist:
#     print "%5.2f %5.2f %5.2f %10.2f %10.2f" % (xx[0],xx[1],xx[2],xx[3],xx[4])
   
   j = nout*2/3 + 1
#  if j<1000/xbin :
   if j<500/xbin :
     print ("\n\n\n   WARNING: few useful boxes. Check count levels in flats.")
     print ("                Or use smaller boxsize!\n")
     system ('echo fiesgainron.py '+image1+' low-box warning: loop '+str(loop)+' only '+str(j)+' boxes | /usr/bin/mail -s "FIES gainron Warning" jht@not.iac.es')     
     if j<100/xbin :  exitNow(4)

   print "\nKeeping the %d boxes with best relative STDDEV" % j
   
#  Fancy way to sort on the 3rd column:
#  datalist.sort(lambda xx1,xx2: cmp(xx1[2], xx2[2]))
   
#  Possibly understandable way:
#  define a cmp function that compares the 3rd element of two lists
   def mycompfunc(xx1,xx2):
      return cmp(xx1[2],xx2[2])
   
#  Use the sort method, and specify what sort function it should use.
   datalist.sort(mycompfunc)
   
   ii=0
   gainlist = []
   ronlist = []
   for xx in datalist[:j]:
     gainlist.append(xx[0])
     ronlist.append(xx[1])
#    print "%d %5.2f %5.2f %5.2f %10.2f %10.2f" % (ii,xx[0],xx[1],xx[2],xx[3],xx[4])
#    print "%d %5.2f %5.2f %5.2f %10.2f %10.2f" % (ii,gainlist[ii],ronlist[ii],xx[2],xx[3],xx[4])
     ii = ii+1
    
   gainlist.sort()
   ronlist.sort() 

#  for xx in gainlist:
#     print xx
#  ii=0
#  for xx in ronlist:
#     print ii, ii+1, xx
#     ii = ii+1


#  Determine median, min and max values.
#  discard the absolute low and high, when determining min and max values
   
   k = (j / 2) + 1
   print "Using entry %d of the sorted GAIN and RON values as median\n" % k
   
   gainmin=gainlist[2]
   gainmed=gainlist[k]
   gainmax=gainlist[-3]
   
   ronmin=ronlist[2]
   ronmed=ronlist[k]
   ronmax=ronlist[-3]

#  Compute std values, while discarding outliers
#  Use the median as an estimator for the mean in order to compute the error-in-mean
   if path.exists(sortgainfile):  remove(sortgainfile)
#  f4 = open(sortgainfile,'w')
   Gsqsum=0.0
   ii=0
   for xx in gainlist[4:j-25]:  ## discard outliers
     Gsqsum=Gsqsum+xx*xx
#    print >> f4, xx
     ii = ii+1
#  Standard expansion of standard STD formula, with median instead of mean
   gainerr=sqrt( (Gsqsum - gainmed*gainmed*ii) / (ii-1) )
#  Error in mean:
   gainerr=gainerr/sqrt(ii)
#  f4.close()

## if path.exists(sortronfile):  remove(sortronfile)
## f4 = open(sortronfile,'w')

   Rsqsum=0.0
   for xx in ronlist[4:j-25]:
     Rsqsum=Rsqsum+xx*xx

##   print >> f4, xx

   ronerr=sqrt( (Rsqsum - ronmed*ronmed*ii) / (ii-1) )
   ronerr=ronerr/sqrt(ii)

## f4.close()

#  print "Gain med, std, error-in-mean", gainmed, gainerr, gainerr/sqrt(ii), ii
#  print "RON med, std, error-in-mean ", ronmed, ronerr, ronerr/sqrt(ii), ii


   print "Observation date: "+obsdate
   print "Files:  "+image1+"  "+image2+"  "+image3+"  "+image4
   print "Results for " + detector + ", amplifier " + \
           amplmode + " in " + gainmode + " gain mode, " + \
           str(xbin) + "x"+str(ybin)+" binning :"
   print "  pixel range    X %d-%d    Y %d-%d" % \
           (xbegin2, xend2, ybegin2, yend2)
   
   print "  median gain is %4.2f e-/ADU     \
          ranging from %4.2f to %4.2f e-/ADU"  % (gainmed, gainmin, gainmax)
   print "  median read noise is %4.2f e-   \
          ranging from %4.2f to %4.2f e-\n\n" % (ronmed, ronmin, ronmax)


#  Clean up the temporary files
   if path.exists("fgrb1.fits"):      remove ("fgrb1.fits")
   if path.exists("fgrb2.fits"):      remove ("fgrb2.fits")
   if path.exists("fgrf1.fits"):      remove ("fgrf1.fits")
   if path.exists("fgrf2.fits"):      remove ("fgrf2.fits")
   if path.exists("fgrbiasdif.fits"): remove ("fgrbiasdif.fits")
   if path.exists("fgrflatdif.fits"): remove ("fgrflatdif.fits")

#  Store left-side values
   if loop==1 :
      leftgain=gainmed
      leftgainerr=gainerr
      leftron=ronmed
      leftronerr=ronerr
      leftmaxflux=maxflux
      leftbias=tmpbias1
      leftbiaserr=tmpbias1err

####### This is where the left/right loop ends #######


# Write results
#print "\ndetector  " + detector
#print "chipid    " + chipid
#print "amplifier " + amplmode
#print "gainmode  " + gainmode
#print "binning   " + str(xbin) + "x"+str(ybin)
#print "\ndate     ",obsdate
#print "files     "+image1+"  "+image2+"  "+image3+"  "+image4
#print "ccdtemp  %8.2f" % ccdtemp
#print "left part   gain,ron  %4.2f,%4.2f" % (leftgain,leftron)
#print "right part  gain,ron  %4.2f,%4.2f" % (gainmed,ronmed)

asciidb = open(workdir+'fiesgainron.database','a',1)
print >> asciidb, "%s  %s  %s  %s  %2s  %4s %3d %3d  %s %s %s %s %8.2f %7.3f %6.3f %7.2f %6.3f %8.2f %7.2f %6.2f %7.3f %6.3f %7.2f %6.3f %8.2f %7.2f %6.2f %5d %7.2f %s" % (obsdate, detector, chipid, mppmode, amplmode, gainmode, xbin, ybin, image1[0:spos], image2[0:spos], image3[0:spos], image4[0:spos], ccdtemp, leftgain, leftgainerr, leftron, leftronerr, leftmaxflux, leftbias, leftbiaserr, gainmed, gainerr, ronmed, ronerr, maxflux, tmpbias1, tmpbias1err, npix, flatexptime, maskpos)  
asciidb.close()

chdir(workdir)
rmdir(tempdir)

# Copy database to WWW
system ('scp fiesgainron.database www@www:html/instruments/qc/')     

# Initiate Quality Control script
system ('./fiesGRqc.py')     
 
print "\nCiao!"   
