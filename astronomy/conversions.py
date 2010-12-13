'''
Some functions for astronomy related unit conversions.

@requires: NumPy
@requires: cosmocalc (http://cxc.harvard.edu/contrib/cosmocalc/)

@version: 0.11

@author: Sami Niemi
@contact: niemi@stsci.edu
'''
import numpy as N
from cosmocalc import cosmocalc

def janskyToMagnitude(jansky):
    '''
    Converts janskys to AB? magnitudes.
    @param jansky: can either be a number of a numpy array
    @return: either a float or numpy array
    '''
    return 8.9 - 2.5*N.log10(jansky)

def arcminSquaredToSteradians(arcmin2):
    '''
    Converts arcmin**2 to steradians.
    @param arcmin2: arcmin**2
    @return: steradians 
    '''
    return arcmin2 / ((180/N.pi)**2 * 60 * 60)

def arcminSquaredToSolidAnge(arcmin2):
    '''
    Converts arcmin**2 to solid angle.
    Calls arcminSqauredToSteradians to
    convert arcmin**2 to steradians and
    then divides this with 4pi.
    @param arcmin2: arcmin**2 
    @return: solid angle
    '''
    return arcminSquaredToSteradians(arcmin2) / 4. / N.pi

def comovingVolume(arcmin2, zmin, zmax,
                   H0 = 70, WM = 0.28):
    '''
    Calculates the comoving volume between two redshifts when
    the sky survey has covered arcmin**2 region.
    @param arcmin2: area on the sky in arcmin**2
    @param zmin: redshift of the front part of the volume
    @param zmax: redshift of the back part of the volume
    @param H0: Value of the Hubble constant
    @param WM: Value of the mass density     
    @return: comoving volume between zmin and zmax of arcmin2
            solid angle in Mpc**3
    '''
    front = cosmocalc(zmin, H0, WM)['VCM_Gpc3']
    back = cosmocalc(zmax, H0, WM)['VCM_Gpc3']
    volume = (back - front) * 1e9 * arcminSquaredToSolidAnge(arcmin2)
    return volume