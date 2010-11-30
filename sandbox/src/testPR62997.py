#! /sw/bin/python
'''
Usage:
python testPR62997.py basename selection,
where:
basename = basename of the dataset to be tested
selection can be either e or t.
e = edits headers, will add LAMPPLAN to primary header
t = tests the LAMPUSED header keyword

@author: Sami-Matias Niemi
'''

import sys
import pyfits as PF
import pylab as P

basename = sys.argv[1]
selection = sys.argv[2]

if selection == 'e':
    try:
        oa = PF.open(basename + '_rawtag_a.fits')
        ob = PF.open(basename + '_rawtag_b.fits')
        oa[0].header.update('LAMPPLAN', 'DeutSMN')
        ob[0].header.update('LAMPPLAN', 'N/A')
        oa.writeto('mod_rawtag_a.fits')
        ob.writeto('mod_rawtag_b.fits')
        print 'Updating headers...'
    except:
        print 'WARNING: Could not find file %s' % basename + '_rawtag_*.fits'
    

if selection == 't':
    #make sure that tag-flash was used
    header0 = PF.open(basename + '_lampflash.fits')[0].header
    if header0['IMAGETYP'].strip() != 'TIME-TAG':
        print 'IMAGETYPE not TIME-TAG but ', header0['IMAGETYP'].strip()
    if header0['OBSMODE'].strip() != 'TIME-TAG':
        print 'OBSMODE not TIME-TAG but ', header0['OBSMODE'].strip()
    if header0['TAGFLASH'].strip() != 'AUTO':
        print 'TAGFLASH not AUTO but ', header0['TAGFLASH'].strip()
    
    #checks that the lamp actually flashed
    lampdata = PF.open(basename + '_lampflash.fits')[1].data
    try:
        P.plot(lampdata[0][6], lampdata[0][7])
        P.xlabel('Wavelength \AA')
        P.ylabel('counts / s')
        P.show()
    except:
        print 'Could not plot lamp data...\n'
        print lampdata
        
    #reads the trailer file
    try:
        tradata = open(basename + '.tra').readlines()
        #print all warnings
        for pos, line in enumerate(tradata):
            if line.strip().startswith('Warning'):
                print '\nWarning in trailer file:'
                print line.strip()
            if line.strip().startswith('lamp'):
                print '\nstring lamp found from the trailer file, will print following three lines...'
                for x in range(4):
                    print tradata[pos+x].strip()
    except:
        print 'WARNING: Could not read trailer file...'
            
    # checks the lamp keywords
    try:
        hdr1 = PF.open(basename + '_rawtag_a.fits')[0].header
        print 'file %s contains following keywords:' % basename + '_rawtag_a.fits' 
        print '\nLAMPUSED = ', hdr1['LAMPUSED']
        print 'LAMPSET = ', hdr1['LAMPSET']
        if 'NONE' in hdr1['LAMPUSED']:
            '\n\nPOSSIBLE PROBLEM in files %s!\n\n' % basename
    except:
        print 'WARNING: Could not read the 0th header of %s' % basename + '_rawtag_a.fits'