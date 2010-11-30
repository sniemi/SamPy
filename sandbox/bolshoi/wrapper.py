'''
@summary: This little wrapper can be used to
run GF (R. Somerville's SAMs program) using
threading.

@author: Sami-Matias Niemi
@contact: niemi@stsci.edu
'''
import glob as g
import os
import shutil
import time
import threading as t
import Queue as Q

class Run_GF_Threaded(t.Thread):
    '''
    Threaded way of running GF.
    '''
    def __init__(self,
                 queue,
                 out_path = '/Users/niemi/Desktop/Research/run/',
                 param_template = '/Users/niemi/Desktop/Research/orig_param_file',
                 gf_binary = '/Users/niemi/Desktop/Research/gf_bolshoi/gf'):
        
        t.Thread.__init__(self)
        self.queue = queue
        
        self.out_path = out_path
        self.param_template = param_template
        self.gf_binary = gf_binary
    
    #Redefines subprocess.call -function
    def _call(self, command, echo = False, wait = False):
        '''
        Actual command line call method.
        '''
        import subprocess
        if echo:
            print command
        else:
            #return subprocess.call(arg.split())
            #Shell = True --> no arg.split()
            #return subprocess.call(command, shell=True)
            #call will do Popen().wait() so it will wait to be ready!
            if wait:
                return subprocess.Popen(command, shell=True).wait()
            else:
                return subprocess.Popen(command, shell=True)
    
    def _remove_ending(self, string, ending ='.dat'):
        '''
        Remove an ending from a filename. Filename must be
        without a path.
        '''
        stop = string.find(ending)
        return string[:stop]
    
    def _modify_gf_param_file(self, new_file, out_path_line, path):
        '''
        Modifies the GF parameter file to point to a right folder.
        Only modifies the date line and the path name of input and
        output line.
        '''
        #read in a template
        fh = open(self.param_template, 'r')
        data = fh.readlines()
        fh.close()
        
        pos = -999
    
        #write modified output
        out = open(path + '/' + new_file, 'w')
        for x, line in enumerate(data):
            if line.startswith('#25 july 2010'):
                today = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime())
                out.write('#' + today + '\n')
            elif line.startswith('#pathname of input and output'):
                pos = x + 1
            else:
                if x == pos:
                    out.write(out_path_line + '\n')
                else:
                    out.write(line)
        out.close()
    
    def _check_dir(self, filename, new_file):
        '''
        Checks wheather the output directory exists or not.
        Will create a new directory if required and skip
        if the directory is already present. Will also
        call the _modify_gf_param_file method.
        @param filename: full path + filename of the input file 
        @param new_file: name of the new parameter file
        @return: a list containing a boolean stating whether
                the directory was present or not and the path
                to the folder that was created.
        '''

        base = os.path.basename(filename)
        path = self.out_path + self._remove_ending(base)
    
        #create output directory
        if not os.path.isdir(path):
            #make new directory
            os.mkdir(path)
            print 'Path %s created' % path
            #make a link to gf
            os.link(self.gf_binary, path + '/gf')
    
            #make a new param file and modify the template
            out_path_line = '\"' + path + '/'  + '\"'
            self._modify_gf_param_file(new_file, out_path_line, path)
     
            return True, path
        else:
            return False, path
    
    def run(self):
        '''
        Method threading will call.
        '''
        while True:
            new_file = 'param_file'
            
            #grabs a file from queue
            filename = self.queue.get()

            x = self._check_dir(filename, new_file)
            path = x[1]
            if x[0]:
                #run gf
                print 'Started running gf in %s' % path
                start_time = time.time()
                command = path + '/gf ' + path + '/%s > /dev/null' % new_file
                print 'Running command %s' % command
                self._call(command, wait = True)
                print 'Finished %s:\ngf took about %.0f minutes to run' % (path, -(start_time - time.time())/60.)
            else:
                print 'Path %s exists, skipping' % path
        
            #signals to queue job is done
            self.queue.task_done()


def main(input_files, cores = 6):
    '''
    Main driver function of the wrapper.
    '''
    queue = Q.Queue()
    #spawn a pool of threads, and pass them queue instance 
    for i in range(cores):
        th = Run_GF_Threaded(queue)
        th.setDaemon(True)
        th.start()
    #populate queue with data   
    for file in input_files:
        queue.put(file)
    #wait on the queue until everything has been processed     
    queue.join()

if __name__ == '__main__':
    cores = 6
    inputs = g.glob('/Users/niemi/Desktop/Research/Bolshoi/bolshoi_isotrees/*.dat')
    #call the main function
    main(inputs, cores)
    print 'All done, check the output'
