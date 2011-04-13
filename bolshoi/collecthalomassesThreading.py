'''
For some reason this script does not work.
I am not sure what's wrong in it, but the finding
part does not work, but randomly dies. It might
be something to do with threads getting confused
which file they are supposed to open or something...
'''
import glob as g
import threading as t
import Queue as Q

class findDMhaloes(t.Thread):
    '''
    Threaded way of finding dark matter haloes from
    Bolshoi isotree files.
    '''
    def __init__(self,
                 queue,
                 times):
        '''
        Initialize the class instance.
        :param queue
        :param times
        '''
        t.Thread.__init__(self)
        self.queue = queue
        #fixed column definitions for isotree files
        self.columns = {'mvir': 9,
                        'orig_mvir': 10,
                        'phantom': 8,
                        'scale': 0}
        #which times to capture
        self.times = times

    def find(self, file):
        '''
        Find all dark matter haloes from a given file
        that are in self.times. Capture the data
        that are specified in self.columns.
        Returns a dictionary where each key is a single
        time. Each line of data is a string so it's easy
        to write out to a file.
        '''
        output = {}
        try:
            print '{0:>s} is processing file {1:>s}\n'.format(self.getName(), file)
            fh = open(file, 'r')
            for line in iter(fh):
                if not line.startswith('#'):
                    tmp = line.split()
                    for key in self.times:
                        if round(float(tmp[self.columns['scale']]), 4) == round(key, 4):
                            a = float(tmp[self.columns['mvir']])
                            b = float(tmp[self.columns['orig_mvir']])
                            c = float(tmp[self.columns['phantom']])
                            #make a string from out data
                            string = '%f %f %f\n' % (a, b, c)
                            #save the string to dictionary
                            if output.has_key(key):
                                output[key] += [string,]
                            else:
                                output[key] = [string,]
            fh.close()
            writeOutput(output, file, self.times)
        except:
            print 'Problem in {0:>s} is processing file {1:>s}\n'.format(self.getName(), file)

    def run(self):
        '''
        Method threading will call.
        '''
        self.out = []
        while True:
            #grabs a file from queue
            filename = self.queue.get()
            #execute
            self.find(filename)
            #signals to queue job is done
            self.queue.task_done()

def findDMDriver(input_files,
                 times,
                 cores=6):
    '''
    Main driver function of the wrapper.
    '''
    queue = Q.Queue()
    #spawn a pool of threads, and pass them queue instance
    for i in range(cores):
        #initiate the class instance
        th = findDMhaloes(queue, times)
        th.setDaemon(True)
        th.start()
    #populate queue with data
    for file in input_files:
        queue.put(file)
    #wait on the queue until everything has been processed
    queue.join()

def writeOutput(data, file, times):
    '''
    Writes the output data to ascii files.
    Each time step is recorded to a single file.
    The filename will contain the output *redshift*
    '''
    print 'File {0:>s} contains {1:d} timesteps'.format(file, len(d.keys()))
    for key in data:
        filename = 'DMhaloz{0:>s}{1:>s}.txt'.format(str(times[key]), file)
        print 'Now outputting to {0:>s} '.format(filename)
        fh = open(filename, 'a')
        for line in d[key]:
            fh.write(line)
        fh.close()

def combineFiles(files, outputfile):
    '''
    Combines the content of all files that are listed
    in the files list to a single file named outputfile.
    Iterates over the input files line-by-line to save
    memory.
    '''
    fh = open(outputfile, 'w')
    for file in files:
        print 'Writing %s to %s' % (file, outputfile)
        for line in iter(open(file, 'r')):
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

    #call the main function
    findDMDriver(inputs,
                 times,
                 cores)

    for key in times:
        out = 'dmMFz%s.txt' % str(times[key])
        print 'Will write', out
        combineFiles(glob.glob('*%s*.txt' % str(times[key])),
                     out)

    print 'All done, check the output file(s)'