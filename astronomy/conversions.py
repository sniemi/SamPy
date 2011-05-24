'''
Some functions for astronomy related unit conversions.

:requires: NumPy
:requires: cosmocalc (http://cxc.harvard.edu/contrib/cosmocalc/)

:version: 0.11

:author: Sami Niemi
:contact: niemi@stsci.edu
'''
import numpy as np
from cosmocalc import cosmocalc

def janskyToMagnitude(jansky):
    '''
    Converts Janskys to AB magnitudes.

    :note: Can be used with SQLite3 database.

    :param jansky: can either be a number or a NumPy array

    :return: either a float or NumPy array
    '''
    return 8.9 - 2.5*np.log10(jansky)

def ABMagnitudeToJansky(ABmagnitude):
    '''
    Converts AB magnitudes to Janskys.

    :note: Can be used with SQLite3 database.

    :param ABmagnitude: can be either a number or a NumPy array

    :return: either a float or NumPy array
    '''
    return 10**((23.9 - ABmagnitude)/2.5)/1e6

def arcminSquaredToSteradians(arcmin2):
    '''
    Converts arcmin**2 to steradians.

    :param arcmin2: arcmin**2

    :return: steradians
    '''
    return arcmin2 / ((180/np.pi)**2 * 60 * 60)

def arcminSquaredToSolidAnge(arcmin2):
    '''
    Converts arcmin**2 to solid angle.
    Calls arcminSqauredToSteradians to
    convert arcmin**2 to steradians and
    then divides this with 4pi.

    :param arcmin2: arcmin**2

    :return: solid angle
    '''
    return arcminSquaredToSteradians(arcmin2) / 4. / np.pi

def comovingVolume(arcmin2, zmin, zmax,
                   H0 = 70, WM = 0.28):
    '''
    Calculates the comoving volume between two redshifts when
    the sky survey has covered arcmin**2 region.

    :param arcmin2: area on the sky in arcmin**2
    :param zmin: redshift of the front part of the volume
    :param zmax: redshift of the back part of the volume
    :param H0: Value of the Hubble constant
    :param WM: Value of the mass density

    :return: comoving volume between zmin and zmax of arcmin2
            solid angle in Mpc**3
    '''
    front = cosmocalc(zmin, H0, WM)['VCM_Gpc3']
    back = cosmocalc(zmax, H0, WM)['VCM_Gpc3']
    volume = (back - front) * 1e9 * arcminSquaredToSolidAnge(arcmin2)
    return volume

def Luminosity(abs_mag):
    '''
    Converts AB magnitudes to luminosities in L_sun

    :param abs_mag: AB magnitude of the object

    :return: luminosity
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
                                                                                                                     
    :param flambda: mag_AB value
    :type flambda: float
    :param wlength: wavelength value [nm]
    :type wlength: float
                                                                                                                     
    :return: the mag_AB value
    :rtype: float
    '''
    import math

    # transform from flambda to fnue                                                                                 
    fnu = (wlength*wlength) / 2.99792458e+16 * flambda

    # compute mag_AB                                                                                                 
    mag_AB = -2.5 * math.log10(fnu) - 48.6

    # return the mag_AB                                                                                              
    return mag_AB

def redshiftFromScale(scale):
    '''
    Converts a scale factor to redshift.
    '''
    return 1./scale - 1.

def scaleFromRedshift(redshift):
    '''
    Converts a redshift to a scale factor.
    '''
    return 1. /(redshift + 1.)

def convertSphericalToCartesian(r, theta, phi):
    '''
    Converts Spherical coordiantes to Cartesian.
    Returns a dictionary.
    http://mathworld.wolfram.com/SphericalCoordinates.html
    '''
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    return {'x' : x,
            'y' : y,
            'z' : z}

def RAandDECfromStandardCoordinates(data):
    '''
    Converts Standard Coordinates on tangent plane
    to RA and DEC on the sky.
    data dictionary must also contain the CD matrix.
    Full equations:
    xi  = cdmatrix(0,0) * (x-crpix(0)) + cdmatrix(0,1)* (y - crpix(1))
    eta = cdmatrix(1,0) * (x-crpix(0)) + cdmatrix(1,1)* (y - crpix(1))
    then
    ra = atan2(xi, cos(dec0)-eta*sin(dec0)) + ra0
    dec = atan2(eta*cos(dec0)+sin(dec0),
                sqrt((cos(dec0)-eta*sin(dec0))**2 + xi**2))

    :param data (dictionary): should contain standard coordinates X, Y,
    RA and DEC of the centre point, and the CD matrix.
    '''
    out = {}
    xi = (data['CD'][0,0] * data['X']) + (data['CD'][0,1]* data['Y'])
    eta = (data['CD'][1,0] * data['X']) + (data['CD'][1,1] * data['Y'])
    xi = np.deg2rad(xi)
    eta = np.deg2rad(eta)
    ra0 = np.deg2rad(data['RA'])
    dec0 = np.deg2rad(data['DEC'])

    ra = np.arctan2(xi, np.cos(dec0) - eta*np.sin(dec0)) + ra0
    dec = np.arctan2(eta*np.cos(dec0) + np.sin(dec0),
                    np.sqrt((np.cos(dec0) - eta*np.sin(dec0))**2 + xi**2))

    ra = np.rad2deg(ra)
    ra = np.mod(ra, 360.0)
    out['RA'] = ra
    out['DEC'] = np.rad2deg(dec)
    return out

def angularDiameterDistance(z,
                            H0=70,
                            WM=0.28):
    '''
    The angular diameter distance DA is defined as the ratio of
    an object's physical transverse size to its angular size
    (in radians). It is used to convert angular separations in
    telescope images into proper separations at the source. It
    is famous for not increasing indefinitely as z to inf; it turns
    over at z about 1 and thereafter more distant objects actually
    appear larger in angular size.
    '''
    return cosmocalc(z, H0, WM)['DA']

def degTodms(ideg):
    if (ideg < 0):
       s = -1
    else:
       s = 1
    ideg = abs(ideg)
    deg = int(ideg)+0.
    m = 60.*(ideg-deg)
    minutes = int(m)+0.
    seconds = 60.*(m-minutes)
    if s < 0:
       dms = "-%02d:%02d:%06.3f" % (deg,minutes,seconds)
    else:
       dms = "%02d:%02d:%06.3f" % (deg,minutes,seconds)
    return dms

def degTohms(ideg):
    ihours = ideg/15.
    hours = int(ihours)+0.
    m = 60.*(ihours-hours)
    minutes = int(m)+0.
    seconds = 60.*(m-minutes)
    hms = "%02d:%02d:%06.3f" % (hours,minutes,seconds)
    return hms

def cot(x):
    return (1./np.tan(x))

def arccot(x):
    return (np.arctan(1./x))