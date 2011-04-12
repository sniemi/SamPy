import glob as g
import fileinput as f
#From Sami's repo
import astronomy.conversions as conv

files = g.glob('/Users/niemi/Desktop/Research/Bolshoi/bolshoi_isotrees/*.dat')

columns = {'mvir' : 9,
           'orig_mvir' : 10,
           'phantom' : 8,
           'scale': 0
           }

scales = []

#we only need one...
files = [files[0],]

#loop over files and save all the scales
for file in files:
    print file
    for line in f.input(file):
        if not line.startswith('#'):
            tmp = line.split()
            scales.append(tmp[columns['scale']])

#find out individual scales
individuals = sorted(set(scales))

#loop over the sorted scales
for scale in individuals[::-1]:
    print scale, conv.redshiftFromScale(float(scale))
