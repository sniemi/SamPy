"""
Functions related to polarimetry, especially HST ACS WFC.

:requires: NumPy
:requires: SciPy
:requires: matplotlib
:requires: Kapteyn Python package

:author: Sami-Matias Niemi
:contact: sammy@sammyniemi.com

:version: 0.5
"""
from time import time
import os, os.path
import numpy as np
import pyfits as pf
import scipy.special as ss
from scipy import ndimage
from kapteyn import maputils
from matplotlib import pyplot as plt


def debias(pol, polerr, limit=0.01):
    """
    This function returns the debiased value of the fractional polarization using the
    estimate of the most probable value of POL from the fit to the peak of the Rice
    distribution given by solving Equ. A2 of Wardle & Kronberg (ApJ, 194, 249, 1974).

    An initial estimate of debiased polarization is given by determining the Bessel
    functions of (POLobs*POLobs/POLERR*POLERR). Then the initial estimate of debiased
    polarization allows improved values for the Bessel functions of (POLobs*POLreal/
    POLERR*POLERR) to be obtained. The procedure is iterated until convergence in
    successive values of debiased polarization is achieved to the limit (1% default)
    of POLERR.

    :Note: this functions works only with single inputs not arrays! Thus, it should
           be rewritten...

    :param pol: Initial value of polarization
    :type pol: float
    :param polerr: Polarization error
    :type: polerr: float

    :return: debiased polarization
    :rtype: float
    """
    RR = pol*pol/(polerr*polerr)
    per = (pol - (polerr*polerr/pol))

    #special case
    if RR > 81.0:
        #Values of Modified Bessell functions > 6E33,
        #so use asymptotic expression for POLDB
        tmp = (pol*pol) - (polerr*polerr)
        if tmp > 0.0:
            POLDB = np.sqrt(tmp)
        else:
            POLDB = 0.0
        return POLDB

    #set the values to dummies for inital run
    POL0 = 0
    POLDB = polerr

    while np.abs(POLDB - POL0) > (limit*polerr):
        #Calculate the debiassed value of polarization
        POLDB = (ss.i0(RR)/ss.i1(RR)) * per
        if POLDB > 0.0:
            POL0 = POLDB
        else:
            return 0.0

        #Recalculate RR with the new value of POL
        RR = (pol*POLDB) / (polerr*polerr)

        #special case
        if RR > 81.0:
            tmp = (pol*pol) - (polerr*polerr)
            if tmp > 0.0:
                POLDB = np.sqrt(tmp)
            else:
                POLDB = 0.0
            return POLDB


        #Calculate the new debiassed value of polarization
        POLDB = (ss.i0(RR)/ss.i1(RR)) * per
        if POLDB < 0.0:
            return 0.0

    return POLDB


def getBasics(header):
    """
    Return basic information from the header:

        1. bias
        2. gain
        3. readout noise

    :Note: This function is useful for ACS WFC polarimetry data.

    :return: bias, gain, readnoise
    :rtype: list
    """
    bias = header['CCDOFSTB']
    gain = header['CCDGAIN']
    readnoise = header['READNSEB']
    return bias, gain, readnoise


def stokesParameters(files, acsWFC=True):
    """
    Calculates Stokes parameters from polarized images.

    :param files: dictionary of form POLx : [image data, header], where
                  x is in [0, 60, 120]
    :type files: dict
    :param acsWFC: for ACS WFC a correction are being applied
    :type acsWFC: boolean

    Assumes that the input arrays are in counts/electrons not in count rate.
    Uses the header information to scale each array to 10000s exposure time.

    :Note: the ACS WFC correction factors are from Biretta et al. 2004 (ISR)

    :return: Stokes I, Q, and U, polarized fraction, degree of (linear) polarization,
             and electric-vector position angle
    :rtype: dictionary
    """
    pol0 = files['POL0'][0]
    pol60 = files['POL60'][0]
    pol120 = files['POL120'][0]
    hdr0 = files['POL0'][1]
    hdr60 = files['POL60'][1]
    hdr120 = files['POL120'][1]

    bias0, gain0, readnoise0 = getBasics(hdr0)
    bias60, gain60, readnoise60 = getBasics(hdr60)
    bias120, gain120, readnoise120 = getBasics(hdr120)

    #scale to 10000s
    pol0 = pol0 / hdr0['EXPTIME'] * 10000.
    pol60 = pol60 / hdr60['EXPTIME'] * 10000.
    pol120 = pol120 / hdr120['EXPTIME'] * 10000.

    #correct of instrumental polarization
    if acsWFC:
        pol60 *= 0.979
        pol120 *= 1.014

    #values are supposed to be in counts, thus set all negative values to 1
    pol0[pol0 < 0.0] = 1.0
    pol60[pol60 < 0.0] = 1.0
    pol120[pol120 < 0.0] = 1.0

    #calculate Stokes parameters
    I = (2 / 3.) * (pol0 + pol60 + pol120)
    Q = (2 / 3.) * (2. * pol0 - pol60 - pol120)
    U = (2 / np.sqrt(3)) * (pol60 - pol120)

    #PU = U / I
    #PQ = Q / I
    #if acsWFC:
    #    PU -= 0.022*np.sin(np.deg2rad(2*42.))
    #    PQ -= 0.022*np.cos(np.deg2rad(2*42.))

    #error images
    p0err = np.sqrt(((pol0 - bias0)/gain0) + (readnoise0/gain0)**2)
    p60err = np.sqrt(((pol60 - bias60)/gain60) + (readnoise60/gain60)**2)
    p120err = np.sqrt(((pol120 - bias120)/gain120) + (readnoise120/gain120)**2)

    #add errors in quadrature
    Ierr = np.sqrt(p0err*p0err + p60err*p60err + p120err*p120err)
    Uerr = Ierr
    Qerr = np.sqrt(p60err*p60err + p120err*p120err)

    #derive error in polarization
    polerr = np.sqrt(( ((Q*Qerr)**2) + ((U*Uerr)**2)) / (Q*Q + U*U))

    #polarized intensity
    pol = np.sqrt(Q*Q + U*U)

    #debias 
    Poli = pol.copy()
    for y in range(Poli.shape[0]):
        for x in range(Poli.shape[1]):
            Poli[y,x] = debias(pol[y,x], polerr[y,x])

    #degree of polarization in units of per cent
    degp = Poli / I * 100.

    if acsWFC:
        #Edeg = 0.5 * np.rad2deg(np.arctan(U/Q)) - 38.2
        Edeg = 90. / np.pi * np.arctan2(U, Q) - 38.2
    else:
        Edeg = 0.5 * np.rad2deg(np.arctan(U/Q))

    out = dict(StokesI=I, StokesQ=Q, StokesU=U,
               polInt=pol, degreeP=degp, polErr=polerr,
               Edeg=Edeg)
    return out


def generateStokes(files, **kwargs):
    """
    Calculates Stokes parameters and the fractional polarization from a
    set of files with different polarizers.

    :param files: POL filter - FITS file mapping
    :type files: dictionary
    :param kwargs: keyword arguments
    :type kwargs: dict

    :return: Stokes parameters: Q, U, I, and polarized intensity, normalized intensity
             and 0th header of the first FITS file in the dictionary (for WCS)
    :rtype: dictionary
    """
    settings = dict(smoothing=False,
                    sigma=3.0,
                    ext=1,
                    saveFITS=True,
                    generatePlots=True,
                    acsWFC=True,
                    expFudge=1000.0)
    settings.update(kwargs)

    #load data to a dictionary
    for key, value in files.items():
        fh = pf.open(value)
        data = fh[settings['ext']].data
        hdr = fh[settings['ext']].header

        if settings['ext'] != 0:
            hdr0 = fh[0].header
            for k, value in hdr0.iteritems():
                if ~hdr.has_key(k):
                    if 'NAXIS' in k or 'COUNT' in k:
                        pass
                    else:
                        hdr.update(k, value)

        #convert from cps to cnts/electrons using a fudge time
        if type(settings['expFudge']) == type(1) or type(settings['expFudge']) == type(1.0):
            data *= float(settings['expFudge'])
            hdr.update('EXPTIME', settings['expFudge'])

        #add some keywords, because hstpolima reads wrong ones
        hdr.update('FILTNAM1', hdr['FILTER1'])
        hdr.update('FILTNAM2', hdr['FILTER2'])

        if settings['smoothing']:
            data = ndimage.gaussian_filter(data, sigma=settings['sigma'])

        #add to dictionary
        files[key] = [data, hdr]

        if os.path.isfile(value.replace('.fits', '_mod.fits')):
            os.remove(value.replace('.fits', '_mod.fits'))

        fh.writeto(value.replace('.fits', '_mod.fits'))
        fh.close()

    stokes = stokesParameters(files, acsWFC=settings['acsWFC'])

    #write out the FITS files
    if settings['saveFITS']:
        for key, value in stokes.iteritems():
            if 'Edeg' in key:
                #convert the electric vector position angle to sky
                value += float(files['POL0'][1]['PA_V3'])

            hdu = pf.PrimaryHDU(value, header=files['POL0'][1])

            if os.path.isfile(key + '.fits'):
                os.remove(key + '.fits')

            hdu.writeto(key + '.fits')

    if settings['generatePlots']:
        for key in stokes.keys():
            plt.figure(figsize=(10, 8))
            ax1 = plt.subplot(111)
            fitsobj = maputils.FITSimage(key + '.fits')
            mplim = fitsobj.Annotatedimage(ax1, cmap='binary')
            im = mplim.Image()
            grat = mplim.Graticule()
            grat.setp_gratline(wcsaxis=0, linestyle=':', zorder=1)
            grat.setp_gratline(wcsaxis=1, linestyle=':', zorder=1)
            grat.setp_tick(fontsize=16)
            grat.setp_axislabel(fontsize=16)
            mplim.plot()
            plt.savefig(key + '.pdf')
            plt.close()

    return stokes


if __name__ == '__main__':
    start = time()

    files = dict(POL0='POL0V_drz.fits',
                 POL60='POL60V_drz.fits',
                 POL120='POL120V_drz.fits')

    generateStokes(files, **{'ext': 1,
                             'smoothing': False,
                             'sigma': 2.0,
                             'generatePlots' : False,
                             'expFudge' : False})
    
    elapsed = time() - start
    print 'Processing took {0:.1f} minutes'.format(elapsed / 60.)
