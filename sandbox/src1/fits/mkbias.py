import pyfits
import sys
import numpy

#This is for ALFOSC
#Overscan might change if used for another instrument

filelist = open(sys.argv[1]).readlines()

print "This script combines BIAS images to a single master BIAS frame."
print "\n%i images will be combined..." % len(filelist)

filedata = [pyfits.getdata(x) for x in filelist]

if len(set(x.shape for x in filedata))  > 1:
   print "Images are not of same size!"
   print "Program will exit..."
   sys.exit(1)

#substracts overscan from all images
i = 0
for image in filedata:
   #y, x = indices(image.shape, dtype=float32)
   overscan = image[0:2047,0:50].mean()
   filedata[i] = 1.*image - overscan
   print "Subtracted overscan of %f" % overscan
   i += 1

   
#calculates the median of all biases
BIAS = numpy.median(filedata)

#writes the master bias frame
pyfits.writeto("masterBIAS.fits", BIAS)
print "maserBIAS.fits has been written..."
