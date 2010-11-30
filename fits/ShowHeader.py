#! /sw/bin/python
'''
Extremely simple script that can be used printing FITS headers.

Accepts wildcard in the name, but then the filename must be given inside quote marks
i.e. "*.fits"

Created on Mar 27, 2009

@author: Sami-Matias Niemi for STScI
'''

__author__ = 'Sami-Matias Niemi'
__version__ = '1.0'

def containsAny(str, set):
    '''
    Checks if a given string contains any of the characters in a given set.
    '''
    for c in set:
        if c in str: return True
    return False

def containsAll(str, set):
    '''
    Checks if a given string contains all characters in a given set.
    '''
    for c in set:
        if c not in str: return False
    return True

if __name__ == "__main__":
    
    import sys
    
    try:
        import pyfits as PF
    except:
        sys.exit('\nNo PyFits installed.. will exit\n')
    
    filename = ''
    extension = 1
    
    try:
        filename = sys.argv[1]
        extension = int(sys.argv[2])
    except:
        print '\nNo header extension given, will print the first extension header of file: %s\n' % filename
        extension = 1
        
    try:
        if containsAny(filename, '*'):
            print 'A wildcard detected..\n'
            import glob
            files = glob.glob(filename)
            for file in files:
                hdulist = PF.open(file)
                hd = hdulist[extension].header
                hdulist.close()
                print 'Header extension %i of %s' % (extension, file)
                print hd
                print
        else:
            hdulist = PF.open(filename)
            hd = hdulist[extension].header
            hdulist.close()
            print
            print hd
    except:
        sys.exit('\nError while opening file %s and reading extensions %i' % (filename, extension))