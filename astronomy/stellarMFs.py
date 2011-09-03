"""
Different stellar mass functions.
Some are based on observational data while others are fitting functions.

:requires: NumPy
:requires: smnIO.sextutils

:version: 0.2

:author: Sami-Matias Niemi
:contact : niemi@stsci.edu
"""
import os
import numpy as N
import smnIO.sextutils as su

#This should be global, as all observational data are in the same place
#Note however that because the data is in Dropbox the absolute path
#may not be the same. Thus the home directory is tracked using the HOME
#environment variable
observation_path = os.getenv('HOME') + '/Dropbox/Research/Observations/'

def stellarMfs():
    """
    :requires: io.sexutils
    :return: sexutils instance to MFs data file.
    """
    file = observation_path + 'stellarmf/sami.dat'
    tmp = su.se_catalog(file)
    return tmp, _getIDs(tmp)


def highRedshiftMFs():
    """
    Stellar mass functions from Valentino Gonzalez et al. arXiv:1008.3901v2

    :note: These values probably use the Salpeter IMF. If so we should then subtract 0.25 dex from log(m*) to go to Chabrier.


    Table 1::

                                log10 (dN/dlog10 (M/M_sun)/Mpc3 )
        log10(M/M_sun)         3.8    err     5.0    err      5.9   err     6.8    err

    :return: high-redshift stellar mass functions from Gonzalez. et al (2011) paper
    :rtype: dictionary
    """
    out = {}
    file = observation_path + 'stellarmf/HighRedshift.dat'
    tmp = N.loadtxt(file)
    out['stellar_mass'] = tmp[:, 0] - 0.25
    out['z = 3.8'] = (tmp[:, 1], tmp[:, 2])
    out['z = 5.0'] = (tmp[:, 3], tmp[:, 4])
    out['z = 5.9'] = (tmp[:, 5], tmp[:, 6])
    out['z = 6.8'] = (tmp[:, 7], tmp[:, 8])
    return out


def bellG(h=0.7, chabrier=True):
    """
    G-band derived stellar mass function for all galaxies
    Schecter Function fit parameters
    phi* M* Alpha j  (next line formal errors)
    real errors are probably systematic: see Bell et al.\ 2003 for
    guidance (the errors depend on passband and/or stellar mass)
    0.0101742      10.7003     -1.10350  5.46759e+08
    0.000512733    0.0154157    0.0239414  1.06609e+07
    Then we present the V/V_max data points; x   phi  phi-1sig  phi+1sig
    Convert to h (default = 0.7) and Chabrier IMF.

    :param h: the Hubble parameter (default h = 0.7)
    :param chabrier: whether or not to convert to Chabrier IMF (default = True)

    :return: log10(stellar mass), log10(phi), log10(phi_low), log10(phi_high)
    """
    file = observation_path + 'bell/sdss2mass_lf/gmf.out'
    data = N.loadtxt(file)
    m = data[:, 0] - 2.0 * N.log10(h) #- 0.15
    if chabrier:
        m -= 0.15
    phi = data[:, 1] * h ** 3
    phi_low = data[:, 2] * h ** 3
    phi_high = data[:, 3] * h ** 3
    return m, N.log10(phi), N.log10(phi_low), N.log10(phi_high)


def bellK(h=0.7, chabrier=True):
    """
    K-band derived stellar mass function for all galaxies
    Schecter Function fit parameters
    phi* M* Alpha j  (next line formal errors)
    real errors are probably systematic: see Bell et al.\ 2003 for
    guidance (the errors depend on passband and/or stellar mass)
    0.0132891      10.6269    -0.856790  5.26440e+08
    0.000586424    0.0144582    0.0422601  1.18873e+07
    Then we present the V/V_max data points; x   phi  phi-1sig  phi+1sig
    Convert to h (default = 0.7) and Chabrier IMF.

    :param h: the Hubble parameter (default h = 0.7)
    :param chabrier: whether or not to convert to Chabrier IMF (default = True)

    :return: log10(stellar mass), log10(phi), log10(phi_low), log10(phi_high)
    """
    file = observation_path + 'bell/sdss2mass_lf/kmf.out'
    data = N.loadtxt(file)
    m = data[:, 0] - 2.0 * N.log10(h) #- 0.15
    if chabrier:
        m -= 0.15
    phi = data[:, 1] * h ** 3
    phi_low = data[:, 2] * h ** 3
    phi_high = data[:, 3] * h ** 3
    return m, N.log10(phi), N.log10(phi_low), N.log10(phi_high)


def panter():
    """
    This function returns Benjamin Panter's stellar mass function from:
    http://www.blackwell-synergy.com/doi/pdf/10.1111/j.1365-2966.2007.11909.x
    It uses the DR3 data with the BC03 models and a Chabrier IMF.

    :return:
    """
    file = observation_path + 'panter/panter.dat'
    data = N.loadtxt(file, comments=';')
    nlow = N.log10(data[:, 1] - data[:, 2])
    nhigh = N.log10(data[:, 1] + data[:, 2])
    n = N.log10(data[:, 1])
    return data[:, 0], n, nlow, nhigh


def fstarBen(mh, m1, f0, beta, gamma):
    """
    Stellar mass to halo mass ratio as a function of halo mass.
    Fitting function from Moster et al.
    """
    mstar = 2.0 * f0 * 10.0 ** mh / ((10.0 ** mh / 10.0 ** m1) ** (-beta) + (10.0 ** mh / 10.0 ** m1) ** gamma)
    fstar = mstar / 10.0 ** mh
    return fstar


def fstarBehroozi():
    """
    Stellar mass to halo mass ratio as a function of halo mass.
    Data from Behroozi et al. ???
    """
    file = observation_path + 'behroozi/mhmstar.dat'
    data = N.loadtxt(file)
    return data[:, 0], data[:, 1]


###############################################################################
def mstar_bell(h=0.7, chabrier=True):
    """
    :warning: Data are missing??

    Stellar mass function from bell et al. (H0=100).
    Convert to Chabrier IMF.
    """
    file = observation_path + ''
    data = N.loadtxt(file)
    m = data[:, 0]
    if chabrier:
        m -= 0.1
    phi = N.log10(data[:, 1])
    phi_low = N.log10(data[:, 2])
    phi_high = N.log10(data[:, 3])
    return m, phi, phi_low, phi_high


def mstar_lin(h=0.7):
    """
    :warning: The observation file is missing. Do not use!
    """
    file = observation_path + 'sdss_mf/SDSS_SMF.dat'
    data = N.loadtxt(file)
    mbin = data[:, 2] - 2.0 * N.log10(h)
    phi_low = N.log10((data[:, 3] - data[:, 4]) * h ** 3)
    phi_high = N.log10((data[:, 3] + data[:, 4]) * h ** 3)
    phi = N.log10(data[:, 3] * h ** 3)
    return mbing, phi, phi_low, phi_high

###############################################################################
def _getIDs(tmp):
    """
    A little helper function to parse header information
    from the stellar mass function ascii file called
    sami.dat.
    :param tmp: instance to sexutils catalogue
    :return: dictionary of IDs
    """
    out = {}
    hdr = tmp._header.split('##')
    for line in hdr:
        if '=' in line:
            tmp = line.strip().split('=')
            out[tmp[0]] = tmp[1]
    return out