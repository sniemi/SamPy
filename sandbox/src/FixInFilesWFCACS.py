#! /usr/bin/env python
'''
DESCRIPTION:


USAGE:
e.g.


HISTORY:
Created on Aug 21, 2009

@author: Sami-Matias Niemi
'''


__author__ = 'Sami-Matias Niemi'
__version__ = '0.98'


def process_args(just_print_help = False):
    from optparse import OptionParser
    
    usage = 'usage: %prog [options]'
    desc = 'This script can be used to fix Phase Retrieval in files.'
    
    parser = OptionParser(usage = usage, version='%prog ' + __version__, description = desc)
         
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      help='Verbose mode on. Will print info to stout.')
    parser.add_option('-i', '--input', dest='input', 
                      help='Name of the input file(s). Wild card * is accepted e.g. "*.in"', 
                      metavar='string')
    parser.add_option('-c', '--chip', dest='chip',
                      help = 'Number of the chip, either 1 or 2.', metavar='integer')
    if just_print_help:
        parser.print_help()
    else:
        return parser.parse_args()

def checkZeroArguments(opts):
    for x in opts.__dict__:
        if opts.__dict__[x] is not None:
            return True
    return False
    
if __name__ == '__main__':    
    '''
    Main program. 
    '''
    import sys, glob, shutil
    
    #command line arguments
    opts, args = process_args()
    
    #process zero arguments
    if checkZeroArguments(opts) == False:
        process_args(True)
        sys.exit(-9)
    
    if opts.input is None: 
        print 'You did not give any input file(s), will exit...'
        sys.exit(-8)
    else:
        input = opts.input
    
    if opts.chip is None:
        print 'You did not specify which chip. Will exit...'
        sys.exit(-5)
    else:
        chip = opts.chip
        
    if opts.verbose is True: verbose = True
    else: verbose = False  

    inlist = glob.glob(input)
    
    wave = '            Wavelength   0.5020\n' 
    came = '           Camera mode    ACSWFC%s\n' % chip
    focu = 'Y                   Focus (microns)       0.0010\n'
    xcom = 'Y                  X-coma (microns)       0.0000\n'
    ycom = 'Y                  Y-coma (microns)       0.0000\n'
    xast = 'Y           X-astigmatism (microns)       0.0000\n'
    yast = 'Y           Y-astigmatism (microns)       0.0000\n'
    sphe = 'N               Spherical (microns)    -0.013900\n'
    xclo = 'N                X-clover (microns)      -0.0040\n'
    yclo = 'N                Y-clover (microns)       0.0100\n'
    xspa = 'I X-spherical astigmatism (microns)       0.0000\n'
    yspa = 'I Y-spherical astigmatism (microns)       0.0000\n'
    xash = 'N               X-ashtray (microns)      -0.0050\n'
    yash = 'N               Y-Ashtray (microns)       0.0030\n'
    fift = 'N   Fifth order spherical (microns)       0.0050\n'
    star = 'Y            Star  1 Background*1e4       0.0000\n'
    sxti = 'Y          Star  1 X-tilt (microns)       0.0000\n'
    syti = 'Y          Star  1 Y-tilt (microns)       0.0000\n'
    spid = 'N             Spider rotation (deg)       0.0000\n'
    blur = 'Y                              Blur       0.3500\n'
    
    change = {'Wavelength' : wave,
              'Camera mode': came,
              'Focus (mic' : focu,
              'X-coma (mic': xcom,
              'Y-coma (mic': ycom,
              'X-astigmati': xast,
              'Y-astigmati': yast,
              'Spherical (': sphe,
              'X-clover (m': xclo,
              'Y-clover (m': yclo,
              'X-spherical': xspa,
              'Y-spherical': yspa,
              'X-ashtray (': xash,
              'Y-Ashtray (': yash,
              'Fifth order': fift,
              'Star  1 Bac': star,
              'Star  1 X-t': sxti,
              'Star  1 Y-t': syti,
              'Spider rota': spid,
              'Blur': blur}
    
    for file in inlist:
        lines = open(file).readlines()
        
        #copy to backup
        if verbose:
            print 'Now processing file %s' % (file)
            print 'Will copy %s to %s' % (file, file+'_backup')
        shutil.copy(file, file+'_backup')
        
        out = open(file, 'w')
        for line in lines:
            replaced = False
            for key in change:
                if key in line.strip():
                    if change[key].strip() != line.strip():
                        if verbose: print 'Changed "%s" to "%s"' % (line.strip(), change[key][:-1])
                        out.write(change[key])
                        replaced = True
            if replaced == False:
                out.write(line)
                    
            #if 'Wavelength' in line.strip():
            #    if verbose: print 'Changed "%s" to "%s"' % (line.strip(), wave.strip())
            #    out.write(wave)
            #elif 'Camera mode' in line.strip():
            #    if verbose: print 'Changed "%s" to "%s"' % (line.strip(), came.strip())
            #    out.write(came)
            #else:
            #    out.write(line)
        out.close()
    