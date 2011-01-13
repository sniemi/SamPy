'''
Observational constrains related to metallicites
in galaxies.

@requires: NumPy

@version: 0.1

@author: Sami-Matias Niemi
@contact: niemi@stsci.edu
'''
import numpy as N

#This should be global, as all observational data are in the same place
#Note however that because the data is in Dropbox the absolute path
#may not be the same. Thus the home directory is tracked using the HOME
#environment variable
observation_path = os.getenv('HOME')+'/Dropbox/Research/Observations/'


def gallazzi(h = 0.7, comments = ';'):
    '''
    Scale stellar masses with h.
    n.b. masses in file are for H0=70.
    '''
    file = observation_ath + 'metals/gallazzi.dat'
    data = N.loadtxt(file, comments = comments)
    twologh = 2.0*N.log10(h)
    return data[:,0]+twologh, data[:,1], data[:,2], data[:,3]
