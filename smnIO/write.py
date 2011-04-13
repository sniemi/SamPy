__author__ = 'Sami- Matias Niemi'
__version__ = 0.1

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