#!/usr/bin/python
# -*- coding: utf-8 -*-

def process_args():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="output",
                  help="Writes data to file named filename", metavar="filename")
    parser.add_option("-i", "--input", dest="input",
                  help="Reads data from input file called filename", metavar="filename")
    parser.add_option("-a", "--add", action="store_true", dest="add",
                      help="Add mode on.")
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Verbose mode on.")
    parser.add_option("-d", "--divide", action="store_true", dest = "divide",
                      help="Divide mode on.")
    parser.add_option("-m", "--multiply", action="store_true", dest="multiply",
                      help="Multiply mode on.")
    parser.add_option("-s", "--separator", dest="delim",
                      help="Sets the data separator/delimiter to given char.", metavar = "separator")
    parser.add_option("-b", "--binary", action="store_true", dest="binary",
                      help="Reads binary data. NOT IMPLEMENTED YET!")
    parser.add_option("-c", "--column1", dest="column1",
                      help="The number of the column(1) to be processed. Numbering begins from 0.", metavar = "number")
    parser.add_option("-x", "--column2", dest="column2",
                      help="The number of the column(2) whose values are used to operate the column1. Numbering begins from 0.", metavar = "number")
    return parser.parse_args()

#def dividef(array1, array2):
#    result = []
#    for i in range(0,len(arra1)):
#        result.append(array1[i]/array2[i])
#    return result

if __name__ == '__main__':
    import sys
    import os.path
    import numpy
    
    (opts, args) = process_args()
    if opts.verbose == True: 
        print "\nVerbose mode.\n"
        if opts.input is not None: print "Your data will be read from %s \n" % opts.input
        if opts.output is not None: print "Your data will be written to %s file.\n" % opts.output

    if (opts.input is None):
        print "\nYou did not give input file!\nWill exit now!\n"
        sys.exit()
        
    if (opts.column1 is None):
        print "You did not give the column1!\nWill exit now!\n"
        sys.exit()
    
    if (opts.column2 is None):
        print "You did not give the column2!\nWill exit now!\n"
        sys.exit()
    
    if opts.delim is None: data = numpy.loadtxt(opts.input, skiprows=0)
    #data = numpy.loadtxt(opts.input, delimiter=" ", skiprows=0)
    else: data = numpy.loadtxt(opts.input, delimiter="%s" % opts.delim, skiprows=0)
    
    if opts.verbose == True: print "The data you are about to modify is:\n", data[:,int(opts.column1)]
    
    if opts.multiply is True: data[:,int(opts.column1)] *= data[:,int(opts.column2)]
    if opts.divide is True: data[:,int(opts.column1)] = data[:,int(opts.column1)] / data[:,int(opts.column2)]
    if opts.add is True: data[:,int(opts.column1)] += data[:,int(opts.column2)]
    
    numpy.savetxt(opts.output, data, fmt='%12.10g')

    if opts.verbose == True: print "The data you are using for modifying is: \n", data[:,int(opts.column2)]

    if opts.verbose == True: print "\nYour modified data looks like this: \n", data[:,int(opts.column1)]
    
    print "\nProgram completed!\n"