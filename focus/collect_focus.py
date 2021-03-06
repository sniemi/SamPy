"""
Collects focus measurement results and outputs them to files, one for each instrument and chip.

This is so horribly written that it should be redone 
completely from scratch. There are Python tuples, lists
and NumPy arrays, and they are all badly mixed.

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu
:organization: Space Telescope Science Insitute
:version: 0.1

:todo: improve documentation
"""
import numpy as N
import glob as G

def findZernikes(files, instrument='WFC3', file_instrument='i'):
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
                outp = (l[0], coords, l[3], float(l[2]), float(l[6]))
                results.append(outp)
    print 'In total, found %i positions and %i stars' % (position, stars)
    return results


def modList(data,
            dtype={'names': ('file', 'cam', 'date', 'MJD', 'Focus'),
                   'formats': ('|S12', '|S8', '|S12', '<f8', '<f8')},
            filecol='file'):
    output = []
    files = set([x[0] for x in data])
    d = N.array(data, dtype=N.dtype(dtype))
    for file in files:
        mask = N.where(d[filecol] == file)
        focusd = N.array([float(x) for x in d[mask]['Focus']])
        m = N.mean(focusd)
        s = N.std(focusd) / N.sqrt(len(focusd))
        tmp = [d[mask]['file'][0],
               d[mask]['cam'][0],
               d[mask]['date'][0],
               d[mask]['MJD'][0]]
        tmp.append(round(m, 5))
        tmp.append(round(s, 5))
        output.append(tmp)
    return output


def writeOutput(data, outputfile, chip,
                header='#file camera date mjd focus error\n'):
    fh = open(outputfile, 'w')
    fh.write(header)
    for line in data:
        st = ''
        for x in line:
            if 'WFC' in str(x):
                #will add the chip number
                st += 'UVIS' + chip + ' '
            elif 'ACS' in str(x):
                #will add the chip number
                st += 'WFC' + chip + ' '
            elif '/' in str(x):
                #this will swap the date to month/date/year
                tmp = x.split('/')
                st += tmp[1] + '/' + tmp[0] + '/' + tmp[2] + ' '
            else:
                try:
                    if x > 55000:
                        st += '%14.6f' % x
                    else:
                        st += '%10.5f' % x
                except:
                    st += str(x) + ' '
        st += '\n'
        fh.write(st)
    fh.close()


def append_to_FocusModel(inputfile, outputfile, path):
    """
    This function appends new measurements to existing data
    files that are read by e.g. Colin's focustool.

    :param: inputfile: Name of the input data file that
                      potentially contains new data.
    :param: outputfile: Name of the output dat file to which
                       new data are appended to.
    :param: path: Path from where the outputfile can be found.

    :return: Boolean indicating if new data were identified.
    :rtype: boolean
    """
    #boolean to control whether new data have been found
    #if True, then the new data will be appended to the
    #outputfile
    newData = False
    #read in data
    inputdata = open(inputfile).readlines()
    outdata = open(path + outputfile).readlines()
    #last line in output data
    lastout = outdata[-1]
    #last MJD in output file
    oMJD = float(lastout.split()[3])
    for line in inputdata:
        if '#' not in line:
            if float(line.split()[3]) > oMJD:
                newData = True
                break
        #New data available, an update is required.
    if newData:
        #file handler
        fh = open(path + outputfile, 'a')
        #find the line that is the same
        try:
            ind = inputdata.index(lastout)
        except:
            #this except is required after year change
            ind = 0
        for x in range(ind + 1, len(inputdata)):
            print 'Adding line %s to %s' % (inputdata[x].strip(), outputfile)
            fh.write(inputdata[x])
        fh.close()
    return newData


def main():
    """
    Driver of collect_focus.py
    """
    #note that the input directory is hardcoded and should be changed every year!
    input_folder = '/grp/hst/OTA/focus/Data/prop12398/'
    output_folder = '/grp/hst/OTA/focus/source/FocusModel/'

    #find all results
    filesC1 = sorted(G.glob(input_folder + '*/resultsChip1.txt'))
    filesC2 = sorted(G.glob(input_folder + '*/resultsChip2.txt'))

    #find all Zernike polynomials
    C1WFC3 = findZernikes(filesC1)
    C2WFC3 = findZernikes(filesC2)
    C1ACS = findZernikes(filesC1, instrument='ACS', file_instrument='j')
    C2ACS = findZernikes(filesC2, instrument='ACS', file_instrument='j')

    #get the mean focuses
    meanC1A = sorted(modList(C1ACS), key=lambda file: file[3])
    meanC2A = sorted(modList(C2ACS), key=lambda file: file[3])
    meanC1W = sorted(modList(C1WFC3), key=lambda file: file[3])
    meanC2W = sorted(modList(C2WFC3), key=lambda file: file[3])

    #write the output
    writeOutput(meanC1A, 'FocusACSChip1.txt', '1')
    writeOutput(meanC2A, 'FocusACSChip2.txt', '2')
    writeOutput(meanC1W, 'FocusWFC3Chip1.txt', '1')
    writeOutput(meanC2W, 'FocusWFC3Chip2.txt', '2')

    #append to the files in the output_folder
    append_to_FocusModel('FocusACSChip1.txt', 'WFC1FocusHistory.txt',
                         output_folder)
    append_to_FocusModel('FocusACSChip2.txt', 'WFC2FocusHistory.txt',
                         output_folder)
    append_to_FocusModel('FocusWFC3Chip1.txt', 'UVIS1FocusHistory.txt',
                         output_folder)
    append_to_FocusModel('FocusWFC3Chip2.txt', 'UVIS2FocusHistory.txt',
                         output_folder)

if __name__ == '__main__':
    #call the main function
    main()
    #the end
    print '\nAll done...'