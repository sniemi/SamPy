#!/usr/bin/env python

import sys, string

def cmldict(argv, cmlargs=None, validity=0):
    """
    The cmldict function takes a dictionary cmlargs with default
    values for the command-line options and returns a modified form of
    this dictionary after the options given in the list argv are
    parsed and inserted. One will typically supply sys.argv[1:] as the
    argv argument. In case cmlargs is None, the dictionary is built
    from scratch inside the function.  The flag validity is false (0)
    if any option in argv can be inserted in cmlargs, otherwise the
    function will issue an error message if an option is not already
    present in cmlargs with a default value (notice that cmlargs=None
    and validity=1 is an incompatible setting).

    Example:
    cmlargs = {'p' : 0, 'file' : None, 'q' : 0, 'v' : 0}
    argv = "-p 2 --file out -q 0".split()
    p = cmldict(argv, cmlargs)

    p equals {'p' : 2, 'file' : out, 'q' : 0}
    """

    if not cmlargs:
        cmlargs = {}

    arg_counter = 0
    while arg_counter < len(argv):
        option = argv[arg_counter]
        if option[0] == '-':  option = option[1:]  # remove 1st hyphen
        else: 
            # not an option, proceed with next sys.argv entry
            arg_counter += 1; continue  
        if option[0] == '-':  option = option[1:]  # remove 2nd hyphen
        
        if not validity or option in cmlargs: 
            # next argv entry is the value:
            arg_counter += 1
            value = argv[arg_counter] 
            cmlargs[option] = value
        elif validity:
            raise ValueError, "The option %s is not registered" % option
        arg_counter += 1
    return cmlargs

if __name__ == '__main__':
    args = "--m 9.1 --b 7 --c 0.1 -A 3.3".split()
    defaults = { 'm' : '1.8', 'func' : 'siny' }
    p = cmldict(args, defaults, 0)
    print p

    # shuffle values into other variables:
    m = p['m']
    b = p['b']
    # and so on (should have validity=1 to ensure that the
    # option keys are defined)
    
    # take action:
    for option in p.keys():
        if option == "m":
            print "option is m", p[option]
        elif option == "b":
            print "option is b", p[option]
        elif option == "c":
            print "option is c", p[option]
        elif option == "A":
            print "option is A", p[option]
        elif option == "func":
            print "option is func", p[option]

    args.append('--error'); args.append('yes')
    print "\nNow comes an exception (!)"
    p = cmldict(args, defaults, 1)
