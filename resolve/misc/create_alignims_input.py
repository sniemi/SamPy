"""
Helper script to generate an input file for alignims_slicer IDL script.

Looks for FITS files, into the IRAF's database folder for
aperture traces and tries to set input flags based
on this information. Note, however, that user needs to
modify the generate file if offset observations were done
because the offset step sizes must be manually entered.
Also, if some was traced but later it was decided that
the trace is not good and the trace file was not removed
from the IRAF database, one should change the related
flags.

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu
:version: 0.2
"""
import sys
import glob as g


def findFITSfiles(scale='lin'):
    """
    Finds all FITS files that start with "s" and contain strings "spec" and "slice".

    This function may require modifying if the filenames are non-standard.
    
    :param scale: identifier for lin or log scaling
    :type scale: string

    :return: filelists based on different wild card identifiers
    :rtype: dictionary
    """
    slice1 = g.glob('s%s*spec*slice1*.fits' % scale)
    slice2 = g.glob('s%s*spec*slice2*.fits' % scale)
    slice3 = g.glob('s%s*spec*slice3*.fits' % scale)
    allspec = g.glob('s%s*spec*slice*.fits' % scale)

    if len(slice1) < 1 or len(slice2) < 1 or\
       len(slice3) < 1 or len(allspec) < 1:
        sys.exit('A problem when searching for FITS files, will exit...')

    out = {'slice1': slice1,
           'slice2': slice2,
           'slice3': slice3,
           'files': allspec,
           'aptrace': _findAptracefiles(scale=scale)}
    return out


def _findAptracefiles(datapath='./database/', scale='lin'):
    """
    Finds all aperture trace files that are located in the IRAF database.

    :param datapath: path to the IRAF's database, default is ./database/
    :type datapath: string
    :param scale: identifier for lin or log scaling
    :type scale: string

    :return: all aperture trace files in the IRAF database folder
    :rtype: list
    """
    return g.glob('%saps%s*spec*slice2*' % (datapath, scale))


def writeOutput(data, slicerlabel, outfile='alignimslin.input'):
    """
    Outputs information to an ascii file.
    This file should be inspected and modified
    before it should be fed to the alignims IDL script.

    The current output format is following:
    file1 file2 file3 fixedslope prefcenter skyoffset tracefile slicer_label

    :param data: input data holding filelists
    :type data: dictionary
    :param slicerlabel: slicer label, for example, A.0
    :type slicerlabel: string
    :param outfile: name of the outputfile
    :type outfile: string
    """
    fh = open(outfile, 'w')
    for file in data['slice2']:
        #add file names, keep order 1,2,3
        str = file.replace('slice2', 'slice1')
        str += ' ' + file
        str += ' ' + file.replace('slice2', 'slice3')

        #try finding aptrace file
        #if found set the flag to 1 otherwise to 0
        apflag = 0
        aptrace = 'NA'
        for f in data['aptrace']:
            trc = f.split('/')[-1]

            if 'off' in trc:
                #we do not want to use any offsetted ones
                continue

            if file[:-5] in trc:
                #found a match, assume we wish to use it
                #sheila's IDL code expects this to be
                #in certain format:
                aptrace = f.split('/ap')[1] + '.fits'

        #add the flag to the string, 1 for fixed slope
        if len(aptrace) < 2:
            apflag = 1
        str += ' %i' % apflag

        #preferred center, set to 120 by default
        str += ' 120.0'

        #this depend on data
        if 'off' in file:
            str += ' please_add_offset'
        else:
            str += ' 0.0'

        #add aptrace file
        str += ' ' + aptrace

        #slicer label
        str += ' ' + slicerlabel

        fh.write(str + '\n')
    fh.close()


if __name__ == '__main__':
    #this could be read from the command line
    slicerlabel = 'unknown'

    #first linear scaling
    fileinfo = findFITSfiles()
    writeOutput(fileinfo, slicerlabel)

    #then log scaling
    fileinfo = findFITSfiles(scale='log')
    writeOutput(fileinfo,
                slicerlabel,
                outfile='alignimslog.input')
