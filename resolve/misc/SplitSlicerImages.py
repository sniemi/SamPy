"""
Splits image slicer FITS files to separate file, one for each slice and adds some information to the FITS header.

Always check the log file after running this script to see that everything worked.

:requires: pyFITS
:requires: SamPY

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu
:version: 0.2
"""
import sys
from optparse import OptionParser
import glob as g
import pyfits as pf
import SamPy.log.Logger as lg


class SplitSlicerImages():
    """
    This class can be used to split slicer images to separate files.
    """

    def __init__(self, ycuts, logfile='splitting.log'):
        """
        Class constructor.

        :param ycuts: ycoordinate cut values
        :type ycuts: dictionary
        :param logfile: name of the log file
        :type logfile: string
        """
        self.ycuts = ycuts
        self.logfile = logfile
        self.log = lg.setUpLogger(self.logfile)


    def _replicateHeader(self, hdu, input):
        """
        Update a FITS header .

        :param hdu: the header to be updated
        :param input: input header which is being replicated to hdu

        :note: this loses comments, do not be used.
        """
        keyrejlist = ['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2', 'NAXIS3', 'EXTEND']
        keycopylist = [k for k in input.items() if k[0] not in keyrejlist]

        for k, com in keycopylist:
            hdu.update(k, input[k])#, comment=str(com))


    def findFiles(self, identifier='Ne'):
        """
        Finds all .fits files that have the identifier in them.
        Uses wild cards on both sides of the identifier. Requires that the file ends with .fits

        :param identifier: to match files
        :type identifier: string

        :return: a list of files matching the identifier
        :rtype: list
        """
        self.identifier = identifier

        self.files = g.glob('*{0:>s}*.fits'.format(self.identifier))

        numb = len(self.files)

        if numb == 0:
            self.log.info('Did not find any files, will exit')
            sys.exit('Did not find any files, will exit')
        else:
            self.log.info('Found {0:d} frames...'.format(numb))

        return self.files


    def splitFiles(self, filelist=None, ext=0, id='slice'):
        """
        Splits all the FITS files in the filelist to three separate files
        one for each slicer.

        :param fileslist: a list of files to be split
        :type filelist: list or None
        :param ext: extension of the fits file
        :type ext: int
        :param splity: y pixel values for splitting
        :param id: name identifier for each slice
        """
        if filelist == None:
            filelist = self.files

        for file in filelist:
            name = file.split('.fits')[0]
            fh = pf.open(file, ignore_missing_end=True)
            #primary header
            prihdr = fh[0].header

            #data
            data = fh[ext].data
            if data.shape[0] == 1:
                data = fh[ext].data[0]

            #first slice, the bottom one
            out = name + '.' + id + '1.fits'
            prihdr.update('SLICE', 1,
                          comment='int 1,2,3 describing the slice')
            prihdr.update('YCUT', '[%i:%i)' % (self.ycuts['ymin1'], self.ycuts['ymax1']),
                          comment='y coordinates of the cut')
            pf.writeto(out,
                       data[self.ycuts['ymin1']:self.ycuts['ymax1'], :],
                       prihdr,
                       output_verify='ignore')
            #make a note to the log
            self.log.info('Writing file %s' % out)

            #second slice, the middle one
            out = name + '.' + id + '2.fits'
            prihdr.update('SLICE', 2,
                          comment='int 1,2,3 describing the slice')
            prihdr.update('YCUT', '[%i:%i)' % (self.ycuts['ymin2'], self.ycuts['ymax2']),
                          comment='y coordinates of the cut')
            pf.writeto(out,
                       data[self.ycuts['ymin2']:self.ycuts['ymax2'], :],
                       prihdr,
                       output_verify='ignore')
            #make a note to the log
            self.log.info('Writing file %s' % out)

            #the last slice, the top one
            out = name + '.' + id + '3.fits'
            prihdr.update('SLICE', 3,
                          comment='int 1,2,3 describing the slice')
            prihdr.update('YCUT', '[%i:%i)' % (self.ycuts['ymin3'], self.ycuts['ymax3']),
                          comment='y coordinates of the cut')
            pf.writeto(out, data[self.ycuts['ymin3']:self.ycuts['ymax3'], :],
                       prihdr,
                       output_verify='ignore')
            #make a log note
            self.log.info('Writing file %s' % out)

            fh.close()

        self._outputFileLists()


    def _outputFileLists(self, idef=('slice1', 'slice2', 'slice3')):
        """
        Generates file lists for each slice.

        :param idef: slicer identifiers
        :type idef: list or tuple of string

        :note: this is poorly written, should be redone...
        """
        for id in idef:
            out = id + 'filelist'
            fh = open(out, 'w')
            for file in self.files:
                tmp = file[:-4] + id
                fh.write(tmp + '\n')
            fh.close()
            self.log.info('Writing %s' % out)


def processArgs(printHelp=False):
    """
    Processes command line arguments.
    """
    parser = OptionParser()

    parser.add_option('-b', '--binning',
                      dest='binning',
                      help='Binning of the data, either 2 for 2x2 or 3 for 3x3',
                      metavar='integer')
    if printHelp:
        parser.print_help()
    else:
        return parser.parse_args()


if __name__ == '__main__':
    opts, args = processArgs()

    if opts.binning is None:
        processArgs(True)
        sys.exit(1)

    if opts.binning == 3:
        #works for 3x3 binning
        ycuts = {'ymin1': 33,
                 'ymax1': 210,
                 'ymin2': 234,
                 'ymax2': 448,
                 'ymin3': 469,
                 'ymax3': 650}
    elif opts.binning == 2:
        #not tested!
        ycuts = {'ymin1': 33 * 2,
                 'ymax1': 210 * 2,
                 'ymin2': 234 * 2,
                 'ymax2': 448 * 2,
                 'ymin3': 469 * 2,
                 'ymax3': 650 * 2}
    else:
        processArgs(True)
        sys.exit(1)

    split = SplitSlicerImages(ycuts)
    #split.findFiles(identifier='normim')
    #split.splitFiles()
    split.findFiles(identifier='ftbz*.Ne')
    split.splitFiles()
    split.findFiles(identifier='ftdbz*spec')
    split.splitFiles()
