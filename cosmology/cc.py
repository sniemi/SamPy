#!/usr/bin/env python
  
import sys
from math import *

try:
  if sys.argv[1] == '-h':
    print '''Cosmology calculator ala Ned Wright (www.astro.ucla.edu/~wright)
input values = redshift, Ho, Omega_m, Omega_vac
ouput values = age at z, distance in Mpc, kpc/arcsec, apparent to abs mag conversion

Options:   -h for this message 
           -v for verbose response '''
    sys.exit()
  if sys.argv[1] == '-v':
    verbose=1
    length=len(sys.argv)-1
  else:
    verbose=0
    length=len(sys.argv)

# if no values, assume Benchmark Model, input is z
  if length == 2:
    if float(sys.argv[1+verbose]) > 100:
      z=float(sys.argv[1+verbose])/299790.    # velocity to redshift
    else:
      z=float(sys.argv[1+verbose])            # redshift
    H0 = 75                         # Hubble constant
    WM = 0.3                        # Omega(matter)
    WV = 1.0 - WM - 0.4165/(H0*H0)  # Omega(vacuum) or lambda

# if one value, assume Benchmark Model with given Ho
  elif length == 3:
    z=float(sys.argv[1+verbose])    # redshift
    H0 = float(sys.argv[2+verbose]) # Hubble constant
    WM = 0.3                        # Omega(matter)
    WV = 1.0 - WM - 0.4165/(H0*H0)  # Omega(vacuum) or lambda

# if Univ is Open, use Ho, Wm and set Wv to 0.
  elif length == 4:
    z=float(sys.argv[1+verbose])    # redshift
    H0 = float(sys.argv[2+verbose]) # Hubble constant
    WM = float(sys.argv[3+verbose]) # Omega(matter)
    WV = 0.0                        # Omega(vacuum) or lambda

# if Univ is General, use Ho, Wm and given Wv
  elif length == 5:
    z=float(sys.argv[1+verbose])    # redshift
    H0 = float(sys.argv[2+verbose]) # Hubble constant
    WM = float(sys.argv[3+verbose]) # Omega(matter)
    WV = float(sys.argv[4+verbose]) # Omega(vacuum) or lambda

# or else fail
  else:
    print 'need some values or too many values'
    sys.exit()

# initialize constants

  WR = 0.        # Omega(radiation)
  WK = 0.        # Omega curvaturve = 1-Omega(total)
  c = 299792.458 # velocity of light in km/sec
  Tyr = 977.8    # coefficent for converting 1/H into Gyr
  DTT = 0.5      # time from z to now in units of 1/H0
  DTT_Gyr = 0.0  # value of DTT in Gyr
  age = 0.5      # age of Universe in units of 1/H0
  age_Gyr = 0.0  # value of age in Gyr
  zage = 0.1     # age of Universe at redshift z in units of 1/H0
  zage_Gyr = 0.0 # value of zage in Gyr
  DCMR = 0.0     # comoving radial distance in units of c/H0
  DCMR_Mpc = 0.0 
  DCMR_Gyr = 0.0
  DA = 0.0       # angular size distance
  DA_Mpc = 0.0
  DA_Gyr = 0.0
  kpc_DA = 0.0
  DL = 0.0       # luminosity distance
  DL_Mpc = 0.0
  DL_Gyr = 0.0   # DL in units of billions of light years
  V_Gpc = 0.0
  a = 1.0        # 1/(1+z), the scale factor of the Universe
  az = 0.5       # 1/(1+z(object))

  h = H0/100.
  WR = 4.165E-5/(h*h)   # includes 3 massless neutrino species, T0 = 2.72528
  WK = 1-WM-WR-WV
  az = 1.0/(1+1.0*z)
  age = 0.
  n=1000         # number of points in integrals
  for i in range(n):
    a = az*(i+0.5)/n
    adot = sqrt(WK+(WM/a)+(WR/(a*a))+(WV*a*a))
    age = age + 1./adot

  zage = az*age/n
  zage_Gyr = (Tyr/H0)*zage
  DTT = 0.0
  DCMR = 0.0

# do integral over a=1/(1+z) from az to 1 in n steps, midpoint rule
  for i in range(n):
    a = az+(1-az)*(i+0.5)/n
    adot = sqrt(WK+(WM/a)+(WR/(a*a))+(WV*a*a))
    DTT = DTT + 1./adot
    DCMR = DCMR + 1./(a*adot)

  DTT = (1.-az)*DTT/n
  DCMR = (1.-az)*DCMR/n
  age = DTT+zage
  age_Gyr = age*(Tyr/H0)
  DTT_Gyr = (Tyr/H0)*DTT
  DCMR_Gyr = (Tyr/H0)*DCMR
  DCMR_Mpc = (c/H0)*DCMR

# tangential comoving distance

  ratio = 1.00
  x = sqrt(abs(WK))*DCMR
  if x > 0.1:
    if WK > 0:
      ratio =  0.5*(exp(x)-exp(-x))/x 
    else:
      ratio = sin(x)/x
  else:
    y = x*x
    if WK < 0: y = -y
    ratio = 1. + y/6. + y*y/120.
  DCMT = ratio*DCMR
  DA = az*DCMT
  DA_Mpc = (c/H0)*DA
  kpc_DA = DA_Mpc/206.264806
  DA_Gyr = (Tyr/H0)*DA
  DL = DA/(az*az)
  DL_Mpc = (c/H0)*DL
  DL_Gyr = (Tyr/H0)*DL

# comoving volume computation

  ratio = 1.00
  x = sqrt(abs(WK))*DCMR
  if x > 0.1:
    if WK > 0:
      ratio = (0.125*(exp(2.*x)-exp(-2.*x))-x/2.)/(x*x*x/3.)
    else:
      ratio = (x/2. - sin(2.*x)/4.)/(x*x*x/3.)
  else:
    y = x*x
    if WK < 0: y = -y
    ratio = 1. + y/5. + (2./105.)*y*y
  VCM = ratio*DCMR*DCMR*DCMR/3.
  V_Gpc = 4.*pi*((0.001*c/H0)**3)*VCM

  if verbose == 1:
    print 'For H_o = ' + '%1.1f' % H0 + ', Omega_M = ' + '%1.2f' % WM + ', Omega_vac = ',
    print '%1.2f' % WV + ', z = ' + '%1.3f' % z
    print 'It is now ' + '%1.1f' % age_Gyr + ' Gyr since the Big Bang.'
    print 'The age at redshift z was ' + '%1.1f' % zage_Gyr + ' Gyr.'
    print 'The light travel time was ' + '%1.1f' % DTT_Gyr + ' Gyr.'
    print 'The comoving radial distance, which goes into Hubbles law, is',
    print '%1.1f' % DCMR_Mpc + ' Mpc or ' + '%1.1f' % DCMR_Gyr + ' Gly.'
    print 'The comoving volume within redshift z is ' + '%1.1f' % V_Gpc + ' Gpc^3.'
    print 'The angular size distance D_A is ' + '%1.1f' % DA_Mpc + ' Mpc or',
    print '%1.1f' % DA_Gyr + ' Gly.'
    print 'This gives a scale of ' + '%.2f' % kpc_DA + ' kpc/".'
    print 'The luminosity distance D_L is ' + '%1.1f' % DL_Mpc + ' Mpc or ' + '%1.1f' % DL_Gyr + ' Gly.'
    print 'The distance modulus, m-M, is '+'%1.2f' % (5*log10(DL_Mpc*1e6)-5)
  else:
    print '%1.2f' % zage_Gyr,
    print '%1.2f' % DCMR_Mpc,
    print '%1.2f' % kpc_DA,
    print '%1.2f' % (5*log10(DL_Mpc*1e6)-5)

except IndexError:
  print 'need some values or too many values'
except ValueError:
  print 'nonsense value or option'
