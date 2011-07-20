'''
Basic reduction steps for SOAR image slicer data.

:requires: PyFITS
:requires: NumPy
:requires: SciPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1

:note: this script does not make use of a pseudo dark at the mo

'''
import glob as g
import sys, shutil
import pyfits as pf
import numpy as np
import scipy.signal as SS
import scipy.interpolate as I
import scipy.optimize as O
import SamPy.log.Logger as lg

import pylab as P

__author__ = 'Sami-Matias Niemi'

class SOARReduction():
    '''
    This class provides basic data reduction steps
    for SOAR image slicer data.
    '''

    def __init__(self, logfile='reduction.log'):
        '''
        Init
        '''
        #set up logger
        self.logfile = logfile
        self.log = lg.setUpLogger(self.logfile)

        #set up some booleans
        self.dataWeird = False


    def renameUnusedFiles(self, PARAM20=980, PARAM21=672, PARAM22=3):
        '''
        Renames all fits files from the directory which have been
        taken with different readout mode than the usual image
        slicer data.

        :note: one could also remove the files, but this is safer
        '''
        all = g.glob('*.fits')
        for file in all:
            #file handler
            fh = pf.open(file, ignore_missing_end=True)
            #primary header
            prihdr = fh[0].header

            if prihdr['PARAM20'] != PARAM20 or\
               prihdr['PARAM21'] != PARAM21 or\
               prihdr['PARAM22'] != PARAM22:
                #rename the file
                shutil.move(file, file + '_ignore')
                #update log
                self.log.info('Renamed {0:>s} with dimensions {1:.0f} {2:.0f} {3:.0f}'\
                .format(file, prihdr['PARAM20'], prihdr['PARAM21'], prihdr['PARAM22']))


    def findBiases(self, identifier='ZERO'):
        '''
        Finds all bias frames

        :param: identifier: to match bias files

        :return: a list of files matching the identifier
        :rtype: list
        '''
        self.biasIdentifier = identifier

        self.biasFiles = g.glob('*{0:>s}*'.format(self.biasIdentifier))
        numb = len(self.biasFiles)
        if numb == 0:
            self.log.info('Did not find any bias frames, will exit')
            sys.exit('Did not find any bias frames, will exit')
        else:
            self.log.info('Found {0:d} bias frames...'.format(numb))
        return self.biasFiles


    def findNonBiasFrames(self, exclude=None):
        '''
        Finds all FITS files that don't have the bias identifier in them
        '''
        if exclude is None:
            e = self.biasIdentifier
        else:
            e = exclude

        #find all files
        self.allFITS = g.glob('*.fits')

        #remove the ones with exclude them
        #if exclude = None then remove the ones with biasIdentifier in them
        self.frames = [a for a in self.allFITS if e not in a]

        numb = len(self.frames)
        if numb == 0:
            self.log.info('Did not find frames that are non-bias frames, will exit')
            sys.exit('Did not find frames that are non-bias frames, will exit')
        else:
            self.log.info('Found {0:d} non-bias frames...'.format(numb))

        return self.frames


    def findFlats(self, identifier='FLAT'):
        '''
        Finds all flat frames and writes a file listing the files.

        :param: identifier: to match flat field frames

        :return: a list of files matching the identifier
        :rtype: list
        '''
        self.flatIdentifier = identifier

        self.flatFiles = g.glob('*{0:>s}.fits'.format(self.flatIdentifier))
        numb = len(self.flatFiles)
        if numb == 0:
            self.log.info('Did not find any flat fields, will exit')
            sys.exit('Did not find any flat fields, will exit')
        else:
            self.log.info('Found {0:d} flat fields...'.format(numb))

        fh = open('flatlist', 'w')
        for file in self.flatFiles:
            fh.write(file + '\n')
        fh.close()
        self.log.info('Wrote a list of flat fields to flatflist')

        return self.flatFiles


    def subtractOverscan(self, filelist, ext=0):
        '''
        Subtracts the overscan region from each file
        in the filelist.

        :note: that modifies the filelist files

        :param: filelist: a list of files
        '''
        for file in filelist:
            #file handler
            fh = pf.open(file, mode='update', ignore_missing_end=True)
            #primary header
            prihdr = fh[0].header

            #data
            data = fh[ext].data
            if data.shape[0] == 1:
                data = fh[ext].data[0]
                self.dataWeird = True

            #TODO: make the overscan an argument
            poscan = np.hstack((data[:, 3:6], data[:, 1372:1381]))
            med = np.median(poscan)

            #update header
            prihdr.update('MEDZPT', med)

            #update data
            data -= med

            #save file
            fh.flush(output_verify='warn')

            #update log
            self.log.info('Subtracted overscan of {0:f} from {1:>s} and saved the file...'.format(med, file))

            #close handler
            fh.close(output_verify='ignore')


    def makeBias(self, combine='median', biaslist=[], output='zeroim.fits'):
        '''
        Combines the bias frames to a single bias frame.

        note: that this does not do sigma clipping at the moment

        :param: combine, either median or mean
        :param: biaslist, a list of bias frames to be combined
        :param: output: the name of the output file

        :return: combined bias frame
        :rtype: ndarray
        '''
        self.masterBias = output

        #if no biaslist is given then assuming that all files should be used
        if len(biaslist) == 0:
            biaslist = self.biasFiles

        if self.dataWeird:
            filedata = [pf.getdata(x, ignore_missing_end=True)[0] for x in biaslist]
        else:
            filedata = [pf.getdata(x, ignore_missing_end=True) for x in biaslist]

        if len(set(x.shape for x in filedata)) > 1:
            self.log.info('BIAS images are not of same size! Program will exit..')
            sys.exit('BIAS images are not of same size! Program will exit..')

        #calculates the median of all biases
        #self.bias = numpy.median(filedata, axis=0)
        cmd = 'np.' + combine + '(filedata, axis=0)'
        self.bias = eval(cmd)

        self.log.info('Bias frames combined with {0:>s}'.format(cmd))

        #write the output
        hdu = pf.PrimaryHDU(self.bias)
        hdulist = pf.HDUList([hdu])
        hdulist.writeto(self.masterBias)
        self.log.info('Master bias saved to {0:>s}'.format(self.masterBias))

        return self.bias


    def makeFlat(self, combine='median', flatlist=[], output='flatima.fits'):
        '''
        Combines the flat field frames to a single flat frame.

        :note: this does not do any sigma clipping at the moment
        '''
        self.combinedFlat = output

        if len(flatlist) == 0:
            flatlist = self.flatFiles

        if self.dataWeird:
            filedata = [pf.getdata(x, ignore_missing_end=True)[0] for x in flatlist]
        else:
            filedata = [pf.getdata(x, ignore_missing_end=True) for x in flatlist]

        if len(set(x.shape for x in filedata)) > 1:
            self.log.info('FLAT images are not of same size! Program will exit..')
            sys.exit('FLAT images are not of same size! Program will exit..')

        #combine the files
        cmd = 'np.' + combine + '(filedata, axis=0)'
        self.flat = eval(cmd)

        self.log.info('FLAT frames combined with {0:>s}'.format(cmd))

        #write the output
        hdu = pf.PrimaryHDU(self.flat)
        hdulist = pf.HDUList([hdu])
        hdulist.writeto(self.combinedFlat)
        self.log.info('Combined flat saved to {0:>s}'.format(self.combinedFlat))

        return self.flat


    def normalizeFlat(self, filename=None, output='normim.fits', nodes=25):
        '''
        Normalizes the flat in a very crude way.

        :note: one should probably use something else for this step
        '''
        self.normFlat = output

        if filename is None:
            inf = self.combinedFlat
            indata = self.flat
        else:
            inf = filename
            indata = pf.getdata(filename)[0]

        s = indata.shape
        nx = s[0]
        ny = s[1]

        #nodes
        xpx = np.arange(nx, dtype=int)
        xnod = np.arange(nodes) * (nx - 1.) / (nodes - 1.)   #spaced nodes incl ends

        #add extra pt half way btwn first and last pts at ends
        dl = xnod[1] - xnod[0]
        xnod = np.insert(xnod, 1, dl / 2.)
        xnod = np.insert(xnod, -1, (xnod[-1] - dl / 2.))

        for i in range(ny):
            line = indata[:, i]
            tmp = SS.medfilt(line, 13)
            #this is stupid as it has been adapted from another script...
            xnod = np.arange(nodes) * (np.max(xpx) - xpx[0]) / (nodes - 1) + xpx[0]
            ynod = np.array([np.mean(tmp[x - 5:x + 5]) for x in xnod])
            ynod[np.isnan(ynod)] = np.mean(tmp)
            fitynods, _t = self._splinefitScipy(xpx, tmp, ynod, xnod)
            fit = self._cspline(xnod, fitynods, xpx)

            #divide with the fit
            indata[:, i] /= fit

        self.normalizedFlat = indata

        self.log.info('FLAT frame {0:>s} was normalized and saved to {1:>s}'.format(inf, output))

        #write the output
        hdu = pf.PrimaryHDU(self.normalizedFlat)
        hdulist = pf.HDUList([hdu])
        hdulist.writeto(self.normFlat)
        self.log.info('Combined flat saved to {0:>s}'.format(self.normFlat))


        return self.normalizedFlat


    def _makeBiasPyraf(self, combine='median', biaslist=[], output='zeroim.fits'):
        '''
        Creates a master bias from given list of bias frames

        :param: combine, either median or mean
        :param: biaslist, a list of bias frames to be combined
        :param: output: the name of the output file
        '''
        from pyraf import iraf
        from pyraf.iraf import imred, ccdred

        iraf.zerocombine(input=biaslist, output=output,
                         combine=combine)#, rdnoise=noise, gain=gain)


    def _fitfunc(self, x, ynodes):
        '''
        The function that is being fitted.
        This can be changed to whatever function if needed.
        Note that ynodes can then be a list of parameters.
        k defines the order of the spline fitting, it is hard coded
        to be 3, but could be changed if needed.

        :param x: the x position where to evaluate the B-spline
        :param ynodes: y position of the nodes

        :return: 1-D evaluated B-spline value at x.
        '''
        return I.splev(x, I.splrep(self.xnodes, ynodes, k=3))

    def _errfunc(self, ynodes, x, y):
        '''
        Error function; simply _fitfunction - ydata

        :param ynodes: y position of the nodes to be evaluated
        :param x: x positions where to evaluate the B-spline
        :param y: y positions

        :return: Spline evaluated y positions - ydata
        '''
        return self._fitfunc(x, ynodes) - y

    def _splinefitScipy(self, x, y, ynodes, xnodes):
        '''
        Return the point which minimizes the sum of squares of M (non-linear)
        equations in N unknowns given a starting estimate, x0, using a
        modification of the Levenberg-Marquardt algorithm.

        :param x:
        :param y:
        :param ynodes:
        :param xnodes:

        :return: fitted parameters, error/success message
        '''
        self.xnodes = xnodes
        return O.leastsq(self._errfunc, ynodes, args=(x, y))

    def _cspline(self, x, y, t):
        '''
        Uses interpolation to find the B-spline representation of 1-D curve.

        :param x: x position
        :param y: y position
        :param t: position in which to evaluate the B-spline

        :return: interpolated y position of the B-sline
        '''
        tck = I.splrep(x, y)
        y2 = I.splev(t, tck)
        return y2


    def subtractBias(self, filelist, ext=0, biasFile=None):
        '''
        Subtracts the bias from the filelist
        '''
        if biasFile is None:
            b = self.bias
            biasFile = self.masterBias
        else:
            b = pf.open(biasFile)[0].data

        for file in filelist:
            #file handler
            fh = pf.open(file, mode='update', ignore_missing_end=True)

            #data
            data = fh[ext].data
            if data.shape[0] == 1 or self.dataWeird == True:
                data = fh[ext].data[0]

            #update data
            data -= b

            #save file
            fh.flush(output_verify='warn')

            #update log
            self.log.info('Subtracted {0:>s} from {1:>s} and saved the file...'.format(biasFile, file))

            #close handler
            fh.close(output_verify='ignore')


if __name__ == '__main__':
    #intiate the class instance
    reduce = SOARReduction()
#    #renames some files
#    reduce.renameUnusedFiles()
#    #find bias files
#    biases = reduce.findBiases()
#    #subtract the overscan
#    reduce.subtractOverscan(biases)
#    #find all the rest of the files
#    frames = reduce.findNonBiasFrames()
#    #subtract the overscan from these files
#    reduce.subtractOverscan(frames)
#    #make a bias frame
#    bias = reduce.makeBias()
#    #subtract the bias frame from the rest
#    reduce.subtractBias(frames)
#    #find flat field files and write a list of flats
#    flats = reduce.findFlats()
#    #combines the flats
#    combflat = reduce.makeFlat()
    norm = reduce.normalizeFlat(filename='flatima.fits')