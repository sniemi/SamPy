'''
Observational constrains related to gas masses in galaxies.

:requires: NumPy

:version: 0.1

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu
'''
import os
import numpy as N

#This should be global, as all observational data are in the same place
#Note however that because the data is in Dropbox the absolute path
#may not be the same. Thus the home directory is tracked using the HOME
#environment variable
observation_path = os.getenv('HOME') + '/Dropbox/Research/Observations/'


def gasFractionKannappan(chabrier=True):
    '''
    Gas fraction fitting function from Kannappan et al.
    using either the Chabrier (default) or diet Salpeter IMF.
    '''
    mstar = N.array([8.75, 9.25, 9.75, 10.25, 10.75, 11.25, 11.75])
    log_gs = N.array([0.2, 0.0, -0.1, -0.4, -0.7, -0.8, -0.85])
    if chabrier:
        #convert from diet salpeter to chabrier
        mstar -= 0.1
    fgas = 10.0 ** log_gs / (1.0 + 10.0 ** log_gs)
    return mstar, fgas


def HIMassFunctionZwaan(mbin, H0=70.0):
    '''
    Observed HI mass function.
    Zwaan et al.
    :param mbin: bins in log10(masses)
    '''
    mstar = 9.8 - 2.0 * N.log10(H0 / 75.0)
    alpha = -1.37
    thetastar = 0.006 * (H0 / 75.0) ** 3
    x = 10.0 ** (mbin - mstar)
    theta = N.log10(2.3 * thetastar * x ** (alpha + 1) * N.exp(-x))
    return theta


def HIMassFunctionBell(h=0.7):
    '''
    HI mass function (predicted using default technique)
    Schecter Function fit parameters
    phi* M* Alpha j  (next line formal errors)
    real errors are probably systematic: see Bell et al.\ 2003 for
    guidance (the errors depend on passband and/or stellar mass)
    0.0142750      9.67205     -1.42495  1.03937e+08
    0.00612444     0.154853     0.205068  1.64674e+07
    Then we present the V/V_max data points; x   phi  phi-1sig  phi+1sig
    '''
    file = observation_path + 'bell/sdss2mass_lf/himf.out'
    data = N.loadtxt(file)
    m = data[:, 0] - 2. * N.log10(h)
    phi = N.log10(data[:, 1] * h ** 3)
    phi_low = N.log10(data[:, 2] * h ** 3)
    phi_high = N.log10(data[:, 3] * h ** 3)
    return m, phi, phi_low, phi_high


def H2MassFunctionBell(h=0.7):
    '''
    H2 mass function from Bell et al.
    '''
    file = observation_path + 'bell/sdss2mass_lf/h2mf.out'
    data = N.loadtxt(file)
    m = data[:, 0] - 2. * N.log10(h)
    phi = N.log10(data[:, 1] * h ** 3)
    phi_low = N.log10(data[:, 2] * h ** 3)
    phi_high = N.log10(data[:, 3] * h ** 3)
    return m, phi, phi_low, phi_high
