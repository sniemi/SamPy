#########################################################
#A short script to copy few files to another location.
#The script will create the output folder if it does not
#exist.
#########################################################

__author__ = 'Sami-Matias Niemi'
__version__ = "1.0"

import shutil
import os

perform = True

inputdir = '/Volumes/cos/PreLaunch/Data/TV06/*/FITS/Jan_15_2009_fixed/'
outputdir = '/Volumes/user/mwolfe/SMNtemp'

if  perform:
	try:
		os.mkdir(outputdir)
		print 'Created a directory: %s' % outputdir
	except:
		print 'Directory already exists, not created again...'

files = (
'CSIL06332204629',
'CSIL06332231205',
'CSIL06332232729',
'CSIL06332235817',
'CSIL06333001340',
'CSIL06333002904',
'CSIL06333004428',
'CSIL06333005952',
'CSIL06333011516',
'CSIL06333013040',
'CSIL06333014604',
'CSIL06333020128',
'CSIL06333021652',
'CSIL06333023216',
'CSIL06333121514',
'CSIL06333122144',
'CSIL06342003153',
'CSIL06332201805',
'CSIL06332192001',
'CSIL06332211605',
'CSIL06332221405',
'CSIL06332203217',
'CSIL06332193415',
'CSIL06332213017',
'CSIL06332222817',
'CSIL06332210041',
'CSIL06332200241',
'CSIL06332215841',
'CSIL06332225641')

for file in files:
	name = '*' + file[4:] + '*rawtag.fits'
	full = inputdir + name
	if perform:
		#shutil.copyfile(full, outputdir)
		try: os.system('cp ' + full + ' ' + outputdir)
		except: print 'Copy error...'
		print 'file %s copied...' % file
	else:
		print 'cp ' + full + ' ' + outputdir
		
print 'All done'
