"""
Basic operations for FITS files.

:requires: PyFITS
:requirs: NumPy

:author: Sami-Matias Niemi
:version: 0.2
"""
import pyfits as pf
import numpy as np

def getWavelengths(filename, length, ext=0):
    """
    Returns ndarray of wavelengths. This information is
    derived using the FITS header.

    :param filename: name of the input file
    :type filename: string
    :param length: how many wavelength values
    :type length: int
    :param ext: FITS extension number
    :type ext: int

    :return: wavelengths
    :rtype: ndarray
    """

    hdr = pf.open(filename)[ext].header

    crval = hdr['CRVAL1']
    crpix = hdr['CRPIX1']
    delta = hdr['CD1_1']

    if 'LIN' in hdr['CTYPE1']:
        if crpix < 0:
            xps = np.arange(0, length - crpix + 1) * delta + crval
            xps = xps[-crpix + 1:]
        elif crpix > 0:
            xps = np.arange(crpix - 1, length + crpix - 1)*delta + crval
        else:
            xps = np.arange(0, length) * delta + crval
    else:
        raise NotImplementedError('Does not support LOG spacing yet...')

    return xps
