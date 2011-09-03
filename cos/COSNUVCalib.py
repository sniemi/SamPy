"""
Calculates pixels shifts between two COS NUV spectra.

This script can be used to determine the shift (in pixels) of one
spectrum with respect to another. The cross correlation between
S1 and S2 is determined and a non-linear fit to the peak of the
correlation is used to determine the exact offset.

:requires: Python 2.5 (not 3.0 compatible)
:requires: PyFits
:requires: NumArray (for boxcar smoothing)
:requires: NumPy (could be written without)

:author: Sami-Matias Niemi for STScI, 01/26/2009

:history: 01/26/09: Initial Release, version 0.1
"""
import math
import numpy as N
import sys
import pyfits as pf
import pylab as P

__author__ = 'Sami-Matias Niemi'
__version__ = 0.1

#This is a helper function. Code adapted from the orignal IDL code:
#http://www.astro.washington.edu/docs/idl/cgi-bin/getpro/library43.html?HRS_OFFSET
def SpectrumOffset(s1, s2, ishift=0, width=15, i1=0, i2=0):
    """
     This function calculates the shift (in pixels) of one spectrum
     with respect to another. The cross correlation between spectrum1
     and spectrum2 is determed and a non-linear fit to the peak of
     the correlation is used to determine the exact offset.

     input:
     :param s1: the first spectrum
     :type s1: ndarray
     :param s2: the second spectrum
     :type s2: ndarray

     optional input:
     ishift - guess of the intial shift in pixels, int
     width - width of the search area in pixels, int
     i1 - spectrum starting point in pixels, int
     i2 - spectrum ending point in pixels, int

     returns:
     a list with offset and correlations in every bin
     """
    approx = long(ishift + 100000.5) - 100000

    ns = len(s1)

    if i2 == 0: i2 = ns - 1

    #extract template from specturm 2
    ns2 = ns / 2
    width2 = width / 2
    it2_start = 0
    it2_end = 0

    if (i1 - approx + width2) > 0: it2_start = (i1 - approx + width2)

    if (i2 - approx - width2) < (ns - 1):
        it2_end = (i2 - approx - width2)
    else:
        it2_end = (ns - 1)

    nt = it2_end - it2_start + 1

    if nt < 1:
        print 'CROSS_CORRELATE - region too small, or WIDTH too large, or ISHIFT too large'
        offset = 0.0
        return

    template2 = s2[it2_start:it2_end + 1]

    #correlate
    corr = []
    mean2 = N.sum(template2) / nt
    sig2 = math.sqrt(N.sum((template2 - mean2) ** 2.))
    diff2 = template2 - mean2

    #find region in the first spectrum
    for i in xrange(width):
        it1_start = it2_start - width2 + approx + i
        it1_end = it1_start + nt - 1
        template1 = s1[it1_start:it1_end + 1]
        mean1 = N.sum(template1) / nt
        sig1 = math.sqrt(N.sum((template1 - mean1) ** 2.))
        diff1 = template1 - mean1

        if sig1 == 0 or sig2 == 0:
            print 'CROSS_CORRELATE - zero variance computed'
            offset = 0.0
            return offset, corr

        corr.append(N.sum(diff1 * diff2) / sig1 / sig2)

    #find maximum
    maxc = N.max(corr)
    K = corr.index(maxc)
    #in the IDL code this was k=!c
    #The system variable !C is set to the one-dimensional subscript of the maximum element

    if K == 0 or K == width - 1:
        print'CROSS_CORRELATE- maximum on edge of search area'
        offset = 0.0
        return offset, corr

    #Use quandratic refinement
    Kmin = (corr[K - 1] - corr[K]) / (corr[K - 1] + corr[K + 1] - 2. * corr[K]) - 0.5
    offset = K + Kmin - width2 + approx

    return offset, corr


def writeOutput(filename, data, header, separator=' '): #frmt
    """
     This function can be used to write tabular data to a file with selected separator.
     """
    output = open(filename, 'w')

    output.write(header)
    for line in data:
        tmpstr = ' '
        for cell in line:
            tmpstr += str(cell) + separator
        tmpstr += '\n'
        output.write(tmpstr)

    output.close()


def get_NUV_PSA_WCA(psalist, wcalist, scale=False, width=512, ishift=1, extrakeys=False, debug=False):
    """
     Does a cross-correlation between a pair of x1d files  containing the PSA and WCA spectra for the same central wavelegth.

     input:
     psalist - a list containing filenames of the x1d spectra for the PSA
     wcalist - a list containing filenames of the x1d spectra for the WCA

     optional input:
     scale - whether wca spectrum is multiplied with boxcar smoothing factor of the
             ratio between psa and wca spectrum
     ishift - guess of the intial shift in pixels, int
     width - width of the search area in pixels, int
     returns:
     a list with central wavelengths, stripes, and calculated offset values.

     """
    if scale: from numarray.convolve import boxcar as bc
    if extrakeys: import glob

    lpsa = len(psalist)
    lwca = len(wcalist)

    result = []

    if debug: print '%i and %i PSA and WCA files will be processed, respectively' % (lpsa, lwca)

    if lpsa != lwca:
        print 'The lists of filenames do not have the same number of elements.'
        print 'psalist has %i elements while wcalist has %i' % (lpsa, lwca)
        print 'Will exit now...'
        sys.exit(-1)

    for psafile, wcafile in zip(psalist, wcalist):
        if debug: print 'Running files %s and %s' % (psafile, wcafile)

        try:
            #psadata, psahdr = pf.getdata(psafile, header = True)
            #wcadata, wcahdr = pf.getdata(wcafile, header = True)
            #Above did not return the whole header for some reason?
            psa = pf.open(psafile)
            wca = pf.open(wcafile)
            psahdr = psa[0].header
            wcahdr = wca[0].header
            psadata = psa[1].data
            wcadata = wca[1].data
            psa.close()
            wca.close()
        except:
            print 'Error while reading data...'

        if extrakeys:
            try:
                #path = '/Volumes/cos/PreLaunch/Data/TV06/FITS/Test_Processing/Jan_15_2009_fixed/'
                #spt = path + psafile[:21] + '_spt.fits'
                path = '/Volumes/cos/PreLaunch/Data/TV03/FITS/Test_Processing/Jan_05_2009/'
                spt = path + psafile[50:-19] + '_spt.fits'
                sptlist = pf.open(spt)
                spthdr = sptlist[2].header
                sptlist.close()
            except:
                print 'Error while opening %s file...' % spt

        cenwav = psahdr['CENWAVE']
        stripe = psahdr['SEGMENT']
        grating = psahdr['OPT_ELEM']
        fppos = psahdr['FPPOS']
        psay = psadata[0][1]
        wcay = wcadata[0][1]

        ldstp = -999.
        ldvdt = -999.
        lxstp = -999.
        lxvdt = -999.
        if extrakeys:
            try:
                ldstp = spthdr['LAPDSTP']
                ldvdt = spthdr['LAPDLVDT']
                lxstp = spthdr['LAPXSTP']
                lxvdt = spthdr['LAPXLVDT']
            except:
                print 'Error while reading extra keys...'

        if cenwav != wcahdr['CENWAVE']:
            print 'Error - PSA and WCA files are not at same CENWAVE'
            print 'Will skip the files'
            continue

        if stripe != wcahdr['SEGMENT']:
            print 'Error - PSA and WCA files are not from the same STRIPE'
            print 'Will skip the files'
            continue

        if debug: print 'Processing the central wavelenght of %i Angstroms' % cenwav
        if debug: print 'Processing the %s segment' % stripe

        if scale:
            mpsay = max(bc(psay, (5,)))
            mwcay = max(bc(wcay, (5,)))
            factor = mpsay / mwcay
            wcay *= factor
            print 'Boxcar smoothing for psa: %s and wca %s' % (mpsay, mwcay)

        #correlation:
        #correlation2 = correlate(psay, wcay, mode = conv.VALID)
        #correlation2 = correlate(psay, wcay, mode = conv.FULL)
        #correlation2 = correlate(psay, wcay)
        #VALID gives the same result as this
        #t = Numeric.cross_correlate(psay, wcay)

        offs, correlation = SpectrumOffset(psay, wcay, width=width, i1=ishift)

        if debug: print 'Correlation: %s' % correlation
        if debug: print 'Offset %8.6f found' % offs

        #NOTE:
        #there is - in front of the offs
        #fix this if used properly calibrated data!!!

        if extrakeys:
            result.append([cenwav, stripe, -offs, psafile, grating, fppos, ldstp, ldvdt, lxstp, lxvdt])
        else:
            result.append([cenwav, stripe, -offs, psafile, grating, fppos])

    return result


def plotOffsets(results):
    nuva = []
    nuvb = []
    nuvc = []

    for line in results:
        if line[1] == 'NUVA': nuva.append([line[0], line[2]])
        if line[1] == 'NUVB': nuvb.append([line[0], line[2]])
        if line[1] == 'NUVC': nuvc.append([line[0], line[2]])

    P.plot([line[0] for line in nuva], [line[1] for line in nuva], 'ro', label='NUVA')
    P.plot([line[0] for line in nuvb], [line[1] for line in nuvb], 'gs', label='NUVB')
    P.plot([line[0] for line in nuvc], [line[1] for line in nuvc], 'bD', label='NUVC')
    P.legend(loc='upper right', shadow=True)
    P.ylim(-10, 10)
    P.title('PSA WCA Separation (TV06 based on Katya\'s List)')
    P.xlabel('CENWAVE (Angstrom)')
    P.ylabel('Separation (pixels)')
    P.savefig('offset')

if __name__ == '__main__':
    import glob

    plot = True
    extrakeys = True

    usedwidth = 20

    sfiles = glob.glob('*x1d_s*.fits')
    cfiles = glob.glob('*x1d_c*.fits')

    results = get_NUV_PSA_WCA(sfiles, cfiles, width=usedwidth, ishift=1, extrakeys=extrakeys, debug=False)

    header = '#CENWAV  STRIPE  OFFSET  PSAFILE  GRATING  FPPOS\n'
    if extrakeys:
        header = '#CENWAV  STRIPE  OFFSET  PSAFILE  GRATING  FPPOS LAPDSTP LAPDLVDT LAPXSTP LAPXLVDT\n'

    filename = 'results.output'

    writeOutput(filename, results, header)

    plotOffsets(results)
