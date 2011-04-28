'''
Find Files
----------

The functions of this module can be used to find
files.

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu
'''
import glob

__author__ = 'Sami-Matias Niemi'

def findFitsFiles():
    '''
    Returns a list of FITS files in the current working directory.

    :return: a list of FITS files
    :rtype: list
    '''
    return glob.glob('*.fits')