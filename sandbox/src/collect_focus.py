#! /usr/stsci/pyssgdev/Python-2.5.4/bin/python

'''
Collects focus measurement results and outputs them
to files, one for each instrument and chip.

Sami-Matias Niemi (niemi@stsci.edu)
'''
import numpy as N
import glob as G

def findZernikes(files, instrument = 'WFC3', file_instrument = 'i'):
    results = []
    position = 0
    stars = 0
    for file in files:
        print 'Processing file %s' % file
        txt = open(file).readlines()
        for line in txt:
            l = line.strip().split()
            if instrument in l[0]:
                position += 1
                coords = l[0][0:3]
            if l[0].startswith(file_instrument):
                stars += 1
                outp = [l[0], coords, l[3], l[2], l[6]]
                results.append(outp)

    print 'In total, found %i positions and %i stars' % (position, stars)
    return results

def modList(data):
    output = []
    files = set([x[0] for x in data])
    d = N.array(data)
    for file in sorted(files):
        mask = N.where(d[:,0] == file)
        focusd = N.array([float(x) for x in d[mask][:,4]])
        m = N.mean(focusd)
        s = N.std(focusd) / N.sqrt(len(focusd))
        tmp = N.append(d[mask][0][0:4], round(m,4))
        output.append(N.append(tmp, round(s,4)))
    return output

def writeOutput(data, outputfile, chip, header = '#file camera date mjd focus error\n'):
    fh = open(outputfile, 'w')
    fh.write(header)
    for line in data:
        st = ''
        for x in line:
            if 'WFC' in x:
                #will add the chip number
                st += 'UVIS' + chip + ' '
            elif 'ACS' in x:
                #will add the chip number
                st += 'WFC' + chip + ' '
            elif '/' in x:
                #this will swap the date to month/date/year
                tmp = x.split('/')
                st += tmp[1] + '/' + tmp[0] + '/' + tmp[2] + ' '
            else:
                st += x + ' '
        st += '\n'
        fh.write(st)
    fh.close()

def append_to_FocusModel(inputfile, outputfile):
    path = '/grp/hst/OTA/focus/source/FocusModel/'
    #data
    inputdata = open(inputfile).readlines()
    outdata = open(path+outputfile).readlines()
    #file handler
    fh = open(path+outputfile, 'a')
    #last lines in data
    lastout = outdata[-1]
    lastin = inputdata[-1]
    #last MJDs
    oMJD = float(lastout.split()[3])
    iMJD = float(lastin.split()[3])

    if oMJD < iMJD:
        #update is required.
        #find the line that is the same
        ind = inputdata.index(lastout)
        for x in range(ind+1, len(inputdata)):
            print 'Adding line %s to %s' % (inputdata[x].strip(), outputfile)
            fh.write(inputdata[x])
    fh.close()


filesC1 = sorted(G.glob('/grp/hst/OTA/focus/Data/prop11877/*/resultsChip1.txt'))
filesC2 = sorted(G.glob('/grp/hst/OTA/focus/Data/prop11877/*/resultsChip2.txt'))

C1WFC3 = findZernikes(filesC1)
C2WFC3 = findZernikes(filesC2)
C1ACS = findZernikes(filesC1, instrument = 'ACS', file_instrument = 'j')
C2ACS = findZernikes(filesC2, instrument = 'ACS', file_instrument = 'j')

C1A = sorted(C1ACS, key=lambda file: file[3])
C2A = sorted(C2ACS, key=lambda file: file[3])
C1W = sorted(C1WFC3, key=lambda file: file[3])
C2W = sorted(C2WFC3, key=lambda file: file[3])

meanC1A = modList(C1A)
meanC2A = modList(C2A)
meanC1W = modList(C1W)
meanC2W = modList(C2W)

writeOutput(meanC1A, 'FocusACSChip1.txt', '1')
writeOutput(meanC2A, 'FocusACSChip2.txt', '2')
writeOutput(meanC1W, 'FocusWFC3Chip1.txt', '1')
writeOutput(meanC2W, 'FocusWFC3Chip2.txt', '2')

append_to_FocusModel('FocusACSChip1.txt', 'WFC1FocusHistory.txt')
append_to_FocusModel('FocusACSChip2.txt', 'WFC2FocusHistory.txt')
append_to_FocusModel('FocusWFC3Chip1.txt', 'UVIS1FocusHistory.txt')
append_to_FocusModel('FocusWFC3Chip2.txt', 'UVIS2FocusHistory.txt')

print '\nAll done...'
