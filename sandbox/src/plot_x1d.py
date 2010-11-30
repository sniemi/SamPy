#! /usr/bin/env python
'''
DESCRIPTION:


USAGE:
e.g.


HISTORY:
Created on Sep 10, 2009

@author: Sami-Matias Niemi
'''

import pyfits as PF
import sys
import pylab as P

__author__ = 'Sami-Matias Niemi'
__version__ = '0.1'

file = sys.argv[1]

fh = PF.open(file)
wave = fh[1].data.field('WAVELENGTH')
flux = fh[1].data.field('FLUX')
fh.close()

for value, wave in enumerate(wave):
    P.plot(wave, flux[value], label='Stripe ' + str(value))

P.xlabel('Wavelength (\AA)')
P.ylabel('Flux')
P.legend(shadow = True)
P.show()
