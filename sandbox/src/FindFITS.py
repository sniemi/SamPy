#! /usr/stsci/pyssg/Python-2.5.1/bin/python
'''
This script can be used to search FITS header keyword values.
Prints out the filename that fulfills the criterium.

@author: Sami-Matias Niemi for STScI
'''

__author__ = 'Sami-Matias Niemi'
__version__ = '1.0'

if __name__ == "__main__": 
    import sys
    
    try:
        import pyfits as PF
    except:
        sys.exit('\nNo PyFits installed.. will exit\n')
    
    try:
        filename = sys.argv[1]
        extension = int(sys.argv[2])
        value = sys.argv[3]
        value2 = sys.argv[4]
    except:
        print '\nUSAGE:'
        print 'FINDFits files extensions value AND value2'
        sys.exit()
        
    import glob
    files = glob.glob(filename)
    for file in files:
        try:
            hdulist = PF.open(file)
            hd = hdulist[extension].header
            hdulist.close()
            for line in hd.ascardlist():
                tmp = str(line)
                if tmp.find(value) >= 0:
                    for line2 in hd.ascardlist():
                        tmp2 = str(line2)
                        if tmp2.find(value2) >= 0:
                            print 'file %s' % file
                            break
        except: pass
