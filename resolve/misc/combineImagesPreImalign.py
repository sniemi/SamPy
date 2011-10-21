"""
Combines FITS images using the imcombine IRAF task.
This script can be used prior to aligning images
because it (tries to) figure out which files were taken
back-to-back and be combined without aligning.

The script calls IRAF from the command line as follows::

  cl -0 < command_file.cl

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import glob as g
import os, re
from itertools import groupby


def writeCommand(data, outputfile, outfileid='lin'):
    """
    Writes an IRAF command file.

    :param data: input data
    :param outputfile: name of the output file
    :param outfileid: id either lin or log

    :return: None
    """
    outfiles = []
    i = 1

    fh = open(outputfile, 'w')
    fh.write('images\nimmatch\n')

    for files in data:
        #create a string containing file names
        fls = ''
        for file in files:
            fls += file + ','
        fls = fls[:-1]

        #name can be taken from the last file
        tmp = file.split('.')
        output = tmp[1] + tmp[2] + 'block{0:d}'.format(i)

        #to make sure that the same output name is not being used twice
        if output in outfiles:
            i += 1
            output = output[:-1] + str(i)
        else:
            i = 1
            output = tmp[1] + tmp[2] + 'block{0:d}'.format(i)
        outfiles.append(output)

        str1 = 'imcombine input="{0:>s}" output={1:>s}med{2:>s} '.format(fls, outfileid, output)
        str1 += 'combine=median reject=avsigclip scale=none lthresh=-1000\n'
        str2 = 'imcombine input="{0:>s}" output={1:>s}sum{2:>s} '.format(fls, outfileid, output)
        str2 += 'combine=sum\n'
        fh.write(str1)
        fh.write(str2)

    fh.write('logout')
    fh.close()


def increaseByOne(data):
    """
    Tests whether numbers in data increase by one. 

    :param data: sequence of numbers
    :type data: list or tuple

    :return: whether the list was continuous or not (boolean, index)
    :rtype: tuple
    """
    out = []
    data.sort()
    for i, value in enumerate(data):
        if i == 0:
            continue
        if data[i - 1] + 1 != value:
            out.append(i)
    if len(out) > 0:
        return False, out
    else:
        return True, -99


def groupContinuousFiles(files):
    """
    Groups files that are of the same target.
    Uses the file names to figure out which
    are of the same target. Uses the numbering
    in the files to figure out which files form
    a continuous block and can be combined without
    aligning the images before.

    :param files: a list of files that will be grouped

    :return: a list of grouped file names
    :rtype: list
    """
    blocks = []
    files.sort()
    split = [(a, a.split('.')[1]) for a in files]

    #groupby object name
    for key, group in groupby(split, lambda x: x[1]):
        tmp = []
        for t in group:
            tmp.append(t[0])
        blocks.append(tmp)

    out = []
    #loop over the grouped list
    for block in blocks:
        filenumb = []
        for file in block:
            filenumb.append(int(re.search('\d+(?<=.)\w+', file).group(0)))
        nosplit, split = increaseByOne(filenumb)
        if nosplit:
            out.append(block)
        else:
            #this block was not continuous, need to split
            start = 0
            for s in split:
                out.append(block[start:s])
                start = s
            out.append(block[start:])
    return out


if __name__ == '__main__':
    slice1 = g.glob('*lin*spec*slice1.fits')
    slice2 = g.glob('*lin*spec*slice2.fits')
    slice3 = g.glob('*lin*spec*slice3.fits')

    s1 = groupContinuousFiles(slice1)
    s2 = groupContinuousFiles(slice2)
    s3 = groupContinuousFiles(slice3)

    writeCommand(s1, 'combine_commandslin1.cl')
    writeCommand(s2, 'combine_commandslin2.cl')
    writeCommand(s3, 'combine_commandslin3.cl')

    #call IRAF
    os.system('cl -o < combine_commandslin1.cl')
    os.system('cl -o < combine_commandslin2.cl')
    os.system('cl -o < combine_commandslin3.cl')


    #log files
    slice1 = g.glob('*log*spec*slice1.fits')
    slice2 = g.glob('*log*spec*slice2.fits')
    slice3 = g.glob('*log*spec*slice3.fits')

    s1 = groupContinuousFiles(slice1)
    s2 = groupContinuousFiles(slice2)
    s3 = groupContinuousFiles(slice3)

    writeCommand(s1, 'combine_commandslog1.cl', outfileid='log')
    writeCommand(s2, 'combine_commandslog2.cl', outfileid='log')
    writeCommand(s3, 'combine_commandslog3.cl', outfileid='log')

    #call IRAF
    os.system('cl -o < combine_commandslog1.cl')
    os.system('cl -o < combine_commandslog2.cl')
    os.system('cl -o < combine_commandslog3.cl')
