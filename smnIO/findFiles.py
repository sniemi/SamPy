import glob

__author__ = 'Sami-Matias Niemi'

def findFitsFiles():
    '''
    Returns a list of FITS files
    in the current working directory
    '''
    return glob.glob('*.fits')