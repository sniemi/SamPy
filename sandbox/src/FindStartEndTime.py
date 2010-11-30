#! /

import glob as G
import pyfits as PF
import sys

filelist = G.glob(sys.argv[1])

ends = []
starts = []
datetime = []

for file in filelist:
    hdr = PF.open(file)[1].header
    ends.append(hdr['EXPEND'])
    starts.append(hdr['EXPSTART'])
    datetime.append(hdr['DATE-OBS'] + ' ' + hdr['TIME-OBS'])
    
ends.sort()
starts.sort()

print 'UT times of start of observation'
for time in datetime:
    print time

print 'Start time of the orbit (in Modified Julian Date):', starts[0]
print 'End time of the orbit (in Modified Julian Date):', ends[-1]

