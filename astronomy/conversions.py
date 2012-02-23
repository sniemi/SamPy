"""
Functions to do Astronomy related unit conversions.

:requires: NumPy
:requires: cosmocalc (http://cxc.harvard.edu/contrib/cosmocalc/)

:version: 0.3

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu
"""
import math
import numpy as np
from cosmocalc import cosmocalc


C = 2.99792458e18 # speed of light in Angstrom/sec
H = 6.62620E-27   # Planck's constant in ergs * sec
HC = H * C
ABZERO = -48.60   # magnitude zero points
STZERO = -21.10


def FnutoFlambda(Fnu, wavelength):
    """

    :param Fnu: Fnu [ers/s/cm**2/Hz]
    :type Fnu: float or ndarray
    :param wavelength: wavelength [AA]
    :type wavelength: float or ndarray

    :return: Flambda [ergs/s/cm**2/AA]
    """
    return Fnu / wavelength / wavelength * C


def ergsperSecondtoLsun(ergss):
    """
    Converts ergs per second to solar luminosity in L_sun.

    :param ergss: ergs per second
    :type ergss: float or ndarray

    :return: luminosity in L_sun
    :rtype: float or ndarray
    """
    return ergss / 3.839e33


def wattsperHertztoErgsperArcsecond(data):
    """
    Converts Watts per Hertz to ergs per arcsecond.

    1 watt per hertz = 48.4813681 ergs per arcsecond.

    :param data: data to be converted
    :type data: float or ndarray

    :return: converted value
    :rtype: float or ndarray
    """
    return data * 48.4813681


def angstromToHertz(A):
    """
    Converts Angstroms to Hertz.

    :param A: wavelength in angstroms
    :type A: float or ndarray

    :return: Hertz
    :rtype: float or ndarray, depending on the input
    """
    return 2.99792458e18 / A


def nanomaggiesToJansky(nanomaggie):
    """
    Converts nanomaggies, used for example in SDSS imaging, to Janskys.

    :param nanomaggie: nanomaggie of the object
    :type nanomaggie: float or ndarray

    :return: Janskys
    :rtype: either a float or ndarray
    """
    return nanomaggie * 3.631e-6


def janskyToMagnitude(jansky):
    """
    Converts Janskys to AB magnitudes.

    :note: Can be used with SQLite3 database.

    :param jansky: janskys of the object
    :type jansky: float or ndarray

    :return: either a float or NumPy array
    """
    return 8.9 - 2.5 * np.log10(jansky)


def ABMagnitudeToJansky(ABmagnitude):
    """
    Converts AB magnitudes to Janskys.

    :note: Can be used with SQLite3 database.

    :param ABmagnitude: AB-magnitude of the object
    :type ABmagnitude: float or ndarray

    :return: either a float or NumPy array
    """
    return 10 ** ((23.9 - ABmagnitude) / 2.5) / 1e6


def arcminSquaredToSteradians(arcmin2):
    """
    Converts :math:`arcmin^{2}` to steradians.

    :param arcmin2: :math:`arcmin^{2}`
    :type arcmin2: float or ndarray

    :return: steradians
    """
    return arcmin2 / ((180 / np.pi) ** 2 * 60 * 60)


def arcminSquaredToSolidAnge(arcmin2):
    """
    Converts :math:`arcmin^{2}` to solid angle.

    Calls arcminSqauredToSteradians to convert :math:`arcmin^{2}`
    to steradians and then divides this with :math:`4\\Pi`.

    :param arcmin2: :math:`arcmin^{2}`
    :type arcmin2: float or ndarray

    :return: solid angle
    """
    return arcminSquaredToSteradians(arcmin2) / 4. / np.pi


def comovingVolume(arcmin2, zmin, zmax,
                   H0=70, WM=0.28):
    """
    Calculates the comoving volume between two redshifts when
    the sky survey has covered :math:`arcmin^{2}` region.

    :param arcmin2: area on the sky in :math:`arcmin^{2}`
    :param zmin: redshift of the front part of the volume
    :param zmax: redshift of the back part of the volume
    :param H0: Value of the Hubble constant
    :param WM: Value of the mass density

    :return: comoving volume between zmin and zmax of arcmin2
            solid angle in Mpc**3
    """
    front = cosmocalc(zmin, H0, WM)['VCM_Gpc3']
    back = cosmocalc(zmax, H0, WM)['VCM_Gpc3']
    volume = (back - front) * 1e9 * arcminSquaredToSolidAnge(arcmin2)
    return volume


def Luminosity(abs_mag):
    """
    Converts AB magnitudes to luminosities in :math:`L_{sun}`

    :param abs_mag: AB magnitude of the object
    :type abs_mag: float or ndarray

    :return: luminosity
    :rtype: float or ndarray
    """
    return 10.0 ** ((4.85 - abs_mag) / 2.5)


def get_flat_flambda_dmag(plambda, plambda_ref):
    """                                                                                                             
    Compute the differential AB-mag for an object flat in f_lambda.

    :param plambda: value of the plambda
    :param plambda_ref: reference value

    :return: magnitude difference
    """
    # compute mag_AB for an object at the desired wavelength                                                         
    mag1 = get_magAB_from_flambda(1.0e-17, plambda)

    # compute mag_AB for an object at the reference wavelength                                                       
    mag2 = get_magAB_from_flambda(1.0e-17, plambda_ref)

    # return the mag difference                                                                                      
    return mag1 - mag2


def get_magAB_from_flambda(flambda, wlength):
    """                                                                                                             
    Converts a mag_AB value at a wavelength to f_lambda.
                                                                                                                     
    :param flambda: mag_AB value
    :type flambda: float
    :param wlength: wavelength value [nm]
    :type wlength: float
                                                                                                                     
    :return: the mag_AB value
    :rtype: float
    """
    # transform from flambda to fnue                                                                                 
    fnu = (wlength * wlength) / 2.99792458e+16 * flambda

    # compute mag_AB                                                                                                 
    mag_AB = -2.5 * math.log10(fnu) - 48.6

    # return the mag_AB                                                                                              
    return mag_AB


def redshiftFromScale(scale):
    """
    Converts a scale factor to redshift.

    :param scale: scale factor
    :type scale: float or ndarray

    :return: redshift
    :rtype: float or ndarray
    """
    return 1. / scale - 1.


def scaleFromRedshift(redshift):
    """
    Converts a redshift to a scale factor.

    :param redshift: redshift of the object
    :type redshift: float or ndarray

    :return: scale factor
    :rtype: float or ndarray
    """
    return 1. / (redshift + 1.)


def convertSphericalToCartesian(r, theta, phi):
    """
    Converts Spherical coordinates to Cartesian ones.

    http://mathworld.wolfram.com/SphericalCoordinates.html

    :param r: radius
    :type r: float or ndarray
    :param theta: :math:`\\theta`
    :type theta: float or ndarray
    :param phi: :math:`\\phi`
    :type phi: float or ndarray

    :return: x, y, z
    :rtype: dictionary
    """
    x = r * np.sin(phi) * np.cos(theta)
    y = r * np.sin(phi) * np.sin(theta)
    z = r * np.cos(phi)
    return {'x': x,
            'y': y,
            'z': z}


def RAandDECfromStandardCoordinates(data):
    """
    Converts Standard Coordinates on tangent plane to RA and DEC on the sky.
    data dictionary must also contain the CD matrix.
    Full equations:

    .. math::

       \\xi  & = cdmatrix(0,0) * (x - crpix(0)) + cdmatrix(0,1) * (y - crpix(1)) \\\\
       \\eta & = cdmatrix(1,0) * (x - crpix(0)) + cdmatrix(1,1) * (y - crpix(1))

    then

    .. math::

       ra  &= atan2(\\xi, \\cos(dec0) - \\eta * \\sin(dec0)) + ra0 \\\\
       dec &= atan2(\\eta * \\cos(dec0) + \\sin(dec0),
                \\sqrt{((\\cos(dec0) - \\eta * \\sin(dec0))^{2} + \\xi^{2})})

    :param data: should contain standard coordinates X, Y, RA and DEC of the centre point, and the CD matrix.
    :type data: dictionary

    :return: RA and DEC
    :rtype: dictionary
    """
    out = {}
    xi = (data['CD'][0, 0] * data['X']) + (data['CD'][0, 1] * data['Y'])
    eta = (data['CD'][1, 0] * data['X']) + (data['CD'][1, 1] * data['Y'])
    xi = np.deg2rad(xi)
    eta = np.deg2rad(eta)
    ra0 = np.deg2rad(data['RA'])
    dec0 = np.deg2rad(data['DEC'])

    ra = np.arctan2(xi, np.cos(dec0) - eta * np.sin(dec0)) + ra0
    dec = np.arctan2(eta * np.cos(dec0) + np.sin(dec0),
                     np.sqrt((np.cos(dec0) - eta * np.sin(dec0)) ** 2 + xi ** 2))

    ra = np.rad2deg(ra)
    ra = np.mod(ra, 360.0)
    out['RA'] = ra
    out['DEC'] = np.rad2deg(dec)
    return out


def angularDiameterDistance(z,
                            H0=70,
                            WM=0.28):
    """
    The angular diameter distance DA is defined as the ratio of
    an object's physical transverse size to its angular size
    (in radians). It is used to convert angular separations in
    telescope images into proper separations at the source. It
    is famous for not increasing indefinitely as z to inf; it turns
    over at z about 1 and thereafter more distant objects actually
    appear larger in angular size.

    :param z: redshift
    :type z: float
    :param H0: value of the Hubble constant
    :type H0: float
    :param WM: :math:`\\Omega_{\\mathrm{matter}}`
    :type WM: float

    :return: angular diameter distance
    :rtype: float
    """
    return cosmocalc(z, H0, WM)['DA']


def degTodms(ideg):
    """
    Converts degrees to degrees:minutes:seconds

    :param ideg: objects coordinate in degrees
    :type ideg: float

    :return: degrees:minutes:seconds
    :rtype: string
    """
    if (ideg < 0):
        s = -1
    else:
        s = 1
    ideg = abs(ideg)
    deg = int(ideg) + 0.
    m = 60. * (ideg - deg)
    minutes = int(m) + 0.
    seconds = 60. * (m - minutes)
    if s < 0:
        dms = "-%02d:%02d:%06.3f" % (deg, minutes, seconds)
    else:
        dms = "%02d:%02d:%06.3f" % (deg, minutes, seconds)
    return dms


def degTohms(ideg):
    """
    Converts degrees to hours:minutes:seconds

    :param ideg: objects coordinates in degrees
    :type ideg: float

    :return: hours:minutes:seconds
    :rtype: string
    """
    ihours = ideg / 15.
    hours = int(ihours) + 0.
    m = 60. * (ihours - hours)
    minutes = int(m) + 0.
    seconds = 60. * (m - minutes)
    hms = "%02d:%02d:%06.3f" % (hours, minutes, seconds)
    return hms


def cot(x):
    """
    .. math::
    
       \\frac{1}{\\tan (x)}

    :param x: value
    :type x: float or ndarray

    :return: cotangent
    :rtype: float or ndarray
    """
    return 1. / np.tan(x)


def arccot(x):
    """
    .. math::
    
       arctan \\left ( \\frac{1}{x} \\right )

    :param x: value
    :type x: float or ndarray

    :return: arcuscotangent
    :rtype: float or ndarray
    """
    return np.arctan(1. / x)