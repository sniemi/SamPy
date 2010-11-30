#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#
# ABOUT    : This script is a quick reduction tool for ALFOSC imaging data.
#            If you wish to use it for other instruments you should change
#            readout noise, gain, and trim section accordingly.
#
# NOTE     : * This script is not Python 3 (3k) compatible (at least prints should be changed as functions)
#            * Pyfits loses the headers of the images at the moment. Should be fixed at some point...
#            * Numpy part is shit, there's hardcoded areas that only work for ALFOSC. Should be fixed...
#            * Does not work with AB mode
#
# USAGE    : reduce.py [-p] [-x] [-v] [-b] [-f] [-s] <file list or name> [-o] <output file>
#            where:
#            [-p] uses Pyraf rather than NumPy and PyFits
#            [-b] creates a master bias or uses the given fits file
#            [-f] creates a master flat or uses the given fits file
#            [-s] reduces the give science fits file
#            [-o] name of the output file
#            [-x] fixes the input list(s) if IRAF does not find image data in MEFs
#            [-v] verbose mode
#
# DEPENDS  : Pyraf or NumPy and PyFits
#
# TESTED ON:
#            Python 2.5.2, Pyraf 1.4, Numpy 1.3.0.dev6137 and PyFits 1.1
#
# AUTHOR   : Sami-Matias Niemi
#
# HISTORY  : 21/06/2008 Initial Release
#            25/11/2008 Added axis = 0 to median calculations, numpy had changed since IR
#            26/11/2008 Added Pyraf possibility (this should be made default...)
# TO BE DONE:
#           - change the pyraf part to be default
#           - fix headers to numpy/pyfits part
#           - Find the filter data from the fits header (no need to give input lists for filters)
#           - Automaticly detect if filelists need fixing (could also use another redu pack in IRAF)
#           - automatically display reduced image(s) in ds9
#           - automatically display the combined image in ds9

__version__ = "0.21"
__author__ = "Sami-Matias Niemi"

def process_args(just_print_help = False):
    """
    Processes the command line arguments of reduce.py data reduction script.
    
    @param just_print_help: will print help
    @type: boolean
    @return: parsed commmand line options
    """
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-b", "--bias", dest="biaslist",
                      help="List of bias frames to be combined or a single file to be used for reduction.", 
                      metavar="names.list/file.fits")
    parser.add_option("-f", "--flat", dest="flatlist",
                      help="List of flat frames to be combined or a single file to be used for reduction.",
                      metavar="names.list/file.fits")     
    parser.add_option("-s", "--science", dest="science",
                      help="Name(s) of the science frame(s) to be reduced.", metavar="names.list/file.fits")
    parser.add_option("-o", "--output", dest="output",
                      help="Name of the output file.", metavar='output.fits')
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Verbose mode.")
    parser.add_option("-p", "--pyraf", action = "store_true", dest="pyraf", 
                      help ="Uses Pyraf rathen than Numpy and PyFits for the reduction")
    parser.add_option("-x", "--fixlist", action = "store_true", dest="fixlist",
                      help = "Fixes (adds [1] at the end of filename) the input list for IRAF.")
    if just_print_help:
        parser.print_help()
    else:
        return parser.parse_args() 

def makebiasPyraf(filelist, output, noise, gain):
    """
    Creates a master bias from given list of bias frames

    @param filelist: list of names of bias frames
    @type: list
    @param
    """
    from pyraf import iraf
    from pyraf.iraf import imred, ccdred

    iraf.zerocombine(input = filelist, output = output, combine = "median", rdnoise = noise, gain = gain)

def makebias(filelist, verbose = False):
    """
    Creates a master bias from given list of bias frames.
    
    @param filelist: list of names of bias frames
    @type: list
    @param verbose: verbose mode
    @type: boolean
    @return: master bias frame (2d-array with pixel values)
    """
    import pyfits
    import numpy
       
    if (verbose): print "\n%i images will be combined to make master BIAS..." % len(filelist)
       
    filedata = [pyfits.getdata(x) for x in filelist]
    
    if len(set(x.shape for x in filedata))  > 1:
       print "BIAS images are not of same size!"
       print "Program will exit..."
       sys.exit(1)
    
    #substracts overscan from all images
    i = 0
    for image in filedata:
       overscan = image[0:2047,0:50].mean()
       filedata[i] = 1.*image - overscan
       if (verbose): print "Subtracted overscan of %f from image %s" % (overscan, filelist[i])
       i += 1
    
    #calculates the median of all biases
    BIAS = numpy.median(filedata, axis=0)
    return BIAS

def makeflatPyraf(filelist, bias, output, noise, gain):
    """
    Creates a master flat from given list of flat frames.
    """
    from pyraf import iraf
    from pyraf.iraf import imred, ccdred

    combine = "median"
    reject = "avsigclip"
    iraf.flatcombine(input = filelist, output = output, combine = combine, reject = reject,
                     rdnoise = noise, gain = gain)


def makeflat(filelist, bias, verbose = False):
    """
    Creates a master flat from given list of flat frames. Also a master bias frame must be given.
    
    @param filelist: list of names of flat frames.
    @type: list
    @param bias: a bias frame.
    @type: array
    @param verbose: verbose mode.
    @type: boolean
    @return: master flat frame (2d-array with pixel values)
    """
    import pyfits
    import numpy
        
    if (verbose): print "\n%i images will be median combined for master FLAT." % len(filelist)
    
    filedata = [pyfits.getdata(x) for x in filelist]
    
    if len(set(x.shape for x in filedata))  > 1:
       print "Flat images are not of same size!"
       print "Program will exit..."
       sys.exit(1)
    
    #subtracts overscan and BIAS from all flats
    i = 0
    for image in filedata:
       overscan = image[0:2047,0:50].mean() #could be median
       image = 1.*image - overscan - bias
       if (verbose): print "Subtracted BIAS and overscan of %f" % overscan 
       norm = image[300:1800,300:1800].mean() #could be median
       filedata[i] = image / norm
       if (verbose): print "File %s normalised by dividing with a level of %f." % (filelist[i], norm)
       i += 1
    
    #calculates the median of all biases
    FLAT = numpy.median(filedata, axis = 0)
    return FLAT

def reducePyraf(filelist, outputlist, bias, flat, trim, trimsec):
    """
    Reduces the given science frame(s). Uses pyraf.
    """
    from pyraf import iraf
    from pyraf.iraf import imred, ccdred

    ccdtype = " "
    iraf.ccdproc(images = filelist, output = outputlist, ccdtype = ccdtype, trim = trim, zerocor = "yes", darkcor = "no", flatcor = "yes",
                 trimsec = trimsec, zero = bias, flat = flat)

def reduce(file, bias, flat, verbose = False):
    """
    Reduces the given science frame. Subtracts the overscan and BIAS frame
    and dives with a given flat.
    
    @param file: name of the file to be reduced
    @type: array
    @param bias: a bias frame
    @type: array
    @param flat: a flat frame
    @type: array
    @param verbose: verbose mode
    @type: boolean
    @return: reduced science image (2d-array with pixel values)
    """
    import pyfits
    import numpy as N
       
    filedata = pyfits.getdata(file)
    
    #subtracts overscan and BIAS and divides by a flat
    overscan = filedata[0:2047,0:50].mean()
    #filedata = (1.*filedata - overscan - bias) / flat
    filedata = (N.array(filedata) - overscan - N.array(bias)) / N.array(flat)
    if (verbose): print "Science frame %s divided by a flat-field image..." % file
    return filedata

def fixListFile(filename):
    """
    Helper function that can be used to fix input files. Sometimes IRAF requires that the fitsdata
    is pointed in the filename i.e. file.fits[1] if multiextension fits are used.

    @param filename: name of the file to be fixed
    @type: string
    @return: name of temp file that contains the original filenames + [1] (string)
    """
    import os
    outputf = "tmp.SMN"
    try:
        os.remove(outputf)
        #print "%s file delted..." % outputf
    except:
        pass
    data = open(filename).readlines()
    output = open(outputf, 'w')
    for line in data:
        output.write(line.strip() + "[1]\n")
    output.write("\n")
    output.close()
    return outputf

if __name__ == '__main__':
    """
    Main program.
    """
    import pyfits
    import sys
    
    #for ALFOSC
    noise = "3.2"
    gain = "0.726"
    trim = "yes"
    trimsec = "[60:2105, 1:2030]" #or something suitable [50:2110, 1:2030]

    (opts, args) = process_args()
    
    verbose = False
    if (opts.verbose is True): verbose = True 
    
    if (opts.biaslist is None and opts.flatlist is None and opts.science is None):
        process_args(True)
        sys.exit(1)
    
    if (opts.biaslist is None):
        print "I cannot do reduction or master bias without bias frame..."
        sys.exit(1)
    
    tmp = False
    if opts.pyraf:
        #uses pyraf
        if verbose: print "You chose to use Pyraf rather than PyFits and NumPy..."
        if opts.biaslist.endswith('.fits'):
            bias = opts.biaslist
            if verbose: print "Will use file: %s as a master bias..." % bias
        else:
            if opts.fixlist:
                biaslist = "@" + fixListFile(opts.biaslist)
            else:
                biaslist = "@" + opts.biaslist
            if verbose: print "Wil use zerocombine to make a master bias..."
            makebiasPyraf(biaslist, opts.output, noise, gain)
            bias = opts.output
            print "Master bias: %s created..." % (bias +".fits")
            tmp = True
    
        if opts.flatlist is not None:
            if opts.flatlist.endswith(".fits"):
                flat = opts.flatlist
                if verbose: print "Will use file: %s as a master flat..." % flat
            else:
                if opts.fixlist:
                    flatlist = "@" + fixListFile(opts.flatlist)
                else:
                    flatlist = "@" + opts.flatlist
                if verbose: print "Will use flatcombine to make a master flat..."
                if tmp:
                    print "WARNING: Only one output file allowed at this point. Therefore, your flat field will be names to SMNFLAT.fits"
                    makeflatPyraf(flatlist, bias, "SMNFLAT.fits", noise, gain)
                    print "Master flat created..."
                    flat = "SMNFLAT.fits"
                else:
                    makeflatPyraf(flatlist, bias, opts.output, noise, gain) 
                    print "Master flat: %s created..." % (opts.output +".fits")
                    flat = opts.output
                    tmp = True

        if opts.science is not None:
            if opts.science.endswith(".fits"):
                science = opts.science + "[1]"
            else:
                if opts.fixlist:
                    science = "@" + fixListFile(opts.science)
                else:
                    science = "@" + opts.science
            if verbose: print "Will use ccdproc to reduce the science frame(s)..."
            if tmp:
                print "WARNING: Only one output file allowed at this point. Therefore, your reduced science frame will be named to SMNReduced.fits"
                reducePyraf(science, "SMNReduced.fits", bias, flat, trim, trimsec)
                print "Data reduced..."
            else:
                output = "@" + opts.output
                reducePyraf(science, output, bias, flat, trim, trimsec)
                print "Data reduced..."

    if opts.pyraf is None:
        if (opts.biaslist[-5:].lower() == ".fits"):
            bias = pyfits.getdata(opts.biaslist)
            if (verbose): print "You chose to use existing master BIAS: %s" %opts.biaslist
        else:
            biaslist = open(opts.biaslist).readlines()
            bias = makebias(biaslist, verbose)
    
        if (opts.flatlist is None and opts.science is None):
            pyfits.writeto(opts.output, bias)
            if (verbose): print "Master BIAS has been made, the file %s has been created." % opts.output
    
        if (opts.flatlist is not None):
            if (opts.flatlist[-5:].lower() == ".fits"):
                flat = pyfits.getdata(opts.flatlist)
                if (verbose): print "You chose to use existing master FLAT: %s" %opts.flatlist
            else:
                flatlist = open(opts.flatlist).readlines()
                flat = makeflat(flatlist, verbose)
    
        if (opts.flatlist is not None and opts.science is None):
            pyfits.writeto(opts.output, flat)
            if (verbose): print "Master FLAT has been made, the file %s has been created." % opts.output

        if (opts.science is not None):
            if (opts.science[-5:].lower() == ".fits"):
                scienceframe = reduce(opts.science, bias, flat, verbose)    
                pyfits.writeto(opts.output, scienceframe)
                if (verbose): print "Reduced science image has been save: %s" % opts.output
            else:
                print "You gave multiple science frames..."
                print "Hope you know what you are doing... and moreover, that this works ;-)"
                sciencelist = open(opts.science).readlines()
                sciencedata = [(reduce(frame, bias, flat, verbose), frame) for frame in sciencelist]
                [pyfits.writeto(out+"_%s" % opts.output, image) for (image, out) in sciencedata]
    
    sys.exit(0)
    
