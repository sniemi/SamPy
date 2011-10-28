"""
This script can be used to flux calibrate an image slicer 2D spectra to SDSS one (of the same target).

Matches the slit width to SDSS fiber, takes into account the difference in area covered
using a boosting factor and fractional pixels.

.. Warning:: On should only fit the observed spectrum that has been recorded at the same place
             as the SDSS spectrum. Otherwise the fitting will artificially throw the flux
             calibration off.

:requires: PyfITS
:requires: NumPy
:requires: SciPy
:requires: matplotlib
:requires: SamPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.5
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


class calibrateToSDSS():
    """
    This class can be used to flux calibrate an image
    slicer 2D spectra to SDSS one (of the same target).
    """
    def __init__(self, configfile, debug, section='DEFAULT'):
        """
        Class constructor.

        :param configfile: name of the configuration file
        :type configfile: string
        :param debug: whether ot output debugging information or not
        :type debug: boolean
        :param section: configure file section to read
        :type section: string
        """
        self.configfile = configfile
        self.section = section
        self.debug = debug
        self.fitting = {}


    def _readConfigs(self):
        """
        Reads in the config file information using configParser.
        """
        self.config = ConfigParser.RawConfigParser()
        self.config.readfp(open(self.configfile))


    def _processConfigs(self):
        """
        Processes configuration information read by the __readConfigs method and produces a dictionary describing slits.
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
        Loads the FITS files using PyFITS and converts the SDSS flux to flux units.
        """
        self.fitting['sdssData'] = pf.open(self.fitting['sdss'])[1].data
        self.fitting['SDSSflux'] = self.fitting['sdssData']['FLUX']*1e-17
        self.fitting['SDSSwave'] = self.fitting['sdssData']['WAVELENGTH']
        self.fitting['obsData'] = pf.open(self.fitting['observed'])[0].data
        self.fitting['obsHeader'] = pf.open(self.fitting['observed'])[0].header


    def _calculateArea(self):
        """
        Calculates the fiber area and the ratio of the fiber to slit area.

        Calculates the number of pixels around the center that should be included.
        Calculates also the fraction that the full pixels do not cover to be used
        later to take into account the "missing flux".
        """
        self.fitting['FiberArea'] = np.pi*(self.fitting['FiberDiameter'] / 2.)**2
        self.fitting['slitPixels'] = self.fitting['FiberDiameter'] / \
                                     self.fitting['platescale'] / \
                                     self.fitting['binning']
        self.fitting['slitPix2'] = int(np.floor((self.fitting['slitPixels'] - 1.0) / 2.))
        self.fitting['slitPixFractional'] = self.fitting['slitPixels'] - (2*self.fitting['slitPix2'] + 1.)
        self.fitting['boosting'] = self.fitting['FiberArea'] / \
                                   (self.fitting['width'] * self.fitting['slitPixels'])


    def _deriveObservedSpectra(self):
        """
        Derives a 1D spectrum from the 2D input data.

        Sums the pixels around the centre of the continuum that match to the SDSS fiber size.
        Multiplies the flux in the pixels next to the last full ones to include with the
        fractional flux we would otherwise be "missing".
        """
        #y center and how many full pixels on either side we can include that would still
        #be within the SDSS fiber
        y = self.fitting['ycenter']
        ymod = self.fitting['slitPix2']

        #modify the lines of the fractional pixel information
        self.fitting['obsData'][y+ymod+1, :] *= (self.fitting['slitPixFractional'] / 2.)
        self.fitting['obsData'][y-ymod-1, :] *= (self.fitting['slitPixFractional'] / 2.)

        #sum the flux
        self.fitting['obsSpectrum'] = np.sum(self.fitting['obsData'][y-ymod-1:y+ymod+2, :], axis=0) / \
                                      self.fitting['boosting']

        #match the resolution, i.e. convolve the observed spectrum with a Gaussian
        self.fitting['obsSpectraConvolved'] = filt.gaussian_filter1d(self.fitting['obsSpectrum'],
                                                                     self.fitting['sigma'])

        #get a wavelength scale
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
                           len(self.fitting['obsSpectraConvolved']), total=True)

        self.fitting['spectraRatio'] = self.fitting['obsSpectraConvolved'] / newflux
        self.fitting['interpFlux'] = newflux


    def _generateMask(self):
        """
        Generates a mask in which Halpha and some other lines have been masked out.

        :todo: The masking out regions has been hardcoded. This should be changed, as
               now depending on the redshift of the galaxy the masking region may not
               fully cover the feature.
        """
        #TODO: remove the hardcoded lines
        halph = [6660, 6757]
        msk = ~((self.fitting['obsWavelengths'] >= halph[0]) & (self.fitting['obsWavelengths'] <= halph[1])) & \
              ~((self.fitting['obsWavelengths'] >= 6000) & (self.fitting['obsWavelengths'] <= 6040)) & \
              ~((self.fitting['obsWavelengths'] >= 6030) & (self.fitting['obsWavelengths'] <= 6070))
        self.fitting['mask'] = msk


    def _fitSmoothFunction(self):
        """
        Fits a smooth function to the spectra ratio.

        Uses the NumPy polyfit to do the fitting.
        """
        fx = np.poly1d(np.polyfit(self.fitting['obsWavelengths'][self.fitting['mask']],
                                  self.fitting['spectraRatio'][self.fitting['mask']],
                                  self.fitting['order']))
        self.fitting['fit'] = fx(self.fitting['obsWavelengths'])

        if self.debug:
            print '\nFitting parameters:'
            print fx


    def _generatePlots(self):
        """
        Generate some plots showing the fit and the spectra.

        These plots are not crucial but rather a convenience when
        inspecting whether the derived fit was reasonable and how
        much the flux values have been modified.
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
        Outputs the sensitivity function to an ascii file. This file can be used later
        for other calibrations if needed.
        """
        fh = open('sensitivity.txt', 'w')
        fh.write('#Wavelength sensitivity\n')
        for a, b in zip(self.fitting['obsWavelengths'], self.fitting['fit']):
            fh.write(str(a) + ' ' + str(b) + '\n')
        fh.close()


    def _updateFITSfiles(self):
        """
        Updates the FITS files that were given in the configuration file with the derived flux factor.

        Interpolates the fitted ratio function if the wavelength scale of the file
        to be updated is different.
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
        Driver function that should be called if all steps of the class should be performed.
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
    #the script starts here
    opts, args = processArgs()

    if opts.configfile is None:
        processArgs(True)
        sys.exit(1)

    if opts.section is None:
        calibrate = calibrateToSDSS(opts.configfile, opts.debug)
    else:
        calibrate = calibrateToSDSS(opts.configfile, opts.debug, opts.section)

    calibrate.run()