#!/usr/bin/python
# angsep.py
# Program to calculate the angular separation between two points
# whose coordinates are given in RA and Dec

print"\n angsep Written by Enno Middelberg 2001\n"

import math
import string
import sys

inp=sys.argv[0:]
del inp[0]
if len(inp)==0:
    print" Program to convert an the angular separation between"
    print" two points in the sky"
    print" Type 'angsep.py RA1 Dec1 RA2 Dec2' to calculate the"
    print" angular separation. All coordinates must be of the"
    print" form hh:mm:ss(.ssssssss) or hh mm ss(.ssssssss)"
    print" (Don't mix!).\n"
    sys.exit()

if len(inp)==4:
    ra1 =string.split(inp[0], ":")
    dec1=string.split(inp[1], ":")
    ra2 =string.split(inp[2], ":")
    dec2=string.split(inp[3], ":")
elif len(inp)==12:
    ra1 =inp[0:3]
    dec1=inp[3:6]
    ra2 =inp[6:9]
    dec2=inp[9:12]
else:
    print" Too few or too many parameters."
    sys.exit()

print ra1, dec1, ra2, dec2

# Calculate angular separation of declinations
# Convert them into degrees and calulate the difference

# conversion of right ascension 1:
ra1hh=(float(ra1[0]))*15
ra1mm=(float(ra1[1])/60)*15
ra1ss=(float(ra1[2])/3600)*15

ra1deg=ra1hh+ra1mm+ra1ss
ra1rad=ra1deg*math.pi/180

# conversion of declination 1:
dec1hh=abs(float(dec1[0]))
dec1mm=float(dec1[1])/60
dec1ss=float(dec1[2])/3600

if float(dec1[0]) < 0:
	dec1deg=-1*(dec1hh+dec1mm+dec1ss)
else:
	dec1deg=dec1hh+dec1mm+dec1ss

dec1rad=dec1deg*math.pi/180

# conversion of right ascension 2:
ra2hh=float(ra2[0])*15
ra2mm=(float(ra2[1])/60)*15
ra2ss=(float(ra2[2])/3600)*15

ra2deg=ra2hh+ra2mm+ra2ss
ra2rad=ra2deg*math.pi/180

# conversion of declination 2:
dec2hh=abs(float(dec2[0]))
dec2mm=float(dec2[1])/60
dec2ss=float(dec2[2])/3600

if float(dec2[0]) < 0:
	dec2deg=-1*(dec2hh+dec2mm+dec2ss)
else:
	dec2deg=dec2hh+dec2mm+dec2ss

dec2rad=dec2deg*math.pi/180

# calculate scalar product for determination
# of angular separation

x=math.cos(ra1rad)*math.cos(dec1rad)*math.cos(ra2rad)*math.cos(dec2rad)
y=math.sin(ra1rad)*math.cos(dec1rad)*math.sin(ra2rad)*math.cos(dec2rad)
z=math.sin(dec1rad)*math.sin(dec2rad)

rad=math.acos(x+y+z)

# Delta RA
deg  = abs((ra2rad-ra1rad)*180/math.pi)
deg_corrected=math.cos(dec1rad)*deg
hh   =int(deg/15)
mm   =int((deg-15*hh)*4)
ss   =(4*deg-60*hh-mm)*60
print "\n Delta RA:  "+string.zfill(`hh`,2)+':'+string.zfill(`mm`,2)+':'+'%10.8f, hms format' % ss

hh   =int(deg)
mm   =int((deg-int(deg))*60)
ss   =((deg-int(deg))*60-mm)*60
print " Delta RA:  "+string.zfill(`hh`,2)+':'+string.zfill(`mm`,2)+':'+'%10.8f, dms format' % ss

# Delta RA corrected for declination (dms format)
deg_corrected=math.cos(dec1rad)*deg
hh   =int(deg_corrected)
mm   =int((deg_corrected-int(deg_corrected))*60)
ss   =((deg_corrected-int(deg_corrected))*60-mm)*60
print " Delta RA:  "+string.zfill(`hh`,2)+':'+string.zfill(`mm`,2)+':'+'%10.8f, dms format, corrected with cos(declination 1)' % ss

# Delta DEC
deg = abs((dec1rad-dec2rad)*180/math.pi)
hh   =int(deg)
mm   =int((deg-int(deg))*60)
ss   =((deg-int(deg))*60-mm)*60
print " Delta DEC: "+string.zfill(`hh`,2)+':'+string.zfill(`mm`,2)+':'+'%10.8f (dms format)' % ss

# use Pythargoras approximation if rad < 1 arcsec
if rad<0.000004848:
    print "\n Angular separation < ~1 arcsec, using Pythagorean approximation."
    rad=math.sqrt((math.cos(dec1rad)*(ra1rad-ra2rad))**2+(dec1rad-dec2rad)**2)
    
# Angular separation
deg=rad*180/math.pi
hh=int(deg)
mm=int((deg-int(deg))*60)
ss=((deg-int(deg))*60-mm)*60

print "\n Angular Separation: "+string.zfill(`hh`,2)+":"+string.zfill(`mm`,2)+":"+'%10.8f (dms format)' % ss
print "\n Accuracy currently not better than 3 microarcsec!\n"
