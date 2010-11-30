#!/usr/bin/python2.4

DEBUG = 1

workdir     = "/home/postprocess/alfosc/imexam/"  
fifopath    = "/home/postprocess/alfosc/"            
irafdir     = "/home/postprocess/alfosc/" 	     
pymodules   = "/home/postprocess/python_modules/" 
ds9_title   = "ALFOSC"     	    	    

import sys
import os
sys.path.append(pymodules)
from ds9 import *
from postprocess import writeTalker


#####################
####### MAIN ########
#####################

display = DS9(fifopath)

if (display.ds9_exists(ds9_title) == 0):
  print "Error: No ALFOSC DS9 instance found!"
  writeTalker('postprocess.imexam',"[DEBUG]: No ALFOSC DS9 instance found!")
  sys.exit(1)


#
# Start up IRAF and imexam. This requires a valid login.cl in directory 'irafdir'
#
os.chdir(irafdir)
from pyraf import iraf
os.chdir(workdir)

#iraf.mscred

writeTalker('postprocess.imexam',"[DEBUG]: Starting imexam")

iraf.imexam(keeplog='no')
#iraf.mscexam(keeplog='no')

