'''
Differrent types of stellar mass functions.

@requires: NumPy

@version: 0.1

@author: Sami-Matias Niemi
@contact: niemi@stsci.edu

@todo: This is hardly finished...
'''
import numpy as N

#This should be global, as all observational data are in the same place
observation_path = '/Users/niemi/Dropbox/Research/Observations/'

def panter():
    '''
    This function returns Benjamin Panter's stellar mass function from:
    http://www.blackwell-synergy.com/doi/pdf/10.1111/j.1365-2966.2007.11909.x
    It uses the DR3 data with the BC03 models and a Chabrier IMF.
    @return:
    '''
    file = observation_path + 'panter/panter.dat'
    data = N.loadtxt(file, comments = ';')
    
    nlow = N.log10(data[:,1] - data[:,2])
    nhigh = N.log10(data[:,1] + data[:,2])
    n = N.log10(data[:,1])

    return data[:,0], n, nlow, nhigh


def fstar_ben(mh, m1, f0, beta, gamma):
  mstar = 2.0*f0*10.0**mh / ((10.0**mh/10.0**m1)**(-beta)+(10.0**mh/10.0**m1)**gamma)
  fstar = mstar / 10.0**mh
  return fstar

def fstar_behroozi_data(file):
    '''
    Stellar mass to halo mass ratio as a function of halo mass.
    '''
    file = observation_path + 'behroozi/mhmstar.dat'
    data = N.loadtxt(file)
    return data[:,0], data[:,1]

def mstar_Bell_H(file, h = 0.7):
    '''
    Stellar mass function at z=0 from bell et al.
    Convert to H_0 = 70 and Chabrier IMF.
    '''
    data = N.loadtxt(file)
    
    m = data[:,0] - 2.0 * N.log10(h) - 0.15
    phi = data[:,1]*h**3
    phi_low = data[:,2]*h**3
    phi_high = data[:,3]*h**3

    return m, N.log10(phi), N.log10(phi_low), N.log10(phi_high)

def mstar_bell(file, h = 0.7):
    '''
    Stellar mass function from bell et al. (H0=100).
    Convert to Chabrier IMF.
    '''
    data = N.loadtxt(file)

    m = data[:,0] - 0.1
    phi = N.log10(data[:,1])
    phi_low = N.log10(data[:,2])
    phi_high = N.log10(data[:,3])
    return m, phi, phi_low, phi_high

def mstar_lin(file, h = 0.7):

    data = N.loadtxt(file)

    mbin = data[:,2] - 2.0*N.log10(h)
    phi_low = N.log10((data[:,3] - data[:,4])*h**3)
    phi_high = N.log10((data[:,3] + data[:,4])*h**3)
    phi = N.log10(data[:,3]*h**3)

    return mbing, phi, phi_low, phi_high

def mhi_bell(file, h = 0.7):
    data = N.loadtxt(file)
    m = data[:,0] - 2.*N.log10(h)
    phi = N.log10(data[:,1]*h**3)
    phi_low = N.log10(data[:,2]*h**3)
    phi_high = N.log10(data[:,3]*h**3)
    return m, phi, phi_low, phi_high

def gallazzi(file, h = 0.7, comments = ';'):
    '''
    Scale stellar masses with h.
    n.b. masses in file are for H0=70.
    '''
    data = N.loadtxt(file, comments = comments)
    twologh = 2.0*N.log10(h)
    return data[:,0]+twologh, data[:,1], data[:,2], data[:,3]