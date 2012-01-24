"""
Functions related to polarimetry.

:requires: NumPy
:requires: SciPy
:requires: matplotlib
:requires: Kapteyn Python package

:author: Sami-Matias Niemi
:contact: sammy@sammyniemi.com

:version: 0.1
"""
from time import time
import os, os.path
import numpy as np
import pyfits as pf
from scipy import ndimage
from kapteyn import maputils
from matplotlib import pyplot as plt


def stokesParameters(pol0, pol60, pol120):
    """
    Calculates Stokes parameters from polarized images.

    :param pol0: POL0 data
    :type pol0: ndarray
    :param pol60: POL60 data
    :type pol60: ndarray
    :param pol120: POL120 data
    :type pol120: ndarray

    :return: Stoke I, Q, U, polarized intensity, and normalized polarized intensity
    :rtype: dictionary
    """
    I = (2 / 3.) * (pol0 + pol60 + pol120)
    Q = (2 / 3.) * (2. * pol0 - pol60 - pol120)
    U = (2 / np.sqrt(3)) * (pol60 - pol120)
    Poli = np.sqrt(Q ** 2 + U ** 2)
    PP = (np.sqrt(Q ** 2 + U ** 2) / I)

    out = dict(StokesI=I, StokesQ=Q, StokesU=U, PolInt=Poli, NormPI=PP)
    return out


def generateStokes(files, **kwargs):
    """

    :param files: POL filter - FITS file mapping
    :type files: dictionary

    :return: stoke parameters: Q, U, I, and polarized intensity, normalized intensity
             and 0th header of the first FITS file in the dictionary (for WCS)
    :rtype: dictionary
    """
    settings = dict(smoothing=False,
                    sigma=3.0,
                    ext=1,
                    saveFITS=True,
                    generatePlots=True)
    settings.update(kwargs)

    #header of the first file, needed for WCS
    hdr = pf.open(files.values()[0])[0].header

    #load data
    for key, value in files.iteritems():
        data = pf.open(value)[settings['ext']].data
        if settings['smoothing']:
            data = ndimage.gaussian_filter(data, sigma=settings['sigma'])
        files[key] = data

    stokes = stokesParameters(files['POL0'], files['POL60'], files['POL120'])

    #write out the FITS files
    if settings['saveFITS']:
        for key, value in stokes.iteritems():
            hdu = pf.PrimaryHDU(value, header=hdr)
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

    return stokes.update(dict(header=hdr))


if __name__ == '__main__':
    start = time()

    files = dict(POL0='POL0V_drz_single_sci.fits',
                 POL60='POL60V_drz_single_sci.fits',
                 POL120='POL120V_drz_single_sci.fits')

    generateStokes(files, **{'ext': 0, 'smoothing': True, 'sigma': 1.5})

    elapsed = time() - start
    print 'Processing took {0:.1f} minutes'.format(elapsed / 60.)