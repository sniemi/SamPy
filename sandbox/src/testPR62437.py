#! /sw/bin/python
'''
@author: Sami-Matias Niemi
'''

import glob as G
import sys

filelist = G.glob('*.tra')

for file in filelist:
    try:
        filedata = open(file, 'r').readlines()
    except:
        print 'Cannot read file %s, skipping...' % file
    
    counter = 0
    
    for line in filedata:
        if 'FPOFFSET' in line:
            counter += 1
            print 'File %s contains line:' % file
            print line.strip()
    
    if counter > 1:
        print 'File %s had FPOFFSET mentioned %i times!' % (file, counter)