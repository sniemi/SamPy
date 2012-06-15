#!/usr/bin/env python
"""
This scripts divides one FITS file with another.

:usage::

    reduce.py [-n] [-m] [-a] [-f] <file list or name> [-o] <output file>
            where:
                    [-m] median combine
                    [-a] average combine
                    [-f] combines given files
                    [-o] name of the output file
                    [-n] uses NumPy and PyFits rather than Pyraf

:requires: PyFITS

:author: Sami-Matias Niemi
:contact: smn2@mssl.ucl.ac.uk

:version: 0.1
"""
from optparse import OptionParser
import pyfits as pf
import os, datetime


def divide(filename1, filename2, ext1, ext2):
    """
    Divide the data of the FITS file 1 with that of file 2.

    :param filename1: name of the first FITS file
    :type filename1: str
    :param filename2: name of the second FITS file
    :type filename2: str
    :param ext1: extension of the first FITS file
    :type ext1: int
    :param ext2: extension of the second FITS file
    :type ext2: int

    :return: data1 / data2
    :rtype: ndarray
    """
    data1 = pf.getdata(filename1, ext=ext1)
    data2 = pf.getdata(filename2, ext=ext2)
    return data1 / data2


def writeFITSfile(data, output):
    """
    Writes data to a FITS file.

    :param data: input data to be written
    :type data: ndarray
    :param output: name of the output file
    :type output: str

    :return None
    """
    if os.path.isfile(output):
        os.remove(output)

    #create a new FITS file, using HDUList instance
    ofd = pf.HDUList(pf.PrimaryHDU())

    #new image HDU
    hdu = pf.ImageHDU(data=data)

    #update and verify the header
    hdu.header.add_history('This file was created at %s' % datetime.datetime.isoformat(datetime.datetime.now()))
    hdu.verify('fix')

    ofd.append(hdu)

    #write the actual file
    ofd.writeto(output)


def processArgs(printHelp=False):
    """
    Processes command line arguments.
    """
    parser = OptionParser()

    parser.add_option('-n', '--nominator', dest='nominator',
                      help="Name of the input FITS file used as a nominator", metavar='string')
    parser.add_option('-d', '--denominator', dest='denominator',
                      help='Name of input FITS file used as a denominator', metavar='string')
    parser.add_option('-o', '--output', dest='output', help='Name of output file', metavar='string')
    parser.add_option('-e', '--extension', dest='extension',
                      help='extensions of the FITS files as nominator denominator pair like "01"', metavar='string')
    if printHelp:
        parser.print_help()
    else:
        return parser.parse_args()


if __name__ == '__main__':
    opts, args = processArgs()

    if opts.nominator is None or opts.denominator is None:
        processArgs(True)
        sys.exit(8)

    if opts.output is None:
        output = opts.nominator.replace('.fits', '') + 'div' + opts.denominator
    else:
        output = opts.output

    if opts.extension is not None:
        ext1 = int(opts.extension[0])
        ext2 = int(opts.extension[1])
    else:
        ext1 = 0
        ext2 = 0

    data = divide(opts.nominator, opts.denominator, ext1, ext2)
    writeFITSfile(data, output)

