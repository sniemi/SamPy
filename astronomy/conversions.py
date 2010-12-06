'''
Some functions for astronomy related unit conversions.

@requires: NumPy

@version: 0.1

@author: Sami Niemi
'''
import numpy as N

def janskyToMagnitude(jansky):
    '''
    Converts janskys to AB? magnitudes.
    @param jansky: can either be a number of a numpy array
    @return: either a float or numpy array
    '''
    return 8.9 - 2.5*N.log10(jansky)
