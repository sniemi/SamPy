#! /usr/bin/env python

from __future__ import division         # confidence unknown
import glob
import os
import sys

import pyfits

def main (args):
    """This is a driver to write a text file from a FITS trailer file."""

    verbosity = 1                       # 0, 1 or 2

    if len (args) < 1:
        print "Specify one or more input FITS trailer file names."
        prtOptions()
        sys.exit()

    for arg in args:
        if arg == "-v":
            verbosity = 2
        elif arg == "-q":
            verbosity = 0
        else:
            files = glob.glob (arg)
            files.sort()
            for input in files:
                i = input.rfind ("_trl.fits")
                if i >= 0:
                    output = input[:i] + ".tra"
                    if os.access (output, os.R_OK):
                        if verbosity > 0:
                            print "Warning:  skipping %s;" \
                            " output file %s already exists" % (input, output)
                    else:
                        if verbosity > 0:
                            print "%s --> %s" % (input, output)
                        convertToAscii (input, output)
                else:
                    if verbosity > 1:
                        print "skipping %s" % input

def prtOptions():
    """Print a list of command-line options and arguments."""

    print "The command-line arguments and options are:"
    print "  -v (verbose)"
    print "  -q (quiet)"
    print "  one or more FITS trailer file names (_trl.fits)"

def convertToAscii (input, output):
    """Copy a FITS ASCII trailer table to an ASCII file.

    @param input: name of the input FITS trailer file
    @type input: string
    @param output: name of the output ASCII file
    @type output: string
    """

    ifd = pyfits.open (input, mode="readonly")
    data = ifd[1].data.field (0)        # first (and should be only) column
    ofd = open (output, "w")
    for row in data:
        row = row.rstrip()
        ofd.write (row + "\n")

    ofd.close()
    ifd.close()

if __name__ == "__main__":

    main (sys.argv[1:])
