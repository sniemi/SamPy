'''
Fits slit image to a direct image to find x and y positions.

Currently the script uses a slit image. In the future however
we probably want to use the spectrum itself because there is
no guarantee that a slit confirmation image has always been
taken.

:todo: try to do the minimalization with scipy.optmize or
some other technique which might be faster and/or more
robust.

:requires: PyFITS
:requires: NumPy
:requires: matplotlib
:requires: SciPy

:author: Sami-Matias Niemi
'''
import matplotlib
#matplotlib.rc('text', usetex=True)
#matplotlib.rcParams['font.size'] = 17
import sys
from optparse import OptionParser
import pyfits as PF
import pylab as P
import numpy as np
import matplotlib.patches as patches
from matplotlib import cm
import scipy.optimize as optimize
import scipy.ndimage.interpolation as interpolation
#from SamPy
import SamPy.smnIO.write
import SamPy.smnIO.read
import SamPy.image.manipulation as m

import scipy.ndimage.filters as f

class FindSlitPosition():
    def __init__(self):
        pass

    def _findSlitPositions(self, slitImage, threshold=1000):
        '''
        Finds slit positions from a slit image.

        This method uses the Sobel filter in scipy.ndimage.filters

        :todo: this is not ready!

        :param: filename

        '''
        #sobel filter
        filtered = f.sobel(slitImage, axis=1)
        #create a mask above the threshold
        msk = filtered > threshold
        masked = filtered[msk]
        #indices
        y, x = np.indices(slitImage.shape)

        yargs = y[msk]

        return masked

    def slitPosition(self, input, xy):
        '''
        Find slit positions from a confirmation image.

        The script assumes that slits are illuminated and that
        background gives at least 10 per cent increase for the
        slit data.

        :note: modper factor is used to modify the mean background to autolocate the slits.

        :param: input: input data
        :param: xy: x and y minimum and maximum position to identify a single slit

        :rtype: dictionary
        '''
        #size modifier
        sizemod = 1

        #modifier
        modper = 1.1

        #shape of the input array
        shape = input.shape

        #check indices, rows and columns
        row, col = np.indices(shape)

        #create an intial mask
        #msk = input > val
        mn = (np.mean(input[2000:3000, 2000:3000]))
        msk = input > (mn * modper)
        rm = col[msk]
        cm = row[msk]

        #mask the appropriate slit
        msk = ((rm > xy['xmin']) & (rm < xy['xmax'])) & ((cm < xy['ymax']) & (cm > xy['ymin']))

        row = rm[msk]
        col = cm[msk]

        #check the ends
        minrow = np.min(row) + sizemod
        maxrow = np.max(row) - sizemod
        mincol = np.min(col) + sizemod
        maxcol = np.max(col) - sizemod

        #get the width and height of the slit image
        xymins = (minrow, mincol)
        height = maxcol - mincol
        width = maxrow - minrow

        out = {}
        out['xy'] = xymins
        out['width'] = width
        out['height'] = height
        out['ymin'] = mincol
        out['ymax'] = maxcol
        out['xmin'] = minrow
        out['xmax'] = maxrow
        out['values'] = input[mincol:maxcol + 1, minrow:maxrow + 1]
        out['shape'] = shape
        out['throughput'] = 1.0

        return out


    def readSlitPositions(self):
        '''
        Reads slit positions from a slitfile and slitdata from another file.

        This file should follow DS9 format, i.e.:
        box 1545  871 7 499 0
        box 1512 1522 7 614 0
        box 1482 2175 7 499 0

        :note: slit image positions, not the slit positions on the sky!

        :return: information about the slits, positions and data in slit image
        :rtype: dictionary
        '''
        slits = []

        filedata = open(self.slitPos, 'r').readlines()
        for i, line in enumerate(filedata):
            out = {}
            tmp = line.split()
            out['width'] = int(tmp[3])
            out['height'] = int(tmp[4])
            out['ymid'] = int(tmp[2])
            out['xmid'] = int(tmp[1])
            out['ymin'] = out['ymid'] - (out['height'] / 2)
            out['ymax'] = out['ymid'] + (out['height'] / 2)
            out['xmin'] = out['xmid'] - (out['width'] / 2) + 1
            out['xmax'] = out['xmid'] + (out['width'] / 2) + 1
            out['xy'] = (out['xmin'], out['ymin'])
            out['shape'] = self.slitImage.shape
            out['throughput'] = 1.0
            out['values'] = self.slitImage[out['ymin']:out['ymax'] + 1, out['xmin']:out['xmax'] + 1].copy()
            out['number'] = i
            out['pixels'] = len(out['values'].ravel())

            if i == 0:
                out['name'] = 'low'
            elif i == 2:
                out['name'] = 'up'
            else:
                out['name'] = 'mid'

            slits.append(out)
        self.slits = slits


    def generateSlitMask(self, slits, throughput=False):
        '''
        This function can be used to generate a slit mask from given slits.
        '''
        if len(set([x['shape'] for x in slits])) > 1:
            print 'Shape of the slits do not match'

        #slitmask
        slitmask = np.zeros(slits[0]['shape'])

        for slit in slits:
            if throughput:
                val = slit['throughput']
            else:
                val = 1.0

            slitmask[slit['ymin']:slit['ymax'] + 1,
                     slit['xmin']:slit['xmax'] + 1] = val

        return slitmask


    def generateSkyMask(self, slits, offsetx=0, offsety=0):
        '''
        This function can be used to generate a slit mask on the sky
        '''

        skymask = np.zeros(slits[0]['shape'])
        for slit in slits:
            skymask[slit['ymin'] + offsety:slit['ymax'] + 1 + offsety,
                    slit['xmin'] + offsetx:slit['xmax'] + 1 + offsetx] = 1

        return skymask


    def generateSlitImages(self, output, type='.pdf'):
        '''
        Generates diagnostic plots from slit image.
        '''
        rotText = 40
        #generate a separate image of the slit data of each slit image.
        for i, slit in enumerate(self.slits):
            fig = P.figure()
            ax = fig.add_subplot(111)

            #take log10 from the slit data
            tmp = slit['values'] * slit['throughput']
            tmp[tmp <= 0.0] = 1
            tmp = np.log10(tmp)

            ax.imshow(tmp,
                      origin='lower', interpolation=None)

            #rotate x axis labels
            for tl in ax.get_xticklabels():
                tl.set_rotation(rotText)

            P.savefig(output + str(i + 1) + type)
            P.close()

        #make a single slit image
        fig = P.figure()
        for i, slit in enumerate(self.slits):
            ax = fig.add_subplot(1, len(self.slits), i + 1)

            #take log10 from the slit data
            tmp = slit['values'] * slit['throughput']
            tmp[tmp <= 0.0] = 1
            tmp = np.log10(tmp)

            #take log10 from the slit data
            ax.imshow(tmp,
                      origin='lower', interpolation=None)

            #rotate x axis labels
            for tl in ax.get_xticklabels():
                tl.set_rotation(rotText)

            #annotate
            ax.annotate('slit' + str(i + 1), xy=(0.5, 1.05),
                        xycoords='axes fraction', ha='center', va='center')

        P.savefig(output + 'All' + type)
        P.close()


    def overPlotSlits(self, output, type='.pdf', logscale=True):
        '''
        Overplot the slits to image data. Will overplot both the original slit
        positions and the best fitted position. Will also plot residuals.

        :param: output, output file name
        :param: type
        :param: logscale, whether a log10 should be taken from the image data
        '''
        #make a copy of the imdata, in case we modify it...
        img = self.img.copy()

        fig = P.figure()
        ax1 = fig.add_subplot(121)
        ax2 = fig.add_subplot(122)

        #show image
        img[img < 0] = 0
        if logscale:
            img[img > 0] = np.log10(img[img > 0])
        ax1.imshow(img, origin='lower', interpolation=None)

        #original Slits
        for slit in self.slits:
            ax1.add_patch(patches.Rectangle(slit['xySky'],
                                            slit['width'],
                                            slit['height'],
                                            fill=False))
            #fitted slit positions
        tmp = self.result['output'][np.argmin(self.result['output'][:, 3]), :]
        rot = tmp[0]
        x = tmp[1]
        y = tmp[2]
        for slit in self.slits:
            tmp = (slit['xySky'][0] + x, slit['xySky'][1] + y)
            patch = patches.Rectangle(tmp,
                                      slit['width'],
                                      slit['height'],
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
        for i, slit in enumerate(self.slits):
            y1 = slit['yminSky'] + y
            y2 = slit['ymaxSky'] + y + 1
            x1 = slit['xmin'] + x
            x2 = slit['xmax'] + x + 1
            z[y1:y2, x1:x2] = slit['values'] / self.result['chiMinData'][i]
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
        ymin = np.min(np.asarray([x['yminSky'] for x in self.slits]))
        ymax = np.max(np.asarray([x['ymaxSky'] for x in self.slits]))
        xmin = np.min(np.asarray([x['xmin'] for x in self.slits]))
        xmax = np.max(np.asarray([x['xmax'] for x in self.slits]))
        ax1.set_xlim(xmin - 200, xmax + 200)
        ax2.set_xlim(xmin - 200, xmax + 200)
        ax1.set_ylim(ymin - 100, ymax + 100)
        ax2.set_ylim(ymin - 100, ymax + 100)
        P.savefig(output + 'Zoomed' + type)
        P.close()
        del img


    def writeDS9RegionFile(self, output='skyslits.reg'):
        '''
        Writes a DS9 region file for all the slits.
        Draws a rectangle around each slit.
        '''
        fh = open(output, 'w')
        for slit in self.slits:
            #DS0 box format is x, y, width, height, but x and y are the centre point
            string = 'box %i %i %i %i 0\n' % (slit['xySky'][0] + slit['width'] / 2,
                                              slit['xySky'][1] + slit['height'] / 2,
                                              slit['width'],
                                              slit['height'])
            fh.write(string)
        fh.close()


    def approxSkyPosition(self, lw=553, up=553, lwthr=0.9, upthr=0.9):
        '''
        Generates an approximated sky position for slits.
        Assumes that both slits are shifted 553 pixels in y direction.
        Such an assumption is crude, but should allow a starting point.

        :note: this functions modifies the slit throughput

        :todo: one should refine this after measuring the sky position accurately.

        :param: lw, pixels to shift the lower slit
        :param: up, pixels to shift the upper slit
        :param: lwthr, 1/lwthr will be the throughput modifier for the lower slit
        :param: upthr, 1/upthr will be the throughput modifier for the upper slit
        '''
        for i, slit in enumerate(self.slits):
            if slit['name'] == 'up':
                mod = - up
                thr = upthr
            elif slit['name'] == 'low':
                mod = lw
                thr = lwthr
            else:
                mod = 0
                thr = 1.0

            self.slits[i]['yminSky'] = slit['ymin'] + mod
            self.slits[i]['ymaxSky'] = slit['ymax'] + mod
            self.slits[i]['xySky'] = (slit['xy'][0], slit['xy'][1] + mod)
            self.slits[i]['throughput'] = 1. / thr


    def chiSquare(self, model, obs):
        '''
        Simple chi**2 calculation
        '''
        r = np.sum((obs - model) ** 2 / model)
        return r


    def _fitfunct(self, x, y, directimage, slits):
        #get data from direct image
        dirdata = []
        for slit in slits:
            d = directimage[slit['ymin'] + int(y):slit['ymax'] + 1 + int(y),
                slit['xmin'] + int(x):slit['xmax'] + 1 + int(x)]
            dirdata.append(d)

        obs = np.hstack((dirdata[0].ravel(),
                         dirdata[1].ravel(),
                         dirdata[2].ravel()))
        obs /= np.max(obs)
        return obs


    def _errorf(self, params, directimage, slits, data):
        return self._fitfunct(params[0], params[1], directimage, slits) - data


    def fitSlitsToDirectImageLSQ(self, slits, directimage, params=[-1, -1]):
        '''
        Uses scipy.optimize.leastsq

        :note: This does not really work at the mo...
        '''
        #generates a model array from the slit values, takes into account potential
        #throughput of a slit
        data = np.hstack((slits[0]['values'].ravel() * slits[0]['throughput'],
                          slits[1]['values'].ravel() * slits[1]['throughput'],
                          slits[2]['values'].ravel() * slits[2]['throughput']))
        data /= np.max(data)

        p = optimize.leastsq(self._errorf,
                             params,
                             args=(directimage, slits, data),
                             full_output=True,
                             ftol=1e-18,
                             xtol=1e-18)
        return p

    def fitSlitsToDirectImage(self,
                              xran=50, yran=50, step=1,
                              rot=1.0, rotstep=0.1, rotation=True,
                              normalize=False, debug=True):
        '''
        Fits a slit image to a direct image.
        This functions does not collapse the slit image, but uses each pixel.
        By default the counts are normalized to a peak count, but this can
        be controlled using the optional keyword normalize.

        :param: xran, +/- x-range to cover
        :param: yran, +/- y-range to cover
        :param: step, size of pixel steps in x and y
        :param: rot, +/- rotation angle in degrees
        :param: rotstep, step in degrees
        :param: normalize, whether slit and direct image values should be normalized or not
        :param: debug, print debugging information

        :rtype: dictionary
        '''

        #generates a model array from the slit values, takes into account potential
        #throughput of a slit
        self.model = np.hstack((self.slits[0]['values'].ravel() * self.slits[0]['throughput'],
                                self.slits[1]['values'].ravel() * self.slits[1]['throughput'],
                                self.slits[2]['values'].ravel() * self.slits[2]['throughput']))
        #self.msk = self.model > 0.0
        #self.model = self.model[self.msk]

        if normalize:
            self.model /= np.max(self.model)

        norm = len(self.model)

        #generate rotations
        if rotation:
            rotations = np.arange(-rot, rot, rotstep)
            rotations[(rotations < 1e-8) & (rotations > -1e-8)] = 0.0
            #make a copy of the direct image
            origimage = self.img.copy()
        else:
            rotations = [0, ]

        out = []
        chmin = -9.99
        cm = 1e50
        #loop over a range of rotations,  x and y positions around the nominal position and record x, y and chisquare
        for r in rotations:
            if rotation:
                if r != 0.0:
                    d = interpolation.rotate(origimage, r, reshape=False)
                else:
                    d = origimage.copy()
            else:
                d = self.img.copy()
            for x in range(-xran, xran, step):
                for y in range(-yran, yran, step):
                    dirdata = []
                    #get data from direct image
                    for s in self.slits:
                        data = d[s['yminSky'] + y:s['ymaxSky'] + 1 + y, s['xmin'] + x:s['xmax'] + 1 + x]
                        dirdata.append(data)

                    obs = np.hstack((dirdata[0].ravel(),
                                     dirdata[1].ravel(),
                                     dirdata[2].ravel()))
                    #obs = obs[self.msk]

                    if normalize:
                        obs /= np.max(obs)

                    chisq = self.chiSquare(self.model, obs)
                    out.append([r, x, y, chisq, chisq / norm])

                    #save the dirdata of the minimum chisqr
                    if chisq < cm:
                        chmin = dirdata
                        cm = chisq

                    if debug:
                        print r, x, y, chisq, chisq / norm

        #return dictionary
        r = {}
        r['rot'] = rot
        r['rotation_step'] = rotstep
        r['xran'] = xran
        r['yran'] = yran
        r['model'] = self.model
        r['output'] = np.array(out)
        r['chiMinData'] = chmin
        self.result = r


    def fakeSlitData(self):
        '''
        Cuts out imaging data to test the fitting algorithm.
        '''
        for slit in self.slits:
            slit['values'] = self.slitImage[slit['ymin']:slit['ymax'] + 1, slit['xmin']:slit['xmax'] + 1]


    def plotMinimalization(self, output='minim', type='.png'):
        '''
        Generates a two dimensional map of the minimalization.

        :param: data
        '''
        d = self.result['output']
        #begin image
        P.figure()
        P.scatter(d[:, 1],
                  d[:, 2],
                  c=1. / np.log10(d[:, 3]),
                  s=20,
                  cmap=cm.get_cmap('jet'),
                  edgecolor='none',
                  alpha=0.5)
        P.xlim(-self.result['xran'], self.result['xran'])
        P.ylim(-self.result['yran'], self.result['yran'])
        P.xlabel('X [pixels]')
        P.ylabel('Y [pixels]')
        P.savefig(output + 'Map' + type)
        P.close()

        #second figure
        P.figure()
        P.scatter(d[:, 0], d[:, 3], s=2)
        P.xlim(-self.result['rot'], self.result['rot'])
        P.ylim(0.9 * np.min(d[:, 3]), 1.05 * np.max(d[:, 3]))
        P.xlabel('Rotation [degrees]')
        P.ylabel('$\chi^{2}$')
        P.savefig(output + 'Rot' + type)
        P.close()

        #third figure
        P.figure()
        P.scatter(d[:, 1], d[:, 3], s=2)
        P.xlim(-self.result['xran'], self.result['xran'])
        P.ylim(0.9 * np.min(d[:, 3]), 1.05 * np.max(d[:, 3]))
        P.xlabel('X [pixels]')
        P.ylabel('$\chi^{2}$')
        P.savefig(output + 'XCut' + type)
        P.close()

        #forth figure
        P.figure()
        P.scatter(d[:, 2], d[:, 3], s=2)
        P.xlim(-self.result['yran'], self.result['yran'])
        P.ylim(0.9 * np.min(d[:, 3]), 1.05 * np.max(d[:, 3]))
        P.xlabel('Y [pixels]')
        P.ylabel('$\chi^{2}$')
        P.savefig(output + 'YCut' + type)
        P.close()


    def outputMinima(self, output='min.txt', stdout=True):
        '''
        Outputs the results to a file and also the screen if stdout = True.
        '''
        tmp = self.result['output'][np.argmin(self.result['output'][:, 3]), :]
        str = '{0:>s}\t{1:>s}\t{2:>s}\t{3:.1f}\t{4:.0f}\t{5:.0f}\t{6:.1f}'.format(self.fitImage,
                                                                                  self.slit,
                                                                                  self.slitPos,
                                                                                  tmp[0],
                                                                                  tmp[1],
                                                                                  tmp[2],
                                                                                  tmp[3])

        #to screen
        if stdout:
            print '\n\ndirect image    slit image    slit pos \t\t rot \t x \t y \t chi**2'
            print str

        #to file
        fh = open(output, 'a')
        fh.write(str + '\n')
        fh.close()

    def runAll(self, opts, args):
        '''
        Driver function
        '''

        if (opts.slit is None or opts.fitImage is None):
            processArgs(True)
            sys.exit(1)

        #rename the command line options
        self.slit = opts.slit
        self.fitImage = opts.fitImage
        #slit position file defaults to slit.reg
        if (opts.position is None):
            self.slitPos = 'slit.reg'
            print 'Using {0:>s} for slit positions'.format(slitPos)
        else:
            self.slitPos = opts.position
            #debugging mode, where slit data are being faked
        debug = opts.debug
        #whether the data should be blurred or not
        blur = opts.blur
        #boolean to control whether the slit positions should be found automatically or not
        automatic = opts.automatic

        #load images
        img = PF.open(self.fitImage, ignore_missing_end=True)[0].data
        if img.shape[0] == 1:
            img = img[0]

        slitimage = PF.open(self.slit, ignore_missing_end=True)[0].data
        if slitimage.shape[0] == 1:
            slitimage = slitimage[0]

        if blur:
            img = m.blurImage(img, 4)

        self.slitImage = slitimage
        self.img = img

        if automatic:
            #gets the slit positions automatically, does not work perfectly
            upslit = self.slitPosition(slitimage, {'xmin': 1460, 'xmax': 1500, 'ymin': 1900, 'ymax': 2500})
            midslit = self.slitPosition(slitimage, {'xmin': 1500, 'xmax': 1525, 'ymin': 1200, 'ymax': 1850})
            lowslit = self.slitPosition(slitimage, {'xmin': 1530, 'xmax': 1550, 'ymin': 600, 'ymax': 1130})
            self.slits = (upslit, midslit, lowslit)
        else:
            self.readSlitPositions()

        self.generateSlitImages('slits')
        self.approxSkyPosition()
        #self.approxSkyPosition(lw=553, up=553)
        self.writeDS9RegionFile()

        if debug:
            self.fakeSlitData()

        #a = fitSlitsToDirectImageLSQ(slits, img)
        #print a
        #import sys; sys.exit()

        #find the chisqr minimum and make a diagnostic plot
        #self.fitSlitsToDirectImage(xran=100, yran=100, rotation=False)
        self.fitSlitsToDirectImage(xran=100, yran=100, rot=3.0, rotstep=0.1)
        self.plotMinimalization()

        #output some info
        self.outputMinima()

        #generates diagnostic plots and writes the slit positions for DS9 inspection
        self.overPlotSlits('overplottedOriginalsLog')


def processArgs(just_print_help=False):
    '''
    Processes command line arguments
    '''
    parser = OptionParser()

    parser.add_option("-s", "--slit", dest="slit",
                      help="Name of the slit image file", metavar="string")
    parser.add_option("-f", "--fitting", dest="fitImage",
                      help='Name of the direct image to which the slit data will be fitted', metavar='string')
    parser.add_option("-d", "--debug", dest="debug", action='store_true',
                      help='Debugging mode on')
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Verbose mode on")
    parser.add_option("-p", "--position", dest="position",
                      help="Name of the slit position file", metavar="string")
    parser.add_option("-b", "--blur", action="store_true", dest="blur",
                      help="Whether the input direct image should be gaussian blurred or not")
    parser.add_option("-a", "--automatic", action="store_true", dest="automatic",
                      help="If on tries to determine slit positions automatically from the slit image")
    if just_print_help:
        parser.print_help()
    else:
        return parser.parse_args()

if __name__ == '__main__':
    #Gets the command line arguments and call main function
    find = FindSlitPosition()
    find.runAll(*processArgs())