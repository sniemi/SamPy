"""
Functions related to polarimetry.

:requires: NumPy
:requires: SciPy
:requires: matplotlib
:requires: Kapteyn Python package

:author: Sami-Matias Niemi
:contact: sammy@sammyniemi.com

:version: 0.2
"""
from time import time
import os, os.path
import numpy as np
import pyfits as pf
from scipy import ndimage
from kapteyn import maputils
from matplotlib import pyplot as plt


def stokesParameters(pol0, pol60, pol120, acsWFC=True):
    """
    Calculates Stokes parameters from polarized images.

    :param pol0: POL0 data
    :type pol0: ndarray
    :param pol60: POL60 data
    :type pol60: ndarray
    :param pol120: POL120 data
    :type pol120: ndarray
    :param acsWFC: for ACS WFC a correction are being applied
    :type acsWFC: boolean

    :Note: the ACS WFC correction factors are from Biretta et al. 2004 (ISR)

    :return: Stokes I, Q, and U, polarized fraction, degree of (linear) polarization,
             and electric-vector position angle
    :rtype: dictionary
    """
    if acsWFC:
        pol60 *= 0.979
        pol120 *= 1.014

    I = (2 / 3.) * (pol0 + pol60 + pol120)
    Q = (2 / 3.) * (2. * pol0 - pol60 - pol120)
    U = (2 / np.sqrt(3)) * (pol60 - pol120)

    PU = U / I
    PQ = Q / I
    
    #if acsWFC:
    #    PU -= 0.022*np.sin(np.deg2rad(2*42.))
    #    PQ -= 0.022*np.cos(np.deg2rad(2*42.))

    Poli = np.sqrt(PQ*PQ + PU*PU)
    PP = Poli / I
    Edeg = 0.5 * np.rad2deg(np.arctan(U/Q)) - 38.2

    out = dict(StokesI=I, StokesQ=Q, StokesU=U, PolInt=Poli, degreeP=PP, Edeg=Edeg)
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

    #load data
    for key, value in files.iteritems():
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

        #convert from count rate to cnts / electrons
        if type(settings['expFudge']) == type(1) or type(settings['expFudge']) == type(1.0):
            data *= float(settings['expFudge'])
            hdr.update('EXPTIME', settings['expFudge'])
            hdr.update('FILTNAM1', hdr['FILTER1'])
            hdr.update('FILTNAM2', hdr['FILTER2'])

        if settings['smoothing']:
            data = ndimage.gaussian_filter(data, sigma=settings['sigma'])
        files[key] = [data, hdr]

        if os.path.isfile(value.replace('.fits', '_mod.fits')):
            os.remove(value.replace('.fits', '_mod.fits'))
        fh.writeto(value.replace('.fits', '_mod.fits'))

    stokes = stokesParameters(files['POL0'][0],
                              files['POL60'][0],
                              files['POL120'][0],
                              settings['acsWFC'])

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
                             'expFudge' : 500})

    elapsed = time() - start
    print 'Processing took {0:.1f} minutes'.format(elapsed / 60.)
