#! /usr/bin/env python
#this program should open file, read it and calculated something...
#usage: file column bins
from numarray.examples.pstats import Stats

def process_args(just_print_help = False):
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-i", "--input", dest="input",
                      help="Name of the input file", metavar="string")
    parser.add_option("-o", "--output", dest="output",
                      help="Name of the output file", metavar="string")     
    parser.add_option("-b", "--bins", dest="bins",
                      help="The number of bins", metavar="int")
    parser.add_option("-c", "--column", dest="column",
                      help="The number of processed column, begins from 0", metavar="int")
    parser.add_option("-s", "--separator", dest="delim",
                      help="Sets the data separator/delimiter to given char.", metavar = "char")
    parser.add_option("-n", "--normed", dest="norm", action="store_true", 
                      help="If normed is true, the first element of the return tuple will be the counts normalized to form a probability density")
    parser.add_option("-a", "--cumulative", dest="cum", action="store_true", 
                      help="A histogram is computed where each bin gives the counts in that bin plus all bins for smaller values")
    parser.add_option("-l", "--log", dest="log", action="store_true", 
                      help="The histogram axis will be set to a log scale",)
    if just_print_help:
        parser.print_help()
    else:
        return parser.parse_args()

def basicStats(data):
    """Calculates basic statistics from a given array
    """
    if (len(data) > 1):
        import numpy as N
        median = N.median(data)
        mean = N.mean(data)
        std = N.std(data)
        max = N.max(data)
        min = N.min(data)
        var = N.var(data)
        return mean, median, std, var, max, min
    else:
        return (-99,)*6   

if __name__ == '__main__':
    import numpy as N
    import pylab as P
    import sys
    
    #Gets the command line arguments
    (opts, args) = process_args()

    if (opts.input is None or opts.column is None):
        process_args(True)
        sys.exit(1)

    if (opts.bins is None): opts.bins = 10

    if opts.delim is None: 
        data = N.loadtxt(opts.input, skiprows=0, comments="#")
    else: 
        data = N.loadtxt(opts.input, delimiter="%s" % opts.delim, skiprows=0, comments="#")

    vec = data[:,opts.column]

    stats = basicStats(vec)
    fmtt = "%16s"*6
    fmt = "%16f"*6 +"\n"
    print fmtt % ("median", "mean", "std", "max", "min", "var")
    print fmt % stats 

    hdata = P.hist(vec, bins=int(opts.bins), normed=opts.norm, cumulative=opts.cum, log=opts.log)
    P.show()

    P.savefig(opts.output)