# The IRAF to DS9 communication is setup to use private fifos.
# To tell ds9 where the fifo's are it is started up with
#   '-fifo_only -fifo /home/postprocess/alfosc/imt1 '
# Note that there is *NO* typo in the line above.

# To tell IRAF where the fifos are, this script sets the environment like
#    setenv IMTDEV fifo:/home/postprocess/alfosc/imt1i:/home/postprocess/fies/imt1o
# This has to be done *before* IRAF is started with the 
#    'from pyraf import iraf'
# statement (see below).

# To make the fifo's use "mknod imt1i p" and "mknod imt1o p"; 
# Set or check the 'fifopath' variable below.

# JHT, Feb 2007

DEBUG = 0

import os
import sys
from subprocess import Popen
from subprocess import PIPE
from time import sleep

xpaget = '/usr/bin/xpaget'
xpaset = '/usr/bin/xpaset'

class DS9:

  def __init__(self,fifopath):

    """	Tell IRAF where to find the DS9 communication fifos
        by setting environment variable.
    """

    os.environ["IMTDEV"] = "fifo:"+fifopath+"imt1i:"+fifopath+"imt1o"


  def ds9_exists(self,ds9_title):
    
    """ Check for an instance of ds9 """

    exists=0

    # Grep for the ds9 title and 'ds9' in output of "ps ax"
    dummyfile = os.popen("ps ax")
    for line in dummyfile.readlines():
       if (line.find(ds9_title)>-1) & (line.find('ds9')>-1):
         exists=line.split()[0]
    dummyfile.close()

    return exists


  def kill_ds9(self,ds9pid):

    """ Kill an DS9 instance """

    if DEBUG: print "Killing ds9 with process ID " + ds9pid
    os.system("kill -9 " + ds9pid)
    

  def start_ds9(self,ds9_title,ds9geometry,fifopath):
    
    """ Start an ds9 instance, killing existing instances with same title """

    ds9pid=self.ds9_exists(ds9_title)

    if ds9pid!=0: self.kill_ds9(ds9pid)

    environ = os.environ	
    environ['XPA_ACL']  = 'false'    	    
    environ['XPA_PORT'] = 'DS9:ALFOSC 12345 12346'
 
    cmd = "nohup /home/postprocess/ds9 -title " + ds9_title + " -fifo " + fifopath + \
             "imt1 -fifo_only -zoom 1.0 -geometry 580x710" + ds9geometry.strip() + " &"
    if DEBUG: print "Starting ds9 ...   "
    p = Popen(cmd, shell=True, env=environ)
    sts = os.waitpid(p.pid, 0)

    # Give ds9 some time to start up
    sleep(1.80)  # 1.8s Enough for fiboff.py; JHT 20/3/2008


  def loadSingleFits(self,ds9_title,fn,frame):

    """ Load a single fits image into a DS9 frame using xpaset """

    ds9pid=self.ds9_exists(ds9_title)
    if ds9pid!=0:
      if os.path.exists(fn):
        xpa = "/usr/bin/xpaset -p %s " % ds9_title
        os.system(xpa + "frame %s" % frame )
        os.system(xpa + "file %s" % fn )
#	os.system(xpa + "scale zscale")
#       os.system(xpa + "zoom to fit")


  def loadMosaicFits(self,ds9_title,fn,frame):

    """ Load a mosaic fits image into DS9 using xpaset """

    ds9pid=self.ds9_exists(ds9_title)
    if ds9pid!=0:
      if os.path.exists(fn):
        xpa = "/usr/bin/xpaset -p %s " % ds9_title
        os.system(xpa + "frame %s" % frame )
        os.system(xpa + "file mosaicimage wcs %s" % fn)
#       os.system(xpa + "scale zscale")
#       os.system(xpa + "zoom to fit")


  def overlayRegions(self,ds9_title,fn,frame):
    
    """ Overlay a DS9 with region information stored in a file using xpaset """
    
    ds9pid=self.ds9_exists(ds9_title)

    if ds9pid!=0:     
      if os.path.exists(fn):
   	xpa = "/usr/bin/xpaset -p %s " % ds9_title
        os.system(xpa + "frame %s" % frame )
	os.system(xpa + "regions file %s" % fn )


  def setTile(self,title):
    """ Tile all frames in a DS9 instance """	
    Popen("%s -p %s tile" % (xpaset,title), shell=True)


  def setSingle(self,title):
    """ Show only one frame in a DS9 instance """	
    Popen("%s -p %s single" % (xpaset,title), shell=True)


  def setFrame(self,title,frame):
    """ Set focus on a frame in a DS9 instance """	
    Popen("%s -p %s frame %s" % (xpaset,title,frame), shell=True)

  
  def isTiled(self,title): 
    """ Check if frames are tiled """
    cmd = "%s %s tile" % (xpaget,title)
    output = Popen(cmd, shell=True, stdout = PIPE).stdout.read()[:-1]
    return output

  def getFile(self,title):
    """ return filename of image in current frame """
    cmd = "%s %s file" % (xpaget,title)
    output = Popen(cmd, shell=True, stdout = PIPE).stdout.read()[:-6]
    return output