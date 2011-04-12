'''
This one uses multiprocessing rather than threading
'''
import fileinput as f
import glob as g
import multiprocessing as m

def findDMhaloes(input):
    '''
    Find all dark matter haloes from a given file
    that are in self.times. Capture the data
    that are specified in self.columns.
    Returns a dictionary where each key is a single
    time. Each line of data is a string so it's easy
    to write out to a file.
    '''
    file = input[0]
    times = input[1]
    columns = input[2]
    output = {}
    print 'Now processing file {0:>s}\n'.format(file)
    for line in f.input(file):
        if not line.startswith('#'):
            tmp = line.split()
            for key in times:
                if round(float(tmp[columns['scale']]), 4) == round(key, 4):
                    a = float(tmp[columns['mvir']])
                    b = float(tmp[columns['orig_mvir']])
                    c = float(tmp[columns['phantom']])
                    #make a string from out data
                    string = '%f %f %f\n' % (a, b, c)
                    #save the string to dictionary
                    if output.has_key(key):
                        output[key] += [string, ]
                    else:
                        output[key] = [string, ]
    writeOutput(output, file, times)

def writeOutput(data, file, times):
    '''
    Writes the output data to ascii files.
    Each time step is recorded to a single file.
    The filename will contain the output *redshift*
    '''
    print 'Outputting data from %s' % file
    print 'File contains {0:d} timesteps'.format(len(d.keys()))
    for key in data:
        filename = 'DMhaloz{0:>s}{1:>s}.txt'.format(str(times[key]), file)
        print 'Now outputting to {0:>s} '.format(filename)
        fh = open(filename, 'a')
        for line in d[key]:
            fh.write(line)
        fh.close()

if __name__ == '__main__':
    #number of cores to use
    cores = 6
    
    #inpute merger tree files
    inputs = g.glob('/Users/niemi/Desktop/Research/Bolshoi/bolshoi_isotrees/*.dat')

    #this is for Bolshoi's tree outputs
    #scale : redshift
    times = {0.9434: 0.059995760017,
             0.9073: 0.102171277417,
             0.8324: 0.201345506968,
             0.7663: 0.304971943103,
             0.7124: 0.403705783268,
             0.6643: 0.505343971097,
             0.6223: 0.606941989394,
             0.5864: 0.705320600273,
             0.5564: 0.797268152408,
             0.5283: 0.892863903085,
             0.4984: 1.00642054575}

    columns = {'mvir': 9,
               'orig_mvir': 10,
               'phantom': 8,
               'scale': 0}


    print 'Starts writing the outputs'
    jobs = []
    for i in range(cores):
        p = multiprocessing.Process(target=findDMhaloes, args=[file])
        jobs.append(p)
        p.start()

    print 'Finished writing the outputs'

    print 'All done, check the output file(s)'
