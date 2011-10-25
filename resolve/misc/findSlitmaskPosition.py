"""
Class to fit spectroscopic observations to a direct image.

The class has been designed for image slicer data where at
the moment three spectra are recorded simultaneously.
However, the class should be modified in several ways
to be more flexible. For example, the slitmask shuold
be generated from all input data with potential rotations
and offsets. This would constrain the slitmask position
better and allow a single solution.

The algorithm currently used to find the slit mask position
is poor. It is very slow when allowing rotations and in
some cases it finds the position poorly. This algorithm
should be rewritten from scratch. I have experimented with
FFT-base image registration techniques which seem to work
well in case of images. However, our spectral data do not
allow reconstruction of an image, because we don't have
information in the dispersion direction. Thus, these
techniques might be difficult to adapt, even though
for imaging data they seem superior. Thus, an iterative
algorithm, which first fits the position in a crude grid
and then in more finely sampled one should be implemented.
In this way one could find the 0th order position first,
make a cutout region around this position and perform the
rotations respect to the initial result. In this way the
rotations were always roughly respect to the galaxy center
and they would also be faster because the area that must
be interpolated would be smaller.

:requires: SamPy
:requires: PyFITS
:requires: NumPy
:requires: matplotlib
:requires: SciPy
:requires: astLib
:requires: pywcs (this could also be replaced with Kapteyn)
:requires: Kapteyn Python package
:requires: Python 2.6 or newer

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.5
"""
import os, sys, datetime
import ConfigParser
from optparse import OptionParser
import pywcs
import pyfits as pf
import numpy as np
from astLib import astCoords
import scipy.stats as stats
from kapteyn import wcs, positions, maputils
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from matplotlib import cm
import SamPy.smnIO.write as write
import SamPy.smnIO.read
import SamPy.image.manipulation as m
import SamPy.fits.modify as modify
import SamPy.astronomy.fluxes as flux
import SamPy.sandbox.odict as o
import SamPy.astronomy.conversions as convert


class FindSlitmaskPosition():
    """
    This class can be used to find a slit mask position in a direct image.

    It fits the slit mask information to profiles built from the direct image
    to recover the mask position on the sky.
    """

    def __init__(self, configfile, debug, section='DEFAULT'):
        """
        Class Constructor.

        :param configfile: name of the configuration file
        :type configfile: string
        :param debug: debugging mode on/off
        :type debug: boolean
        :param section: name of the section of the configuration file to process
        :type section: string
        """
        self.slits = o.OrderedDict()
        self.sky = {}
        self.direct = {}
        self.fitting = {}
        self.result = {}

        self.configfile = configfile
        self.section = section
        self.debug = debug

        self._readConfigs()
        self._processConfigs()


    def _readConfigs(self):
        """
        Reads the config file information using configParser.
        """
        self.config = ConfigParser.RawConfigParser()
        self.config.readfp(open(self.configfile))


    def _generateSlitProfile(self, spectrum, hdr):
        """
        Generates a slit profile by convolving the spectrum with a filter transmission curve.

        :param spectrum: 2D spectral image
        :type spectrum: ndarray
        :param hdr: header of the spectral image
        :type hdr: PyFITS header instance

        :note: reading in the filter file has been hardcoded, so if the format of the
               filter curve changes, the usecols part must be changed as well.

        :return: flux at a given point in the slit
        :rtype: ndarray
        """
        #read the filter information
        filter = np.loadtxt(self.direct['filterfile'], usecols=(1, 2))
        wave = filter[:, 0]
        thr = filter[:, 1]

        #normalize if the throughput is more than unity
        if np.max(thr) > 1.0:
            thr /= np.max(thr)

        npix = spectrum.shape[1]
        #get wave info, note one could use WCS for this
        crval = hdr['CRVAL1']
        crpix = hdr['CRPIX1']
        delta = hdr['CD1_1']

        if 'LIN' in hdr['CTYPE1']:
            if crpix < 0:
                xps = np.arange(0, npix - crpix + 1) * delta + crval
                xps = xps[-crpix + 1:]
            elif crpix > 0:
                xps = np.arange(crpix - 1, npix + crpix - 1) * delta + crval
            else:
                xps = np.arange(0, npix) * delta + crval

            minwave = np.min(xps)
            maxwave = np.max(xps)
            deltal = maxwave - minwave
            #width = convert.angstromToHertz(maxwave) - convert.angstromToHertz(minwave)

            #go through the spectrum line by line
            out = []
            for i, f in enumerate(spectrum):
                res = flux.convolveSpectrum(xps, f, wave, thr)
                #convert to micro Jansky
                tmp = res['flux'] * deltal ** 2 * 3.3356409e4 * 1e6

                if tmp < 0.0:
                    tmp = 0.0
                out.append(tmp)

            return np.asarray(out)

        else:
            raise NotImplementedError, 'non linear spectrum scaling not implemented yet'


    def _processSlitfiles(self):
        """
        Reads in the slit and direct image FITS files.
        Pulls out some useful header keywords such as POSANGLE, which can be
        used for the initial guess for rotation.
        """
        #load images
        for slit in self.slits:
            fh = pf.open(self.slits[slit]['file'], ignore_missing_end=True)
            self.slits[slit]['header0'] = fh[0].header
            slitimage = fh[0].data
            fh.close()
            if slitimage.shape[0] == 1:
                slitimage = slitimage[0]
            self.slits[slit]['image'] = slitimage
            self.slits[slit]['profile'] = self._generateSlitProfile(slitimage, self.slits[slit]['header0'])
            self.slits[slit]['pixels'] = len(self.slits[slit]['profile'])
            self.slits[slit]['POSANGLE'] = self.slits[slit]['header0']['POSANGLE']

        if self.debug:
            print '\nslits:'
            print self.slits


    def _processDirectImage(self, ext=0):
        """
        Processes the given Direct Image file.

        This method performs several tasks:

          1. trims the image (optional, depends on self.cutout)
          2. supersamples the original image by a given factor
          3. rotates the image by -POSANGLE degrees, note the minus sign
          4. gets the plate scale from the rotated header

        :param ext: FITS extension, change this if the SDSS data changes or if other data are used.
        :type ext: int
        """
        #load images
        fh = pf.open(self.dirfile)
        self.direct['originalHeader0'] = fh[ext].header
        img = fh[ext].data
        fh.close()
        self.direct['originalImage'] = img

        #cut out a region
        if self.cutout:
            ra = self.slits['mid']['header0']['RA']
            dec = self.slits['mid']['header0']['DEC']
            ra = astCoords.hms2decimal(ra, ':')
            dec = astCoords.dms2decimal(dec, ':')
            wcs = pywcs.WCS(self.direct['originalHeader0'])
            pix = wcs.wcs_sky2pix(np.array([[ra, dec], ]), 1)
            xmid = pix[0, 0]
            ymid = pix[0, 1]
            xstart = int(xmid - self.direct['xsize'] / 2.)
            xstop = int(xmid + self.direct['xsize'] / 2.)
            ystart = int(ymid - self.direct['ysize'] / 2.)
            ystop = int(ymid + self.direct['ysize'] / 2.)
            imgT, hdrT = modify.hextract(self.dirfile, xstart, xstop, ystart, ystop)
            shape = imgT.shape
            file = 'resized.fits'
        else:
            shape = img.shape
            file = self.dirfile

        #super sample
        if self.direct['factor'] != 1:
            xnew = int(shape[1] * self.direct['factor'])
            ynew = int(shape[0] * self.direct['factor'])
            imgS, hdrS = modify.hrebin(file, xnew, ynew, total=True)
            self.direct['xnew'] = xnew
            self.direct['ynew'] = ynew
            self.direct['supersampledImage'] = imgS
            self.direct['supersampledHeader'] = hdrS
            self.direct['supersampledFile'] = 'rebinned.fits'
        else:
            self.direct['xnew'] = int(shape[1])
            self.direct['ynew'] = int(shape[0])
            self.direct['supersampledImage'] = img
            self.direct['supersampledHeader'] = self.direct['originalHeader0']
            self.direct['supersampledFile'] = self.dirfile


        #set rotation, note that the rotaion is in minus direction
        #instead of using SPA one could also calculate this from WCS CD matrix
        self.direct['rotation'] = -self.slits['mid']['POSANGLE'] + self.direct['originalHeader0']['SPA']
        #make a rotation
        imgR, hdrR = modify.hrot(self.direct['supersampledFile'],
                                 self.direct['rotation'],
                                 xc=None,
                                 yc=None)
        self.direct['rotatedImage'] = imgR
        self.direct['rotatedHeader'] = hdrR
        self.direct['rotatedFile'] = 'rotated.fits'

        #convert the images from nanomaggies to micro Janskys and remove values < 0.0
        self.direct['originalImage'] = convert.nanomaggiesToJansky(self.direct['originalImage']) * 1e6
        #self.direct['originalImage'][self.direct['originalImage'] < 0.0] = 0.0
        self.direct['supersampledImage'] = convert.nanomaggiesToJansky(self.direct['supersampledImage']) * 1e6
        #self.direct['supersampledImage'][self.direct['supersampledImage'] < 0.0] = 0.0
        self.direct['rotatedImage'] = convert.nanomaggiesToJansky(self.direct['rotatedImage']) * 1e6
        #self.direct['rotatedImage'][self.direct['rotatedImage'] < 0.0] = 0.0

        #WCS info
        self.direct['WCS'] = pywcs.WCS(hdrR)
        #self.direct['WCS'] = wcs.Projection(hdrR)

        #get the plate scale from the header
        self.direct['platescale'] /= self.direct['factor']

        if self.debug:
            print '\ndirect:'
            print self.direct


    def _processConfigs(self):
        """
        Process configuration information and produces several dictionaries describing the information.
        These dictionaries will be used later on for example when generating a slit mask or running
        the fitting algorithm. These dictionaries will also hold the direct imaging data as well as
        the spectroscopic profiles.
        """
        self.spectra = list(self.config.get(self.section, 'spectra').strip().split(','))
        self.dirfile = self.config.get(self.section, 'directimage')
        widths = [float(a) for a in self.config.get(self.section, 'widths').strip().split(',')]
        heights = [float(a) for a in self.config.get(self.section, 'heights').strip().split(',')]
        thrs = [float(a) for a in self.config.get(self.section, 'throughputs').strip().split(',')]
        offseta = self.config.getfloat(self.section, 'offsetalong')
        offsetb = self.config.getfloat(self.section, 'offsetbetween')
        binning = self.config.getint(self.section, 'binning')
        platescaleS = self.config.getfloat(self.section, 'platescaleSpectra')
        platescaleD = self.config.getfloat(self.section, 'platescaleDirect')
        factor = self.config.getfloat(self.section, 'supersample')
        names = list(self.config.get(self.section, 'names').strip().split(','))
        names = [name.strip() for name in names]
        filtercurve = self.config.get(self.section, 'throughputfile')
        postageTolerance = self.config.getfloat(self.section, 'postageTolerance')
        xsize = self.config.getfloat(self.section, 'xsize')
        ysize = self.config.getfloat(self.section, 'ysize')
        self.cutout = self.config.getboolean(self.section, 'cutout')

        for f, n, w, h, t in zip(self.spectra, names, widths, heights, thrs):
            self.slits[n] = {'widthSky': w,
                             'widthPixels': w / platescaleS / binning,
                             'heightSky': h,
                             'heightPixels': h / platescaleS / binning,
                             'throughput': 1. / t,
                             'binning': binning,
                             'file': f,
                             'name': n}

        #sky related
        self.sky['offseta'] = offseta
        self.sky['offsetb'] = offsetb
        self.sky['platescaleSpectra'] = platescaleS

        #direct image information
        self.direct['filterfile'] = filtercurve
        self.direct['postageTolerance'] = postageTolerance
        self.direct['factor'] = factor
        self.direct['platescale'] = platescaleD
        self.direct['xsize'] = xsize
        self.direct['ysize'] = ysize

        #fitting related
        self.fitting['xrange'] = self.config.getint(self.section, 'xrange')
        self.fitting['xstep'] = self.config.getint(self.section, 'xstep')
        self.fitting['yrange'] = self.config.getint(self.section, 'yrange')
        self.fitting['ystep'] = self.config.getint(self.section, 'ystep')
        self.fitting['method'] = self.config.get(self.section, 'fittingMethod')
        try:
            self.fitting['rotation'] = self.config.getfloat(self.section, 'rotation')
            self.rotation = True
        except:
            self.rotation = False
        try:
            self.normalize = self.config.getboolean(self.section, 'normalize')
        except:
            self.normalize = False
        self.fitting['rotstep'] = self.config.getfloat(self.section, 'rotationstep')

        if self.debug:
            print '\nsky:'
            print self.sky
            print '\nfitting:'
            print self.fitting


    def _calculatePosition(self):
        """
        This method can be used to calculate the WCS values.
        Uses the pywcs to calculate the pixel to RA and DEC transformations.
        Uses astLib.astCoords to transform RA and DEC to decimal degrees.
        """
        #get RA and DEC from the header
        ra = self.slits['mid']['header0']['RA']
        dec = self.slits['mid']['header0']['DEC']
        ra = astCoords.hms2decimal(ra, ':')
        dec = astCoords.dms2decimal(dec, ':')
        pix = self.direct['WCS'].wcs_sky2pix(np.array([[ra, dec], ]), 1)
        self.direct['xposition'] = int(pix[0, 0])
        self.direct['yposition'] = int(pix[0, 1])
        self.result['RAinit'] = ra
        self.result['DECinit'] = dec

        if self.debug:
            print self.direct['xposition'], self.direct['yposition']


    def _plotGalaxy(self):
        """
        Very simple script to plot an image of the galaxy

        :Note: At the moment the low and high end clipping values for scaling the image
               has been hardcoded. At some point these could be transferred to be read
               from the configuration file.
        """
        tol = np.floor(self.direct['postageTolerance'] / self.direct['platescale'])
        xp = self.direct['xposition']
        yp = self.direct['yposition']

        #make a figure
        fig = plt.figure(1)
        ax = fig.add_subplot(111)

        #from Kapteyn
        f = maputils.FITSimage(self.direct['rotatedFile'])
        annim = f.Annotatedimage(ax, clipmin=0.01, clipmax=1)
        annim.Image(alpha=0.9)
        grat = annim.Graticule()
        grat.setp_gratline(wcsaxis=0, linestyle=':')
        grat.setp_gratline(wcsaxis=1, linestyle=':')
        annim.plot()

        plt.savefig('Galaxy.pdf')
        plt.close()

        #zoomed in version with the spectra
        fig = plt.figure(figsize=(15, 15))
        ax1 = fig.add_subplot(4, 1, 1)

        f = maputils.FITSimage(self.direct['rotatedFile'])
        f.set_limits(pxlim=(xp - tol, xp + tol), pylim=(yp - tol, yp + tol))
        annim = f.Annotatedimage(ax1, clipmin=0.01, clipmax=1)
        annim.Image()
        grat = annim.Graticule()
        grat.setp_gratline(wcsaxis=0, linestyle=':')
        grat.setp_gratline(wcsaxis=1, linestyle=':')
        units = r'nanomaggies'
        colbar = annim.Colorbar(fontsize=7)
        colbar.set_label(label=units, fontsize=14)
        annim.plot()

        i = 2
        for slit in self.slits.values():
            ax = fig.add_subplot(4, 1, i)
            f = maputils.FITSimage(slit['file'])
            #f.set_imageaxes('Wavelength [AA]','Pixels')
            m = f.Annotatedimage(ax)
            m.Image()
            grat = m.Graticule()
            grat.setp_gratline(wcsaxis=0, linestyle=':')
            grat.setp_gratline(wcsaxis=1, linestyle=':')
            ax.set_xlabel('Wavelength [AA]')
            ax.set_ylabel('Pixels')
            m.plot()
            i += 1

        #annim.interact_toolbarinfo()
        #annim.interact_imagecolors()
        #annim.interact_writepos()
        #plt.show()
        plt.savefig('GalaxyZoomed.pdf')
        plt.close()


    def _plotInitialSlitPositions(self):
        """
        Very simple script to plot an image of the galaxy.
        """
        tol = np.floor(self.direct['postageTolerance'] / self.direct['platescale']) # pixels
        xp = self.direct['xposition']
        yp = self.direct['yposition']

        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        ax.imshow(np.log10(self.direct['rotatedImage'].copy()), origin='lower')

        for slit in self.slits.values():
            patch = patches.Rectangle(slit['xy'],
                                      slit['xmax'] - slit['xmin'],
                                      slit['ymax'] - slit['ymin'],
                                      fill=False)
            ax.add_patch(patch)

        ax.plot(xp, yp, 'ko')
        plt.xlim(0, ax.get_xlim()[1])
        plt.ylim(0, ax.get_ylim()[1])
        plt.savefig('InitialMaskPosition.pdf')

        #zoomed in version
        ax.set_xlim(xp - tol, xp + tol)
        ax.set_ylim(yp - tol, yp + tol)
        plt.savefig('InitialMaskPositionZoomed.pdf')
        plt.close()


    def _plotFinalSlitPositions(self):
        """
        Very simple script to plot an image of the galaxy.
        """
        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        tmp = self.result['FinalImage'].copy()
        #msk = tmp < 0.0
        #tmp[~msk] = np.log10(tmp[~msk])
        #tmp[msk] = 0.0
        ax.imshow(np.log10(tmp), origin='lower')
        del tmp

        #slits
        for slit in self.slits.values():
            w = slit['width']
            h = slit['height']
            if slit['name'] == 'mid':
                patch = patches.Rectangle((self.result['xcenter'] - w / 2.,
                                           self.result['ycenter'] - h / 2.),
                                                                           w, h, fill=False)
            elif slit['name'] == 'low':
                patch = patches.Rectangle((self.result['xcenter'] - w / 2. - self.direct['xshiftSky'],
                                           self.result['ycenter'] - h / 2. - self.direct['yshiftSky']),
                                                                                                      w, h, fill=False)
            elif slit['name'] == 'up':
                patch = patches.Rectangle((self.result['xcenter'] - w / 2. + self.direct['xshiftSky'],
                                           self.result['ycenter'] - h / 2. + self.direct['yshiftSky']),
                                                                                                      w, h, fill=False)


            #t2 = matplotlib.transforms.Affine2D().rotate_deg(self.result['rotation']) + ax.transData
            #patch.set_transform(t2)
            ax.add_patch(patch)

        plt.savefig('FinalMaskPosition.pdf')

        #zoomed in version
        tol = np.floor(self.direct['postageTolerance'] / self.direct['platescale']) # pixels
        xp = self.direct['xposition'] + self.result['x']
        yp = self.direct['yposition'] + self.result['y']
        ax.set_xlim(xp - tol, xp + tol)
        ax.set_ylim(yp - tol, yp + tol)
        plt.savefig('FinalMaskPositionZoomed.pdf')
        plt.close()


    def _generateSlitMask(self):
        """
        Generates a slit mask that can be used for the direct image.

        :Note: At the moment this method can be used to generate a single slit mask
               with three slits. In the future this method should be changed to allow
               a creation of a slitmask containing rotations and offsets.
        """
        #calculate the x and y offsets between the slits on the sky in the direct image frame
        ymod = self.sky['offseta'] / self.direct['platescale']
        xmod = self.sky['offsetb'] / self.direct['platescale']
        self.direct['yshiftSky'] = ymod
        self.direct['xshiftSky'] = xmod

        for slit in self.slits:
            #calculate the positions in the frame of the direct image
            wd = self.slits[slit]['widthSky'] / self.direct['platescale'] / 2.
            hd = self.slits[slit]['heightSky'] / self.direct['platescale'] / 2.

            if slit == 'mid':
                self.slits[slit]['xmin'] = np.round(self.direct['xposition'] - wd)
                self.slits[slit]['xmax'] = np.round(self.direct['xposition'] + wd)
                self.slits[slit]['ymin'] = np.round(self.direct['yposition'] - hd)
                self.slits[slit]['ymax'] = np.round(self.direct['yposition'] + hd)
            elif slit == 'up':
                self.slits[slit]['xmin'] = np.round(self.direct['xposition'] - wd + xmod)
                self.slits[slit]['xmax'] = np.round(self.direct['xposition'] + wd + xmod)
                self.slits[slit]['ymin'] = np.round(self.direct['yposition'] - hd + ymod)
                self.slits[slit]['ymax'] = np.round(self.direct['yposition'] + hd + ymod)
            elif slit == 'low':
                self.slits[slit]['xmin'] = np.round(self.direct['xposition'] - wd - xmod)
                self.slits[slit]['xmax'] = np.round(self.direct['xposition'] + wd - xmod)
                self.slits[slit]['ymin'] = np.round(self.direct['yposition'] - hd - ymod)
                self.slits[slit]['ymax'] = np.round(self.direct['yposition'] + hd - ymod)

            self.slits[slit]['xy'] = (self.slits[slit]['xmin'], self.slits[slit]['ymin'])
            self.slits[slit]['height'] = self.slits[slit]['ymax'] - self.slits[slit]['ymin']
            self.slits[slit]['width'] = self.slits[slit]['xmax'] - self.slits[slit]['xmin']


    def _chiSquare(self, y, yfit, weight, nfree=None):
        """
        Weighted chi square.

        :param y: measured data
        :type y: ndarray
        :param yfit: calculated data based on model or least squares fitting
        :type yfit: ndarray
        :param weight: data point weights: for statistical uncertainties use 1/y
        :type weight: ndarray
        :param nfree: the number of degrees of freedom, default is number of data points - 1
        :type nfree: int

        :return: chi square value
        :rtype: float
        """
        if nfree == None:
            nfree = len(y) - 1
        return np.sum(weight * (y - yfit) * (y - yfit)) / float(nfree)


    def _fitSlitsToDirectImage(self):
        """
        Fits a slit mask profiles to a direct image to recover the position and orientation of the slitmask.

        By default the counts are not normalized to a peak count, but this can
        be controlled using the optional keyword normalize. This should be used for
        debugging purposes only. I included this part because in the beginning we
        were missing flux calibration.

        :Note: This is a very slow algorithm because of the insanely many nested for loops...

        :todo: rewrite the algorithm.

        :rtype: dictionary
        """
        #generates a model array from the slit values, takes into account potential
        #throughput of a slit
        model = np.array([])
        for vals in self.slits.values():
            #must rebin/interpolate to the right scale, conserve surface flux
            new = m.frebin(vals['profile'], int(vals['height']), total=True)
            model = np.append(model, new)
            self.fitting[vals['name']] = new

        if self.normalize:
            model /= np.max(model)

        #mask out negative values and especially those equal to zero
        msk = model > 0.0
        self.fitting['model'] = model[msk] * 10.0
        self.fitting['mask'] = msk

        #basic model information
        mean = np.mean(self.fitting['model'])
        sig = np.sqrt(np.sum((self.fitting['model'] - mean) ** 2))
        diff = self.fitting['model'] - mean
        self.fitting['sig'] = sig
        self.fitting['diff'] = diff

        #generate rotations
        if self.rotation:
            rotations = np.arange(-self.fitting['rotation'], self.fitting['rotation'], self.fitting['rotstep'])
            rotations[(rotations < 1e-8) & (rotations > -1e-8)] = 0.0
            #make a copy of the direct image
            origimage = self.direct['rotatedImage'].copy()
        else:
            rotations = [0, ]

        #x and yranges to cover in the grid
        xran = range(-self.fitting['xrange'], self.fitting['xrange'], self.fitting['xstep'])
        yran = range(-self.fitting['yrange'], self.fitting['yrange'], self.fitting['ystep'])

        #define some helper variables
        out = []
        corrmin = -1e10
        cm = 1e30

        #loop over a range of rotations, x and y positions
        #this should be done in some other way than having three nested loops... not good
        for r in rotations:
            if self.rotation:
                if r != 0.0:
                    #d = interpolation.rotate(origimage, r, reshape=False)
                    d, hdrR = modify.hrot2(origimage.copy(), self.direct['rotatedHeader'], r, xc=None, yc=None)
                else:
                    d = origimage.copy()
                    hdrR = self.direct['rotatedHeader']
            else:
                d = self.direct['rotatedImage'].copy()
                hdrR = self.direct['rotatedHeader']

            #only for debugging purposes
            if self.normalize:
                d /= np.max(d)

            for x in xran:
                for y in yran:
                    #all slits
                    dirdata = np.array([])
                    for s in self.slits.values():
                        #direct image data
                        dirdat = d[s['ymin'] + y:s['ymax'] + y,\
                                   s['xmin'] + x:s['xmax'] + x]
                        #sum the counts inside the slit
                        dirdat = np.sum(dirdat, axis=1)
                        dirdata = np.append(dirdata, dirdat.ravel())

                    #remove the masked pixels
                    dirdata = dirdata[self.fitting['mask']]

                    #chi**2, p-value
                    chisq = stats.chisquare(dirdata, self.fitting['model'])
                    #chisq = self._chiSquare(dirdata, self.fitting['model'], 1./self.fitting['model'])

                    #correlation coeff
                    mean = np.mean(dirdata)
                    sig = np.sqrt(np.sum((dirdata - mean) ** 2))
                    diff = dirdata - mean
                    corr = np.sum(self.fitting['diff'] * diff) / self.fitting['sig'] / sig

                    #save info
                    tmp = [r, x, y, chisq[0], chisq[0] / s['pixels'], chisq[1], corr]
                    #tmp = [r, x, y, chisq, chisq / s['pixels'], 0.0, corr]
                    out.append(tmp)

                    if chisq[0] < cm:
                    #if chisq < cm:
                        cm = chisq[0]
                        #cm = chisq
                        minpos = tmp
                        dir = dirdata
                        img = d
                        hdr = hdrR

                    if corr > corrmin:
                        corrmin = corr
                        minpos2 = tmp
                        dir2 = dirdata

                    if self.debug:
                        print r, x, y, chisq[0] / s['pixels'], chisq[1], corr
                        #print r, x, y, chisq / s['pixels'], 0.0, corr

        #save results
        self.result['outputs'] = out
        self.result['minimaPosition'] = minpos
        self.result['FinalImage'] = img
        self.result['FinalHeader'] = hdr
        self.result['WCS'] = pywcs.WCS(hdr)
        #self.result['WCS'] = wcs.Projection(hdr)
        #choose the method
        if 'chi' in self.fitting['method']:
            self.result['rotation'] = minpos[0]
            self.result['posangle'] = minpos[0] + self.slits['mid']['POSANGLE']
            self.result['x'] = minpos[1]
            self.result['y'] = minpos[2]
            self.result['bestfit'] = dir
            self.result['xcenter'] = self.direct['xposition'] + minpos[1]
            self.result['ycenter'] = self.direct['yposition'] + minpos[2]
            self.result['pvalue'] = minpos[5]
        elif 'corr' in self.fitting['method']:
            self.result['rotation'] = minpos2[0]
            self.result['posangle'] = minpos[0] + self.slits['mid']['POSANGLE']
            self.result['x'] = minpos2[1]
            self.result['y'] = minpos2[2]
            self.result['bestfit'] = dir2
            self.result['xcenter'] = self.direct['xposition'] + minpos2[1]
            self.result['ycenter'] = self.direct['yposition'] + minpos2[2]
            self.result['pvalue'] = minpos2[5]
        else:
            raise NotImplementedError, 'This minimization method has not yet been implemented...'

        if self.debug:
            print minpos
            print minpos2


    def _plotModelProfile(self):
        """
        Plots model profile.
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for slit in self.slits:
            ax.plot(self.fitting[slit], label=slit)
        plt.xlim(0, ax.get_xlim()[1])
        plt.ylim(0, ax.get_ylim()[1])
        plt.ylabel('Flux [microJy]')
        plt.legend(shadow=True, fancybox=True, loc='best')
        plt.savefig('ModelProfile.pdf')
        plt.close()


    def _plotMinimalization(self):
        """
        Plots a two dimensional map of the minimization.
        Also plots the best fit model and the spectroscopic data profiles.
        """
        #minima profiles
        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        ax.plot(self.fitting['model'], label='Model (Slit Profiles)')
        ax.plot(self.result['bestfit'], label='Best Fit')
        plt.legend(shadow=True, fancybox=True, loc='best')
        plt.xlim(0, ax.get_xlim()[1])
        plt.ylim(0, ax.get_ylim()[1])
        plt.ylabel('Flux [microJy]')
        plt.savefig('MinimaProfile.pdf')
        plt.close()

        #minima map
        data = self.result['outputs']
        d = np.asarray([[x[0], x[1], x[2], x[4]] for x in data])
        msk = d[:, 0] == self.result['rotation']
        plt.title('Chisq Minimalization Map: Rotation = %.2f' % self.result['rotation'])
        plt.scatter(d[:, 1][msk],
                    d[:, 2][msk],
                    c=1. / d[:, 3][msk],
                    s=20,
                    cmap=cm.get_cmap('jet'),
                    edgecolor='none',
                    alpha=0.2)
        plt.xlim(-self.fitting['xrange'], self.fitting['xrange'])
        plt.ylim(-self.fitting['yrange'], self.fitting['yrange'])
        plt.xlabel('X [pixels]')
        plt.ylabel('Y [pixels]')
        plt.savefig('MinimaMapChisq.png')
        plt.close()

        #minima map2
        d = np.asarray([[x[1], x[2], x[6]] for x in data])
        plt.title('Correlation Minimalization Map: Rotation = %.2f' % self.result['rotation'])
        plt.scatter(d[:, 0][msk],
                    d[:, 1][msk],
                    c=d[:, 2][msk],
                    s=20,
                    cmap=cm.get_cmap('jet'),
                    edgecolor='none',
                    alpha=0.2)
        plt.xlim(-self.fitting['xrange'], self.fitting['xrange'])
        plt.ylim(-self.fitting['yrange'], self.fitting['yrange'])
        plt.xlabel('X [pixels]')
        plt.ylabel('Y [pixels]')
        plt.savefig('MinimaMapCorr.png')
        plt.close()


    def _outputMinima(self):
        """
        Outputs the results to a file and also to the screen if debugging was turned on.
        """
        if 'chi' in self.fitting['method']:
            str = '{0:.2f}\t{1:.0f}\t{2:.0f}\t{3:.0f}\t{4:.0f}\t{5:.2f}\t\t{6:.2f}\n'.format(self.result['rotation'],
                                                                                             self.result['xcenter'],
                                                                                             self.result['ycenter'],
                                                                                             self.result['x'],
                                                                                             self.result['y'],
                                                                                             self.result[
                                                                                             'minimaPosition'][3],
                                                                                             self.result[
                                                                                             'minimaPosition'][4])
        elif 'corr' in self.fitting['method']:
            str = '{0:.2f}\t{1:.0f}\t{2:.0f}\t{3:.0f}\t{4:.0f}\t{5:.5f}\n'.format(self.result['rotation'],
                                                                                  self.result['xcenter'],
                                                                                  self.result['ycenter'],
                                                                                  self.result['x'],
                                                                                  self.result['y'],
                                                                                  self.result['minimaPosition'][6])
        else:
            raise NotImplementedError, 'This minimization method has not yet been implemented...'

        fh1 = open('min.txt', 'a')
        fh1.write(str)
        fh1.close()

        if self.debug:
            if 'chi' in self.fitting['method']:
                print '\n\nr \t x \t y \txoff \tyoff \tchi**2   reduced chi**2'
            elif 'corr' in self.fitting['method']:
                print '\n\nr \t x \t y \txoff \tyoff \tcorrelation coefficient'
            else:
                raise NotImplementedError, 'This minimization method has not yet been implemented...'
            print str
            print '\nInitial RA and DEC (of the centre of the centre slit)'
            print astCoords.decimal2hms(self.result['RAinit'], ':'), astCoords.decimal2dms(self.result['DECinit'], ':')
            print '\nFinal RA and DEC (of the centre of the centre slit)'
            print astCoords.decimal2hms(self.result['RA'], ':'), astCoords.decimal2dms(self.result['DEC'], ':')
            print '\nDistance on the sky (in arcseconds)'
            print astCoords.calcAngSepDeg(self.result['RAinit'],
                                          self.result['DECinit'],
                                          self.result['RA'],
                                          self.result['DEC']) * 3600


    def _calculateSkyCoords(self):
        """
        Calculates sky coordinates for the slits.
        Resamples the direct image pixels back to the
        slit image pixels. Takes the average in x-direction
        which is assumed to be across the slit, so that
        the sky coordinates are at the centre of the slit
        in this direction.
        """
        #calculate the RA and DEC of the centre of the centre slit
        centre = np.array([[self.result['xcenter'], self.result['ycenter']], ], np.float_)
        sky = self.result['WCS'].wcs_pix2sky(centre, 1)
        self.result['RA'] = sky[0][0]
        self.result['DEC'] = sky[0][1]

        #each slit pixels
        for key, value in self.slits.items():
            ymin = value['ymin'] + self.result['y']
            ymax = value['ymax'] + self.result['y']
            y = np.arange(ymin, ymax)
            #y is now sampled to the supersampled direct image
            #what we ultimately need is the coordinates
            #for slit pixels...
            resample = value['pixels']
            ybin = m.frebin(y, resample)

            #for x, given that it is the slit width
            #we need the mean value
            xmin = value['xmin'] + self.result['x']
            xmax = value['xmax'] + self.result['x']
            mean = np.mean(np.array([xmin, xmax]))
            #x = np.zeros(len(y)) + mean
            xbin = np.zeros(len(ybin)) + mean

            pixels = []
            for a, b in zip(xbin, ybin):
                pixels.append([a, b])
            pixels = np.asanyarray(pixels)
            sky = self.result['WCS'].wcs_pix2sky(pixels, 1)
            #sky = self.result['WCS'].toworld(pixels)

            self.slits[key]['coordinates'] = sky

            #record x and y in the slit frame
            self.slits[key]['coordinatesXY'] = pixels
            self.slits[key]['coordinatesX'] = np.ones(value['pixels'])
            self.slits[key]['coordinatesY'] = np.arange(value['pixels']) + 1

            #RA and DEC of the centre of the slit
            centre = np.array([[mean, (ymax + ymin) / 2.], ])
            sky = self.result['WCS'].wcs_pix2sky(centre, 1)
            self.slits[key]['RA'] = sky[0][0]
            self.slits[key]['DEC'] = sky[0][1]

            if self.debug:
                print self.slits[key]['RA'], self.slits[key]['DEC']


    def _writeDS9region(self):
        """
        Writes a ds9 region file. The region file contains small boxes for each slit pixel.
        This can be used to inspect that the slitmask RAs and DECs are sensible.
        """
        fh = open('slitsFittedPositions.reg', 'w')
        fh.write('#File written by findSlitmaskPosition.py on %s\n'\
        % datetime.datetime.isoformat(datetime.datetime.now()))
        fh.write('global color=green width=1\n')
        for slit, value in self.slits.items():
            for RA, DEC in value['coordinates']:
                fh.write('fk5; point %f %f # point=box 3\n' % (RA, DEC))

        fh.close()


    def _writeOutputCoordinates(self):
        """
        Outputs coordinates for each pixel.
        Pickles all this information to a file named coordinates.pk for further processing.
        The pickled filename has been hardcoded.
        """
        tmpdic = {}

        for slit, value in self.slits.items():
            list = []

            fh = open('%s_coordinates.txt' % slit, 'w')
            fh.write('#File written by findSlitmaskPosition.py on %s\n'\
            % datetime.datetime.isoformat(datetime.datetime.now()))
            fh.write('#x\ty\tx2\ty2\tRA\tDEC\n')
            for tmp1, x, y, tmp2 in zip(value['coordinates'],
                                        value['coordinatesX'],
                                        value['coordinatesY'],
                                        value['coordinatesXY']):
                fh.write('%i %i %f %f %f %f \n' % (x, y, tmp2[0], tmp2[1], tmp1[0], tmp1[1]))
                list.append([x, y, tmp2[0], tmp2[1], tmp1[0], tmp1[1]])

            tmpdic[slit] = list

            fh.close()

        write.cPickleDumpDictionary(tmpdic, 'coordinates.pk')


    def _makeFinalFITS(self):
        """
        Combines the tree separate FITS files to a single file where each slice is a separate header.
        Updates the header to contain RA and DEC information so that the mapping between pixels
        and WCS can be derived from the header information.
        """
        ext = 0
        output = 'final.fits'
        if os.path.isfile(output):
            os.remove(output)

        #make a new FITS file
        ofd = pf.HDUList(pf.PrimaryHDU())

        for slit, value in self.slits.items():
            #old data
            fh = pf.open(value['file'])
            data = fh[ext].data
            hdr = fh[ext].header

            #new image HDU
            hdu = pf.ImageHDU(data=data, header=hdr)

            #update header
            hdu.header.update('SNAME', value['name'], 'Name of the slit')
            hdu.header.update('RA2', value['RA'], 'Fitted RA at the centre of the slit in degrees')
            hdu.header.update('DEC2', value['DEC'], 'Fitted DEC at the centre of the slit in degrees')
            hdu.header.update('PSANGLE2', self.result['posangle'], 'Fitted position angle')
            hdu.header.update('PSCALE', self.sky['platescaleSpectra'] * value['binning'],
                              'plate scale in arcsec per pixel')
            hdu.header.add_history('Original File: %s' % value['file'])
            hdu.header.add_history('Updated: %s' % datetime.datetime.isoformat(datetime.datetime.now()))
            #hdu.verify('fix')

            ofd.append(hdu)

        #write the actual file
        ofd.writeto(output, output_verify='ignore')


    def _pickleVars(self):
        """
        This simple method pickles all important variables.
        Mainly useful for debugging when trying to figure out
        what went wrong. By default this method is not called
        as it is quite slow to pickle all this information and
        moreover it is not usually needed.
        """
        if self.debug:
            tmp1 = self.result.copy()
            tmp2 = self.direct.copy()
            del tmp1['WCS']
            del tmp2['WCS']
            write.cPickleDumpDictionary(tmp1, 'results.pk')
            write.cPickleDumpDictionary(self.slits, 'slits.pk')
            write.cPickleDumpDictionary(self.fitting, 'fitting.pk')
            write.cPickleDumpDictionary(tmp2, 'direct.pk')
            del tmp1
            del tmp2
        else:
            tmp1 = self.result.copy()
            del tmp1['WCS']
            write.cPickleDumpDictionary(tmp1, 'results.pk')
            write.cPickleDumpDictionary(self.slits, 'slits.pk')
            write.cPickleDumpDictionary(self.fitting, 'fitting.pk')
            del tmp1


    def run(self):
        """
        Driver function, which runs all the steps.

        Note that by default the last step should not be performed
        because it is time consuming and useful only for debugging
        purposes.
        """
        self._processSlitfiles()
        self._processDirectImage()
        self._calculatePosition()
        self._generateSlitMask()
        self._plotGalaxy()
        self._plotInitialSlitPositions()
        self._fitSlitsToDirectImage()
        self._plotModelProfile()
        self._calculateSkyCoords()
        self._plotMinimalization()
        self._plotFinalSlitPositions()
        self._outputMinima()
        self._writeDS9region()
        self._writeOutputCoordinates()
        self._makeFinalFITS()
        #self._pickleVars()


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
        find = FindSlitmaskPosition(opts.configfile, opts.debug)
    else:
        find = FindSlitmaskPosition(opts.configfile, opts.debug, opts.section)

    find.run()
