"""
Reduces ACS WFC polarimetry data.

:requires: astrodither / astrodrizzle
:requires: PyRAF
:requires: IRAF
:requires: NumPy
:requires: SciPy
:requires: matplotlib

:author: Sami-Matias Niemi
:contact: sammy@sammyniemi.com

:version: 0.6
"""
import matplotlib
matplotlib.use('PDF')
import os, glob, shutil, datetime
from optparse import OptionParser
from itertools import groupby, izip, count
from time import time
import numpy as np
import pyfits as pf
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import NullFormatter
import scipy.stats
from scipy import ndimage
from pytools import asnutil
import pyraf
from pyraf import iraf
from iraf import stsdas, hst_calib, acs, calacs, images, immatch, sregister, blkavg
import acstools

try:
    #different naming convention in linux and macosx
    import drizzlepac as a
except:
    import astrodither as a
try:
    #different naming convention in linux and macosx
    from drizzlepac import astrodrizzle, tweakreg, pixtopix
except:
    from astrodither import astrodrizzle, tweakreg, pixtopix

    
class sourceFinding():
    """
    This class provides methods for source finding.
    """

    def __init__(self, image, **kwargs):
        """
        Init.

        :param image: 2D image array
        :type image: numpy.ndarray

        :param kwargs: additional keyword arguments
        :type kwargs: dictionary
        """
        self.image = image
        #set default parameter values and then update using kwargs
        self.settings = dict(above_background=10.0,
                             clean_size_min=9,
                             clean_size_max=110,
                             sigma=1.5,
                             disk_struct=3,
                             output='objects.txt')
        self.settings.update(kwargs)


    def _diskStructure(self, n):
        """
        """
        struct = np.zeros((2 * n + 1, 2 * n + 1))
        x, y = np.indices((2 * n + 1, 2 * n + 1))
        mask = (x - n) ** 2 + (y - n) ** 2 <= n ** 2
        struct[mask] = 1
        return struct.astype(np.bool)


    def find(self):
        """
        Find all pixels above the median pixel after smoothing with a Gaussian filter.

        :Note: maybe one should use mode instead of median
        """
        #smooth the image
        img = ndimage.gaussian_filter(self.image, sigma=self.settings['sigma'])

        #find pixels above the median
        msk = self.image > np.median(img)
        #get background image and calculate statistics
        backgrd = self.image[~msk]
        std = np.std(backgrd).item() #items required if image was memmap'ed by pyfits
        mean = np.mean(backgrd[backgrd > 0.0]).item() #items required if image was memmap'ed by pyfits
        rms = np.sqrt(std ** 2 + mean ** 2)

        print 'Background: average={0:.4f} and rms={1:.4f}'.format(mean, rms)

        #find objects above the background
        self.mask = ndimage.median_filter(self.image, self.settings['sigma']) > rms * self.settings[
                                                                                      'above_background'] + mean
        #mask_pix = im > rms * above_background + mean
        #mask = (mask + mask_pix) >= 1

        #get labels
        self.label_im, self.nb_labels = ndimage.label(self.mask)

        print 'Finished the initial run and found {0:d} objects...'.format(self.nb_labels)

        return self.mask, self.label_im, self.nb_labels


    def getContours(self):
        """
        Derive contours using the diskStructure function.
        """
        if not hasattr(self, 'mask'):
            self.find()

        self.opened = ndimage.binary_opening(self.mask,
                                             structure=self._diskStructure(self.settings['disk_struct']))
        return self.opened


    def getSizes(self):
        """
        Derives sizes for each object.
        """
        if not hasattr(self, 'label_im'):
            self.find()

        self.sizes = np.asarray(ndimage.sum(self.mask, self.label_im, range(self.nb_labels + 1)))
        return self.sizes


    def getFluxes(self):
        """
        Derive fluxes or counts.
        """
        if not hasattr(self, 'label_im'):
            self.find()

        self.fluxes = np.asarray(ndimage.sum(self.image, self.label_im, range(1, self.nb_labels + 1)))
        return self.fluxes


    def cleanSample(self):
        """
        Cleans up small connected components and large structures.
        """
        if not hasattr(self, 'sizes'):
            self.getSizes()

        mask_size = (self.sizes < self.settings['clean_size_min']) | (self.sizes > self.settings['clean_size_max'])
        remove_pixel = mask_size[self.label_im]
        self.label_im[remove_pixel] = 0
        labels = np.unique(self.label_im)
        self.label_clean = np.searchsorted(labels, self.label_im)


    def getCenterOfMass(self):
        """
        Finds the center-of-mass for all objects using numpy.ndimage.center_of_mass method.

        :return: xposition, yposition, center-of-masses
        :rtype: list
        """
        if not hasattr(self, 'label_clean'):
            self.cleanSample()

        self.cms = ndimage.center_of_mass(self.image,
                                          labels=self.label_clean,
                                          index=np.unique(self.label_clean))
        self.xcms = [c[1] for c in self.cms]
        self.ycms = [c[0] for c in self.cms]

        print 'After cleaning found {0:d} objects'.format(len(self.xcms))

        return self.xcms, self.ycms, self.cms


    def plot(self):
        """
        Generates a diagnostic plot.

        :return: None
        """
        if not hasattr(self, 'opened'):
            self.getContours()

        if not hasattr(self, 'xcms'):
            self.getCenterOfMass()

        plt.figure(1, figsize=(18, 8))
        s1 = plt.subplot(131)
        s1.imshow(np.log10(np.sqrt(self.image)), interpolation=None, origin='lower')
        s1.plot(self.xcms, self.ycms, 'x', ms=4)
        s1.contour(self.opened, [0.2], c='b', linewidths=1.2, linestyles='dotted')
        s1.axis('off')
        s1.set_title('log10(sqrt(IMAGE))')

        s2 = plt.subplot(132)
        s2.imshow(self.mask, cmap=plt.cm.gray, interpolation=None, origin='lower')
        s2.axis('off')
        s2.set_title('Object Mask')

        s3 = plt.subplot(133)
        s3.imshow(self.label_clean, cmap=plt.cm.spectral, interpolation=None, origin='lower')
        s3.axis('off')
        s3.set_title('Cleaned Object Mask')

        plt.subplots_adjust(wspace=0.02, hspace=0.02, top=1, bottom=0, left=0, right=1)
        plt.savefig('SourceExtraction.pdf')
        plt.close()


    def generateOutput(self):
        """
        Outputs the found positions to an ascii and a DS9 reg file.

        :return: None
        """
        if not hasattr(self, 'xcms'):
            self.getCenterOfMass()

        fh = open(self.settings['output'], 'w')
        rg = open(self.settings['output'], 'w')
        fh.write('#X coordinate in pixels [starts from 1]\n')
        fh.write('#Y coordinate in pixels [starts from 1]\n')
        rg.write('#File written on {0:>s}\n'.format(datetime.datetime.isoformat(datetime.datetime.now())))
        for x, y in zip(self.xcms, self.ycms):
            fh.write('%10.3f %10.3f\n' % (x + 1, y + 1))
            rg.write('circle({0:.3f},{1:.3f},5)\n'.format(x + 1, y + 1))
        fh.close()


    def runAll(self):
        """
        Performs all steps of source finding at one go.

        :return: source finding results such as positions, sizes, fluxes, etc.
        :rtype: dictionary
        """
        self.find()
        self.getContours()
        self.getSizes()
        self.getFluxes()
        self.cleanSample()
        self.getCenterOfMass()
        self.plot()
        self.generateOutput()

        results = dict(xcms=self.xcms, ycms=self.ycms, cms=self.cms,
                       sizes=self.sizes, fluxes=self.fluxes)

        return results


class reduceACSWFCpoli():
    """
    This class provides methods for reducing ACS WFC polarimetry data.
    Uses astrodrizzle to combine images.
    """

    def __init__(self, input, **kwargs):
        """
        Init.

        :param input: FITS association
        :type input: string
        :param kwargs: additional keyword arguments
        :type kwargs: dictionary
        """
        self.input = input
        self.settings = dict(asndir='asn', rawdir='raw',
                             jref='/grp/hst/cdbs/jref/',
                             mtab='/grp/hst/cdbs/mtab/',
                             sourceImage='POL0V_drz.fits',
                             sigma=5.0)
        self.settings.update(kwargs)

        #add env variables to both system and IRAF
        os.putenv('jref', self.settings['jref'])
        os.putenv('mtab', self.settings['mtab'])
        iraf.set(jref=self.settings['jref'])
        iraf.set(mtab=self.settings['mtab'])

        #IRAF has funny True and False
        self.yes = iraf.yes
        self.no = iraf.no


    def createAssociations(self):
        """
        Finds raw data and generates proper FITS associations for each POL filter.

        Groups by all data based on the FILTER1 header keyword.
        """
        orig = os.getcwd()

        try:
            os.mkdir(self.settings['asndir'])
        except:
            for d in glob.glob('./' + self.settings['asndir'] + '/*.*'):
                os.remove(d)

        #find all raw files
        os.chdir(os.getcwd() + '/' + self.settings['rawdir'] + '/')
        raws = glob.glob('*_raw.fits')

        out = open('../rawFiles.txt', 'w')
        out.write('#File written on {0:>s}\n'.format(datetime.datetime.isoformat(datetime.datetime.now())))
        out.write('#file filter1 filter2 PA_V3\n')
        data = {}

        for raw in raws:
            hdr = pf.open(raw)[0].header
            print raw, hdr['FILTER1'], hdr['FILTER2'], hdr['PA_V3']
            if 'POL' in hdr['FILTER1'] or 'POL' in hdr['FILTER2']:
                out.write('%s %s %s %s\n' % (raw, hdr['FILTER1'], hdr['FILTER2'], hdr['PA_V3']))
                data[raw] = (hdr['FILTER1'], hdr['FILTER2'], hdr['PA_V3'])
            else:
                print 'skipping line, no POL filter data'

        out.close()

        #group data by FILTER1
        newass = {}
        f2d = [(a, data[a][1]) for a in data]
        f2d = sorted(f2d, key=lambda x: x[1])
        for key, group in groupby(f2d, lambda x: x[1]):
            tmp = []
            print '\nnew group found:'
            for member in group:
                print member
                tmp.append(member[0])
            newass[key] = tmp

        #create new associations
        asns = []
        awd = '../' + self.settings['asndir'] + '/'
        print '\n\nCreate new associations to ./%s/' % self.settings['asndir']
        for key, value in newass.iteritems():
            asnt = asnutil.ASNTable(value, output=key)
            asnt.create()
            asnt.write()
            shutil.move(key + '_asn.fits', awd)
            asns.append(key + '_asn.fits')

        #check the new associations
        for asn in asns:
            data = pf.open('../' + self.settings['asndir'] + '/' + asn)[1].data
            print asn
            for row in data:
                print row

        os.chdir(orig)

        self.associations = asns

        if self.input is None:
            self.input = [x for x in self.associations if 'POL' in x]
        else:
            self.input = glob.glob(self.input)


    def copyRaws(self):
        """
        Copy all _raw, _spt, and _asn files to a temporary working directory.

        :Note: One should run either copyRaws or copyFLTs but usually not both!
        """
        #make a new dir
        path = 'tmp'
        try:
            os.mkdir(path)
        except:
            for d in glob.glob('./%s/*.*' % path):
                os.remove(d)

        for fle in glob.glob('./raw/*_raw.fits'):
            shutil.copy(fle, path)

        for fle in glob.glob('./support/*_spt.fits'):
            shutil.copy(fle, path)

        for fle in glob.glob('./asn/*_asn.fits'):
            shutil.copy(fle, path)

        #change the current working directory to tmp
        os.chdir(os.getcwd() + '/' + path)
        iraf.chdir(os.getcwd())


    def copyFLTs(self):
        """
        Copy all _flt, _spt, and _asn files to a temporary working directory.

        :Note: One should run either copyRaws or copyFLTs but usually not both!
        """
        #make a new dir
        path = 'tmp'
        try:
            os.mkdir(path)
        except:
            for d in glob.glob('./%s/*.*' % path):
                os.remove(d)

        for fle in glob.glob('./opus/*_flt.fits'):
            shutil.copy(fle, path)

        for fle in glob.glob('./support/*_spt.fits'):
            shutil.copy(fle, path)

        for fle in glob.glob('./asn/*_asn.fits'):
            shutil.copy(fle, path)

        #change the current working directory to tmp
        os.chdir(os.getcwd() + '/' + path)
        iraf.chdir(os.getcwd())


    def omitPHOTCORR(self):
        """
        Sets PHOTCORR keyword to OMIT to prevent crashing.

        :note: find a proper fix for this.
        :note: Change from iraf to pyfits.
        """
        for raw in glob.glob('*_raw.fits'):
            iraf.hedit(images=raw + '[0]', fields='PHOTCORR', value='OMIT',
                       add=self.no, addonly=self.no, delete=self.no,
                       verify=self.no, show=self.yes, update=self.yes)


    def runCalACS(self):
        """
        Calls calACS and processes all given files or associations.
        """
        for f in self.input:
            calacs.run(input=f)

        #remove the raw files
        for f in glob.glob('*_raw.fits'):
            os.remove(f)


    def destripeFLT(self):
        """
        Uses the acs_destripe routine from the acstools to remove the bias striping.

        Renames the original FLT files as _flt_orig.fits.
        The destriped files are called as _flt_destripe.fits.
        """
        acstools.acs_destripe.clean('*_flt.fits',
                                    'destripe',
                                    clobber=False,
                                    maxiter=20,
                                    sigrej=2.0)
        for f in glob.glob('*_flt.fits'):
            shutil.move(f, f.replace('_flt.fits', '_flt_orig.fits'))
        for f in glob.glob('*_flt_destripe.fits'):
            shutil.copy(f, f.replace('_flt.destripe.fits', '_flt.fits'))


    def destripeFLTSMN(self):
        """
        Uses an algorithm developed by SMN to destripe the ACS FLT frames.
        This is an extremely simple method in which the median of each row
        is being first subtracted from the row after which a median of the
        full frame is being added back to each row to not to remove any sky/
        background. Each pixel that is known to be bad is being masked using
        the DQ array. In addition, any good pixel above sigma is not taken
        into account. This allows to exclude bright objects and cosmic rays.
        Note that such masking is not extremely accurate, but given the fact
        that the algorithm deals with medians, it should suffice.
        """
        nullfmt = NullFormatter()

        for input in glob.glob('*_flt.fits'):
            shutil.copy(input, input.replace('_flt.fits', '_flt_orig.fits'))

            inp = input.replace('.fits', '')

            fh = pf.open(input, mode='update')
            data = fh[1].data
            org = data.copy()
            dqarr = fh[3].data

            medians = []

            for i, l, dq in izip(count(), data, dqarr):
                msk = ~(dq > 0)
                d = l[msk]
                #mask additionally everything above x sigma
                sig = np.median(d) + self.settings['sigma'] * np.std(d)
                msk2 = d < sig
                median = np.median(d[msk2])
                if ~np.isnan(median):
                    data[i] -= median
                    medians.append(median)
                else:
                    print 'Will not remove nan median on line %i' % i

            medians = np.asarray(medians)

            #add back the background
            md = org[~(dqarr > 0)]
            background = np.median(md[md < (np.median(md) + self.settings['sigma'] * np.std(md))])
            data += background

            fh.close()

            #generate a ratio plot
            plt.figure()
            plt.title(inp)
            ims = plt.imshow(data / org, origin='lower', vmin=0.98, vmax=1.02)
            cb = plt.colorbar(ims)
            cb.set_label('Destriped / Original')
            plt.savefig(inp + 'ratio.pdf')
            plt.close()

            #calculate Gaussian KDE and evaluate it
            est2 = []
            vals = medians - background
            kde = scipy.stats.gaussian_kde(vals)
            for x in np.arange(np.int(np.min(vals)), np.int(np.max(vals)), 0.1):
                y = kde.evaluate(x)[0]
                est2.append([x, y])
            est2 = np.asarray(est2)

            #generate a plot showing the distribution of median subtractions
            plt.figure()
            gs = gridspec.GridSpec(2, 1, height_ratios=[4, 1])
            gs.update(wspace=0.0, hspace=0.0, top=0.96, bottom=0.07)
            axScatter = plt.subplot(gs[0])
            axHist = plt.subplot(gs[1])
            axScatter.set_title(inp)
            axScatter.plot(medians - background, np.arange(len(medians)), 'bo')
            axScatter.xaxis.set_major_formatter(nullfmt)
            n, bins, patches = axHist.hist(medians - background, bins=35, normed=True)
            axHist.plot(est2[:, 0], est2[:, 1], 'r-', label='Gaussian KDE')
            axHist.set_xlabel('Medians - Background')
            axScatter.set_ylabel('Row')
            axScatter.set_ylim(-1, 2046)
            axHist.legend()
            plt.savefig(inp + 'dist.pdf')
            plt.close()


    def updateHeader(self):
        """
        Calls astrodrizzle's updatenpol to update the headers of the FLT files.
        """
        a.updatenpol.update('*_flt.fits', self.settings['jref'])


    def initialProcessing(self):
        """
        Does the initial processing as follows:

            1. use astrodrizzle to combine images of the same POL filter using
               the shifts file generated by the tweakreg at point one.

        """
        #run astrodrizzle separately for each POL
        kwargs = dict(final_pixfrac=1.0, final_fillval=1.0, preserve=False,
                      updatewcs=True, final_wcs=False, build=True, skysub=False)
        for f in self.input:
            astrodrizzle.AstroDrizzle(input=f, mdriztab=False, editpars=False, **kwargs)


    def findImprovedAlignment(self):
        """
        Tries to find stars to be used for improved alignment.

        Generates coordinate lists for each POL file and for every _flt file.
        Maps all the positions to uncorrected/distorted frame using pixtopix transformation.
        Finally, runs the tweakreg to find improved alignment and updates the WCS in the
        headers.
        """
        #find some good stars
        source = sourceFinding(pf.open(self.settings['sourceImage'])[1].data)
        results = source.runAll()

        #find improved locations for each star
        acc = []
        for x, y in zip(results['xcms'], results['ycms']):
            acc.append(iraf.imcntr('POL*_drz.fits[1]', x_init=x, y_init=y, cboxsize=45, Stdout=1))
        o = open('tmp.txt', 'w')
        o.write('#File written on {0:>s}\n'.format(datetime.datetime.isoformat(datetime.datetime.now())))
        for line in acc:
            for l in line:
                o.write(l.replace('[', '').replace(']', '') + '\n')
        o.close()

        data = open('tmp.txt').readlines()

        pol0 = open('POL0coords.txt', 'w')
        pol60 = open('POL60coords.txt', 'w')
        pol120 = open('POL120coords.txt', 'w')
        pol0r = open('POL0coords.reg', 'w')
        pol60r = open('POL60coords.reg', 'w')
        pol120r = open('POL120coords.reg', 'w')

        for line in data:
            tmp = line.split(':')
            x = tmp[1].replace('y', '').strip()
            y = tmp[2].strip()
            out = '%s %s\n' % (x, y)
            reg = 'image;circle(%s,%s,5)\n' % ( x, y)
            if 'POL0' in line:
                pol0.write(out)
                pol0r.write(reg)
            elif 'POL60' in line:
                pol60.write(out)
                pol60r.write(reg)
            elif 'POL120' in line:
                pol120.write(out)
                pol120r.write(reg)
            else:
                print 'Skipping line:', line

        pol0.close()
        pol60.close()
        pol120.close()
        pol0r.close()
        pol60r.close()
        pol120r.close()

        data = open('../rawFiles.txt').readlines()
        pol0 = [line.split()[0].split('_raw')[0] + '_flt.fits' for line in data if 'POL0' in line.split()[2]]
        pol60 = [line.split()[0].split('_raw')[0] + '_flt.fits' for line in data if 'POL60' in line.split()[2]]
        pol120 = [line.split()[0].split('_raw')[0] + '_flt.fits' for line in data if 'POL120' in line.split()[2]]

        for file in pol0:
            x, y = pixtopix.tran(file + "[1]", 'POL0V_drz.fits[1]', 'backward',
                                 coords='POL0coords.txt', output=file.replace('.fits', '') + '.coords',
                                 verbose=False)

        for file in pol60:
            x, y = pixtopix.tran(file + "[1]", 'POL60V_drz.fits[1]', 'backward',
                                 coords='POL60coords.txt', output=file.replace('.fits', '') + '.coords',
                                 verbose=False)

        for file in pol120:
            x, y = pixtopix.tran(file + "[1]", 'POL120V_drz.fits[1]', 'backward',
                                 coords='POL120coords.txt', output=file.replace('.fits', '') + '.coords',
                                 verbose=False)
        del x
        del y

        coords = glob.glob('*_flt.coords')

        #remove comment lines from each coords file and produce a DS9 region file
        for f in coords:
            data = open(f).readlines()
            out = open(f, 'w')
            reg = open(f.replace('.coords', '.reg'), 'w')
            reg.write('#File written on {0:>s}\n'.format(datetime.datetime.isoformat(datetime.datetime.now())))
            for line in data:
                if not line.startswith('#'):
                    out.write(line)
                    tmp = line.split()
                    reg.write('image;circle({0:>s},{1:>s},5)\n'.format(tmp[0], tmp[1]))
            out.close()
            reg.close()

        #create a mapping file
        out = open('regcatalog.txt', 'w')
        for f in coords:
            out.write('%s %s\n' % (f.replace('.coords', '.fits'), f))
        out.close()

        params = {'catfile': 'regcatalog.txt', 'shiftfile': True, 'outshifts': 'flt1_shifts.txt', 'updatehdr': True,
                  'verbose': False, 'minobj': 15, 'use2dhist': False, 'see2dplot': False,
                  'searchrad': 50, 'searchunits': 'pixels', 'tolerance': 50.0, 'separation': 30.0, 'nclip': 3}
        tweakreg.TweakReg('*_flt.fits', editpars=False, **params)
        params.update({'outshifts': 'flt_shifts.txt', 'searchrad': 15, 'tolerance': 3})
        tweakreg.TweakReg('*_flt.fits', editpars=False, **params)
        #params = {'updatehdr': True, 'verbose': False, 'minobj': 15, 'use2dhist': True, 'see2dplot': False,
        #          'searchrad': 2.5, 'searchunits': 'pixels'}
        #tweakreg.TweakReg('*_flt.fits', editpars=False, **params)


    def registerPOLs(self):
        """
        Aligns and registers the POL files. In addition, produces block averages files.

        :return: None
        """
        #copy the first round files to backup and check the shifts
        drzs = glob.glob('*POL*_drz*.fits')
        for drz in drzs:
            shutil.move(drz, drz.replace('_drz.fits', '_backup.fits'))
        params = {'outshifts': 'backup_shifts.txt', 'updatehdr': True,
                  'verbose': False, 'minobj': 20, 'use2dhist': True,
                  'residplot': 'residuals', 'see2dplot': False,
                  'searchrad': 35, 'searchunits': 'pixels'}
        #we can do this twice to get the alignment really good
        tweakreg.TweakReg('*_backup.fits', editpars=False, **params)
        tweakreg.TweakReg('*_backup.fits', editpars=False, **params)

        #user sregister to resample to separate POL frames to a single WCS frame
        sregister('POL*_backup.fits[1]', 'POL0V_backup.fits[1]', 'P0lin_sci.fits,P60lin_sci.fits,P120lin_sci.fits',
                  fitgeometry='rscale', calctype='double', interpolant='linear', fluxconserve=self.yes)
        sregister('POL*_backup.fits[1]', 'POL0V_backup.fits[1]', 'P0drz_sci.fits,P60drz_sci.fits,P120drz_sci.fits',
                  fitgeometry='rscale', calctype='double', interpolant='drizzle', fluxconserve=self.yes)
        sregister('POL*_backup.fits[3]', 'POL0V_backup.fits[1]', 'P0lin_wht.fits,P60lin_wht.fits,P120lin_wht.fits',
                  fitgeometry='rscale', calctype='double', interpolant='linear', fluxconserve=self.yes)
        sregister('POL*_backup.fits[3]', 'POL0V_backup.fits[1]', 'P0drz_wht.fits,P60drz_wht.fits,P120drz_wht.fits',
                  fitgeometry='rscale', calctype='double', interpolant='drizzle', fluxconserve=self.yes)

        #average in 10x10x10 blocks
        blkavg('P0lin_sci.fits', 'P0lin_smt.fits', b1=10, b2=10, b3=10, option='average')
        blkavg('P60lin_sci.fits', 'P60lin_smt.fits', b1=10, b2=10, b3=10, option='average')
        blkavg('P120lin_sci.fits', 'P120lin_smt.fits', b1=10, b2=10, b3=10, option='average')
        blkavg('P0drz_sci.fits', 'P0drz_smt.fits', b1=10, b2=10, b3=10, option='average')
        blkavg('P60drz_sci.fits', 'P60drz_smt.fits', b1=10, b2=10, b3=10, option='average')
        blkavg('P120drz_sci.fits', 'P120drz_smt.fits', b1=10, b2=10, b3=10, option='average')


    def doFinalDrizzle(self):
        """
        Does the final drizzling.

        :return: None
        """
        #we can now perform the final drizzle to drizzle all FLT images to POL frames
        kwargs = {'final_pixfrac': 1.0, 'skysub': False,
                  'final_outnx': 2300, 'final_outny': 2300,
                  'final_ra': 128.8369, 'final_dec': -45.1791,
                  'updatewcs': False, 'final_wcs': True, 'preserve': False,
                  'build': True, 'final_fillval': 1.0, #' final_wht_scl' : 'expsq',
                  'final_refimage': 'jbj901akq_flt.fits[1]'}
        for f in self.input:
            astrodrizzle.AstroDrizzle(input=f, mdriztab=False, editpars=False, **kwargs)


    def runAll(self):
        """
        Runs all steps of the pipeline at one go.

        :return: None
        """
        self.createAssociations()
        self.copyRaws()
        self.omitPHOTCORR()
        self.runCalACS()
        self.destripeFLT()
        #self.destripeFLTSMN()
        self.updateHeader()
        self.initialProcessing()
        self.findImprovedAlignment()
        self.registerPOLs()
        self.doFinalDrizzle()


def processArgs(printHelp=False):
    """
    Processes command line arguments.
    """
    parser = OptionParser()

    parser.add_option('-i', '--input',
                      dest='input',
                      help='Input association FILE to be processed [*POL*_asn.fits].',
                      metavar='string')

    parser.add_option('-p', '--pipeline',
                      dest='pipeline',
                      action='store_true',
                      help='Use OPUS FLT files. Assumes that _flt files are in ./opus/ folder.',
                      metavar='boolean')
    if printHelp:
        parser.print_help()
    else:
        return parser.parse_args()


if __name__ == '__main__':
    start = time()

    opts, args = processArgs()

    settings = dict(jref='/Users/sammy/Research/pulsar/data/12240/refs/',
                    mtab='/Users/sammy/Research/pulsar/data/12240/refs/')

    #settings = dict(jref='/astro/data/puppis0/niemi/pulsar/data/12240/refs/',
    #                mtab='/astro/data/puppis0/niemi/pulsar/data/12240/refs/')

    reduce = reduceACSWFCpoli(opts.input, **settings)

    if opts.pipeline:
        reduce.createAssociations()
        reduce.copyFLTs()
        reduce.destripeFLTSMN()
        reduce.updateHeader()
        reduce.initialProcessing()
        reduce.findImprovedAlignment()
        reduce.registerPOLs()
        reduce.doFinalDrizzle()
    else:
        reduce.runAll()

    elapsed = time() - start
    print 'Processing took {0:.1f} minutes'.format(elapsed / 60.)
