"""
This script can be used to flux calibrate an image slicer 2D spectra to SDSS one (of the same target).

:requires: PyfITS
:requires: NumPy
:requires: SciPy
:requires: matplotlib
:requires: SamPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.3
"""
import os, sys, datetime
import ConfigParser
from optparse import OptionParser
import pyfits as pf
import numpy as np
import scipy.ndimage.filters as filt
import scipy.interpolate as interpolate
from matplotlib import pyplot as plt
import SamPy.fits.basics as basics
import SamPy.fitting.fits as ff
import SamPy.image.manipulation as m
#import scipy.optimize as optimize

__author__ = 'Sami-Matias Niemi'


class calibrateToSDSS():
    """
    This class can be used to flux calibrate an image
    slicer 2D spectra to SDSS one (of the same target).
    """
    def __init__(self, configfile, debug, section='DEFAULT'):
        """
        Constructor
        """
        self.configfile = configfile
        self.section = section
        self.debug = debug
        self.fitting = {}


    def _readConfigs(self):
        """
        Reads the config file information using configParser.
        """
        self.config = ConfigParser.RawConfigParser()
        self.config.readfp(open(self.configfile))


    def _processConfigs(self):
        """
        Process configuration information and produce a dictionary describing slits.
        """
        self.fitting['sigma'] = self.config.getfloat(self.section, 'sigma')
        self.fitting['ycenter'] = self.config.getint(self.section, 'ycenter')
        self.fitting['width'] = self.config.getfloat(self.section, 'width')
        self.fitting['platescale'] = self.config.getfloat(self.section, 'platescale')
        self.fitting['binning'] = self.config.getint(self.section, 'binning')
        self.fitting['FiberDiameter'] = self.config.getfloat(self.section, 'fiberDiameter')
        self.fitting['sdss'] = self.config.get(self.section, 'SDSSspectrum')
        self.fitting['observed'] = self.config.get(self.section, 'observedspectrum')
        self.fitting['order'] = self.config.getint(self.section, 'order')

        names = list(self.config.get(self.section, 'update').strip().split(','))
        self.fitting['update'] = [name.strip() for name in names]

        if self.debug:
            print '\nConfiguration parameters:'
            print self.fitting


    def _loadData(self):
        """
        Loads the FITS files using PyFITS and modifies the SDSS flux.
        """
        self.fitting['sdssData'] = pf.open(self.fitting['sdss'])[1].data
        self.fitting['SDSSflux'] = self.fitting['sdssData']['FLUX']*1e-17
        self.fitting['SDSSwave'] = self.fitting['sdssData']['WAVELENGTH']
        self.fitting['obsData'] = pf.open(self.fitting['observed'])[0].data
        self.fitting['obsHeader'] = pf.open(self.fitting['observed'])[0].header


    def _calculateArea(self):
        """
        Calculates the fiber area and the ratio.

        :note: Doesn't necessarily need the boosting factor, it could be removed.
        """
        self.fitting['FiberArea'] = np.pi*(self.fitting['FiberDiameter'] / 2.)**2
        self.fitting['slitPixels'] = self.fitting['FiberDiameter'] / \
                                     self.fitting['platescale'] / \
                                     self.fitting['binning']
        self.fitting['slitPix2'] = int(self.fitting['slitPixels'] / 2.)
        self.fitting['boosting'] = self.fitting['FiberArea'] / \
                                   (self.fitting['width'] *
                                    self.fitting['slitPix2'] * 2.)


    def _deriveObservedSpectra(self):
        """
        Derives a 1D spectrum from the 2D input data.
        Sums the pixels around the centre of the continuum that match to the SDSS fiber size.
        """
        y = self.fitting['ycenter']
        ymod = self.fitting['slitPix2']
        self.fitting['obsSpectrum'] = np.sum(self.fitting['obsData'][y-ymod:y+ymod+1, :], axis=0)*\
                                      self.fitting['boosting']
        
        self.fitting['obsSpectraConvolved'] = filt.gaussian_filter1d(self.fitting['obsSpectrum'],
                                                                     self.fitting['sigma'])

        self.fitting['obsWavelengths'] = basics.getWavelengths(self.fitting['observed'],
                                                               len(self.fitting['obsSpectraConvolved']))


    def _calculateDifference(self):
        """
        Calculates the difference between the derived observed and SDSS spectra.
        Interpolates the SDSS spectra to the same wavelength scale. In this interpolation
        the flux is conserved.
        """
        ms = (self.fitting['SDSSwave'] >= np.min(self.fitting['obsWavelengths'])) &\
             (self.fitting['SDSSwave'] <= np.max(self.fitting['obsWavelengths']))
        newflux = m.frebin(self.fitting['SDSSflux'][ms],
                           len(self.fitting['obsSpectraConvolved']))#, total=True)

        self.fitting['spectraRatio'] = self.fitting['obsSpectraConvolved'] / newflux
        self.fitting['interpFlux'] = newflux


    def _generateMask(self):
        """
        Generates a mask in which Halpha and some other lines have been removed
        :todo: This is now hard coded, make something better...
        """
        #TODO: remove the hardcoded lines
        halph = [6660, 6757]
        msk = ~((self.fitting['obsWavelengths'] >= halph[0]) & (self.fitting['obsWavelengths'] <= halph[1])) & \
              ~((self.fitting['obsWavelengths'] >= 6004) & (self.fitting['obsWavelengths'] <= 6042)) & \
              ~((self.fitting['obsWavelengths'] >= 6040) & (self.fitting['obsWavelengths'] <= 6068))
        self.fitting['mask'] = msk


    def _fitSmoothFunction(self):
        """
        Fits a smooth function to the spectra ratio.
        Two options can be used, either NumPy polyfit or SciPy curve_fit.
        By default the NumPy polyfit is being used.
        """
        #with NumPy polyfit
        fx = np.poly1d(np.polyfit(self.fitting['obsWavelengths'][self.fitting['mask']],
                                  self.fitting['spectraRatio'][self.fitting['mask']],
                                  self.fitting['order']))
        self.fitting['fit'] = fx(self.fitting['obsWavelengths'])
        #with scipy curvefit
        #popt, pconv = optimize.curve_fit(ff.polynomial5,
        #                                 self.fitting['obsWavelengths'][self.fitting['mask']],
        #                                 self.fitting['spectraRatio'][self.fitting['mask']])
        #self.fitting['fit2'] = ff.polynomial5(self.fitting['obsWavelengths'], *popt)

        if self.debug:
            print '\nFitting parameters:'
            print fx
            #print popt


    def _generatePlots(self):
        """
        Generate some plots showing the fit and the spectra.
        """
        #first
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.plot(self.fitting['SDSSwave'], self.fitting['SDSSflux'], label='SDSS')
        ax.plot(self.fitting['obsWavelengths'][self.fitting['mask']],
                self.fitting['obsSpectraConvolved'][self.fitting['mask']],
                label='Convolved and Masked')
        ax.plot(self.fitting['obsWavelengths'],
                self.fitting['obsSpectrum']/self.fitting['fit'],
                label='Fitted Spectra')
        ax.set_ylabel('Flux [erg/cm**2/s/AA]')
        ax.set_xlabel('Wavelength [AA]')
        ax.set_xlim(3800, 9200)
        plt.legend(shadow=True, fancybox=True)
        plt.savefig('Spectra.pdf')
        ax.set_xlim(5450, 6950)
        plt.savefig('SpectraZoomed.pdf')
        plt.close()

        #second
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.scatter(self.fitting['obsWavelengths'][self.fitting['mask']],
                   self.fitting['spectraRatio'][self.fitting['mask']], s = 2,
                   label = 'Observed Spectra / SDSS (masked)')
        ax.plot(self.fitting['obsWavelengths'], self.fitting['fit'], 'r-',
                label = 'Fit')
        #ax.plot(self.fitting['obsWavelengths'], self.fitting['fit2'], 'g-',
        #        label = 'Fit2')
        ax.set_ylabel('Ratio')
        ax.set_xlabel('Wavelength [AA]')
        plt.legend(shadow=True, fancybox=True, numpoints=1)
        plt.savefig('Fitting.pdf')
        plt.close()


    def _outputSensitivity(self):
        """
        Outputs the sensitivity function to an ascii file.
        """
        fh = open('sensitivity.txt', 'w')
        fh.write('#Wavelength sensitivity\n')
        for a, b in zip(self.fitting['obsWavelengths'], self.fitting['fit']):
            fh.write(str(a) + ' ' + str(b) + '\n')
        fh.close()


    def _updateFITSfiles(self):
        """
        Updates the FITS files. Interpolates the fitted ratio function if
        the wavelength scale of the file to be updated is different.
        """
        #must interpolate the fitted function to right wavelength scale
        interp = interpolate.interp1d(self.fitting['obsWavelengths'], self.fitting['fit'])
        #loop over the files to be updated.
        for file in self.fitting['update']:
            fh = pf.open(file)
            hdu = fh[0].header
            data = fh[0].data

            ft = interp(basics.getWavelengths(file, len(data[0,:])))
            for i, line in enumerate(data):
                data[i, :] = line / ft
            new = file.split('.fits')[0] + 'senscalib.fits'

            hdu.add_history('Original File: %s' % file)
            hdu.add_history('Pixel values modified by fluxCalibrateToSDSS.py (SMN)')
            hdu.add_history('Updated: %s' % datetime.datetime.isoformat(datetime.datetime.now()))

            if os.path.isfile(new):
                os.remove(new)
            fh.writeto(new, output_verify='ignore')
            fh.close()
            
            if self.debug:
                print '\nFile %s updated and saved as %s' % (file, new)

                
    def run(self):
        """
        Driver function, runs all the required steps.
        """
        self._readConfigs()
        self._processConfigs()
        self._loadData()
        self._calculateArea()
        self._deriveObservedSpectra()
        self._calculateDifference()
        self._generateMask()
        self._fitSmoothFunction()
        self._generatePlots()
        self._outputSensitivity()
        self._updateFITSfiles()


def processArgs(printHelp=False):
    """
    Processes command line arguments.
    """
    parser = OptionParser()

    parser.add_option('-c', '--configfile', dest='configfile',
                      help="Name of the configuration file", metavar="string")
    parser.add_option('-s', '--section', dest='section',
                      help="Name of the section of the config file", metavar="string")
    parser.add_option('-d', '--debug', dest='debug', action='store_true',
                      help='Debugging mode on')
    if printHelp:
        parser.print_help()
    else:
        return parser.parse_args()


if __name__ == '__main__':
    opts, args = processArgs()

    if opts.configfile is None:
        processArgs(True)
        sys.exit(1)

    if opts.section is None:
        calibrate = calibrateToSDSS(opts.configfile, opts.debug)
    else:
        calibrate = calibrateToSDSS(opts.configfile, opts.debug, opts.section)

    calibrate.run()