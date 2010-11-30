import pyfits
import sys
import numpy

#few means shoud be changed to median!!

#This is for ALFOSC
#Overscan might change if used for another instrument

filelist = open(sys.argv[1]).readlines()
bias = pyfits.getdata(sys.argv[2])

print "This script makes a flatfield image..."
print "\n%i images will be median combined for master flat." % len(filelist)

filedata = [pyfits.getdata(x) for x in filelist]

if len(set(x.shape for x in filedata))  > 1:
   print "Images are not of same size!"
   print "Program will exit..."
   sys.exit(1)

#subtracts overscan and BIAS from all flats
i = 0
for image in filedata:
   overscan = image[0:2047,0:50].mean() #should be median
   image = 1.*image - overscan - bias
   print "Subtracted BIAS and overscan of %f" % overscan 
   norm = image[300:1800,300:1800].mean() #should be median
   filedata[i] = image / norm
   print "File %s normalised by dividing with a level of %f." % (filelist[i], norm)
   i += 1

#calculates the median of all biases
FLAT = numpy.median(filedata)

#writes the master bias frame
pyfits.writeto("FLAT.fits", FLAT)
print "FLAT.fits has been written..."
