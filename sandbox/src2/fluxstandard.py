#!/usr/bin/python

# for old bundle use calib directory calibdata/
# for new bundle use calib directory calibdata2/
# Set the 'calibdir' parameter below accordingly !!

import sys
from math     import sqrt
from os       import path, remove, chdir, rmdir, system, listdir, readlink
from tempfile import mkdtemp
from shutil   import copy, copytree, move
from pyraf    import iraf
from pyraf    import gwm

###################################################################
#
# Invocation: 
#
#   ./fluxstandard FIqa0012 
#   ./fluxstandard -i FIqa0012     (for interactive use)
#
# Purpose:
#
#   reduce flux-standard data into system efficiency,
#   and store the results in ./reduced/ and in file FIESphotometry
#
# Description:
#
#   Some standard reduction steps are carried out,
#   and a standard wavelength solution is attached to the spectrum.
#
#   Note: as the images are clipped to 61:2088,13:2040,
#   the ThAr and Halo calib frames should be as well.
#   See ./calibdata/
#
#   Once reduced to a 1D spectrum, the FORTRAN program
#   cal2.f is used to relate the observed countrates to
#   the tabulated flux values of the standard stars
#   See ./fluxdata/
#
#   From the final efficiency spectrum, 500-Angstrom wide averages
#   are computed centered on the BVR bands.  The results are
#   stored in file ./FIESphotometry
#
#   Output:
#      ./FIESphotometry                     BVR efficiency averages
#      ./reduced/FIxxNNNNNN.fits            a copy of the original image
#      ./reduced/FIxxNNNNNNgucsd1Drn.fits   fully reduced 1D spectrum
#      ./reduced/FIxxNNNNNNgucsd1Drn.dat    same, but ASCII
#      ./reduced/F*.SP*.FIxxNNNNNN.dat      efficiency spectrum
#
# JHT, Jan 2007
#
###################################################################


# Make exit procedure
def exitNow(code):

  if code==1:
    system ('echo fluxstandard.py '+image1+' file-not-found warning | \
       /usr/bin/mail -s "FIES fluxstandard Warning" '+mailaddress)   
  if code==2:
    system ('echo fluxstandard.py '+image1+' target-name warning | \
       /usr/bin/mail -s "FIES fluxstandard Warning" '+mailaddress)   
  if code==3:
    system ('echo fluxstandard.py '+image1+' header-setup warning | \
       /usr/bin/mail -s "FIES fluxstandard Warning" '+mailaddress)   

  print "Ciao!\n"
  chdir(workdir)
  if code<=3: rmdir(tempdir)
  sys.exit(0)


############# main part of script starts here ##########



# Check syntax

arglist=sys.argv[1:]
nparam=len(arglist) 

interactive="no"
if nparam == 2:
  if arglist[0] == "-i": 
     interactive="yes"
     arglist[0]=arglist[1]
     nparam=1
  if arglist[1] == "-i": 
     interactive="yes"
     nparam=1

if nparam != 1:
  print "\n Usage:  this script needs 1 argument, which is "+ \
       "the FIES spectrum of a \n         standard star.  Additionally the '-i' flag "+\
       "may be specified to \n         enable interactive use of the script.\n"
  print " Examples:  ./fluxstandard.py FIpk110123"
  print "            ./fluxstandard.py -i FIpk110123.fits\n"
  sys.exit(0)

# Define who should receive the warning emails, e.g. "jht,jclasen"
mailaddress="jht@not.iac.es"

# Define directories
datadir="/raid1/data/fies/"
workdir="/home/qc-user/fies/fluxstandard/"

#### set this correctly #######
#calibdir=workdir+"calibdata/"
calibdir=workdir+"calibdata2/"
###############################

fluxdir=workdir+"fluxdata/"
redudir=workdir+"reduced/"
# Create temp directory
tempdir=mkdtemp("","fs-",workdir+"tmp/")
chdir(tempdir)

# Determine filename and add ".fits" if necessary
spos=arglist[0].rfind(".fits")
if spos == -1: spos=len(arglist[0])
image1 = arglist[0][0:spos]+".fits"


# Quit if the file does not exist
if not path.exists(datadir+image1): 
  datadir2=datadir+image1[0:6]+'/'
  if path.exists(datadir2+image1): 
     datadir=datadir2
  else:
     print "FIES image "+datadir+image1+" not found!"
     print "FIES image "+datadir2+image1+" not found!"
     exitNow(1)


# Define supported flux standard stars
standards=["SP0501+527", "SP1045+378", "SP1550+330", "SP2148+286", "SP2317-054"]

# Check the OBJECT/TCSTGT headers 
#iraf.images()
#iraf.images.imutil()

print "\nChecking the OBJECT keywords ... \n" 
object=iraf.images.imutil.hselect(datadir+image1+"[0]", "OBJECT", "yes", Stdout=1)[0]
print "OBJECT        ",object
iraf.images.imutil.imgets(datadir+image1+"[1]","TCSTGT")
tcstgt=iraf.images.imutil.imgets.value
print "TCS target    ",tcstgt

# Does the OBJECT or TCSTGT header hold a valid star name?
nstandard=0
found=0
for fs in standards:
  nstandard=nstandard+1
  if (object.find(fs)>-1) | (tcstgt==fs):
    object=fs
    plotsymbol=nstandard
    found=1
if found==0: 
  print "\nFIES image "+datadir+image1+" has wrong OBJECT/TCSTGT name!"
  exitNow(2)


print "\nCollecting data from essential keywords ... \n" 

iraf.images.imutil.imgets(datadir+image1+"[1]","FIFMSKID")
maskID=int(iraf.images.imutil.imgets.value)
print "MASK position = ",maskID
if (maskID!=1) & (maskID!=2) & (maskID!=3) & (maskID!=5): 
  print "FIES image "+datadir+image1+" has wrong MASK position!"
  exitNow(3)

iraf.images.imutil.imgets(datadir+image1+"[1]","AMPLM")
amplmode=iraf.images.imutil.imgets.value
print "Amplifier     = ",amplmode
if amplmode!='B': 
  print "FIES image "+datadir+image1+" has wrong amplifier mode!"
  exitNow(3)

iraf.images.imutil.imgets(datadir+image1+"[1]","GAINM")
gainmode=iraf.images.imutil.imgets.value
print "Gain          = ",gainmode
if gainmode!='HIGH': 
  print "FIES image "+datadir+image1+" has wrong gain mode!"
  exitNow(3)

iraf.images.imutil.imgets(datadir+image1+"[1]","DETXBIN")
xbin=int(iraf.images.imutil.imgets.value)
print "Xbin          = ",xbin
iraf.images.imutil.imgets(datadir+image1+"[1]","DETYBIN")
ybin=int(iraf.images.imutil.imgets.value)
print "Ybin          = ",ybin
if (xbin!=1) | (ybin!=1): 
  print "FIES image "+datadir+image1+" has wrong binning mode!"
  exitNow(3)

xsize = int(iraf.images.imutil.hselect(datadir+image1+"[1]", "NAXIS1", "yes", Stdout=1)[0])
ysize = int(iraf.images.imutil.hselect(datadir+image1+"[1]", "NAXIS2", "yes", Stdout=1)[0])
print "Xsize         = ",xsize
print "Ysize         = ",ysize

if (xsize != 2198) | (ysize != 2052):
  print "\nUse full-frame readout: no windowing !\n"
  exitNow(3)



# Make local copy
print ("\nMaking local clipped copy ...")   
iraf.images.imutil.imcopy(datadir+image1+"[1][61:2088,13:2040]", image1)
# Strip ".fits" extension
image1 =image1[0:spos]


# Read more headers
print "\nCollecting data from even more keywords ... \n" 

iraf.images.imutil.imgets(image1, "DATE-OBS")
obsdate = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(image1, "CCDTEMP")
ccdtemp = float(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(image1, "AIRMASS")
airmass = float(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(image1, "TELFOCUS")
telfocus = float(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(image1, "CHIPID")
chipid = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(image1, "MPP")
mppmode = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(image1, "EXPTIME")
exptime=float(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(image1, "CCDNAME")
detector = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(image1, "FIFMSKNM")
maskpos = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(image1, "FICARMNM")
armpos = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(image1, "FILMP6")
tophalogen = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(image1, "FILMP1")
bothalogen = iraf.images.imutil.imgets.value
iraf.images.imutil.imgets(image1, "GAIN")
gainlevel = float(iraf.images.imutil.imgets.value)
iraf.images.imutil.imgets(image1, "RDNOISE")
ron = float(iraf.images.imutil.imgets.value)

iraf.images.imutil.imgets(image1, "STFLTNM")
stfilter = iraf.images.imutil.imgets.value

print "Instrument setup:\nArm                   ", armpos
print "Mask                  ", maskpos
print "Top Halogen (0/1)     ", tophalogen
print "Bottom Halogen (0/1)  ", bothalogen


############ Start data reduction ###########

if interactive=="yes": gwm.window("FIES fluxstandard pipeline ;-)")

iraf.noao.imred(_doprint=0)
iraf.noao.imred.echelle(_doprint=0)

iraf.noao.imred.echelle.apedit.width=5.0
if (maskID==5):
   mastertharlink="masterThArF1"
   masterhalolink="masterHaloF1"
   iraf.noao.imred.echelle.apedit.width=7.0
if (maskID==1):
   mastertharlink="masterThArF2"
   masterhalolink="masterHaloF2"
if (maskID==2):
   mastertharlink="masterThArF3"
   masterhalolink="masterHaloF3"
if (maskID==3):
   mastertharlink="masterThArF4"
   masterhalolink="masterHaloF4"


print "\nCopy master calibs 'database' files to temp directory ..."
system("ls -l "+calibdir+mastertharlink+".fits")
system("ls -l "+calibdir+masterhalolink+".fits")
masterthar=readlink(calibdir+mastertharlink+".fits")
masterhalo=readlink(calibdir+masterhalolink+".fits")
copytree(calibdir+"database","./database")

# strip .fits from masterfile names
spos2=masterthar.rfind(".fits")
if spos2 != -1: masterthar=masterthar[0:spos2]
spos2=masterhalo.rfind(".fits")
if spos2 != -1: masterhalo=masterhalo[0:spos2]
print masterthar,masterhalo

print "\nMultiply by value of gain ..."
iraf.images.imutil.imarith(image1,"*",gainlevel,image1+"g",verbose="yes")

print "\nSubtracting scattered light (and bias level) ... "
print "  X fit ... "
highcut=2.5
if maskpos.split()[0]=="F1":highcut=2.0
iraf.images.imfit.fit1d (image1+"g", image1+"xfit", "fit", axis=1, function="spline3", naver=1, sample="*", \
                                 order=12, low=4, high=highcut, niter=15, interact=interactive)

print "  Y fit ... "
iraf.images.imfit.fit1d (image1+"xfit", image1+"xyfit", "fit", axis=2, function="spline3", naver=1, sample="*", \
                                 order=8, low=3, high=3, niter=7, interact=interactive)
iraf.images.imutil.imarith(image1+"g","-",image1+"xyfit",image1+"gu",verbose="yes")


print "\nKill strong cosmics ..."
iraf.images.imfilter.median(image1+"gu",image1+"m",1,7)
iraf.images.imutil.imarith(image1+"gu","-",image1+"m",image1+"r",verbose="yes")
lines=iraf.images.imutil.imstat(image1+"r",field="stddev",nclip=1,Stdout=1)
print "StdDev in filtered image ", float(lines[1])
threshold=10*float(lines[1])
iraf.images.imutil.imreplace(image1+"r",0,lower=threshold)
iraf.images.imutil.imarith(image1+"r","+",image1+"m",image1+"guc",verbose="yes")


print "\nFind and trace apertures ... "
iraf.noao.imred.echelle.aprecenter(image1+"guc", refer=masterhalo, find="no", recenter="yes", resize="no", nsum=15, \
                                           shift="yes", interact=interactive)
iraf.noao.imred.echelle.aptrace(image1+"guc", find="no", recenter="no", resize="no", trace="yes", nsum=15, \
                                        step=10, nlost=3, function="spline3", naver=1, \
                                        sample="*", order=5, low=3, high=3, niter=3, interact=interactive)

print "\n\nExtracting orders ... "
iraf.noao.imred.echelle.apsum(image1+"guc", output=image1+"gucs", find="no", recenter="no", resize="no", trace="no", \
                                      extract="yes", extras="no", review="no", backgro="none", weights="variance", \
                                      clean="yes", readnoi=ron, gain=gainlevel, interact="no")

print "\nWavelength calibration ... "
iraf.images.imutil.hedit(image1+"gucs", "REFSPEC1", masterthar+"s", add="yes", verify="no", show="yes", delete="no")
iraf.images.imutil.hedit(image1+"gucs", "THARFILE", masterthar , add="yes", verify="no", show="yes", delete="no")
iraf.images.imutil.hedit(image1+"gucs", "HALOFILE", masterhalo , add="yes", verify="no", show="yes", delete="no")
iraf.noao.imred.echelle.dispcor(image1+"gucs", image1+"gucsd", linearize="yes", flux="yes", dw="INDEF", w1="INDEF", \
                                            w2="INDEF", nw="INDEF", verbose="yes", samedisp="no", ignoreaps="no", \
                                            confirm="no", listonly="no")

print "\nMerging orders ... "
iraf.noao.imred.echelle.scombine(image1+"gucsd", image1+"gucsd1D", group="all", combi="sum", reject="none", \
                                            dw="INDEF", w1="INDEF", w2="INDEF", nw="INDEF", \
                                            first="no", scale="none", zero="none", weight="none")

print "\nRebin to 1 Angstrom dispersion ... "
iraf.noao.imred.echelle.dispcor(image1+"gucsd1D", image1+"gucsd1Dr", linearize="yes", flux="yes", \
                                            dw=1., w1=3500., w2=9250., nw="INDEF", verbose="yes", \
                                            samedisp="no", ignoreaps="no", confirm="no", listonly="no")

print "\nAccount for exposure time ... "
iraf.images.imutil.imarith(image1+"gucsd1Dr","/",exptime,image1+"gucsd1Drn",verbose="yes")

print "\nWriting ASCII spectrum ... "
iraf.noao.onedspec(_doprint=0)
iraf.noao.onedspec.wspec (image1+"gucsd1Drn", image1+"gucsd1Drn.dat", header="yes", wformat="%d")

if interactive=="yes": 
  print "Splot  ..."
  iraf.noao.imred.echelle.splot(image1+"gucsd1D")

print "\nMoving image copy to 'reduced' directory   ..." 
move(image1+"gucsd1Drn.fits",redudir)
move(image1+"gucsd1Drn.dat",redudir)
print "\nCopy original image to 'reduced' directory   ..." 
copy(datadir+image1+".fits",redudir)


########## Spectrum reduced #######


# Now compute system efficiency.

print "\n\nComputing system efficiency ..." 

# Write parameter file of FORTRAN program cal2.f

paramfile   =fluxdir+"cal2.params"
outfile     =redudir+maskpos.replace(' ','')+"."+object+"."+image1+".dat"
standardfile=fluxdir+object.lower()+".mj"

if path.exists(paramfile):
  print "\nDeleting old file: ", paramfile
  remove(paramfile)

print "Writing file:      ", paramfile 
f4 = open(paramfile,'w')
print >> f4, standardfile
print >> f4, redudir+image1+"gucsd1Drn.dat"
print >> f4, outfile
f4.close()

chdir(fluxdir)
print "\nRunning standalone calibration program "+fluxdir+"cal2"
system (fluxdir+"cal2") 



######## Output 'photometry' ########

print "\n\nDoing photometry of 500 Angstrom wide BVR intervals ... "

# Read out generated efficiency values, to obtain average efficiency
# in the B,V,R wavelength intervals

print "\nReading system efficiencies from file ", outfile, " ..."
f4 = open(outfile,'r')
lines = f4.readlines()
f4.close()

b1=4050
b2=4550
v1=5150
v2=5650
r1=6150
r2=6650

meaneffB = 0.
meaneffV = 0.
meaneffR = 0.
kB = 0
kV = 0
kR = 0
# Skip lines with '#', and with zero efficiency
for line in lines:
   if line[0] != '#':
      efficiency=float(line.split()[3])
      if efficiency>0 : 
         wav=float(line.split()[0])
         if (wav>=b1) & (wav<=b2):
            kB=kB+1
            meaneffB=meaneffB+efficiency
         if (wav>=v1) & (wav<=v2):
            kV=kV+1
            meaneffV=meaneffV+efficiency
         if (wav>=r1) & (wav<=r2):
            kR=kR+1
            meaneffR=meaneffR+efficiency

meaneffB = meaneffB/kB
meaneffV = meaneffV/kV
meaneffR = meaneffR/kR


print "\nPhotometry value will be saved in file 'FIESphotometry' ..."
print "Photometry ", obsdate, "   fiber ", maskpos.replace(' ',''), "   B ", meaneffB, \
      "   V ", meaneffV, "   R ", meaneffR, " ", plotsymbol, " ", object

asciidb = open(workdir+'FIESphotometry','a',1)
print >>  asciidb, "%s %20s %7.1f %7.1f %7.1f     %2d   %s   %4.2f %8d   %s   %s " % \
          (obsdate, maskpos.replace(' ',''), meaneffB, meaneffV, meaneffR, plotsymbol, object, airmass, int(telfocus), stfilter, image1)
asciidb.close()

chdir(workdir)
#rmdir(tempdir)

system ('scp FIESphotometry www@www:html/instruments/qc/')     

print "\n\nAll done !!!\n"
