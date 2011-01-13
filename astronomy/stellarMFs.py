'''
Differrent types of stellar mass functions.

@requires: NumPy

@version: 0.1

@author: Sami-Matias Niemi
@contact: niemi@stsci.edu

@todo: This is hardly finished...
'''
import os
import numpy as N
import io.sextutils as su

#This should be global, as all observational data are in the same place
#Note however that because the data is in Dropbox the absolute path
#may not be the same. Thus the home directory is tracked using the HOME
#environment variable
observation_path = os.getenv('HOME')+'/Dropbox/Research/Observations/'

def stellarMfs():
    '''
    @requires: io.sexutils
    @return: sexutils instance to MFs data file.
    '''
    file = observation_path + 'stellarmf/sami.dat'
    tmp = su.se_catalog(file)
    return tmp, _getIDs(tmp)

def bellG(h = 0.7, chabrier = True):
    '''
    G-band derived stellar mass function for all galaxies
    Schecter Function fit parameters
    phi* M* Alpha j  (next line formal errors)
    real errors are probably systematic: see Bell et al.\ 2003 for
    guidance (the errors depend on passband and/or stellar mass)
    0.0101742      10.7003     -1.10350  5.46759e+08
    0.000512733    0.0154157    0.0239414  1.06609e+07
    Then we present the V/V_max data points; x   phi  phi-1sig  phi+1sig
    Convert to h (default = 0.7) and Chabrier IMF.
    '''
    file = observation_path + 'bell/sdss2mass_lf/gmf.out'
    data = N.loadtxt(file)
    m = data[:,0] - 2.0 * N.log10(h) #- 0.15
    if chabrier:
        m -= 0.15
    phi = data[:,1]*h**3
    phi_low = data[:,2]*h**3
    phi_high = data[:,3]*h**3
    return m, N.log10(phi), N.log10(phi_low), N.log10(phi_high)

def bellK(h = 0.7, chabrier = True):
    '''
    K-band derived stellar mass function for all galaxies
    Schecter Function fit parameters
    phi* M* Alpha j  (next line formal errors)
    real errors are probably systematic: see Bell et al.\ 2003 for
    guidance (the errors depend on passband and/or stellar mass)
    0.0132891      10.6269    -0.856790  5.26440e+08
    0.000586424    0.0144582    0.0422601  1.18873e+07
    Then we present the V/V_max data points; x   phi  phi-1sig  phi+1sig
    Convert to h (default = 0.7) and Chabrier IMF.
    '''
    file = observation_path + 'bell/sdss2mass_lf/kmf.out'
    data = N.loadtxt(file)
    m = data[:,0] - 2.0 * N.log10(h) #- 0.15
    if chabrier:
        m -= 0.15
    phi = data[:,1]*h**3
    phi_low = data[:,2]*h**3
    phi_high = data[:,3]*h**3
    return m, N.log10(phi), N.log10(phi_low), N.log10(phi_high)

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
    '''
    Stellar mass to halo mass ratio as a function of halo mass.
    Fitting function from ???
    '''
    mstar = 2.0*f0*10.0**mh / ((10.0**mh/10.0**m1)**(-beta)+(10.0**mh/10.0**m1)**gamma)
    fstar = mstar / 10.0**mh
    return fstar

def fstar_behroozi_data():
    '''
    Stellar mass to halo mass ratio as a function of halo mass.
    Data from Behroozi et al. ???
    '''
    file = observation_path + 'behroozi/mhmstar.dat'
    data = N.loadtxt(file)
    return data[:,0], data[:,1]

def mstar_bell(h = 0.7):
    '''
    Stellar mass function from bell et al. (H0=100).
    Convert to Chabrier IMF.
    '''
    file = observation_path + 'behroozi/mhmstar.dat'
    
    data = N.loadtxt(file)

    m = data[:,0] - 0.1
    phi = N.log10(data[:,1])
    phi_low = N.log10(data[:,2])
    phi_high = N.log10(data[:,3])
    return m, phi, phi_low, phi_high






def mstar_lin(h = 0.7):
    '''
    @warning: The observation file is missing. Do not use!
    '''
    file = observation_path + 'sdss_mf/SDSS_SMF.dat'
    data = N.loadtxt(file)
    mbin = data[:,2] - 2.0*N.log10(h)
    phi_low = N.log10((data[:,3] - data[:,4])*h**3)
    phi_high = N.log10((data[:,3] + data[:,4])*h**3)
    phi = N.log10(data[:,3]*h**3)
    return mbing, phi, phi_low, phi_high

def _getIDs(tmp):
    '''
    A little helper function to parse header information
    from the stellar mass function ascii file called
    sami.dat.
    @param tmp: instance to sexutils catalogue 
    @return: dictionary of IDs
    '''
    out = {}
    hdr = tmp._header.split('##')
    for line in hdr:
        if '=' in line:
            tmp = line.strip().split('=')
            out[tmp[0]] = tmp[1]
    return out