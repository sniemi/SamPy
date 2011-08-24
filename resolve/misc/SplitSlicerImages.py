"""
Splits image slicer FITS files to separate file, one for each slice.
Adds some information to the FITS header.

:requires: pyFITS

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1

:todo: Make a command line argument reader; file id and y cuts (y1 & y2)

"""
import glob as g
import pyfits as pf
import SamPy.log.Logger as lg

__author__ = 'Sami-Matias Niemi'

class SplitSlicerImages():
    """
    This class can be used to split slicer images to separate files.
    """

    def __init__(self, logfile='splitting.log'):
        """
        Init
        """
        #set up logger
        self.logfile = logfile
        self.log = lg.setUpLogger(self.logfile)


    def _replicateHeader(self, hdu, input):
        """
        Update a header

        :note: this loses comments, should not be used

        :param: hdu, the header to be updated
        :param: input, input header which is being replicated to hdu
        """
        keyrejlist = ['SIMPLE', 'BITPIX', 'NAXIS', 'NAXIS1', 'NAXIS2', 'NAXIS3', 'EXTEND']
        keycopylist = [k for k in input.items() if k[0] not in keyrejlist]

        for k, com in keycopylist:
            hdu.update(k, input[k])#, comment=str(com))


    def findFiles(self, identifier='Ne'):
        """
        Finds all .fits files that have the identifier in them.
        Uses wild cards on both sides of the identifier.
        Requires that the file ends with .fits

        :param: identifier: to match files

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


    def splitFiles(self, filelist=None, ext=0, splity=[215, 456], id='slice'):
        """
        Splits all the FITS files in the filelist to three separate files
        one for each slicer.

        :param: fileslist, a list of files to be split
        :param: ext, extension of the fits file
        :param: splity, y pixel values for splitting
        :param: id, name identifier for each slice
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

            for i, y in enumerate(splity):
                if i == 0:
                    out = name + '.' + id + str(i + 1) + '.fits'
                    prihdr.update('SLICE', i + 1, comment='int 1,2,3 describing the slice')
                    prihdr.update('YCUT', '[0:%i)' %(y), comment='y coordinates of the cut')
                    pf.writeto(out, data[:y, :], prihdr, output_verify='ignore')
                    #make a note to the log
                    self.log.info('Writing file %s' % out)
                elif i == 1:
                    out = name + '.' + id + str(i + 1) + '.fits'
                    prihdr.update('SLICE', i + 1, comment='int 1,2,3 describing the slice')
                    prihdr.update('YCUT', '[%i:%i)'% (splity[0], y), comment='y coordinates of the cut')
                    pf.writeto(out, data[splity[0]:y, :], prihdr, output_verify='ignore')
                    #make a note to the log
                    self.log.info('Writing file %s' % out)

            #the last slice
            out = name + '.' + id + '3.fits'
            prihdr.update('SLICE', 3, comment='int 1,2,3 describing the slice')
            prihdr.update('YCUT', '[%i:%i]' % (y, len(data[:,0])), comment='y coordinates of the cut')
            pf.writeto(out, data[y:, :], prihdr, output_verify='ignore')
            #make a log note
            self.log.info('Writing file %s' % out)

            fh.close()

        self._outputFileLists()

        
    def _outputFileLists(self, idef=['slice1', 'slice2', 'slice3']):
        """
        Generates file lists for each slice.

        :note: this is poorly written...
        """
        for id in idef:
            out = id+'filelist'
            fh = open(out, 'w')
            for file in self.files:
                tmp = file[:-4] + id
                fh.write(tmp+'\n')
            fh.close()
            self.log.info('Writing %s' % out)


if __name__ == '__main__':
    split = SplitSlicerImages()
    split.findFiles(identifier='ftbz*.Ne')
    split.splitFiles()