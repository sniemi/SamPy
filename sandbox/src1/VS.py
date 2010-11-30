# this is module VS

### JHT: if you have to update this module, then also
###      check for possible updates in the other modules HG, VG, HS, VS

import os,math
import Tkinter as Tk
from tiasgatfuncs import *

def doit(fn,dp,mt):
  """ JHT: this is the module that analyses an ALFOSC image of
           a Vertical Slit, and recommends an alignment offset to the
           current APERTURE WHEEL stepper motor units."""
          

  ## First check if data file exists
  if not os.access(dp+fn+".fits",os.F_OK): 
     messageOut(mt,"File not found:  "+dp+fn+".fits\n")
     return "File not found:  "+dp+fn+".fits"

  messageOut(mt,"\nVertical-Slit analysis of file:  "+dp+fn+".fits\n")

  from pyraf import iraf
  from pyraf import gwm


  ## Read current grism wheel position from image FITS header
  iraf.images.imutil.imgets(dp+fn,"GRISM")
  grismid=iraf.images.imutil.imgets.value
  if grismid.find("pen")==-1: 
     messageOut(mt,"Vertical-Slit mode:  grism wheel should be Open\n")
     return "File  %s:  Vertical-Slit mode:  grism wheel should be Open" % fn




  ## Read current aperture wheel position from image FITS header
  iraf.images.imutil.imgets(dp+fn,"APERTUR")
  slitid=iraf.images.imutil.imgets.value
  if slitid.find("Vert")==-1: 
     messageOut(mt,"Vertical-Slit mode:  no vertical slit in aperture wheel\n")
     return "File  %s:  Vertical-Slit mode:  no vertical slit in aperture wheel" % fn

  slitwidth=float(slitid.split('_',9)[1].strip('\"'))
  messageOut(mt,"Slit width "+str(slitwidth)+"   "+slitid+"\n")

  iraf.noao(_doprint=0)
  iraf.noao.imred(_doprint=0)
  iraf.noao.imred.specred(_doprint=0)

  if not os.access("/tmp/tiasgat/",os.F_OK):
    os.mkdir("/tmp/tiasgat/")
    os.chmod("/tmp/tiasgat/",0777)
  if os.access("/tmp/tiasgat/plot",os.F_OK):     os.remove("/tmp/tiasgat/plot")
  if os.access("/tmp/tiasgat/plot2",os.F_OK):    os.remove("/tmp/tiasgat/plot2")
  if os.access("/tmp/tiasgat/aplast",os.F_OK):   os.remove("/tmp/tiasgat/aplast")
  if os.access("/tmp/tiasgat/tvmarks",os.F_OK):  os.remove("/tmp/tiasgat/tvmarks")
  if os.access("/tmp/tiasgat/logfile",os.F_OK):  os.remove("/tmp/tiasgat/logfile")

  ## Note that this will *not* update any uparm files !! (see pyraf documentation)
  iraf.noao.imred.specred.dispaxis=2
  iraf.noao.imred.specred.database="/tmp/tiasgat/"
  iraf.noao.imred.specred.plotfile="/tmp/tiasgat/plot"
  iraf.noao.imred.specred.logfile="/tmp/tiasgat/logfile"
  width=6*slitwidth    # x6 or else the widest slits go wrong
  if width<4: width=4  # smaller than 4 and apfind will not find it
  messageOut(mt,"Using width of "+str(width)+" pixels \n")
  iraf.noao.imred.specred.apedit.width=width



  ## Display image on ds9
  iraf.set(stdimage="imt512")
  iraf.display(dp+fn,1,fill="no",Stdout="/dev/null")

# Suppress IRAF query for number of apertures to find
# This is only necesary for the widest slits: then the call to
# apfind results in an empty database file, as it cannot find an aperture.
# But aptrace works fine anyway (except for the annoying query) !? 
  iraf.noao.imred.specred.apfind.setParam('nfind.p_value', 1)
  iraf.noao.imred.specred.apfind.setParam('nfind.p_mode','h')

  ## 'find' and trace spectrum; this will dump a plot to /tmp/tiasgat/plot
  lines = iraf.noao.imred.specred.apfind(dp+fn,nfind=1,interactive="no", edit="no", nsum=20, Stdout=1)
  for i in range (0,len(lines)):     messageOut(mt,lines[i]+"\n")


  lines = iraf.noao.imred.specred.aptrace(dp+fn,interactive="no",step=5,low_reject=2.5,
                   high_reject=2.5,function="leg",order=2,niterate=5,naverage=1, Stdout=1)
  for i in range (0,len(lines)):     messageOut(mt,lines[i]+"\n")


  ## Start graphics window; select the correct plot; show plot
  gwm.window("Tiasgat!  graphics")
  iraf.plot.gkiextract("/tmp/tiasgat/plot",2,Stdout="/tmp/tiasgat/plot2")
  gwm.getActiveGraphicsWindow().load("/tmp/tiasgat/plot2")


### how to read the aperture file, as output by aptrace ####
### 
### center    line 6        gives zero point
### max,min   lines 24-25   n = (2 * x - (max + min)) / (max - min)
### c1,c2     lines 26-27   
### 
### The polynomial can be expressed as the sum
###     
###             poly = sum from i=1 to order {c_i * z_i} 
###     
### where  the  the  c_i  are  the  coefficients and the z_i are defined
### interatively as:
###     
###             z_1 = 1
###             z_2 = n
###             z_i = ((2*i-3) * n * z_{i-1} - (i-2) * z_{i-2}) / (i - 1)
###     
### So for order=2 and for vertical slit/grism:   X=center+c1+c2*n
###             X=center + c1 + c2*(2 * Y - (max + min)) / (max - min)
    
### translated to X=a + bY
###    a=center + c1 - c2*(max+min)/(max-min)
###    b=2*C2/(max-min)


  ## Read the aperture definition file
  apfile=open("/tmp/tiasgat/ap"+dp.replace('/','_')+fn,'r')
  lines=apfile.readlines()
  apfile.close()
  #print lines[5], lines[23:]
  c0    = float(lines[5].split(None,9)[1].strip())
  lower = float(lines[23].strip())
  upper = float(lines[24].strip())
  c1    = float(lines[25].strip())
  c2    = float(lines[26].strip())
  a = c0 + c1 - c2*(upper+lower)/(upper-lower)
  b = 2*c2/(upper-lower)
  #print "zeropoint ", a, "    slope ",b

  ## Remove aperture definition file
  if os.access("/tmp/tiasgat/ap"+dp.replace('/','_')+fn,os.F_OK): 
    os.remove("/tmp/tiasgat/ap"+dp.replace('/','_')+fn)

  ## Mark the fit on the image display
  if os.access("/tmp/tiasgat/tvmarks",os.F_OK):   os.remove("/tmp/tiasgat/tvmarks")
  tvmarkfile=open("/tmp/tiasgat/tvmarks",'w')
  for i in range(int(lower),int(upper)+1,3):
     tvmarkfile.write(str(a+b*i)+"  "+str(i)+" 100 s \n")
  tvmarkfile.close()
  iraf.tv.tvmark(1,"",commands="/tmp/tiasgat/tvmarks",interactive="no")

  ## Read current grism wheel position from image FITS header
  iraf.images.imutil.imgets(dp+fn,"ALAPRSTP")
  oldwheelunits=float(iraf.images.imutil.imgets.value)
  #print "APERSTEP", oldwheelunits

  ## Read binning FITS headers
  iraf.images.imutil.imgets(dp+fn,"CDELT1")
  xbin=float(iraf.images.imutil.imgets.value)
  iraf.images.imutil.imgets(dp+fn,"CDELT2")
  ybin=float(iraf.images.imutil.imgets.value)
  iraf.images.imutil.imgets(dp+fn,"CRVAL1")
  xstart=float(iraf.images.imutil.imgets.value)
  messageOut(mt,"\nBinning factors "+str(int(xbin))+" x "+str(int(ybin))+"\n")
  #messageOut(mt,"Xstart "+str(int(xstart))+"\n")
  #messageOut(mt,"half "+str(int((lower+upper)/2))+"\n")
  if xbin==1:
    messageOut(mt,"\nSlitpos:   X-position at CCD center "+str((xstart-1+a+b*(lower+upper)/2))+" according to fit\n")
  else:
    messageOut(mt,"\nSlitpos:   X-binning is not 1:   set wrongly in vsalign.run ?!\n\n")

  ## Correct the angle for the binning factors.
  ## A full wheel turn corresponds to 320000 units
  offsetangle=320000 * math.atan(b*xbin/ybin) / (2*math.pi)
  messageOut(mt,"Alignment: Offset to motor units "+str(offsetangle)+"\n")

  newwheelunits=offsetangle + oldwheelunits
  if newwheelunits < 0:  newwheelunits+=320000

  return "Result for %s :  current APERTURE wheel units  %d,  suggested new value  %d" % \
         (fn, (0.5+oldwheelunits), (0.5+newwheelunits))
