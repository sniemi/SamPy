"""
Basic operations for FITS files.

:requires: PyFITS
:requirs: NumPy

:author: Sami-Matias Niemi
:version: 0.1
"""
import pyfits as pf
import numpy as np

def getWavelengths(filename, length, ext=0):
    """
    Returns ndarray of wavelengths. This information is
    derived using the FITS header.

    :param: filename, name of the input file
    :param: length, how many wavelength values
    :param: ext, FITS extension number

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
            raise NotImplementedError, 'crpix > 0 not implemented yet'
        else:
            xps = np.arange(0, length) * delta + crval
    else:
        raise NotImplementedError('Does not support LOG spacing yet...')

    return xps
