#! /usr/bin/env python
'''
DESCRIPTION:
This script can be used to process COS focus sweet data.
the script edits header keywords that are related to
calibrations, and points to new reference files that 
are assumed to be located in /smov/cos/lref. Note that
user may have to edit the "EDIT THESE" block if e.g. the
above path is incorrect.
After all keywords have been updated the script will run
CALCOS to each file. The script tests that the version
of CALCOS is 2.10 or later.

USAGE:
e.g.
python COSfocusKeywordsCalib.py "*rawtag*.fits"
Note that double quote marks " are required if ran
from a command line.

HISTORY:
Created on Aug 21, 2009

@author: Sami-Matias Niemi
'''

import pyfits as PF
import sys
import glob as G
import calcos as C

filelist = G.glob(sys.argv[1])

#######################################################
#EDIT THESE:
#######################################################
omitlist = ['FLATCORR',                  
            'DEADCORR',                
            'DQICORR',
            'PHACORR',
            'BADTCORR',
            'HELCORR',
            'X1DCORR',
            'BACKCORR',
            'FLUXCORR',
            'TDSCORR']

refdir = '/smov/cos/lref/'

performlist = ['DOPPCORR']

statflag = {'STATFLAG' : False}

reffiles={'XTRACTAB': refdir + 'fuv_smov_v1_r_1dx.fits',
          'LAMPTAB' : refdir + 'fuv_090330_lamp.fits',
          'DISPTAB' : refdir + 'fuv_2006_090603_r_disp.fits', 
          'WCPTAB'  : refdir + 't2314311lmod2_wcp.fits'}
########################################################


#reffiles={'FLATFILE': 'lref$n9n20182l_flat.fits'
#          'DEADTAB' : 'lref$s7g1700gl_dead.fits'
#          'BPIXTAB' : 'lref$s7g1700dl_bpix.fits'
#          'BRFTAB'  : 'lref$s7g1700el_brf.fits'
#          'GEOFILE' : 'lref$s7g1700cl_geo.fits'
#          'PHATAB'  : 'lref$s7g1700jl_pha.fits'
#          'BADTTAB' : 'lref$s7o1739kl_badt.fits'
#          'XTRACTAB': 'lref$s7g17007l_1dx.fits'
#          'LAMPTAB' : 'lref$s7g1700il_lamp.fits'
#          'DISPTAB' : 'lref$t2k1224el_disp.fits' 
#          'IMPHTTAB': 'N/A                    '
#          'FLUXTAB' : 'lref$s7g1700kl_phot.fits'
#          'WCPTAB'  : 'lref$t2314311l_wcp.fits'
#          'BRSTTAB' : 'lref$s7g1700fl_burst.fits'
#          'TDSTAB'  : 'lref$t2314312l_tds.fits'}

#COS focus cals:
#FLATCORR= 'OMIT    '           / apply flat-field correction
#DEADCORR= 'PERFORM '           / correct for deadtime
#DQICORR = 'PERFORM '           / data quality initialization
#STATFLAG=                    T / Calculate statistics?
#TEMPCORR= 'PERFORM '           / correct for thermal distortion
#GEOCORR = 'PERFORM '           / correct FUV for geometic distortion
#IGEOCORR= 'PERFORM '           / interpolate geometric distortion in INL file
#RANDCORR= 'PERFORM '           / add pseudo-random numbers to raw x and y
#RANDSEED=                   -1 / seed for pseudo-random number generator
#PHACORR = 'PERFORM '           / filter by pulse-height
#BADTCORR= 'PERFORM '           / filter by time (excluding bad time intervals)
#DOPPCORR= 'PERFORM '           / orbital Doppler correction
#HELCORR = 'PERFORM '           / heliocentric Doppler correction
#X1DCORR = 'PERFORM '           / 1-D spectral extraction
#BACKCORR= 'PERFORM '           / subtract background (when doing 1-D extraction)
#WAVECORR= 'PERFORM '           / use wavecal to adjust wavelength zeropoint
#FLUXCORR= 'PERFORM '           / convert count-rate to absolute flux units
#BRSTCORR= 'OMIT    '           / switch controlling search for FUV bursts
#TDSCORR = 'PERFORM '           / switch for time-dependent sensitivity correctio 
#/ CALIBRATION REFERENCE FILES
#FLATFILE= 'lref$n9n20182l_flat.fits' / Pixel to Pixel Flat Field Reference File
#DEADTAB = 'lref$s7g1700gl_dead.fits' / Deadtime Reference Table
#BPIXTAB = 'lref$s7g1700dl_bpix.fits' / bad pixel table 
#BRFTAB  = 'lref$s7g1700el_brf.fits' / Baseline Reference Frame Reference Table
#GEOFILE = 'lref$s7g1700cl_geo.fits' / Geometric Correction Reference File
#PHATAB  = 'lref$s7g1700jl_pha.fits' / Pulse Height Discrimination Reference Tabl
#BADTTAB = 'lref$s7o1739kl_badt.fits' / Bad Time Interval Reference Table
#XTRACTAB= 'lref$s7g17007l_1dx.fits' / 1-D Spectral Extraction Information Table
#LAMPTAB = 'lref$s7g1700il_lamp.fits' / template calibration lamp spectra table
#DISPTAB = 'lref$t2k1224el_disp.fits' / Dispersion Coefficient Reference Table 
#IMPHTTAB= 'N/A                    ' / Imaging photometric table
#FLUXTAB = 'lref$s7g1700kl_phot.fits' / Spectroscopic flux calibration table
#WCPTAB  = 'lref$t2314311l_wcp.fits' / wavecal parameters table
#BRSTTAB = 'lref$s7g1700fl_burst.fits' / burst parameters table
#TDSTAB  = 'lref$t2314312l_tds.fits' / time-dependent sensitivity correction tabl


#MAIN PROGRAM STARTS
if C.__version__ != '2.10' or (int(C.__version__[0]) < 3 and float(C.__version__[2:]) < 10):
    print 'You are trying to use CALCOS version %s!' % C.__version__
    print 'If you are using STScI machine, please use irafdev version!'
    sys.exit(-9)

#edit keywords
for file in filelist:
    fd = PF.open(file, mode='update')
    phdr = fd[0].header

    hdr = fd[1].header

    for omit in omitlist:
        phdr.update(omit, 'OMIT')
    for per in performlist:
        phdr.update(per, 'PERFORM')
    for key in reffiles:
        phdr.update(key, reffiles[key])
    for key in statflag:
        phdr.update(key, statflag[key])
    fd.close()
    print 'Keywords of file %s have been modified...' % file

#calibration
filelist = [file[:-14] for file in filelist if 'rawtag_a.fits' in file]
for file in filelist:
    C.calcos(file)

#collapsing
#for file in filelist:
    #which file should be process?
#    data = PF.open(file[] + '_corr_a/b.fits')[1].data

    #find centre, collapse dispersion direction and find max

    #define area, + / - width

    #collapse in cross-dispersion direction

    #save a new file


print 'Script ends...'

