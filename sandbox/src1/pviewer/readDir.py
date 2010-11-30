#!/usr/bin/env python

from glob import *
from os import *
import readMDA
import sys

def readDir(s):
	dd = []
	files = glob(s)
	i = 0
	for file in files:
		dd.append(readMDA.readMDA(file, verbose=0, maxdim=0))
		print "file:%-15s rank:%d %s" % (dd[i][0]['filename'],
		dd[i][0]['rank'], str(dd[i][0]['dimensions']))
		i = i+1
	return dd

if __name__ == "__main__":
	print "sys.argv = ", sys.argv
	if (len(sys.argv) < 2) :
		print "usage: readDir.py <filename>"
	else:
		dd = readDir(sys.argv[1:])

