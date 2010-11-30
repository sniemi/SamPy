#!/usr/bin/env python
#
# simple python script for extracting mostly used types of archives
# this script extracts .tar, .tar.gz, .tar.bz2, .gz and .zip archives 
#

import sys    # required for fetching command line arguments 
import os    # required for calling commands for archive extracting

def unpack(s):                                    # this is definition of depack
    if (s.find('.tar.gz') != -1):                #    function. It takes string
        os.system("tar -xvvzf " + filename)        #   filename as argument.
    elif (s.find('.tar.bz2') != -1):            #    functon than calls 
        os.system("tar -xvvjf " + filename)        #   appropriate command according
    elif (s.find('.tar') != -1):                #     to file extension
        os.system("tar -xvvf " + filename)
    elif (s.find('.gz') != -1):
        os.system("gunzip" + filename)            
    elif (s.find('.zip') != -1):        
        os.system("unzip " + filename)
    else: print "Wrong archive or filename"        # other types not supported

try:                                            # this is main program
    filename = sys.argv[1]                        # first argument right after
    unpack(filename)                            #    'unpack' command goes in the
except IndexError:                                #    filename string
    print "Filename is invalid!"                #    than the depack function is called

# try-except block is used for handling IndexError exception if no argument is passed