'''
Fits slit positions to a direct image to find sky positions and a rotation angle.
Fits all three slits separately to recover their position on the sky.
All Inputs should be given in a configuration file, only command line argument
needed is the name of the configuration file.

:requires: PyFITS
:requires: NumPy
:requires: matplotlib
:requires: SciPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.2
'''
import matplotlib
import sys, os
import ConfigParser
from optparse import OptionParser
import pyfits as PF
import pylab as P
import numpy as np
import matplotlib.patches as patches
from matplotlib import cm
import scipy.ndimage.interpolation as interpolation
#from SamPy
import SamPy.smnIO.write as write
import SamPy.smnIO.read
import SamPy.image.manipulation as m


class FindSlitPositionsInDirectImage():
    '''
    This class can be used to find slit positions in a direct image.
    It fits the slits separately to recover their sky positions.
    '''
    def __init__(self, configfile, debug, section='DEFAULT'):
        '''
        Constructor
        '''
        self.configfile = configfile
        self.section = section
        self.debug = debug

        self._readConfigs()
        self._readFITSfiles()
        self._processConfigs()


    def _readConfigs(self):
        '''
        Reads the config file information using configParser.
        '''
        self.config = ConfigParser.RawConfigParser()
        self.config.readfp(open(self.configfile))

        self.slitfile = self.config.get(self.section, 'slitimage')
        self.dirfile = self.config.get(self.section, 'directimage')


    def _readFITSfiles(self):
        '''
        Reads in the slit and direct image FITS files.
        '''
        #load images
        fh = PF.open(self.dirfile, ignore_missing_end=True)
        self.dirImageHDR = fh[0].header
        img = fh[0].data
        fh.close()
        if img.shape[0] == 1:
            img = img[0]
        self.directImage = img

        fh = PF.open(self.slitfile, ignore_missing_end=True)
        self.slitImageHDR = fh[0].header
        slitimage = fh[0].data
        fh.close()
        if slitimage.shape[0] == 1:
            slitimage = slitimage[0]
        self.slitImage = slitimage


    def _processConfigs(self):
        '''
        Process configuration information and produce a dictionary
        describing slits.
        '''
        ltolerance = 10

        xcoords = [int(a) for a in self.config.get(self.section, 'xcoordinates').strip().split(',')]
        ycoords = [int(a) for a in self.config.get(self.section, 'ycoordinates').strip().split(',')]
        widths = [float(a) for a in self.config.get(self.section, 'widths').strip().split(',')]
        heights = [float(a) for a in self.config.get(self.section, 'heights').strip().split(',')]
        thrs = [float(a) for a in self.config.get(self.section, 'throughputs').strip().split(',')]
        offseta = self.config.getfloat(self.section, 'offsetalong')
        offsetb = self.config.getfloat(self.section, 'offsetbetween')
        platescale = self.config.getfloat(self.section, 'platescale')
        names = list(self.config.get(self.section, 'names').strip().split(','))
        names = [name.strip() for name in names]
        
        out = {}
        for n, x, y, w, h, t in zip(names, xcoords, ycoords, widths, heights, thrs):
            n = n.strip()

            wd = w / platescale
            hd = h / platescale

            xmin = int(x)
            xmax = int(np.floor(xmin + wd))
            xmid = int(np.round((2*xmin+wd) / 2.))

            ymin = int(y)
            ymax = int(np.floor(ymin + hd))
            ymid = int(np.round((2*ymin+hd) / 2.))

            #slit image values
            vals = self.slitImage[ymin:ymax + 1, xmin:xmax + 1].copy()
            vals2 = self.slitImage[ymin-ltolerance:ymax + ltolerance + 1, \
                                   xmin-ltolerance:xmax + ltolerance + 1].copy()

            #make the dictionary
            out[n] = {'xmid': xmid, 'ymid': ymid,
                      'skywidth': w, 'skyheight': h,
                      'wd' : wd, 'hd' : hd,
                      'width': xmax-xmin, 'height': ymax-ymin,
                      'xmin': xmin, 'xmax': xmax,
                      'ymin': ymin, 'ymax': ymax,
                      'xy': (xmin, ymin),
                      'shape': vals.shape,
                      'throughput': 1. / t,
                      'values': vals,
                      'valuesLarge' : vals2,
                      'tolerance' : ltolerance,
                      'pixels': len(vals.ravel())}

        self.slits = out

        sky = {}
        sky['offseta'] = offseta
        sky['offsetb'] = offsetb
        sky['platescale'] = platescale
        self.sky = sky

        #fitting related
        fitting = {}
        fitting['xrange'] = self.config.getint(self.section, 'xrange')
        fitting['xstep'] = self.config.getint(self.section, 'xstep')
        fitting['yrange'] = self.config.getint(self.section, 'yrange')
        fitting['ystep'] = self.config.getint(self.section, 'ystep')
        try:
            fitting['rotation'] = self.config.getfloat(self.section, 'rotation')
            self.rotation = True
        except:
            self.rotation = False
        try:
            self.normalize = self.config.getboolean(self.section, 'normalize')
        except:
            self.normalize = False

        fitting['rotstep'] = self.config.getfloat(self.section, 'rotationstep')
        self.fitting = fitting

        if self.debug:
            print '\nslits:'
            print self.slits
            print '\nsky:'
            print self.sky
            print '\nfitting:'
            print self.fitting


    def generateSlitImages(self, output='slits', type='.pdf'):
        '''
        Generates diagnostic plots from slit image.
        '''
        rotText = 40
        #generate a separate image of the slit data of each slit image.
        for slit in self.slits:
            s = self.slits[slit]

            fig = P.figure()
            ax = fig.add_subplot(111)

            #take log10 from the slit data
            tmp = s['values'] * s['throughput']
            tmp[tmp <= 0.0] = 1
            tmp = np.log10(tmp)

            ax.imshow(tmp,
                      origin='lower',
                      interpolation=None)

            #rotate x axis labels
            for tl in ax.get_xticklabels():
                tl.set_rotation(rotText)

            P.savefig(output + slit + type)
            P.close()

        #make a single slit image
        fig = P.figure()
        for i, slit in enumerate(self.slits):
            s = self.slits[slit]
            ax = fig.add_subplot(1, len(self.slits), i + 1)

            #take log10 from the slit data
            tmp = s['values'] * s['throughput']
            tmp[tmp <= 0.0] = 1
            tmp = np.log10(tmp)

            #take log10 from the slit data
            ax.imshow(tmp,
                      origin='lower', interpolation=None)

            #rotate x axis labels
            for tl in ax.get_xticklabels():
                tl.set_rotation(rotText)

            #annotate
            ax.annotate(slit, xy=(0.5, 1.05),
                        xycoords='axes fraction', ha='center', va='center')

        P.savefig(output + 'All' + type)
        P.close()


    def writeDS9RegionFile(self, output='slits.reg'):
        '''
        Writes a DS9 region file for all the slits.
        Draws a rectangle around each slit.
        '''
        fh = open(output, 'w')
        for slit in self.slits:
            s = self.slits[slit]
            #DS0 box format is x, y, width, height, but x and y are the centre point
            string = 'box %i %i %i %i 0\n' % (s['xmid'],
                                              s['ymid'],
                                              s['width'],
                                              s['height'])
            fh.write(string)
        fh.close()


    def approxSkyPosition(self):
        '''
        Generates an approximated sky position for slits.

        :note: this works only if the slits have the same width
        '''
        yoff = int(np.round(self.sky['offseta'] / self.sky['platescale']))
        xoff = int(np.round(self.sky['offsetb'] / self.sky['platescale']))

        for slit in self.slits:
            if slit == 'up':
                self.slits[slit]['ymidSky'] = self.slits['mid']['ymid'] + yoff
                self.slits[slit]['yminSky'] = self.slits[slit]['ymidSky'] - self.slits[slit]['height']/2
                self.slits[slit]['ymaxSky'] = self.slits[slit]['yminSky'] + self.slits[slit]['height']

                self.slits[slit]['xmidSky'] = self.slits['mid']['xmid'] - xoff
                self.slits[slit]['xminSky'] = self.slits[slit]['xmidSky'] - self.slits[slit]['width']/2
                self.slits[slit]['xmaxSky'] = self.slits[slit]['xminSky'] + self.slits[slit]['width']

            elif slit == 'low':
                self.slits[slit]['ymidSky'] = self.slits['mid']['ymid'] - yoff
                self.slits[slit]['yminSky'] = self.slits[slit]['ymidSky'] - self.slits[slit]['height']/2
                self.slits[slit]['ymaxSky'] = self.slits[slit]['yminSky'] + self.slits[slit]['height']

                self.slits[slit]['xmidSky'] = self.slits['mid']['xmid'] + xoff
                self.slits[slit]['xminSky'] = self.slits[slit]['xmidSky'] - self.slits[slit]['width']/2
                self.slits[slit]['xmaxSky'] = self.slits[slit]['xminSky'] + self.slits[slit]['width']

            else:
                self.slits[slit]['ymidSky'] = self.slits['mid']['ymid']
                self.slits[slit]['yminSky'] = self.slits['mid']['ymin']
                self.slits[slit]['ymaxSky'] = self.slits['mid']['ymax']

                self.slits[slit]['xmidSky'] = self.slits['mid']['xmid']
                self.slits[slit]['xminSky'] = self.slits[slit]['xmidSky'] - self.slits[slit]['width']/2
                self.slits[slit]['xmaxSky'] = self.slits[slit]['xminSky'] + self.slits[slit]['width']

            self.slits[slit]['xySky'] = (self.slits[slit]['xminSky'], self.slits[slit]['yminSky'])

        fh = open('skyApproximated.reg', 'w')
        for s in self.slits.values():
            #DS0 box format is x, y, width, height, but x and y are the centre point
            string = 'box %i %i %i %i 0\n' % (s['xmidSky'],
                                              s['ymidSky'],
                                              s['width'],
                                              s['height'])
            fh.write(string)
        fh.close()


    def _chiSquare(self, model, obs):
        '''
        Simple chi**2 calculation
        '''
        r = np.sum((obs - model) ** 2 / model)
        return r


    def fitSlitsToDirectImage(self, normalize=False):
        '''
        Fits slits to a direct image to recover their position an orientation.

        By default the counts are not normalized to a peak count, but this can
        be controlled using the optional keyword normalize.

        :note: this is a very slow algorithm because of the insanely many nested
               for loops...

        :rtype: dictionary
        '''
        #generates a model array from the slit values, takes into account potential
        #throughput of a slit
        for slit in self.slits:
            s = self.slits[slit]
            model = s['values'].ravel() * s['throughput']
            #mask out negative values
            msk = model > 0.0
            model = model[msk]
            if self.normalize:
                model /= np.max(model)
            self.slits[slit]['model'] = model
            self.slits[slit]['mask'] = msk

        #generate rotations
        if self.rotation:
            rotations = np.arange(-self.fitting['rotation'], self.fitting['rotation'], self.fitting['rotstep'])
            rotations[(rotations < 1e-8) & (rotations > -1e-8)] = 0.0
            #make a copy of the direct image
            origimage = self.directImage.copy()
        else:
            rotations = [0, ]

        out = {}
        chmin = {}
        cm = {}
        minpos = {}
        for slit in self.slits:
            chmin[slit] = -9.99
            cm[slit] = 1e20
            out[slit] = []
            minpos[slit] = -1e10

        #loop over a range of rotations,  x and y positions around the nominal position and record x, y and chisquare
        for r in rotations:
            if self.rotation:
                if r != 0.0:
                    d = interpolation.rotate(origimage, r, reshape=False)
                else:
                    d = origimage.copy()
            else:
                d = self.directImage.copy()
            for x in range(-self.fitting['xrange'], self.fitting['xrange'], self.fitting['xstep']):
                for y in range(-self.fitting['yrange'], self.fitting['yrange'], self.fitting['ystep']):
                    #all slits
                    for slit in self.slits:
                        s = self.slits[slit]
                        #direct image data
                        dirdat = d[s['yminSky'] + y:s['ymaxSky'] + y + 1,
                                   s['xminSky'] + x:s['xmaxSky'] + x + 1]
                        dirdata = dirdat.ravel()

                        #remove the masked pixels
                        dirdata = dirdata[s['mask']]

                        if self.normalize:
                            dirdata /= np.max(dirdata)

                        chisq = self._chiSquare(s['model'], dirdata)

                        tmp = [r, x, y, chisq, chisq / s['pixels'], slit]
                        out[slit].append(tmp)

                        #save the dirdata of the minimum chisqr
                        if chisq < cm[slit]:
                            chmin[slit] = dirdat
                            cm[slit] = chisq
                            minpos[slit] = tmp

                        if self.debug:
                            print r, x, y, chisq / s['pixels'], slit

        #results dictionary
        r = {}
        r['outputs'] = out
        r['chiMinData'] = chmin
        r['minimaPosition'] = minpos
        self.result = r

        if self.debug:
            print '\nMinima positions:'
            print self.result['minimaPosition']


    def fitSlitsToDirectImage2(self):
        '''
        Fits slits to a direct image to recover their position an orientation.

        By default the counts are not normalized to a peak count, but this can
        be controlled using the optional keyword normalize.

        :note: this is a very slow algorithm because of the insanely many nested
               for loops...

        :rtype: dictionary
        '''
        #generates a model array from the slit values, takes into account potential
        #throughput of a slit
        for slit in self.slits:
            s = self.slits[slit]
            model = s['values'].ravel() * s['throughput']
            #mask out negative values
            msk = model > 0.0
            model = model[msk]
            mean = np.mean(model)
            sig = np.sqrt(np.sum((model - mean)**2))
            diff = model - mean
            self.slits[slit]['model'] = model
            self.slits[slit]['mask'] = msk
            self.slits[slit]['sig'] = sig
            self.slits[slit]['diff'] = diff

        #generate rotations
        if self.rotation:
            rotations = np.arange(-self.fitting['rotation'], self.fitting['rotation'], self.fitting['rotstep'])
            rotations[(rotations < 1e-8) & (rotations > -1e-8)] = 0.0
            #make a copy of the direct image
            origimage = self.directImage.copy()
        else:
            rotations = [0, ]

        out = {}
        chmin = {}
        cm = {}
        minpos = {}
        for slit in self.slits:
            chmin[slit] = -9.99
            cm[slit] = 1e20
            out[slit] = []
            minpos[slit] = -1e10

        #loop over a range of rotations,  x and y positions around the nominal position and record x, y and chisquare
        for r in rotations:
            if self.rotation:
                if r != 0.0:
                    d = interpolation.rotate(origimage, r, reshape=False)
                else:
                    d = origimage.copy()
            else:
                d = self.directImage.copy()
            for x in range(-self.fitting['xrange'], self.fitting['xrange'], self.fitting['xstep']):
                for y in range(-self.fitting['yrange'], self.fitting['yrange'], self.fitting['ystep']):
                    #all slits
                    for slit in self.slits:
                        s = self.slits[slit]
                        #direct image data
                        dirdat = d[s['yminSky'] + y:s['ymaxSky'] + y + 1,
                                   s['xminSky'] + x:s['xmaxSky'] + x + 1]
                        dirdata = dirdat.ravel()

                        #remove the masked pixels
                        dirdata = dirdata[s['mask']]

                        mean = np.mean(dirdata)
                        sig = np.sqrt(np.sum((dirdata - mean)**2))
                        diff = template1 - mean
                        
                        corr = np.sum(s['diff'] * diff) / s['sig'] / sig

                        tmp = [r, x, y, 1./corr, 1./corr, slit]
                        out[slit].append(tmp)

                        #save the dirdata of the minimum chisqr
                        if chisq < cm[slit]:
                            chmin[slit] = dirdat
                            cm[slit] = 1./corr
                            minpos[slit] = tmp

                        if self.debug:
                            print r, x, y, 1./corr, slit

        #results dictionary
        r = {}
        r['outputs'] = out
        r['chiMinData'] = chmin
        r['minimaPosition'] = minpos
        self.result = r

        if self.debug:
            print '\nMinima positions:'
            print self.result['minimaPosition']


    def plotMinimalization(self, output='minima', type='.png'):
        '''
        Generates a two dimensional map of the minimalization
        for each slit separately.

        :note: When fitting rotation all rotations are plotted on
               top, so the plot may not be that useful.

        '''
        data = self.result['outputs']
        for slit in data:
            d = np.asarray([[x[1], x[2], x[4]]for x in data[slit]])
            P.figure()
            P.scatter(d[:, 0],
                      d[:, 1],
                      c=1. / np.log10(d[:, 2]),
                      s=30,
                      cmap=cm.get_cmap('jet'),
                      edgecolor='none',
                      alpha=0.2)
            P.xlim(-self.fitting['xrange'], self.fitting['xrange'])
            P.ylim(-self.fitting['yrange'], self.fitting['yrange'])
            P.xlabel('X [pixels]')
            P.ylabel('Y [pixels]')
            P.savefig(output + 'Map' + slit + type)
            P.close()


    def outputMinima(self):
        '''
        Outputs the results to a file and also the screen if  debug = True.
        '''
        if self.debug:
            print '\n\ndirect image    slit image     \t rot' + \
                   '\t x \t y \t xoff \t yoff \t chi**2    reduced chi**2 \t slit'

        fh1 = open('min.txt', 'a')
        fh2 = open('skyFitted.reg', 'w')
        fh3 = open('slitmask.txt', 'w')

        for res in self.result['minimaPosition'].values():
            r = res[0]
            x = res[1]
            y = res[2]
            n = res[5]

            #take into account possible trimming of the direct image
            try:
                xtr = self.dirImageHDR['LTV1']
            except:
                xtr = 0
            try:
                ytr = self.dirImageHDR['LTV2']
            except:
                ytr = 0

            #derive the mid positions in a full frame
            xpos = x + self.slits[n]['xmidSky'] - xtr
            ypos = y + self.slits[n]['ymidSky'] - ytr

            #save the positions to result dictionary
            self.slits[n]['xminFitted'] = x + self.slits[n]['xminSky'] - xtr
            self.slits[n]['xmaxFitted'] = x + self.slits[n]['xmaxSky'] - xtr
            self.slits[n]['yminFitted'] = y + self.slits[n]['yminSky'] - ytr
            self.slits[n]['ymaxFitted'] = y + self.slits[n]['ymaxSky'] - ytr

            #write the file
            fh3.write('slit\t\t= %s\n' % (n))
            fh3.write('rotation\t= %.3f\n' % -r)
            fh3.write('x\t\t= %i\n' % xpos)
            fh3.write('y\t\t= %i\n' % ypos)
            fh3.write('\n')

            tmp = 'box {0:1f} {1:1f} {2:1f} {3:1f} {4:.3f} \n'.format(xpos,
                                                                      ypos,
                                                                      self.slits[n]['wd'],
                                                                      self.slits[n]['hd'],
                                                                      r)
            fh2.write(tmp)

            str = '{0:>s}\t{1:>s}\t{2:.2f}\t{3:.0f}\t{4:.0f}\t{5:.0f}\t{6:.0f}\t{7:>s}\t{8:.1f}\t{9:>s}'.format(self.dirfile,
                                                                                                                self.slitfile,
                                                                                                                -r,
                                                                                                                xpos,
                                                                                                                ypos,
                                                                                                                x,
                                                                                                                y,
                                                                                                                res[3],
                                                                                                                res[4],
                                                                                                                n)
            fh1.write(str + '\n')
            if self.debug:
                print str

        fh1.close()
        fh2.close()
        fh3.close()

        if self.debug:
            print
            print xtr, ytr


    def overPlotSlits(self, output='overplottedOriginalsLog', type='.pdf', logscale=True):
        '''
        Overplot the slits to image data. Will overplot both the original slit
        positions and the best fitted position. Will also plot residuals.

        :note: it looks lie the fitted slit positions are in a wrong place in the
               image. Maybe the patch.set_transform is not working as I assume...

        :param: output, output file name
        :param: type
        :param: logscale, whether a log10 should be taken from the image data
        '''
        #make a copy of the imdata, in case we modify it...
        img = self.directImage.copy()

        fig = P.figure()
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        #show image
        img[img < 0] = 0
        if logscale:
            img[img > 0] = np.log10(img[img > 0])
            
        ax1.imshow(img, origin='lower', interpolation=None)

        #original Slits
        for slit in self.slits.values():
            ax1.add_patch(patches.Rectangle(slit['xySky'],
                                            slit['width'],
                                            slit['height'],
                                            fill=False))

        #fitted slit positions
        for mins in  self.result['minimaPosition'].values():
            rot = mins[0]
            n = mins[5]
            tmp = (self.slits[n]['xminSky'] + mins[1], self.slits[n]['yminSky'] + mins[2])
            patch = patches.Rectangle(tmp,
                                      self.slits[n]['wd'],
                                      self.slits[n]['hd'],
                                      fill=False,
                                      ec='red')
            t2 = matplotlib.transforms.Affine2D().rotate_deg(rot) + ax1.transData
            patch.set_transform(t2)
            ax1.add_patch(patch)

        #rotate x axis labels
        for tl in ax1.get_xticklabels():
            tl.set_rotation(40)
            #rotate x axis labels
        for tl in ax2.get_xticklabels():
            tl.set_rotation(40)

        #plot residuals
        z = np.ones(img.shape)
        for mins in self.result['minimaPosition'].values():
            x = mins[1]
            y = mins[2]
            n = mins[5]
            s = self.slits[n]
            y1 = s['yminSky'] + y
            y2 = s['ymaxSky'] + y + 1
            x1 = s['xminSky'] + x
            x2 = s['xmaxSky'] + x + 1
            z[y1:y2, x1:x2] = (s['values']/np.max(s['values'])) / \
                               (self.result['chiMinData'][n]/np.max(self.result['chiMinData'][n]))

        i2 = ax2.imshow(z, origin='lower', interpolation=None,
                        cmap=cm.get_cmap('binary'), vmin=0.795, vmax=1.205)
        c2 = fig.colorbar(i2, ax=ax2, shrink=0.7, fraction=0.05)
        c2.set_label('Slit Values / Direct Image Data')

        #annotate
        ax1.annotate('Fitted Position', xy=(0.5, 1.05),
                     xycoords='axes fraction', ha='center', va='center')
        ax2.annotate('Residuals', xy=(0.5, 1.05),
                     xycoords='axes fraction', ha='center', va='center')

        #save the first image
        P.savefig(output + type)

        #zoom-in version
        ymin = np.min(np.asarray([x['yminSky'] for x in self.slits.values()]))
        ymax = np.max(np.asarray([x['ymaxSky'] for x in self.slits.values()]))
        xmin = np.min(np.asarray([x['xminSky'] for x in self.slits.values()]))
        xmax = np.max(np.asarray([x['xmaxSky'] for x in self.slits.values()]))
        ax1.set_xlim(xmin - 200, xmax + 200)
        ax2.set_xlim(xmin - 200, xmax + 200)
        ax1.set_ylim(ymin - 100, ymax + 100)
        ax2.set_ylim(ymin - 100, ymax + 100)
        P.savefig(output + 'Zoomed' + type)
        P.close()
        del img


    def outputShiftedImage(self):
        '''
        Outputs a FITS file in which the slits have been shifted
        to the best fitted positions.
        '''
        outfile1 = 'fittedSlitImage.fits'
        outfile2 = 'fittedSlitImageFullFrame.fits'

        zeros = np.zeros(self.slitImage.shape)

        r = []
        for res in self.result['minimaPosition'].values():
            r.append(res[0])
            x = res[1]
            y = res[2]
            n = res[5]
            d = self.slits[n]['values']
            xmin = self.slits[n]['xminSky'] + x
            xmax = self.slits[n]['xmaxSky'] + x
            ymin = self.slits[n]['yminSky'] + y
            ymax = self.slits[n]['ymaxSky'] + y
            zeros[ymin:ymax + 1, xmin:xmax + 1] = d

        rot = np.median(np.asarray(r))
        #note: -rot, because when fitting the direct image was rotated not the slits
        img = interpolation.rotate(zeros, -rot, reshape=False)

        if self.debug:
            print '\n{0:.2f} degree rotation to the fits file'.format(-rot)

        #output to a fits file
        hdu = PF.PrimaryHDU(img)
        if os.path.isfile(outfile1):
            os.remove(outfile1)
        hdu.writeto(outfile1)

        #output a second image
        zeros = np.zeros((3096, 3096))
        for slit in self.slits:
            xmin = self.slits[slit]['xminFitted']
            xmax = self.slits[slit]['xmaxFitted']
            ymin = self.slits[slit]['yminFitted']
            ymax = self.slits[slit]['ymaxFitted']

            zeros[ymin - self.slits[slit]['tolerance']:ymax + 1 + self.slits[slit]['tolerance'],\
                  xmin - self.slits[slit]['tolerance']:xmax + 1 + self.slits[slit]['tolerance']] = \
                  self.slits[slit]['valuesLarge']

        #note: -rot, because when fitting the direct image was rotated not the slits
        img = interpolation.rotate(zeros, -rot, reshape=False)

        #output to a fits file
        hdu = PF.PrimaryHDU(img)
        if os.path.isfile(outfile2):
            os.remove(outfile2)
        hdu.writeto(outfile2)

    def pickleVars(self):
        '''
        This simple method pickles all important variables
        '''
        write.cPickleDumpDictionary(self.result, 'results.pk')
        write.cPickleDumpDictionary(self.slits, 'slits.pk')
        write.cPickleDumpDictionary(self.fitting, 'fitting.pk')

        
    def run(self):
        '''
        Driver function, runs all required steps.
        '''
        self.generateSlitImages()
        self.writeDS9RegionFile()
        self.approxSkyPosition()
        self.fitSlitsToDirectImage()
        #self.fitSlitsToDirectImage2()
        self.plotMinimalization()
        self.outputMinima()
        self.overPlotSlits()
        self.outputShiftedImage()
        self.pickleVars()


def processArgs(printHelp=False):
    '''
    Processes command line arguments
    '''
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
        find = FindSlitPositionsInDirectImage(opts.configfile, opts.debug)
    else:
        find = FindSlitPositionsInDirectImage(opts.configfile, opts.debug, opts.section)

    find.run()