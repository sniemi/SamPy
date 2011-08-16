"""
Class to fit spectroscopic observations to a direct image.
The class has been designed for image slicer data where at
the moment three spectra are recorded simultaneously.

:requires: SamPy
:requires: PyFITS
:requires: NumPy
:requires: matplotlib
:requires: SciPy
:requires: astLib
:requires: pywcs (this could also be replated with Kapteyn)
:requires: Kapteyn Python package

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1

:todo:
 1. Download SDSS image based on the RA and DEC of the spectrum
 2. supersample the SDSS image, preserve WCS information [DONE]
 3. develop a fitting routine that is not pixel based so that subpixel shifts can happen
 4. add another correlation based minimalization and compare to chi**2
 5. write the derived RA and DEC information to the spectra FITS header
 6. append the derived RA and DEC and some other information to sqlite db
 7. remove some of the dependences
 8. one could cut a smaller area from the supersampled image to which the fit is done

"""
import sys
import ConfigParser
from optparse import OptionParser
import matplotlib
import pywcs
import pyfits as PF
import numpy as np
from astLib import astCoords
import scipy.stats as stats
import scipy.ndimage.interpolation as interpolation
from kapteyn import wcs, positions, maputils
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from matplotlib import cm
import SamPy.smnIO.write as write
import SamPy.smnIO.read
import SamPy.image.manipulation as m
import SamPy.fits.modify as modify
import SamPy.astronomy.fluxes as flux


class FindSlitmaskPosition():
    """
    This class can be used to find slit positions in a direct image.
    It fits the slits separately to recover their sky positions.
    """

    def __init__(self, configfile, debug, section='DEFAULT'):
        """
        Constructor
        """
        self.slits = {}
        self.sky = {}
        self.direct = {}
        self.fitting = {}
        self.result = {}

        self.configfile = configfile
        self.section = section
        self.debug = debug

        self._readConfigs()
        self._processConfigs()
        self._processSlitfiles()
        self._processDirectImage()


    def _readConfigs(self):
        """
        Reads the config file information using configParser.
        """
        self.config = ConfigParser.RawConfigParser()
        self.config.readfp(open(self.configfile))


    def _generateSlitProfile(self, spectrum, hdr):
        """
        :todo: this is just a dummy now, in the future this should convolve
               the given 2D spectrum with a system throughput curve
        """
        #read the filter information
        filter = np.loadtxt(self.direct['filterfile'])
        wave = filter[:,0]
        thr = filter[:,0]
        #normalize
        if np.max(thr) > 1:
            thr /= np.max(thr)

        #get wave info, note one could use WCS for this
        crval = hdr['CRAVAL1']
        crpix = hdr['CRPIX1']

        #go through the spectrum line by line
        out = []
        for i, line in enumerate(spectrum):
            wave = 
            res = flux.convolveSpectrum(wave, flux, wave, throughput)
            out.append(res['flux'])

        return np.asarray(out)
    


    def _processSlitfiles(self):
        """
        Reads in the slit and direct image FITS files.
        """
        #load images
        for slit in self.slits:
            fh = PF.open(self.slits[slit]['file'], ignore_missing_end=True)
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
         * 1. supersamples the original image by a given factor
         * 2. rotates the image by a -POSANGLE
         * 3. gets the plate scale from the rotated header

        :param: ext, FITS extension
        :param: factor, the supersampling factor
        """
        #load images
        fh = PF.open(self.dirfile)
        self.direct['originalHeader0'] = fh[ext].header
        img = fh[ext].data
        fh.close()
        self.direct['originalImage'] = img

        #super sample
        shape = img.shape
        xnew = int(shape[1] * self.direct['factor'])
        ynew = int(shape[0] * self.direct['factor'])
        imgS, hdrS = modify.hrebin(self.dirfile, xnew, ynew)
        self.direct['xnew'] = xnew
        self.direct['ynew'] = ynew
        self.direct['supersampledImage'] = imgS
        self.direct['supersampledHeader'] = hdrS
        self.direct['supersampledFile'] = 'rebinned.fits'

        #make the rotation to the supersampled image
        self.direct['rotation'] = self.slits['mid']['POSANGLE']
        imgR, hdrR = modify.hrot('rebinned.fits', self.direct['rotation'], xc=None, yc=None)
        self.direct['rotatedImage'] = imgR
        self.direct['rotatedHeader'] = hdrR
        self.direct['rotatedFile'] = 'rotated.fits'

        #WCS info
        self.direct['WCS'] = pywcs.WCS(hdrR)

        #get the plate scale from the header
        self.direct['platescale'] = hdrS['BSCALE']

        if self.debug:
            print '\ndirect:'
            print self.direct


    def _processConfigs(self):
        """
        Process configuration information and produce a dictionary
        describing slits.

        :todo: replace platescale d with header keyword BSCALE

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
        factor = self.config.getfloat(self.section, 'supersample')
        names = list(self.config.get(self.section, 'names').strip().split(','))
        names = [name.strip() for name in names]
        filtercurve = self.config.get(self.section, 'throughputfile')
        postageTolerance = self.config.getfloat(self.section, 'postageTolerance')

        for f, n, w, h, t in zip(self.spectra, names, widths, heights, thrs):
            self.slits[n] = {'widthSky': w,
                             #'widthPixels': w / platescaleS / binning,
                             'heightSky': h,
                             #'heightPixels': h / platescaleS / binning,
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

        #fitting related
        self.fitting['xrange'] = self.config.getint(self.section, 'xrange')
        self.fitting['xstep'] = self.config.getint(self.section, 'xstep')
        self.fitting['yrange'] = self.config.getint(self.section, 'yrange')
        self.fitting['ystep'] = self.config.getint(self.section, 'ystep')
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
        This method can be used to calculate the WCS values.\\
        """
        #get RA and DEC from the header
        ra = self.slits['mid']['header0']['RA']
        dec = self.slits['mid']['header0']['DEC']
        ra = astCoords.hms2decimal(ra, ':')
        dec = astCoords.dms2decimal(dec, ':')
        pix = self.direct['WCS'].wcs_sky2pix(np.array([[ra, dec],]), 1)
        self.direct['xposition'] = int(pix[0,0])
        self.direct['yposition'] = int(pix[0,1])
        self.result['RAinit'] = ra
        self.result['DECinit'] = dec

        if self.debug:
            print self.direct['xposition'], self.direct['yposition']
            

    def _plotGalaxy(self):
        """
        Very simple script to plot an image of the galaxy

        :todo: remove the hardcoded limits for the plots
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
        units = r'ADUs'
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
        Very simple script to plot an image of the galaxy
        """
        tol = np.floor(self.direct['postageTolerance'] / self.direct['platescale']) # pixels
        xp = self.direct['xposition']
        yp = self.direct['yposition']

        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        ax.imshow(np.log10(self.direct['rotatedImage']), origin='lower')

        for slit in self.slits.values():
            patch = patches.Rectangle(slit['xy'],
                                      slit['xmax']-slit['xmin'],
                                      slit['ymax']-slit['ymin'],
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
        Very simple script to plot an image of the galaxy
        """
        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        ax.imshow(np.log10(interpolation.rotate(self.direct['rotatedImage'], self.result['rotation'], reshape=False)),
                  origin='lower')

        #slits
        for slit in self.slits.values():
            patch = patches.Rectangle((slit['xy'][0] + self.result['x'],
                                       slit['xy'][1] + self.result['y']),
                                       slit['xmax']-slit['xmin'],
                                       slit['ymax']-slit['ymin'],
                                       fill=False)
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

        :todo: remove the hard coded if statements
        :todo: make sure that the signs in front of xmod and ymod are right!
        """
        #calculate the x and y offsets between the slits on the sky in the direct image frame
        ymod = int(np.round(self.sky['offseta'] / self.direct['platescale']))
        xmod = int(np.round(self.sky['offsetb'] / self.direct['platescale']))
        self.direct['yshiftSky'] = ymod
        self.direct['xshiftSky'] = xmod

        for slit in self.slits:
            #calculate the positions in the frame of the direct image
            wd = np.floor(self.slits[slit]['widthSky'] / self.direct['platescale'] / 2.)
            hd = np.floor(self.slits[slit]['heightSky'] / self.direct['platescale'] / 2.)

            if slit == 'mid':
                self.slits[slit]['xmin'] = self.direct['xposition'] - wd
                self.slits[slit]['xmax'] = self.direct['xposition'] + wd
                self.slits[slit]['ymin'] = self.direct['yposition'] - hd
                self.slits[slit]['ymax'] = self.direct['yposition'] + hd
            elif slit == 'up':
                self.slits[slit]['xmin'] = self.direct['xposition'] - wd + xmod
                self.slits[slit]['xmax'] = self.direct['xposition'] + wd + xmod
                self.slits[slit]['ymin'] = self.direct['yposition'] - hd + ymod
                self.slits[slit]['ymax'] = self.direct['yposition'] + hd + ymod
            elif slit == 'low':
                self.slits[slit]['xmin'] = self.direct['xposition'] - wd - xmod
                self.slits[slit]['xmax'] = self.direct['xposition'] + wd - xmod
                self.slits[slit]['ymin'] = self.direct['yposition'] - hd - ymod
                self.slits[slit]['ymax'] = self.direct['yposition'] + hd - ymod

            self.slits[slit]['xy'] = (self.slits[slit]['xmin'], self.slits[slit]['ymin'])
            self.slits[slit]['height'] = self.slits[slit]['ymax'] - self.slits[slit]['ymin']
            self.slits[slit]['width'] = self.slits[slit]['xmax'] - self.slits[slit]['xmin']


    def _fitSlitsToDirectImage(self):
        """
        Fits slits to a direct image to recover their position an orientation.

        By default the counts are not normalized to a peak count, but this can
        be controlled using the optional keyword normalize.

        :note: this is a very slow algorithm because of the insanely many nested
               for loops...

        :todo: maybe change the rotaion method??

        :rtype: dictionary
        """
        #generates a model array from the slit values, takes into account potential
        #throughput of a slit
        model = np.array([])
        for vals in self.slits.values():
            #must rebin/interpolate to the right scale
            new = m.frebin(vals['profile'], int(vals['height']))
            model = np.append(model, new)
            self.fitting[vals['name']] = new

        if self.normalize:
            model /= np.max(model)

        #mask out negative values
        msk = model > 0.0
        self.fitting['model'] = model[msk]
        self.fitting['mask'] = msk

        #model basics
        mean = np.mean(self.fitting['model'])
        sig = np.sqrt(np.sum((self.fitting['model'] - mean)**2))
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

        #xrange to cover
        xran = range(-self.fitting['xrange'], self.fitting['xrange'], self.fitting['xstep'])
        yran = range(-self.fitting['yrange'], self.fitting['yrange'], self.fitting['ystep'])

        out = []
        chmin = 1e40
        corrmin = -1e10
        cm = 1e30
        dir = model * 0.0 - 1e4

        #loop over a range of rotations, x and y positions around the nominal position and record x, y and chisquare
        for r in rotations:
            if self.rotation:
                if r != 0.0:
                    d = interpolation.rotate(origimage, r, reshape=False)
                else:
                    d = origimage.copy()
            else:
                d = self.direct['rotatedImage'].copy()

            if self.normalize:
                d /= np.max(d)
                d *= 3.0

            for x in xran:
                for y in yran:
                    #all slits
                    dirdata = np.array([])
                    for s in self.slits.values():
                        #direct image data
                        dirdat = d[s['ymin'] + y:s['ymax'] + y, \
                                   s['xmin'] + x:s['xmax'] + x]
                        #sum the counts inside the slit
                        dirdat = np.sum(dirdat, axis=1)
                        dirdata = np.append(dirdata, dirdat.ravel())

                    #remove the masked pixels
                    dirdata = dirdata[self.fitting['mask']]

                    #chi**2, p-value
                    chisq = stats.chisquare(dirdata, self.fitting['model'])

                    #correlation coeff
                    mean = np.mean(dirdata)
                    sig = np.sqrt(np.sum((dirdata - mean)**2))
                    diff = dirdata - mean
                    corr = np.sum(self.fitting['diff'] * diff) / self.fitting['sig'] / sig

                    #save info
                    tmp = [r, x, y, chisq[0], chisq[0] / s['pixels'], chisq[1], corr]
                    out.append(tmp)

                    #save the dirdata of the minimum chisqr
                    if chisq[0] < cm:
                        cm = chisq[0]
                        chmin = dirdat
                        minpos = tmp
                        dir = dirdata

                    if corr > corrmin:
                        corrmin = corr
                        minpos2 = tmp

                    if self.debug:
                        print r, x, y, chisq[0] / s['pixels'], chisq[1], corr

        #calculate the centres
        xc = self.direct['xposition'] + minpos[1]
        yc = self.direct['yposition'] + minpos[2]
        #save results
        self.result['outputs'] = out
        self.result['chiMinData'] = chmin
        self.result['minimaPosition'] = minpos
        self.result['rotation'] = minpos[0]
        self.result['x'] = minpos[1]
        self.result['y'] = minpos[2]
        self.result['bestfit'] = dir
        self.result['xcenter'] = xc
        self.result['ycenter'] = yc
        self.result['pvalue'] = minpos[5]

        if self.debug:
            print minpos
            print minpos2


    def _plotModelProfile(self):
        """
        Plots model profile
        """
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for slit in self.slits:
            ax.plot(self.fitting[slit], label=slit)
        plt.xlim(0, ax.get_xlim()[1])
        plt.ylim(0, ax.get_ylim()[1])
        plt.legend(shadow=True, fancybox=True, loc='best')
        plt.savefig('ModelProfile.pdf')
        plt.close()


    def _plotMinimalization(self):
        """
        Generates a two dimensional map of the minimalization
        for each slit separately.

        :note: When fitting rotation all rotations are plotted on
               top, so the plot may not be that useful.

        """
        #minima profiles
        fig = plt.figure(1)
        ax = fig.add_subplot(111)
        ax.plot(self.fitting['model'], label = 'Model (Slit Profiles)' )
        ax.plot(self.result['bestfit'], label = 'Best Fit')
        plt.legend(shadow=True, fancybox=True, loc='best')
        plt.xlim(0, ax.get_xlim()[1])
        plt.ylim(0, ax.get_ylim()[1])
        plt.savefig('MinimaProfile.pdf')
        plt.close()

        #minima map
        data = self.result['outputs']
        d = np.asarray([[x[1], x[2], x[4]] for x in data])
        plt.scatter(d[:, 0],
                    d[:, 1],
                    c=1. / d[:, 2],
                    s=20,
                    cmap=cm.get_cmap('jet'),
                    edgecolor='none',
                    alpha=0.2)
        plt.xlim(-self.fitting['xrange'], self.fitting['xrange'])
        plt.ylim(-self.fitting['yrange'], self.fitting['yrange'])
        plt.xlabel('X [pixels]')
        plt.ylabel('Y [pixels]')
        plt.savefig('MinimaMap.png')
        plt.close()


    def _outputMinima(self):
        """
        Outputs the results to a file and also the screen if  debug = True.
        """
        str = '{0:.2f}\t{1:.0f}\t{2:.0f}\t{3:.0f}\t{4:.0f}\t{5:.2f}\t\t{6:.2f}\n'.format(self.result['rotation'],
                                                                                         self.result['xcenter'],
                                                                                         self.result['ycenter'],
                                                                                         self.result['x'],
                                                                                         self.result['y'],
                                                                                         self.result['minimaPosition'][3],
                                                                                         self.result['minimaPosition'][4])

        fh1 = open('min.txt', 'a')
        fh1.write(str)
        fh1.close()

        if self.debug:
            print '\n\nr \t x \t y \txoff \tyoff \tchi**2   reduced chi**2'
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
        Generates a footprint as well and outputs a DS9 region file.
        """
        img, hdr = modify.hrot('rotated.fits', self.result['rotation'],
                               xc=None, yc=None, output='fittedRotated.fits')
        self.result['WCS'] = pywcs.WCS(hdr)
        #self.result['FinalImage'] = img
        self.result['FinalHeader'] = hdr

        #calculate the RA and DEC of the centre of the centre slit
        pixels = np.array([[self.result['xcenter'], self.result['ycenter']], ], np.float_)
        sky = self.result['WCS'].wcs_pix2sky(pixels, 1)
        self.result['RA'] = sky[0][0]
        self.result['DEC'] = sky[0][1]


    def _pickleVars(self):
        """
        This simple method pickles all important variables
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
        Driver function, runs all required steps.
        """
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
        self._pickleVars()


def processArgs(printHelp=False):
    """
    Processes command line arguments
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