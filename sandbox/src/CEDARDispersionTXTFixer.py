#! /usr/bin/env python
'''
A script to fix CEDAR's ASCII dispersion solution output.

ABOUT:
         This script can be used to modify .txt files that CEDAR produce when
         dispersion solution output has been saved. 

USAGE:   
         CEDARDispersionTXTFixer.py [-h] [-v] [-r] [-c] [-f] string [-o] srtring
         where:
         [-h] prints help
         [-v] verbose mode on
         [-r] creates an output file called dispersion.txt which is 
              in format that can be used as an input to update_*_disp.pro scripts.
         [-c] compares results to TV06 six data found from CDBS
         [-f] user defined string that is used to search text files to be processed.
              User can specify wild cards e.g. "*wcal.txt".
         [-o] name of the output file. This does not change the name of the output
              file that optional argument -c produces.

DEPENDS:
         Python 2.5 or 2.6 (not version 3.x compatible)
         Pyfits

EXITSTA:  
         0: No errors

AUTHOR :
         Sami-Matias Niemi, for STScI

HISTORY:
         May 15 2009: Initial Version

@author: Sami-Matias Niemi
'''

__author__ = 'Sami-Matias Niemi'
__version__ = '0.9'

#Processes command line arguments
def process_args(just_print_help = False):
    from optparse import OptionParser
    
    usage = 'usage: %prog [options]'
    desc = 'This script can be used to modify .txt files that CEDAR produce when dispersion solution output has been saved. '
    
    parser = OptionParser(usage = usage, version='%prog ' + __version__, description = desc)
    parser.add_option("-c", "--compare", action="store_true", dest="comparison",
                      help="Compare results to TV06 data.")        
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Verbose mode on.")
    parser.add_option("-f", "--find", dest="find", 
                      help='''User define string that is used to find text files to be processed.
                              User must specify any wild cards in this string e.g. "*wcal.txt".''', 
                      metavar="string")
    parser.add_option("-o", "--output", dest="output",
                      help="Name of the output file.", metavar="string")
    parser.add_option("-r", "--reference", action="store_true",dest="reference",
                      help="Creates an output file called dispersions.txt.")
    if just_print_help:
        parser.print_help()
    else:
        return parser.parse_args()

def checkZeroArguments(opts):
    for x in opts.__dict__:
        if opts.__dict__[x] is not None:
            return True
    return False

#Main program begins
if __name__    == '__main__':
    import glob
    import sys
    import pyfits as PF
    
    #command line arguments
    (opts, args) = process_args()
    
    if checkZeroArguments(opts) == False:
        process_args(True)
        sys.exit(-9)
    
    #verbose
    verbose = False
    if opts.verbose is True: verbose = True
    
    #CDBS TV06 files
    cdbspath = '/grp/hst/cdbs/lref/'
    fuvfile = 't2k1224el_disp.fits'
    nuvfile = 't2917094l_disp.fits'

    #search string
    if opts.find is not None: search = opts.find
    else: search = '*wcal.txt'
    
    if verbose: print '\nWill use string: %s to indetify ASCII files containing dispersion solutions' % search
    
    #finds all files containing search string
    txtfiles = glob.glob(search)
    
    #outputfile
    if opts.output is not None:
        out = open(opts.output, 'w')
        if opts.comparison is True: outcomp = open(opts.output + '.comparison', 'w')
        if opts.reference is not None: outref = open('dispersion.txt', 'w')
        if verbose: print '\n Output will be written to file %s'  % opts.output
        outfile = opts.output
    else:
        outfile = 'CEDARDispersionTXTFixer.output'
        out = open(outfile, 'w')
        if opts.comparison is True: outcomp = open('CEDARDispersionTXTFixer.output.comparison', 'w')
        if opts.reference is not None: outref = open('dispersion.txt', 'w')
        if verbose: print '\n You did not specify output filename. Will use default CEDARDispersionTXTFixer.output'

    
    
    #main loop
    for file in txtfiles:
        if verbose: print '\nTrying to open file: %s' % file
        try:
            fulldata = open(file, 'r').readlines()
        except:
            if verbose: print '\nERROR: Cannot read file %s' % file
            pass
        
        #splits the file
        sdata = [line.strip().split() for line in fulldata]
        filename = sdata[0][0]

        #gets all coefficients
        coeffs = []
        RMS = ''
        if verbose: print '\nSearching for coefficient values...'
        for line in sdata:
            try:
                if line[0].startswith('C'):
                    if verbose: print '\nFound:', line
                    coeffs.append([line[2], line[4]])
                if line[0].startswith('RMS'):
                    if verbose: print '\nRMS of fit was %s' % line[4]
                    RMS = line[4]
            except: pass
        
        if verbose: print '\nTrying to find equivalent (%s) FITS file for header information...' % filename
        
        #Tries to open equivalent FITS file
        try:
            hdr0 = PF.open(filename)[0].header
        except:
            if verbose: print '\nERROR: Could not open %s. Will not get header information.' % filename
            pass
        
        #Tries to get all required header keywords
        try:
            cenwav = hdr0['CENWAVE']
            stripe = hdr0['SEGMENT']
            grating = hdr0['OPT_ELEM']
            fppos = hdr0['FPPOS']
            aperture = hdr0['APERTURE']
        except:
            if verbose: print '\nERROR: Could not read all required header keywords of %s' % filename
            cenwave = 'NA'
            strip = 'XNA'
            grating = 'NA'
            fppos = 'NA'
            aperture = 'NA'
                    
        #comparison to CDBS
        #should be rewritten, as it now opens the file for nothing on every round...
        if opts.comparison is True:
            if verbose: print '\nWill try to compare calculated results to the dispersion solution of TV06 data.'
            try:
                if stripe.startswith('N'):
                    if verbose: print 'Trying to open %s' % cdbspath + nuvfile
                    CDBSdata = PF.open(cdbspath + nuvfile)[1].data
                    CDBScoeff = [line[5] for line in CDBSdata 
                                 if line[0].strip() == stripe and 
                                    line[1].strip() == grating and
                                    line[2].strip() == aperture and
                                    line[3] == cenwav]
                    
                if stripe.startswith('F'):
                    if verbose: print 'Trying to open %s' % cdbspath + fuvfile
                    CDBSdata = PF.open(cdbspath + fuvfile)[1].data
                    CDBScoeff = [line[5] for line in CDBSdata 
                                 if line[0].strip() == stripe and 
                                    line[1].strip() == grating and
                                    line[2].strip() == aperture and
                                    line[3] == cenwav]
            except:
                if verbose: print '\nERROR: Cannot open CDBS file...'
                CDBScoeff = 'NA'
            
            #lets calculate delta
            delta = []
            for new, old in zip(coeffs, CDBScoeff[0]): 
                delta.append(float(new[0]) - old)          
        
        #some quick results to screen    
        if verbose: print stripe, grating, aperture, cenwav, fppos, coeffs, CDBScoeff, delta
        
        #output
        cfs = ''
        CDBSfs = ''
        deltas = ''
        for x in coeffs:
            cfs += x[0] + ' ' + x[1] + ' '
        if opts.comparison is True:
            for x in CDBScoeff[0]: CDBSfs += str(x) + ' '
            for x in delta: deltas += str(x) + ' '
        else:
            CDBSfs = ' '
        
        #normal outputs
        if verbose: print '\nWill output data to %s' % outfile
        out.write(stripe + ' ' + grating + ' ' + aperture + ' ' + str(cenwav) +
                  ' ' + str(fppos) + ' ' + cfs + CDBSfs + deltas + '\n')
        
        #output in reference file format
        if opts.reference is True:
            if verbose: print '\nWill output data to dispersion.txt'
            outref.write(stripe + ' ' + grating + ' ' + aperture + ' ' + str(cenwav) +
                  ' ' + str(fppos) + ' ' + coeffs[0][0] + ' ' + coeffs[1][0] + ' ' + coeffs[2][0] +
                  ' ' + coeffs[3][0] + '\n')
        
        #comparison output
        if opts.comparison is True:
            if verbose: print '\nWill output data to %s' % outfile + '.comparison'
            outcomp.write(stripe + ' ' + grating + ' ' + aperture + ' ' + str(cenwav) +
                          ' ' + str(fppos) + ' ' + deltas + '\n')
    
    #closes open files
    out.close()
    if opts.comparison: outcomp.close()
    if opts.reference: outref.close()
    
    #exits
    if verbose: print '\n\nScripts finished...'
    sys.exit(0)
