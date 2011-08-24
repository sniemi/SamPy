'''
This file contains functions that can be used to store data

:author: Sami-Matias Niemi
'''
__author__ = 'Sami- Matias Niemi'
__version__ = 0.1

import cPickle

def combineFiles(files, outputfile):
    '''
    Combines the content of all files that are listed
    in the files list to a single file named outputfile.
    Iterates over the input files line-by-line to save
    memory.
    '''
    i = 0
    fh = open(outputfile, 'w')
    for file in files:
        i += 1
        print 'Writing %s to %s' % (file, outputfile)
        for line in iter(open(file, 'r')):
            fh.write(line)
    print 'The content of {0:d} files were combined to a single file'.format(i)
    fh.close()


def cPickleDumpDictionary(dictionary, output):
    '''
    Dumps a dictionary of data to a cPickled file

    :param: dictionary, a Python data container does not have to be a dictionary
    :param: output, name of the output file

    :return: None
    '''
    out = open(output, 'wb')
    cPickle.dump(dictionary, out)
    out.close()
