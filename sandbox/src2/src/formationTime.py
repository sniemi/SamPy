import numpy as N
import os

debug = False

dir = '/Users/Sammy/Research/field_ellipticals/mergertrees/'
dirfE = dir + 'IfEs/'
dirE =  dir + 'Es/'

fElist = os.listdir(dirfE)
Elist = os.listdir(dirE)

fEresult = []
Eresult = []

tmp = 0

for file in fElist:
    if file[-10:] == 'MergerTree':
        tmp += 1
        data = N.loadtxt(dirfE + file, delimiter = ',', comments='#', usecols=(3,10), 
                         skiprows=45, dtype=[('redshift', float), ('STmass', float)])
        data.sort(order = ('redshift', 'STmass'))
        masslimit = data[0][1]*0.5

        pos1 = 0

        for rs1, ms1 in reversed(data):
            stmass = ms1
            redshift = rs1
            pos1 += 1
            pos2 = 0
            for rs2, ms2 in reversed(data):
                pos2 += 1
                if pos1 != pos2 and rs1 == rs2:
                    stmass += ms2
            if stmass > masslimit:
                if debug:
                    print 'DEBUG: found redshift %f' % redshift
                    print 'DEBUG: halo: %s\nDEBUG: stmass: %f, required stmass: %f\n' % (file, stmass, masslimit)
                fEresult.append(redshift)
                break

print '%i files done from path %s' % (tmp, dirfE)

tmp = 0        
for file in Elist:
    if file[-10:] == 'MergerTree':
        tmp += 1
        data = N.loadtxt(dirE + file, delimiter = ',', comments='#', usecols=(3,10), 
                         skiprows=45, dtype=[('redshift', float), ('STmass', float)])
        data.sort(order = ('redshift', 'STmass'))
        masslimit = data[0][1]*0.5

        pos1 = 0

        for rs1, ms1 in reversed(data):
            stmass = ms1
            redshift = rs1
            pos1 += 1
            pos2 = 0
            for rs2, ms2 in reversed(data):
                pos2 += 1
                if pos1 != pos2 and rs1 == rs2:
                    stmass += ms2
            if stmass > masslimit:
                if debug:
                    print 'DEBUG: found redshift %f' % redshift
                    print 'DEBUG: halo: %s\nDEBUG: stmass: %f, required stmass: %f\n' % (file, stmass, masslimit)
                Eresult.append(redshift)
                break

print '%i files done from path %s' % (tmp, dirE)

#Writes the data
r1 = open('IfEFormation.time' ,'w')
r2 = open('EFormation.time', 'w')
r1.write('#Formation redshift\n')
r2.write('#Formation redshift\n')
for redshift in fEresult: r1.write(str(redshift) + '\n')
for redshift in Eresult: r2.write(str(redshift) + '\n')
r1.close()
r2.close()

print '\n\nAll done... Please check .time files for results!\n\n'
