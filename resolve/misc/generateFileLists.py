'''
Contains a class that can be used to generate file lists from SOAR data

:requires: pyFITS
:requires: NumPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
'''
import glob as g
import pyfits as pf
import numpy as np

__author__ = 'Sami-Matias Niemi'

class SOARFileLists():
    '''
    Generates different file lists
    '''

    def __init__(self, path=None, ext=0, idef='.fits'):
        '''
        Init
        '''
        if path is None:
            self.path = './'
        else:
            self.path = path
        self.ext = ext
        self.idef = idef
        self.allFiles = self._findAllFiles()

    def _findAllFiles(self):
        '''
        Returns a list of all files that are located in
        the path and have the idef identifier.

        :rtype: list
        '''
        return g.glob(self.path + '*' + self.idef)

    def findParams(self, params=['PARAM20', 'PARAM21', 'PARAM22']):
        '''
        Reads header keywords from each FITS file.
        '''
        out = {}
        array = []
        self.params = params
        for file in self.allFiles:
            try:
                hdr = pf.open(file, ignore_missing_end=True)[self.ext].header
            except:
                print 'Cannot read file %s, will skip...' % file
            tmp = []
            for param in params:
                try:
                    tmp.append(hdr[param])
                except:
                    print 'Cannot find %s from %s' % (param, file)
            out[file] = tmp
            array.append([file,] + tmp)
        self.fileInfo = out
        self.arrayInformation = np.asarray(array)
        return self.fileInfo, self.arrayInformation

    def printFileInfo(self, fileInfo=None):
        '''
        Prints file information to the screen
        '''
        if fileInfo is None:
            self.fileInfo, _ = self.findParams()

        for key in self.fileInfo:
            print key, self.fileInfo[key]

    def saveFileInfo(self, output='fileinfo.txt', fileInfo=None):
        '''
        Saves file information to a file
        '''
        if fileInfo is None:
            self.fileInfo, _ = self.findParams()

        fh = open(output, 'w')
        for key in self.fileInfo:
            tmp = key + '\t'
            for val in self.fileInfo[key]:
                tmp += '\t' + str(val)
            fh.write(tmp+'\n')
        fh.close()

    def separateByParams(self):
        '''

        :note: this only works when the three default params have been used
        '''
        vls = np.array(self.arrayInformation)
        binnings = set(vls[:,3])
        ycuts = set(vls[:,2])
        xcuts = set(vls[:,1])

        for bin in binnings:
            fh = open('filelistbin' + bin, 'w')
            tmp = vls[vls[:, 3] == bin]
            for line in tmp:
                tmp2 = line[0] + '\t' + line[1] + '\t' + line[2] + '\n'
                fh.write(tmp2)

if __name__ == '__main__':
    files = SOARFileLists()
    fi, fa = files.findParams()
    files.saveFileInfo()
    files.separateByParams()
    