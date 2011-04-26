'''
:about: This script is a quick way of combining fits files

:usage: reduce.py [-n] [-m] [-a] [-f] <file list or name> [-o] <output file>
        where:
                [-m] median combine
                [-a] average combine
                [-f] combines given files
                [-o] name of the output file
                [-n] uses NumPy and PyFits rather than Pyraf

:date: 26/11/2008 Initial Release
:author: Sami-Matias Niemi
:contact: niemi@stsci.edu
'''

__version__ = "0.1a"
__author__ = "Sami-Matias Niemi"

def process_args(just_print_help = False):
    """
    Processes the command line arguments o FITSCombine.py data reduction script.
    
    :param just_print_help: will print help
    :type just_print_help: boolean
    :return: parsed commmand line options
    """
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-m", "--median", action = "store_true", dest="med",
                      help="The combined image is a median from input images")
    parser.add_option("-a", "--average", action = "store_true", dest="avg",
                      help="The combined image is an average from input images")     
    parser.add_option("-f", "--files", dest="input",
                      help="File list of the files to be combined", metavar="file.list")
    parser.add_option("-o", "--output", dest="output",
                      help="Name of the output file.", metavar='output.fits')
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Verbose mode.")
    parser.add_option("-n", "--numpy", action ="store_true", dest="numpy",
                      help ="Uses Numpy and PyFits rathen than Pyraf for combining.")
    if just_print_help:
        parser.print_help()
    else:
        return parser.parse_args() 


def combinePyraf(input, output, median, scale):
    """
    Combines given images using IRAF's imcombine.
    """
    from pyraf import iraf
    from pyraf.iraf import imred

    reject = "sigclip"
    combine = ""
    if median: combine = "median"
    else: combine = "average"

    iraf.imcombine(input = input, output = output, combine = combine, reject = reject, scale = scale)

def combine(filelist, median = False, verbose = False):
    """
    Combines given images.
    
    :param filelist: list of files to be combined.
    :type filelist: list
    :param median: Performs median combining, if False uses average values
    :type median: boolean
    :param verbose: verbose mode.
    :type verbose: boolean
    :return: The combined image (2d-array with pixel values)
    """
    import pyfits
    import numpy
        
    if verbose:
        if median: 
            print "\n%i images will be median combined" % len(filelist)
        else:
            print "\n%i images will be average combined" % len(filelist)
    
    filedata = [pyfits.getdata(x) for x in filelist]
    
    if len(set(x.shape for x in filedata))  > 1:
       print "Given images have different dimensions!"
       print "Program will exit..."
       sys.exit(1)
    
    if median:
        IM = numpy.median(filedata, axis = 0)
    else:
        IM = numpy.mean(filelist, axis = 0)
    return IM

if __name__ == '__main__':
    """
    Main program.
    """
    import pyfits
    import sys
    
    #if scaling is done
    #works only for Pyraf for time being...
    scale = "exposure"

    (opts, args) = process_args()
    
    verbose = False
    if (opts.verbose is True): verbose = True 
    
    if (opts.input is None or opts.output is None):
        process_args(True)
        sys.exit(1)
    
    if opts.numpy:
        files = open(opts.input).readlines()
    
        if opts.med:
            median = True
            combined = combine(files, median, verbose)
        if opts.avg:
            median = False
            combined = combine(files, median, verbose)

        pyfits.writeto(opts.output, combined)
        print "Combined fits file has been written. See the image: %s" % opts.output
    else:
        files = "@" + opts.input
        median = False
        if opts.med:
            median = True
        if opts.avg:
            median = False
        
        combinePyraf(files, opts.output, median, scale)
        print "Combined fits file has been written using imcombine. See the image: %s" % opts.output

    sys.exit(0)
    
