"""
Observational constrains related to metallicities in galaxies.

:requires: NumPy

:version: 0.1

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu
"""
import os
import numpy as np

#This should be global, as all observational data are in the same place
#Note however that because the data is in Dropbox the absolute path
#may not be the same. Thus the home directory is tracked using the HOME
#environment variable
observation_path = os.getenv('HOME') + '/Dropbox/Research/Observations/'


def gallazzi(h=0.7):
    """
    Scale stellar masses with h.
    n.b. masses in file are for H0=70 so no scaling is required
    if using Hubble constant 70.

    :param h: Hubble parameter to scale to
    :type h: float

    return: Stellar masses
    :rtype: a list of NumPy arrays
    """
    file = observation_path + 'metals/gallazzi.dat'
    data = np.loadtxt(file, comments=';')
    twologh = 2.0 * np.log10(h)
    return data[:, 0] + twologh, data[:, 1], data[:, 2], data[:, 3]
