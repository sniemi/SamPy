"""
Galaxy luminosity functions at different wavelengths from different papers.

:requires: NumPy
:requires: SamPy

:version: 0.2

:author: Sami-Matias Niemi
:contact: sammyniemi2010@gmail.com
"""
import os
import numpy as np
import SamPy.astronomy.conversions as conv

#This should be global, as all observational data are in the same place
#Note however that because the data is in Dropbox the absolute path
#may not be the same. Thus the home directory is tracked using the HOME
#environment variable
observation_path = os.getenv('HOME') + '/Dropbox/Research/Observations/'


def bellG():
    """
    G-band LF for all galaxies.

    Schechter Function fit parameters::

        phi* M* Alpha j  (next line formal errors)
        real errors are probably systematic: see Bell et al.\ 2003 for
        guidance (the errors depend on passband and/or stellar mass)
        0.0172471     -19.7320     -1.02577  1.57122e+08
        0.000552186    0.0264740    0.0249926  2.29536e+06
        Then we present the V/V_max data points; x   phi  phi-1sig  phi+1sig

    :return: absolute magnitude, phi, phi_lo, phi_high
    """
    file = observation_path + 'bell/sdss2mass_lf/glf.out'
    data = np.loadtxt(file)
    M = data[:, 0]
    phi = data[:, 1]
    phi_low = data[:, 2]
    phi_high = data[:, 3]
    return M, phi, phi_low, phi_high


def Herschel100Lapi():
    """
    Herschel 100 micron band luminosity function at different redshift bins from Lapi et al. (2011)

    :return: luminosity functions at different bins
    :rtype: dictionary
    """
    file = observation_path + 'lf/Herschel100mic'
    data = np.loadtxt(file)

    #convert the values to Lsun, takes into account the width of the PACS 100 micron band
    #lsun = conv.ergsperSecondtoLsun((10**data[:, 0] * conv.angstromToHertz(100 * 1e4) * 1e7))
    lsun = conv.ergsperSecondtoLsun((10**data[:, 0] *
                                     (conv.angstromToHertz(85 * 1e4) - conv.angstromToHertz(125 * 1e4)) * 1e7))

    out = {'Lsun': lsun,
           'z1.5': data[:, 1:4],
           'z1.8': data[:, 4:7],
           'z2.2': data[:, 7:10],
           'z3.2': data[:, 10:]}
    return out


def Herschel250Lapi():
    """
    Herschel 250 micron band luminosity function at different redshift bins from Lapi et al. (2011)

    :return: luminosity functions at different bins
    :rtype: dictionary
    """
    file = observation_path + 'lf/Herschel250mic'
    data = np.loadtxt(file)

    #convert the values to Lsun
    #lsun = conv.ergsperSecondtoLsun((10**data[:, 0] * conv.angstromToHertz(250 * 1e4) * 1e7))
    lsun = conv.ergsperSecondtoLsun((10**data[:, 0] *
                                     (conv.angstromToHertz(200*1e4) - conv.angstromToHertz(300*1e4)) * 1e7))

    out = {'Lsun': lsun,
           'z1.4': data[:, 1:4],
           'z1.8': data[:, 4:7],
           'z2.2': data[:, 7:10],
           'z3.2': data[:, 10:]}
    return out


def Herschel250Dye():
    """
    Herschel 250 micron band luminosity function at different redshift bins from Dye et al. A&A 518, L10 (2010)

    :return: luminosity functions at different bins
    :rtype: dictionary
    """
    file = observation_path + 'lf/Herschel250micDye'
    data = np.loadtxt(file)

    out = {'Lsun': data[:, 0],
           'z0.5': data[:, 1],
           'z0.5max': data[:, 2]}

    return out