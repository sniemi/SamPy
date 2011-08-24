'''
Different luminosity functions.

:requires: NumPy

:version: 0.1

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu

:warning: This has never been tested!
:todo: add more LFs. There are for example several more from the Bell.
'''
import os
import numpy as N

#This should be global, as all observational data are in the same place
#Note however that because the data is in Dropbox the absolute path
#may not be the same. Thus the home directory is tracked using the HOME
#environment variable
observation_path = os.getenv('HOME') + '/Dropbox/Research/Observations/'

def bellG():
    '''
    G-band LF for all galaxies
    Schecter Function fit parameters
    phi* M* Alpha j  (next line formal errors)
    real errors are probably systematic: see Bell et al.\ 2003 for
    guidance (the errors depend on passband and/or stellar mass)
    0.0172471     -19.7320     -1.02577  1.57122e+08
    0.000552186    0.0264740    0.0249926  2.29536e+06
    Then we present the V/V_max data points; x   phi  phi-1sig  phi+1sig

    :return: absolute magnitude, phi, phi_lo, phi_high
    '''
    file = observation_path + 'bell/sdss2mass_lf/glf.out'
    data = N.loadtxt(file)
    M = data[:, 0]
    phi = data[:, 1]
    phi_low = data[:, 2]
    phi_high = data[:, 3]
    return M, phi, phi_low, phi_high