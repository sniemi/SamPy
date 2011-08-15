"""
Class to fit spectroscopic observations to a direct image.
The class has been designed for image slicer data where at
the moment three spectra are recorded simultaneously.

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
 2. supersample the SDSS image, preserve WCS information
 3. develop a fitting rountine that is not pixel based so that subpixel shifts can happen
 4. add another correlation based minimalization and compare to chi**2
 5. write the derived RA and DEC information to the spectra FITS header
 6. append the derived RA and DEC and some other information to sqlite db
 7. remove some of the dependences

"""
import sys
import ConfigParser
from optparse import OptionParser
import matplotlib
import pywcs
import pyfits as PF
import numpy as np
from astLib import astCoords
import scipy.ndimage.interpolation as interpolation
from kapteyn import wcs, positions, maputils
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from matplotlib import cm
import SamPy.smnIO.write as write
import SamPy.smnIO.read
import SamPy.image.manipulation as m


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

        self.configfile = configfile
        self.section = section
        self.debug = debug

        self._readConfigs()
        self._processConfigs()
        self._readFITSfiles()


    def _readConfigs(self):
        """
        Reads the config file information using configParser.
        """
        self.config = ConfigParser.RawConfigParser()
        self.config.readfp(open(self.configfile))


    def _generateSlitProfile(self, spectrum):
        """
        :todo: this is just a dummy now, in the future this should convolve
               the given 2D spectrum with a system throughput curve
        """
        return np.sum(spectrum, axis=1)


    def _readFITSfiles(self):
        """
        Reads in the slit and direct image FITS files.
        """
        #load images
        fh = PF.open(self.dirfile, ignore_missing_end=True)
        self.direct['header0'] = fh[0].header
        img = fh[0].data
        fh.close()
        if img.shape[0] == 1:
            img = img[0]
        self.direct['originalImage'] = img
        self.direct['wcs'] = pywcs.WCS(self.direct['header0'])

        for slit in self.slits:
            fh = PF.open(self.slits[slit]['file'], ignore_missing_end=True)
            self.slits[slit]['header0'] = fh[0].header
            slitimage = fh[0].data
            fh.close()
            if slitimage.shape[0] == 1:
                slitimage = slitimage[0]
            self.slits[slit]['image'] = slitimage
            self.slits[slit]['profile'] = self._generateSlitProfile(slitimage)
            self.slits[slit]['pixels'] = len(self.slits[slit]['profile'])

        #note the minus sign in rotation!
        self.direct['rotation'] = - self.slits['mid']['header0']['POSANGLE']
        self.direct['image'] = interpolation.rotate(img.copy(), self.direct['rotation'])

        if self.debug:
            print '\ndirect:'
            print self.direct
            print '\nslits:'
            print self.slits
            print '\nsky:'
            print self.sky
            print '\nfitting:'
            print self.fitting


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
        platescaleD = self.config.getfloat(self.section, 'platescaleDirect')
        names = list(self.config.get(self.section, 'names').strip().split(','))
        names = [name.strip() for name in names]
        filtercurve = self.config.get(self.section, 'throughputfile')
        postageTolerance = self.config.getfloat(self.section, 'postageTolerance')

        for f, n, w, h, t in zip(self.spectra, names, widths, heights, thrs):
            self.slits[n] = {'widthSky': w,
                             'widthPixels': w / platescaleS / binning,
                             'heightSky': h,
                             'heightPixels': h / platescaleS / binning,
                             'throughput': 1. / t,
                             'binning': binning,
                             'file': f}

        #sky related
        self.sky['offseta'] = offseta
        self.sky['offsetb'] = offsetb
        self.sky['platescaleSpectra'] = platescaleS
        self.sky['platescaleDirect'] = platescaleD

        #direct image information
        self.direct['platescale'] = platescaleD
        self.direct['filterfile'] = filtercurve
        self.direct['postageTolerance'] = postageTolerance

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


    def _calculatePosition(self):
        """
        This method can be used to calculate the WCS values.
        """
        #get RA and DEC from the header
        ra = self.slits['mid']['header0']['RA']
        dec = self.slits['mid']['header0']['DEC']
        ra = astCoords.hms2decimal(ra, ':')
        dec = astCoords.dms2decimal(dec, ':')
        self.direct['wcs'].rotateCD(self.direct['rotation'])
        pix = self.direct['wcs'].wcs_sky2pix(np.array([[ra, dec],]), 1)
        self.direct['xposition'] = 825 #int(pix[0,0])
        self.direct['yposition'] = 1511 #int(pix[0,1])
        print ra, dec
        print pix
        print self.direct['xposition'], self.direct['yposition']

        #using kapteyn
        #pr = wcs.Projection(self.direct['header0'])
        #w, p, u, e = positions.str2pos('%i, %i' % (self.direct['xposition'], self.direct['yposition'], pr)
        #if e == '':
        #    print "pixels:", p
        #    print "world coordinates:", w, u

        #using pywcs
        pixels = np.array([[self.direct['xposition'], self.direct['yposition']], ], np.float_)
        sky = self.direct['wcs'].wcs_pix2sky(pixels, 1)
        print sky


    def _plotGalaxy(self):
        """
        Very simple script to plot an image of the galaxy
        """
        tol = np.floor(self.direct['postageTolerance'] / self.direct['platescale'])
        xp = 956
        yp = 1212
        #rot = self.direct['rotation']

        #make a figure
        fig = plt.figure(1)
        frame = fig.add_subplot(111)
        #frame.set_title(self.dirfile)

        #from Kapteyn
        f = maputils.FITSimage(self.dirfile)
        annim = f.Annotatedimage(frame, cmap='Spectral', clipmin=0.01, clipmax=12)
        annim.Image(alpha=0.9)
        grat = annim.Graticule()
        grat.setp_gratline(wcsaxis=0, linestyle=':')
        grat.setp_gratline(wcsaxis=1, linestyle=':')
        annim.plot()

        plt.savefig('Galaxy.pdf')
        plt.close()

        #zoomed in version with the spectra
        fig = plt.figure(figsize=(15, 15))
        frame1 = fig.add_subplot(4, 1, 1)

        #orig = maputils.FITSimage(self.dirfile)
        f = maputils.FITSimage(self.dirfile)
        #f = orig.reproject_to(rotation=rot)
        f.set_limits(pxlim=(xp - tol, xp + tol), pylim=(yp - tol, yp + tol))
        annim = f.Annotatedimage(frame1, clipmin=0.01, clipmax=10)
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
        frame = fig.add_subplot(111)
        frame.imshow(np.log10(self.direct['image']), origin='lower')
        for slit in self.slits.values():
            patch = patches.Rectangle(slit['xy'],
                                      slit['xmax']-slit['xmin'],
                                      slit['ymax']-slit['ymin'],
                                      fill=False)
            frame.add_patch(patch)
        plt.savefig('InitialMaskPosition.pdf')

        #zoomed in version
        frame.set_xlim(xp - tol, xp + tol)
        frame.set_ylim(yp - tol, yp + tol)
        plt.savefig('InitialMaskPositionZoomed.pdf')
        plt.close()


    def _plotFinalSlitPositions(self):
        """
        Very simple script to plot an image of the galaxy
        """
        fig = plt.figure(1)
        frame = fig.add_subplot(111)
        frame.imshow(np.log10(self.direct['image']), origin='lower')

        #slits
        for slit in self.slits.values():
            patch = patches.Rectangle((slit['xy'][0] + self.result['x'],
                                       slit['xy'][1] + self.result['y']),
                                       slit['xmax']-slit['xmin'],
                                       slit['ymax']-slit['ymin'],
                                       fill=False)
            t2 = matplotlib.transforms.Affine2D().rotate_deg(self.result['rotation']) + frame.transData
            patch.set_transform(t2)
            frame.add_patch(patch)
            
        plt.savefig('FinalMaskPosition.pdf')

        #zoomed in version
        tol = np.floor(self.direct['postageTolerance'] / self.direct['platescale']) # pixels
        xp = self.direct['xposition'] + self.result['x']
        yp = self.direct['yposition'] + self.result['y']
        frame.set_xlim(xp - tol, xp + tol)
        frame.set_ylim(yp - tol, yp + tol)
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
                self.slits[slit]['xmin'] = self.direct['xposition'] - wd - xmod
                self.slits[slit]['xmax'] = self.direct['xposition'] + wd - xmod
                self.slits[slit]['ymin'] = self.direct['yposition'] - hd + ymod
                self.slits[slit]['ymax'] = self.direct['yposition'] + hd + ymod
            elif slit == 'low':
                self.slits[slit]['xmin'] = self.direct['xposition'] - wd + xmod
                self.slits[slit]['xmax'] = self.direct['xposition'] + wd + xmod
                self.slits[slit]['ymin'] = self.direct['yposition'] - hd - ymod
                self.slits[slit]['ymax'] = self.direct['yposition'] + hd - ymod

            self.slits[slit]['xy'] = (self.slits[slit]['xmin'], self.slits[slit]['ymin'])


    def _chiSquare(self, model, obs):
        """
        Simple chi**2 calculation
        """
        r = np.sum((obs - model) ** 2 / model)
        return r


    def _fitSlitsToDirectImage(self):
        """
        Fits slits to a direct image to recover their position an orientation.

        By default the counts are not normalized to a peak count, but this can
        be controlled using the optional keyword normalize.

        :note: this is a very slow algorithm because of the insanely many nested
               for loops...

        :rtype: dictionary
        """
        #generates a model array from the slit values, takes into account potential
        #throughput of a slit
        model = np.array([])
        for vals in self.slits.values():
            #must interpolate to the right scale
            ypixs = np.arange(vals['ymax'] - vals['ymin'])
            newprof = np.interp(ypixs, np.arange(len(vals['profile'])), vals['profile'])
            m = newprof * vals['throughput']
            #mask out negative values
            model = np.append(model, m)
        if self.normalize:
            model /= np.max(model)

        msk = model > 0.0
        self.fitting['model'] = model[msk]
        self.fitting['mask'] = msk

        #generate rotations
        if self.rotation:
            rotations = np.arange(-self.fitting['rotation'], self.fitting['rotation'], self.fitting['rotstep'])
            rotations[(rotations < 1e-5) & (rotations > -1e-5)] = 0.0
            #make a copy of the direct image
            origimage = self.direct['image'].copy()
        else:
            rotations = [0, ]

        #xrange to cover
        xran = range(-self.fitting['xrange'], self.fitting['xrange'], self.fitting['xstep'])
        yran = range(-self.fitting['yrange'], self.fitting['yrange'], self.fitting['ystep'])

        out = []
        chmin = -1e40
        cm = 1e30
        minpos = -1e40
        dir = model * 0.0 - 1e4

        #loop over a range of rotations, x and y positions around the nominal position and record x, y and chisquare
        for r in rotations:
            if self.rotation:
                if r != 0.0:
                    d = interpolation.rotate(origimage, r, reshape=False)
                else:
                    d = origimage.copy()
            else:
                d = self.direct['image'].copy()

            if self.normalize:
                d /= np.max(d)

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
                        #ravel
                        dirdata = np.append(dirdata, dirdat.ravel())

                    #remove the masked pixels
                    dirdata = dirdata[self.fitting['mask']]

                    #if self.normalize:
                    #    dirdata /= np.max(dirdata)

                    chisq = self._chiSquare(self.fitting['model'], dirdata)

                    tmp = [r, x, y, chisq, chisq / s['pixels']]
                    out.append(tmp)

                    #save the dirdata of the minimum chisqr
                    if chisq < cm:
                        chmin = dirdat
                        cm = chisq
                        minpos = tmp
                        dir = dirdata

                    if self.debug:
                        print r, x, y, chisq / s['pixels']

        #results dictionary
        r = {'outputs': out,
             'chiMinData': chmin,
             'minimaPosition': minpos,
             'rotation' : minpos[0],
             'x' : minpos[1],
             'y' : minpos[2],
             'bestfit': dir}
        self.result = r

        if self.debug:
            print '\nMinima positions:'
            print self.result['minimaPosition']


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
        ax.plot(self.fitting['model'], label = 'Model for Fitting' )
        ax.plot(self.result['bestfit'], label = 'Best fit')
        plt.legend(shadow=True, fancybox=True)
        plt.savefig('MinimaProfile.pdf')
        plt.close()

        #minima map
        data = self.result['outputs']
        d = np.asarray([[x[1], x[2], x[4]] for x in data])
        plt.scatter(d[:, 0],
                    d[:, 1],
                    c=1. / np.log10(d[:, 2]),
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
        xpos = self.direct['xposition'] + self.result['x']
        ypos = self.direct['yposition'] + self.result['y']
        r = self.result['rotation']

        str = '{2:.2f}\t{3:.0f}\t{4:.0f}\t{5:.0f}\t{6:.0f}\t{7:>s}\n'.format(r,
                                                                             xpos,
                                                                             ypos,
                                                                             self.result['x'],
                                                                             self.result['y'],
                                                                             self.result['minimaPosition'][3])

        fh1 = open('min.txt', 'a')
        fh1.write(str)
        fh1.close()

        if self.debug:
            print '\n\nr \t x \t y \t xoff \t yoff \t chi**2    reduced chi**2'
            print str



    def _pickleVars(self):
        """
        This simple method pickles all important variables
        """
        tmp = self.direct.copy()
        del tmp['wcs']
        write.cPickleDumpDictionary(self.result, 'results.pk')
        write.cPickleDumpDictionary(self.slits, 'slits.pk')
        write.cPickleDumpDictionary(self.fitting, 'fitting.pk')
        write.cPickleDumpDictionary(tmp, 'direct.pk')
        del tmp


    def run(self):
        """
        Driver function, runs all required steps.
        """
        self._calculatePosition()
        self._generateSlitMask()
        self._plotGalaxy()
        self._plotInitialSlitPositions()
        self._fitSlitsToDirectImage()
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