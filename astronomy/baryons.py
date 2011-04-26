'''
Helper functions related to baryonic constrains such as mass functions.

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


def BellBaryonicMassFunction(h=0.7):
    '''
    G-derived baryonic mass function using default gas
    Schecter Function fit parameters
    phi* M* Alpha j  (next line formal errors)
    real errors are probably systematic: see Bell et al. 2003 for
    guidance (the errors depend on passband and/or stellar mass)
        0.0105038      10.7236     -1.22776  6.65221e+08
      0.000857033    0.0448084    0.0552834  1.45862e+07
    Then we present the V/V_max data points; x   phi  phi-1sig  phi+1sig

    :param h: Hubble parameter
    :type h: float

    :note: In Chabrier IMF.
    '''
    data = N.loadtxt(observation_path + 'bell/sdss2mass_lf/barymf1.out')
    m = data[:, 0] - 2.0 * N.log10(h) - 0.15
    phi = data[:, 1] * h ** 3
    phi_low = data[:, 2] * h ** 3
    phi_high = data[:, 3] * h ** 3
    return m, N.log10(phi), N.log10(phi_low), N.log10(phi_high)
