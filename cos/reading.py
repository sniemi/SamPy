"""
Routines useful for dealing with cos spectra, especially reading different files.
"""
import numpy as np
import pyfits

def readx1d(filename):
    """
    Read an x1d format spectrum from calcos.

    :param filename: name of the x1d file
    :type filename: string

    For the output spectra::

        wa = wavelengths (Angstroms)
        fl = flux
        er = 1 sigma error in flux
        dq = data quality, > 0 means bad for some reason
        gr = gross count rate, gross counts / (exposure time in s)
        bg = background count rate
        net = (gr - bg) / eps, where eps is the flat fielding.
    """
    vnum = int(filename.split('/')[-1][4:6])
    fh = pyfits.open(filename)
    hd = fh[0].header
    optelem = hd['OPT_ELEM']
    cwa = hd['CENTRWV']
    exptime = fh[1].header['EXPTIME']

    keys = 'WAVELENGTH FLUX ERROR DQ GROSS NET BACKGROUND'.split()
    names = 'wa,fl,er,dq,gr,net,bg'
    r = fh['SCI'].data
    fh.close()
    vals = [r[k][0] for k in keys]
    isort = vals[0].argsort()
    for i in range(1, len(vals)):
        vals[i] = vals[i][isort]
    sp1 = np.rec.fromarrays(vals, names=names)

    vals = [r[k][1] for k in keys]
    isort = vals[0].argsort()
    for i in range(1, len(vals)):
        vals[i] = vals[i][isort]
    sp2 = np.rec.fromarrays(vals, names=names)
    if sp1.wa[0] < sp2.wa[0]:
        info1 = vnum, optelem, cwa, 'FUVB', exptime
        info2 = vnum, optelem, cwa, 'FUVA', exptime
    else:
        info2 = vnum, optelem, cwa, 'FUVB', exptime
        info1 = vnum, optelem, cwa, 'FUVA', exptime

    return [sp1, sp2], [info1, info2]
