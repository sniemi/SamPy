###################################################################
# ABOUT:
#    This Python script calculates photometry from ACS files. The
#	 class can be used to run calacs for calibrating the raw data.
#	 The class contains also a simple interface for SexTractor that
#	 can be used to find locations of stars in the image. 
#
# DEPENDS:
#    pyraf
#
# AUTHOR:
#    Sami-Matias Niemi, for STScI
#
# HISTORY:
#    02/10/09 Initial Version
#
# CURRENT VERSION:
#    1.0
##################################################################

import pyraf
from pyraf import iraf as I
from pyraf.iraf import stsdas as S	

__author__ = 'Sami-Matias Niemi'
__version__ = "1.0"

class ACSPhotometry():
	'''
	A class to do ACS photometry.
	'''
	#Note: could be cleaned from all useless self declarations.

	def __init__(self, path, out):
		#should be expanded to be usable from commandline
		#for time being, does not use path and output for anything
		self.path = path
		self.out = out


	def omitPhotcorr(self, file):
		'''
		This function will change PHOTCORR keyword value to OMIT in the header
		of given file. The file can contain wildcards i.e. multiple files can
		be given on one command..
		'''

		I.hedit(file, fields='PHOTCORR', value = 'omit', verify='no', show = 'no')

	def runCalACS(self, file):
		'''
		Runs calacs for the given file. Uses the default parameters.
		'''

		S.hst()
		S.hst.acs()
		S.hst.acs.calacs(file)

	def gStat(self, file):
		'''
		Calculates statistics from given image. Extension must be given
		on filename e.g. file.fits[1]
		Returns:
		All statistics given by IRAF task gstat.
		'''

		stat = S.gstat(file, fields='doall', Stdout=1)
		return stat

	def hdiff(self, file1, file2):
		'''
		Compares headers from two files with hdiff.
		Returns:
		The differences found.
		'''

		hdiff = S.hdiff(file1, file2, Stdout=1)
		return hdiff

	def queryKeywords(self, file, keywords):
		'''
		Queries keywords from header. Can be used to get e.g. exposure times
		from multiple raw files with wildcard in file name.
		Returns:
		Queried keywords
		'''
		self.file = file
		self.keywords = keywords		

		keyw = I.hselect(self.file, self.keywords, 'yes', Stdout=1)
		return keyw

	def getBandpar(self, configuration):
		'''
		'''
		self.conf = configuration
		#example configuration = 'acs,wfc1,f435w'		

		#load right packages, output should be supressed if possible
		S.hst()
		S.hst.synphot()
		
		bands = S.hst.synphot.bandpar(self.conf, Stdout=1)
		return bands

	def calculateZeropoint(self, photflam):
		'''
		Calculates the zeropoint from a given header keyword photflam value.
		Returns:
		the zeropoint value
		'''
		import math
	
		self.photflam = photflam

		zp = -21.1 - 2.5*math.log10(self.photflam)
		return zp

	def getSize(self, file):
		'''
		This function can be used to get the size of the image. It actually
		returns a simple information found from the image header, however,
		when parsed correctly the image size is available.
		'''
		self.file = file

		head = I.imheader(self.file, Stdout=1)
		return head

	def doImcalc(self, input, output, operation):
		'''
		Simple interface for IRAF task imcalc. Can be used for simple
		arithmetic operations between images. This could be rewritten with
		PyFits and NumPy to give broader selection of operations.
		'''
		self.input = input
		self.output = output
		self.operation = operation

		I.imcalc(self.input, self.output, self.operation)

	def displayDS9(self, image, buffer):
		'''
		Displays the given image on DS9. The function requires that
		the DS9 is already running. In the future this should be changed.
		'''
		I.display(image, buffer)

	def markStars(self, data, buffer):
		'''
		Can be used to show an overlapping image on DS9 buffer. The data is taken
		from the a table; containing x and y coordinates.  Uses a fixed size for the
		points.
		'''
		I.tvmark(buffer, data, mark='point', nx=0, ny=0, points=0.5, color=204)

	def interactiveImexam(self, image, frame):
		'''
		Can be used to call interactive IRAF task imexam for a given frame. DS9 must be
		running and a right frame should be given.
		'''
		I.imexam(image, frame=frame)

	def doPhotometryACS(self, file, inputcoords, apertures, zeropoint, bgsigma, skyann, skydann):
		'''
		This function can be used to do photometry from a given image. Input parameters
		can be varied, however, the task assumes that photometry is done from an ACS
		image and the exposure time is found from the header of the file. 
		Object recentering is done with centroid algorithm and shifts up to 6 pixels are
		possible. For skyfitting algorithm mode is adopted.
		'''
		#load packages, should supress the output
		I.digiphot()
		I.apphot()

		#setting up for ACS
		I.datapar(sigma = bgsigma, exposure = 'exptime', gain = 'ccdgain')
		I.centerpars(calgorithm = 'centroid', cbox = 10., maxshift = 6.)
		I.fitskypars(salgorithm = 'mode', annulus = skyann, \
					 dannulus = skydann, skyvalue = 0.)
		I.photpars(apertures = apertures, zmag = zeropoint)

		I.phot(file, coords=inputcoords, verify='no', verbose = 'no')

	def getMeaningfulColumns(self, input, columns, output):
		'''
		Uses IRAF task tdump for parsing columns from a table.
		'''
		I.tdump(input, colum=columns, datafil=output)

	def mergeTables(self, merged, output):
		'''
		Can be used to merge multiple tables together.
		'''
		I.tmerge(merged, output, option='merge')

	def changeColumn(self, table, column, name, fmt, unit):
		'''
		Changes the column name and format that IRAF supports. Also unit can be
		set. Verbose output has been supressed.
		'''
		I.tchcol(table, column, name, newfmt=fmt, newunit = unit, verbose='no')

	def calculateac05(self, input, column, operation, outputfmt):
		'''
		Can be used to calculate the ac05 (from 3 pix to 10pix) aperture correction.
		Uses IRAF task tcalc, and adds the calculated values as a new column at the
		end of the table.
		'''
		I.tcalc(input, column, operation, colfmt=outputfmt)

	def correctMagnitude(self, input, column, operation, outputfmt):
		'''
		Essentially the same as calculateac05 function.
		'''
		I.tcalc(input, column, operation, colfmt=outputfmt)

def useSextractor(input):
	'''
	Very simple interface for running sextractor for given image. Does not return
	anything to the Python program. This function is superseded by the class:
	'SexTractor' class written by Sami-Matias Niemi for the Nordic Optical Telescope.
	'''
	import os

	command = 'sex %s' % input
	os.system(command)

if __name__ == '__main__':
	import glob as G
	import Photometry as P

	verbose = False
	doAll = False
	
	calibpath = '../../calib/'

	log = open('output.log', 'w')

	log.write('#This is outputlog of Photometry.py\n\n')

	ph = P.ACSPhotometry('path', 'output')
	
	#edits PHOTCORR keywords
	if doAll: ph.omitPhotcorr('*raw.fits[0]')

	#reduce raw files	
	if doAll:
		for file in G.glob('*_asn.fit*'):
			ph.runCalACS(file)

	#get some statistics
	stats = []
	for file in G.glob('*_crj.fit*'):
		stats.append(ph.gStat(file+ '[1]'))

	log.write('\n#Image Statistics:\n')
	for line in stats:
		for row in line:
			log.write(row + '\n')
			if verbose: print row

	
	diff = ph.hdiff(calibpath + 'j8c0d1011_crj.fits[1]', 'j8c0d1011_crj.fits[1]')

	log.write('\n#Header Difference:\n')
	for line in diff:
		log.write(line + '\n')
		if verbose: print line

	#lets check some header keywords
	keys = '$l,filter*,exptime,photflam,photzpt'
	phots = ph.queryKeywords(calibpath + '*drz.fits[1]', keys)

	log.write('\n#Photometric keyword values\n')
	for line in phots:
		log.write(line + '\n')
		if verbose: print line
		tmp = line.split()
		if tmp[1] == 'F606W':
			expf606w = tmp[3]
			photflamf606 = tmp[4] 
		if tmp[2] == 'F435W':
			expf435w = tmp[3]
			photflamf435 = tmp[4]
		if tmp[2] == 'F814W':
			expf814w = tmp[3]
			photflamf814 = tmp[4]
	
	#could be better with a dictionary?
	info = [['F435W', float(expf435w)*2., float(photflamf435), 'j8c0a1011_drz.fits[1]'], \
			['F606W', float(expf606w)*2., float(photflamf606), 'j8c0c1011_drz.fits[1]'], \
			['F814W', float(expf814w)*2., float(photflamf814), 'j8c0d1011_drz.fits[1]']]

	#checks bandpar
	log.write('\n#Bandpar values:\n')
	for line in info:
		bands = ph.getBandpar('acs,wfc1,' + line[0])
		for l in bands:
			log.write(l + '\n')
			if verbose: print l

	#calculates zeropoints
	log.write('\n#Zeropoints:\n')
	for line in info:
		zp = ph.calculateZeropoint(line[2])
		line.append(zp)
		if verbose: print 'Zeropoint of %s is %8.5f' % (line[0], zp)
		log.write('Zeropoint of %s is %8.5f\n' % (line[0], zp))		

	#check image sizes
	log.write('\n#Image sizes:\n')
	size = ph.getSize(calibpath + '*_drz.fits[1]')
	for line in size:
		if line.find('j8c0a1011_drz.fits') != -1:
			sizea = line[-18:-9]
		if line.find('j8c0c1011_drz.fits') != -1:
			sizec = line[-18:-9]
		if line.find('j8c0d1011_drz.fits') != -1:
			sizeb = line[-18:-9]

	#find the sizes:
	dim = [sizea.split(','), sizeb.split(','), sizec.split(',')]
	xdim = [float(d[0]) for d in dim]
	ydim = [float(d[1]) for d in dim]	

	#Do the imcalc
	if verbose: print 'Will make all the images of same size...'
	if doAll:
		for line in info:
			ph.doImcalc(calibpath + line[3] + '[1:%s,1:%s]' %(str(int(min(xdim))), str(int(min(ydim)))), \
						line[0] + '_drz.fits', 'im1*' + str(line[1]))

	#make the colour image
	if verbose: print 'Will combine three images...'
	weight = info[0][2] / info[1][2]
	if doAll:
		ph.doImcalc('F435W_drz.fits,F606W_drz.fits,F814W_drz.fits', 'colour_drz.fits', \
					'''"(%s*im1 + im2 + im3)/6."''' % str(weight))

	#lets find the stars from the colour image with sextractor
	if verbose : print 'Will use sextractor to find stars...'
	useSextractor('colour_drz.fits')

	#will finally do the photometry
	#I will use fixed values at this point. These values were manually measured with imexam
	bgsigma = 4.1 #this could be catched from sextractor, but probably gives wrong values fro drizzled image
	skyann = 10.
	skydann = 5.
	coords = 'output.cat' #from sextractor
	for line in info:
		file = line[0] + '_drz.fits[1]'
		ph.doPhotometryACS(file, coords, '3,10', line[4], bgsigma, skyann, skydann)

	#lets get the columns we will need
	for line in info:
		input = line[0] + '_drz.fits1.mag.1'
		columns = 'c7,8,15,29,30,31,38,39,40'
		output = line[0] + '.phota'
		ph.getMeaningfulColumns(input, columns, output)

	#lets merge the three filter tables
	ph.mergeTables('F435W.phota,F606W.phota,F814W.phota', 'phot_all.tab')

	#now the very ugly part. Should be rewritten...
	table = 'phot_all.tab'
	unit = '''""'''
	ph.changeColumn(table, 'c1', 'x_435', '%8.6g', unit)
	ph.changeColumn(table, 'c2', 'y_435', '%8.6g', unit)
	ph.changeColumn(table, 'c3', 'sky_435', '%6.5g', unit)
	ph.changeColumn(table, 'c4', 'flux3_435', '%11.9g', unit)
	ph.changeColumn(table, 'c5', 'mag3_435', '%7.6g', unit)
	ph.changeColumn(table, 'c6', 'err3_435', '%6.5g', unit)
	ph.changeColumn(table, 'c7', 'flux10_435', '%11.9g', unit)
	ph.changeColumn(table, 'c8', 'mag10_435', '%7.6g', unit)
	ph.changeColumn(table, 'c9', 'err10_435', '%6.5g', unit)
	ph.changeColumn(table, 'c10', 'x_606', '%8.6g', unit)
	ph.changeColumn(table, 'c11', 'y_606', '%8.6g', unit)
	ph.changeColumn(table, 'c12', 'sky_606', '%6.5g', unit)
	ph.changeColumn(table, 'c13', 'flux3_606', '%11.9g', unit)
	ph.changeColumn(table, 'c14', 'mag3_606', '%7.6g', unit)
	ph.changeColumn(table, 'c15', 'err3_606', '%6.5g', unit)
	ph.changeColumn(table, 'c16', 'flux10_606', '%11.9g', unit)
	ph.changeColumn(table, 'c17', 'mag10_606', '%7.6g', unit)
	ph.changeColumn(table, 'c18', 'err10_606', '%6.5g', unit)
	ph.changeColumn(table, 'c19', 'x_814', '%8.6g', unit)
	ph.changeColumn(table, 'c20', 'y_814', '%8.6g', unit)
	ph.changeColumn(table, 'c21', 'sky_814', '%6.5g', unit)
	ph.changeColumn(table, 'c22', 'flux3_814', '%11.9g', unit)
	ph.changeColumn(table, 'c23', 'mag3_814', '%7.6g', unit)
	ph.changeColumn(table, 'c24', 'err3_814', '%6.5g', unit)
	ph.changeColumn(table, 'c25', 'flux10_814', '%11.9g', unit)
	ph.changeColumn(table, 'c26', 'mag10_814', '%7.6g', unit)
	ph.changeColumn(table, 'c27', 'err10_814', '%6.5g', unit)

	#lets calculate the aperture correction (ac05)
	for line in info:
		number = line[0][1:4]
		column = number + '_apcor'
		operation = '''"mag3_''' + number + '-mag10_' + number + '''"'''
		ph.calculateac05(table, column, operation, '%6.5g')

	#lets get ac05 and AC05 corrected magnitudes
	for line in info:
		ac05 = 0.
		AC05 = 0.
		number = line[0][1:4]
		column = 'cmag_' + number
		if number == '435':
			ac05 = 0.14
			AC05 = 0.107
		if number == '606':
			ac05 = 0.13
			AC05 = 0.088
		if number == '814':
			ac05 = 0.18
			AC05 = 0.087
		operation = '''"mag3_''' + number + '-' + str(ac05) + '-' + str(AC05) + '''"'''
		ph.correctMagnitude(table, column, operation, '%7.6g')

	log.close()
