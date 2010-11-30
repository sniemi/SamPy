#!/usr/bin/python
# -*- coding: utf-8 -*-

def process_args():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="output",
                  help="Writes data to file named filename", metavar="filename")
    parser.add_option("-i", "--input", dest="input",
                  help="Reads data from input file called filename", metavar="filename")
    parser.add_option("-a", "--add", dest="add",
                      help="Adds given value to data")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Verbose mode on.")
    parser.add_option("-l", "--log", action="store_true", dest="logg",
                      help="Log_10 mode on.")
    parser.add_option("-d", "--divide", dest="divide",
                      help="Divides data with a given number.", metavar ="number")
    parser.add_option("-m", "--multiply", dest="multiply",
                      help="Multiplies data with a given number.", metavar = "number")
    parser.add_option("-s", "--separator", dest="delim",
                      help="Sets the data separator/delimiter to given char.", metavar = "separator")
    parser.add_option("-b", "--binary", action="store_true", dest="binary",
                      help="Reads binary data. NOT IMPLEMENTED YET!")
    parser.add_option("-c", "--column", dest="column",
                      help="Number of the column to be processed. Numbering begins from 0.", metavar = "number")
    parser.add_option("-e", "--extract", action="store_true", dest="extract",
                      help="Sets extraction mode on.")
    parser.add_option("--low", dest="low",
                      help="Sets the lower limit (x >=) for data extraction.", metavar ="number")
    parser.add_option("--high", dest="high",
                      help="Sets the upper limit (x <=) for data extraction.", metavar ="number")
    return parser.parse_args()

if __name__ == '__main__':
    import sys
    import os.path
    from numpy import *
    
    
    (opts, args) = process_args()
    if opts.verbose == True: 
        print "\nVerbose mode.\n"
        if opts.add is not None: print "%s will be added to your data.\n" % opts.add
        if opts.input is not None: print "Your data will be read from %s \n" % opts.input
        if opts.output is not None: print "Your data will be written to %s file.\n" % opts.output
        if opts.logg == True: print "Logarithm mode on.\n"
        if opts.divide is not None: print "Your data will be divided by %s\n" % opts.divide

    if (opts.input is None):
        print "\nYou did not give input file!\nWill exit now!\n"
        sys.exit()
        
    if (opts.column is None):
        print "You did not give the column!\nWill exit now!\n"
        sys.exit()
    
    if opts.delim is None: data = loadtxt(opts.input, skiprows=0)
    else: data = loadtxt(opts.input, delimiter="%s" % opts.delim, skiprows=0)
    
    if opts.verbose == True: print "The data you are about to modify is:\n", data[:,int(opts.column)]
    
    if opts.multiply is not None: data[:,int(opts.column)] *= float(opts.multiply)
    if opts.divide is not None: data[:,int(opts.column)] = data[:,int(opts.column)] / float(opts.divide)
    if opts.logg == True: data[:,int(opts.column)] = log(data[:,int(opts.column)]) 
    if opts.add is not None: data[:,int(opts.column)] += float(opts.add)
    if opts.extract == True:
        x, y = shape(data)
        temp1 = 0
        extracted = []
        for lines in range(x):
            if (data[lines,int(opts.column)] >= float(opts.low) and data[lines,int(opts.column)] <= float(opts.high)):
                extracted.append(data[lines,:])
                temp1 += 1
        
        if opts.verbose == True: print "\n%i lines fulfil your criteria!" % temp1
        
        savetxt(opts.output, extracted, fmt='%12.10g')
    else: savetxt(opts.output, data, fmt='%12.10g')


    if opts.verbose == True: print "\nYour modified data looks like this: \n", data[:,int(opts.column)]
    
    print "\nProgram completed!\n"