"""
Combines FITS images using the imcombine IRAF task.

The script calls IRAF from the command line as follows::

  cl -0 < command_file.cl

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import glob as g
import os
from itertools import groupby


def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def writeCommand(data, outputfile, outfileid='lin'):
    """
    Writes an IRAF command file.

    :param data:
    :param outputfile: name of the output file
    :param outfileid: id either lin or log

    :return: None
    """
    fh = open(outputfile, 'w')
    fh.write('images\nimmatch\n')
    for files in data:
        #create a string contaning file names
        fls = ''
        for file in files:
            fls += file + ','
        fls = fls[:-1]
        #name can be taken from the last fiel
        tmp = file.split('.')
        output = tmp[1] + tmp[2]

        print fls

        str1 = 'imcombine input="%s" output=%smed%s ' % (fls, outfileid, output)
        str1 += 'combine=median reject=avsigclip scale=none lthresh=-1000\n'
        str2 = 'imcombine input="%s" output=%ssum%s ' % (fls, outfileid, output)
        str2 += 'combine=sum\n'
        fh.write(str1)
        fh.write(str2)

    fh.write('logout')
    fh.close()


def groupFiles(files):
    """
    Groups files that are of the same target.
    Uses the file names to figure out which
    are of the same target. The identification
    could also be done based on the FITS header.

    :param file: a list of files that will be grouped

    :return: a list of grouped file names
    :rtype: list
    """
    out = []
    files.sort()    
    split = [(a, a.split('.')[1]) for a in files]
    for key, group in groupby(split, lambda x: x[1]):
        tmp = []
        for t in group:
            tmp.append(t[0])
        out.append(tmp)
    return out


if __name__ == '__main__':
    slice1 = g.glob('str_lin*RS*slice1.fits')
    slice2 = g.glob('str_lin*RS*slice2.fits')
    slice3 = g.glob('str_lin*RS*slice3.fits')

    s1 = groupFiles(slice1)
    s2 = groupFiles(slice2)
    s3 = groupFiles(slice3)

    writeCommand(s1, 'combine_commandslin1.cl')
    writeCommand(s2, 'combine_commandslin2.cl')
    writeCommand(s3, 'combine_commandslin3.cl')

    #call IRAF
    os.system('cl -o < combine_commandslin1.cl')
    os.system('cl -o < combine_commandslin2.cl')
    os.system('cl -o < combine_commandslin3.cl')


    #log files
    slice1 = g.glob('str_log*RS*slice1.fits')
    slice2 = g.glob('str_log*RS*slice2.fits')
    slice3 = g.glob('str_log*RS*slice3.fits')

    s1 = groupFiles(slice1)
    s2 = groupFiles(slice2)
    s3 = groupFiles(slice3)

    writeCommand(slice1, 'combine_commandslog1.cl', outfileid='log')
    writeCommand(slice2, 'combine_commandslog2.cl', outfileid='log')
    writeCommand(slice3, 'combine_commandslog3.cl', outfileid='log')

    #call IRAF
    os.system('cl -o < combine_commandslog1.cl')
    os.system('cl -o < combine_commandslog2.cl')
    os.system('cl -o < combine_commandslog3.cl')
