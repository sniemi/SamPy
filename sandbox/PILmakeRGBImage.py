#!/usr/bin/env python

import pyfits
import Image

import numpy as np

bFits = '/Users/mrdavis/pylunch/rgb/data/b/j8r001010_drz.fits'
gFits = '/Users/mrdavis/pylunch/rgb/data/g/j8r001030_drz.fits'
rFits = '/Users/mrdavis/pylunch/rgb/data/r/j8r001020_drz.fits'

def gamma(x,g):
  return 255*((x/255)**(1./g))

def invgamma(x,g):
  x = np.float_(x)
  x = 255.*((x/255.)**(g))
  return np.uint16(x)

class FitsToImage():
  def __init__(self,fits):
    self.__load_sci_data(fits)
    
  def __load_sci_data(self,fits):
    self.data = pyfits.getdata(fits,1)[:2049,:2049]
    
    self.zeroed = False
    self.scaled = False
    
  def __zero_data(self):
    w = np.where(self.data != 0)
    self.data[w] = self.data[w] - self.data[w].min()
    self.zeroed = True
    
  def scale_data(self,scale_max):
    if not self.zeroed:
      self.__zero_data()
      
    self.scale_max = scale_max
      
    self.data = np.uint16( (self.data/scale_max) * 255. )
    
    self.scaled = True
    
  def auto_scale_data(self,percentile_max=99):
    if not self.zeroed:
      self.__zero_data()

    max = np.percentile(self.data, percentile_max)
    
    self.scale_data(max)
    
  def get_image(self):
    if not self.scaled:
      self.auto_scale_data()
      
    im = Image.new('L',(self.data.shape[1], self.data.shape[0]))
    
    im.putdata(self.data.ravel())
    
    return im

def image_handler(auto=True,bmax=None,gmax=None,rmax=None):
  bfti = FitsToImage(bFits)
  if not auto or bmax:
    bfti.scale_data(bmax)
  bim = bfti.get_image()
  print 'Blue scale max =\t' + str(bfti.scale_max)
#  print 'Saving blue image.'
#  bim.save('btest.png')
  
  gfti = FitsToImage(gFits)
  if not auto or gmax:
    gfti.scale_data(gmax)
  gim = gfti.get_image()
  print 'Green scale max =\t' + str(gfti.scale_max)
#  print 'Saving green image.'
#  gim.save('gtest.png')
  
  rfti = FitsToImage(rFits)
  if not auto or rmax:
    rfti.scale_data(rmax)
  rim = rfti.get_image()
  print 'Red scale max =\t\t' + str(rfti.scale_max)
#  print 'Saving red image.'
#  rim.save('rtest.png')
  
  rgbim = Image.merge('RGB',(rim,gim,bim))
  print 'Saving RGB image.'
  rgbim.save('rgbtest.png')

def usage():
  print 'Usage: makeRGB.py auto'
  print 'Usage: makeRGB.py <blue max> <green max> <red max>'
    
if __name__ == '__main__':
  import sys
  
  if len(sys.argv) == 2:
    image_handler()
  elif len(sys.argv) == 4:
    bmax = float(sys.argv[1])
    gmax = float(sys.argv[2])
    rmax = float(sys.argv[3])
    image_handler(False,bmax,gmax,rmax)
  else:
    usage()
    exit()
