"""
IO class for COS instrument handbook plotting.
Can be used to read FITS image and tabular data.

:date: Created on Mar 18, 2009

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu
"""

import pyfits as PF
import numpy as N

__author__ = 'Sami-Matias Niemi'
__version__ = '0.2'

class COSHBIO():
    """
    IO class for COS instrument handbook plotting.
    Can be used to read FITS image and tabular data as well as ASCII data.
    As the path of the files is given in the constructor, this is only useful
    if the data is in same folder... (should be changed?)
    """

    def __init__(self, path, output):
        """
        Init
        """
        self.path = path
        self.output = output

    def FITSImage(self, file, extension):
        """
        Reads FITS image data to an array.
        Returns data as a NumPy array.
        """
        filename = self.path + file
        try:
            hdulist = PF.open(filename)
            data = hdulist[extension].data
            hdulist.close()
        except:
            print 'An error in IO.py when calling readFITS function and reading ', filename
            data = [0, ]

        return N.array(data)


    def FITSTable(self, file, extension=1):
        """
        Reads FITS table to an array...
        Returns data as a numpy array
        """
        filename = self.path + file
        try:
            tmp = PF.open(filename)
            data = tmp[extension].data
            tmp.close()
        except:
            print 'Error while reading file %s' % filename
            data = [0, ]

        return data

    def ASCIITable(file, comment='#'):
        """
        A simple function for reading data from a file into a table.
        Comment lines and empty lines are skipped.
        """
        filename = self.path + file
        try:
            tmp = open(filename, 'r').readlines()
        except:
            print 'An error in IO.py when calling readASCIITable function and reading ', filename

        results = []
        for line in tmp:
            tmp = line.strip()
            tmp = tmp.split()
            try:
                if tmp[0][0] != comment:
                    results.append(tmp)
            except: pass

    def HeaderKeyword(self, file, extension, keyword):
        """
        A simple function to pull out a header keyword value.
        """
        filename = self.path + file
        try:
            tmp = PF.open(filename)
            hdu = tmp[extension].header
            tmp.close()
        except:
            print 'Error while reading file %s' % filename

        try:
            result = hdu[keyword]
        except:
            print 'Error while pulling out the keyword %s value... will return -100' % keyword
            result = -100
        return result

    def Header(self, file, extension):
        """
        """
        filename = self.path + file
        try:
            tmp = PF.open(filename)
            hdu = tmp[extension].header
            tmp.close()
        except:
            print 'Error while reading file %s' % filename

        return hdu


    def writeToASCIIFile(self, data, outputfile, header='', separator=' '):
        """
        Writes data to an ASCII file.
        """
        try:
            file = open(outputfile, 'w')
        except:
            print 'Problem while opening file %s' % outputfile

        try:
            file.write(header)
            for line in data:
                tmp = ''
                try:
                    for cell in line:
                        tmp += str(cell) + separator
                    tmp = tmp[:-1] + '\n'
                    file.write(tmp)
                except: pass
        except: pass
