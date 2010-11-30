import numpy as N
import pylab as P
import os

def striplist(list):
    return([x.strip() for x in list])

debug = True

dir = '/Users/Sammy/Research/field_ellipticals/mergertrees/'
dirfE = dir + 'IfEs/'
dirE =  dir + 'Es/'

cmd = 'ls %s*.MergerTree'

temp = os.popen3(cmd % dirfE)
temp1 = os.popen3(cmd % dirE)

fElist = striplist(temp[1].readlines())
Elist = striplist(temp1[1].readlines())

fEresult = []
Eresult = []

for file in fElist:
    data = N.loadtxt(file, delimiter = ',', comments='#', usecols=(3,10), 
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

for file in Elist:
    data = N.loadtxt(file, delimiter = ',', comments='#', usecols=(3,10), 
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

#Writes the data
r1 = open('IfEFormation.time' ,'w')
r2 = open('EFormation.time', 'w')
for redshift in fEresult: r1.write(redshift + '\n')
for redshift in Eresult: r2.write(Eresult + '\n')
r1.close()
r2.close()
