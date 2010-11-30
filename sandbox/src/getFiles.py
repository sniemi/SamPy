###########################################################
#A script that can be used to find and copy files.
#Uses an input list for files to be copied.
#An output directory must be given
#

import os
import sys

__author__ = 'Sami-Matias Niemi'
__version__ = "1.0"

if len(sys.argv) != 3:
	sys.exit("Two command line arguments must be given...")
else:
	inputfile = str(sys.argv[1])	#'G225Mfiles.txt'
	outputdir = str(sys.argv[2])	#'G225M'
	print 'Input filelist %s given' % inputfile
	print 'Files will be copid to ./%s' % outputdir

inputdir = '/Volumes/cos/PreLaunch/Data/TV03/FITS/Test_Processing/*/'

inputlist = open(inputfile, 'r').readlines()
filelist = [line.split()[0] for line in inputlist]

try:
	os.mkdir(outputdir)
except:
	pass

for file in filelist:
	name = '*' + file + '*_rawtag.fits'
	full = inputdir + name
	try:
		os.system('cp ' + full + ' ./' + outputdir)
	except:
		print 'Could not copy file %s' % file

print 'done'
