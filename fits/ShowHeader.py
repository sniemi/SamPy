"""
Extremely simple script that prints out a FITS header to stdout.

Defaults to the 0th extension if not specified.

Accepts wildcard in the name, but then the filename must be given inside quote marks i.e. "*.fits"

:date: Mar 27, 2009
:author: Sami-Matias Niemi
:contact: sniemi@email.unc.edu
"""
import sys
import pyfits as PF

__author__ = 'Sami-Matias Niemi'
__version__ = '1.0'

def containsAny(str, set):
    """
    Checks if a given string contains any of the characters in a given set.

    :param str: input string
    :type str: string
    :param set: set if characters
    :type set: string

    :rtype: boolean
    """
    for c in set:
        if c in str: return True
    return False


def containsAll(str, set):
    """
    Checks if a given string contains all characters in a given set.

    :param str: input string
    :type: string
    :param set: set if characters
    :type: string

    :rtype: boolean
    """
    for c in set:
        if c not in str: return False
    return True


def showHeader(filename, extension):
    """
    Shows the FITS header of a given file.

    :note: Ignores missing END, for non-standard FITS files.

    :param filename: name of the file
    :type filename: string
    :param extension: number of the FITS extension
    :type extension: integer
    """
    try:
        if containsAny(filename, '*'):
            print 'A wildcard detected..\n'
            import glob

            files = glob.glob(filename)
            for file in files:
                hdulist = PF.open(file, ignore_missing_end=True)
                hd = hdulist[extension].header
                hdulist.close()
                print 'Header extension %i of %s' % (extension, file)
                print hd
                print
        else:
            hdulist = PF.open(filename, ignore_missing_end=True)
            hd = hdulist[extension].header
            hdulist.close()
            print
            print hd
    except:
        sys.exit('\nError while opening file %s and reading extensions %i' % (filename, extension))

if __name__ == "__main__":
    try:
        filename = sys.argv[1]
        extension = int(sys.argv[2])
    except:
        print '\nNo header extension given, will print the first extension header of file: %s\n' % filename
        extension = 0
    showHeader(filename, extension)