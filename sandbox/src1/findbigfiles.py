#!/sw/bin/python

import os
import sys

global sizelimit
sizelimit = sys.argv[1]

def checksize(arg, dirname, files): 
    for file in files: 
        filepath = os.path.join(dirname, file) 
        if os.path.isfile(filepath): 
            size = os.path.getsize(filepath) 
            if size > (float(sizelimit)*1000000.0): 
                size_in_Mb = size/1000000.0 
                arg.append((size_in_Mb, filepath)) 

print 'Will check files bigger than %s Mb' % sizelimit

bigfiles = [] 
#root = os.environ['HOME'] 
root = '/'
os.path.walk(root, checksize, bigfiles) 

for size, name in bigfiles: 
    print '%22s is %4f Mb' % (name, size)
