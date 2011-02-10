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
    Converts Janskys to AB magnitudes.
    @note: Can be used with SQLite3 database.
    @param jansky: can either be a number or a NumPy array
    @return: either a float or NumPy array
    '''
    return 8.9 - 2.5*N.log10(jansky)

def ABMagnitudeToJansky(ABmagnitude):
    '''
    Converts AB magnitudes to Janskys.
    @note: Can be used with SQLite3 database.
    @param ABmagnitude: can be either a number or a NumPy array
    @return: either a float or NumPy array 
    '''
    return 10**((23.9 - ABmagnitude)/2.5)/1e6

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

def Luminosity(abs_mag):
    '''
    Converts AB magnitudes to luminosities in L_sun
    @param abs_mag: AB magnitude of the object
    @return: luminosity 
    '''
    return 10.0**((4.85-abs_mag)/2.5)

def get_flat_flambda_dmag(plambda, plambda_ref):
    '''                                                                                                             
    Compute the differential AB-mag for an object flat in f_lambda                                                   
    '''
    # compute mag_AB for an object at the desired wavelength                                                         
    mag1 = get_magAB_from_flambda(1.0e-17, plambda)

    # compute mag_AB for an object at the reference wavelength                                                       
    mag2 = get_magAB_from_flambda(1.0e-17, plambda_ref)

    # return the mag difference                                                                                      
    return (mag1 - mag2)

def get_magAB_from_flambda(flambda, wlength):
    '''                                                                                                             
    Converts a mag_AB value at a wavelength to f_lambda                                                              
                                                                                                                     
    @param flambda: mag_AB value                                                                                     
    @type flambda: float                                                                                             
    @param wlength: wavelength value [nm]                                                                            
    @type wlength: float                                                                                             
                                                                                                                     
    @return: the mag_AB value                                                                                        
    @rtype: float                                                                                                    
    '''
    import math

    # transform from flambda to fnue                                                                                 
    fnu = (wlength*wlength) / 2.99792458e+16 * flambda

    # compute mag_AB                                                                                                 
    mag_AB = -2.5 * math.log10(fnu) - 48.6

    # return the mag_AB                                                                                              
    return mag_AB

