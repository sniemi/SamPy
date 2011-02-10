#! /usr/bin/env python
'''
ABOUT:
Creates STIS Spectroscopic pixel-to-pixel flat fields from RAW data.
Uses spline fits after dust motes, bad pixels, etc. have been masked
to fit and to remove the low frequency structure. The data are divided
by each fit to normalize the data before it is combined and co-added with
appropriate weighting of flux errors.

Both 50CCD and 52x2 data can be used. For 52x2 row fitting is not
done currently due to emission lines in the lamp spectrum.

For more information see STIS ISR 1999-06 by Bohlin and TIR 2010 by Niemi.

DEPENDS:
Python 2.5 or later (not 3.x compatible however)
NumPy
PyFITS
SciPy
matplotlib

TESTED:
Python 2.5.4
NumPy 1.4.0.dev7576
SciPy
PyFITS 2.2.2
matplotlib 1.0.svn

HISTORY:
Created on November 23, 2009

VERSION HISTORY:
0.1: testing version (SMN)
0.2: test release (SMN)
0.3: first full working version (SMN)
0.4: modified FITS output to comply with CDBS rules (SMN)
0.5: improved documentation (SMN)
0.6: fixed and imporved _badspot function (SMN)

@author: Sami-Matias Niemi
@version: 0.6
@organization: STScI
@contact: niemi@stsci.edu
@requires: NumPy
@requires: SciPy
@requires: PyFITS
@requires: matplotlib
@todo: For improved median filter, one could use scipy.ndimage.filters.median_filter
'''

import matplotlib
matplotlib.use('PDF')
matplotlib.rcParams['legend.fontsize'] = 9
import pyfits as PF
import numpy as N
import pylab as PL
import scipy.signal as SS
import scipy.interpolate as I
import scipy.optimize as O
import glob as G    
import datetime as D
import pyraf
from pyraf.iraf import stsdas,hst_calib,stis
from matplotlib import cm
from matplotlib.patches import Circle
import math, os, os.path, sys, shutil
        
__author__ = 'Sami-Matias Niemi'
__version__ = '0.5'

class Findfiles:
    '''
    Finds all files that are suitable for making a STIS CCD
    spectroscopy flat field. Searches from input directory
    all files that math the extension.
    '''
    def __init__(self, input, output, extension = '_raw'):
        '''
        Note that the detector (CCD) and optical element (G430M)
        has been hard coded to the self.obsmode dictionary.
        @param input: an input directory
        @param output: an output directory
        @param extension: an extension that used used to identify files  
        '''
        self.input = input
        self.output = output
        self.extension = extension
        self.obsmode = {'DETECTOR' : 'CCD', 'OPT_ELEM' : 'G430M'}

    def obsMode(self, filelist):
        '''
        Checks that the observation mode matches.
        Uses the hard coded self.obsmode dictionary.
        @param filelist: a list of file names to be tested.
        @return: a list of file names that are of right obsmode.  
        '''
        ok = True
        out = []
        for file in filelist:
            hdr = PF.open(file)[0].header
            for key in self.obsmode:
                if self.obsmode[key] != hdr[key]:
                    ok = False
            if ok:
                out.append(file)
        return out
    
    def gain(self, filelist, value):
        '''
        Checks that gain equals the given value.
        @param filelist: a list of file names to be tested
        @param value: a gain value that the gain have to match
        @return: a list of file names that match the gain value
        '''
        out = []
        for file in filelist:
            hdr = PF.open(self.input + file)[0].header
            if hdr['CCDGAIN'] == value:
                out.append(file)
        return out
    
    def apertureFilter(self, filelist, aperture = '50CCD', filter = 'Clear'):
        '''
        Checks that the aperture and filer matches the given ones.
        @param filelist: a list of file names to be tested.
        @param aperture: an aperture that the tested file must match.
        @param filter: a filter that the tested file must match.
        @return: a list of file names that match the aperture and filter.
        '''
        #another possibility could be:
        #APER_FOV= '50x50           '   / aperture field of view
        out = []
        for file in filelist:
            hdr = PF.open(self.input + file)[0].header
            if hdr['APERTURE'].strip() == aperture and \
               hdr['FILTER'].strip() == filter:
                out.append(file)
        return out
                
    def cenwave(self, filelist, cenwave = 5216):
        '''
        Checks that the central wavelength matches.
        @param filelist: a list of file names to be tested.
        @param cenwave: a central wavelength that the test file must match.
        @return a list of file names that match the aperture and filter.
        '''
        out = []
        for file in filelist:
            hdr = PF.open(self.input + file)[0].header
            if hdr['CENWAVE'] == cenwave:
                out.append(file)
        return out
    
    def slitwheelPos(self, filelist, positions, nominal, tolerance = 1):
        '''
        Finds and matches all slit wheel positions present in files listed in
        the filelist variable.
        @param filelist: a list of file names to be tested.
        @param positions: a list of positions that are used for matching.
        @param nominal: the nominal slit wheel position.      
        @param tolerance: tolerance of slit wheel steps.
        @return: dictionary of slit wheel positions and file names  
        '''
        #find all OSWABPS
        tmp = []
        pos = {}
        for file in filelist:
            hdr1 = PF.open(self.input + file)[1].header
            tmp.append([file, hdr1['OSWABSP']])

        for a in positions:
            pos[a] = [line[0] for line in tmp if line[1] > nominal + a - tolerance and line[1] < nominal + a + tolerance]

        return pos
    
    def writeToASCIIFile(self, data, outputfile, header = ''):
        '''
        Writes file lists to an ASCII file. Each line contains one filename.
        @param data: data that is written to the ascii file.
        @param outputfile: the name of the output file.
        @param header: header that is included to the beginning of the ascii file.
        '''
        try:
            file = open(self.input + outputfile, 'w')
        except:
            print 'Problem while opening file %s' % outputfile
    
        try:
            file.write(header)
            for line in data:
                file.write(line+'\n')
        except: pass

class PrepareFiles:
    '''
    Prepares files; modified header keywords.
    '''
    def __init__(self, input, output):
        '''
        Note that switches dictionary has been hard coded.
        It currently only changes the CRCORR keyword.
        @param input: an input directory
        @param output: an output directory
        '''
        self.input = input
        self.output = output
        self.switches = {'CRCORR' : 'PERFORM'}
        
    def changeKeywords(self, filelist):
        '''
        Modifies header keywords of FITS files.
        Switches self.switches keywords.
        @param filelist: a list of filenames 
        @todo: This will now crash if the keyword is not present...
        '''
        for file in filelist:
            fh = PF.open(file, 'update')
            hdr0 = fh[0].header
            for key in self.switches:
                hdr0[key] = self.switches[key]
            fh.close()

class MakeFlat:
    '''
    This class can be used to generate a pixel-to-pixel flat field 
    from given data files.
    '''
    def __init__(self, input, output):
        '''
        @param input: an input directory
        @param output: an output directory  
        '''
        self.input = input
        self.output = output
    
    def _plot50(self, flat, xcen, ycen, rad, fname):
        '''
        This function can be used to plot flat file images where
        dust motes have been circled. Will save the output figure
        to fname.pdf.
        @param flat: flat field array
        @param xcen: a list of x central coordinates for dust motes
        @param ycen: a list of y central coordinates for dust motes
        @param rad: a list of radius for dust motest   
        '''
        
        ax = PL.subplot(111)
        b = PL.gca()
        #P.title(fname)
        
        ims = ax.imshow(flat, origin='lower',
                        cmap = cm.gray,
                        interpolation = None,
                        vmin = 0.98,
                        vmax = 1.02)
        cb = PL.colorbar(ims, orientation='vertical')
        cb.set_label('Normalized Counts')
        
        #loop over xcen and ycen and ratio and draw circles
        for x, y, r in zip(xcen, ycen, rad):
            cir = Circle((x,y), radius=r, fc = 'none', ec = 'r')
            b.add_patch(cir)

        #PL.show()         
        PL.savefig(fname + '.pdf')       
        PL.close()
    
    def _plotFit(self, xpx, img, fit, good, i, xnod, ynod, fitynods, tmp, file, column = True):
        '''
        Plot Spline fit and the data for comparison for ith row or column.
        Will also plot median filtered data for columns. The plot is saved 
        to file_tmp_Fit.pdf
        @param xpx: x pixels
        @param img: y (counts) values
        @param fit: fitted y values
        @param good: mask that specifies good pixels
        @param i: the ith row or column
        @param xnod: a list of x node positions
        @param ynod: a list of original y node positions
        @param fitynods: a list of fitted y node positions
        @param tmp: median filtered count values
        @param file: the name of the file that is being plotted
        @param column: Boolean to define whether this is a column or row fit plot        
        '''
        
        fig = PL.figure()
        #P.title(file)
        
        left, width = 0.1, 0.8
        rect1 = [left, 0.3, width, 0.65]
        rect2 = [left, 0.1, width, 0.2]
    
        ax1 = fig.add_axes(rect2)  #left, bottom, width, height
        ax2 = fig.add_axes(rect1)        
        
        if column: ax2.plot(xpx, img[:,i], 'b-', label = 'Data', zorder = 1)
        else: ax2.plot(xpx, img[i,:], 'b-', label = 'Data', zorder = 1)
        if column: ax2.plot(xpx[good], tmp[good,i], 'y-', label='Median Filtered', zorder = 4)
        if column: ax2.plot(xpx, fit[:,i], 'r-', label = 'Spline Fit', lw = 1.5, zorder = 6)
        else: ax2.plot(xpx, fit[i,:], 'r-', label = 'Spline Fit', lw = 1.5, zorder = 6)
        ax2.plot(xpx, self._cspline(xnod, ynod, xpx), 'm-', label = 'Original Spline', zorder = 5)
        ax2.plot(xnod, ynod, 'ms', label = 'Original Nods', zorder = 7)
        ax2.plot(xnod, fitynods, 'ro', label = 'Fitted Nods', zorder = 7)

        if column: ax1.plot(xpx, fit[:,i]/img[:,i], 'r-', zorder = 6)
        else: ax1.plot(xpx, fit[i,:]/img[i,:], 'r-', zorder = 6)
        ax1.axhline(1. , zorder = 3)       

        ax1.set_xlim(-2,1025)
        ax2.set_xlim(-2,1025)
        ax2.set_ylim(0.98*N.min(tmp[good,i]), 1.02*N.max(tmp[good,i]))
        ax1.set_ylim(0.95, 1.05)
        ax1.set_ylim(0.95, 1.05)

        ax2.set_xticklabels([])
        ax2.set_yticks(ax2.get_yticks()[1:])
        #ax1.set_yticks(ax1.get_yticks()[::2])
        
        ax1.set_ylabel('Fit / Data')
        ax2.set_ylabel('Counts')
        if column: ax1.set_xlabel('Column %i Pixels' % i)
        else: ax1.set_xlabel('Row %i Pixels' % i)
    
        try:
            ax2.legend(numpoints = 1, shadow = True, fancybox = True, loc = 'best')
        except:
            ax2.legend(loc = 'best')
        
        if column: tmp = 'Column'
        else: tmp = 'Row'
        
        PL.savefig(file + '_%sFit.pdf' % tmp)
        PL.close()
    
    def _badspot(self, mask, opt_elem):
        '''
        Loads SMNdust.stis file that holds information about dust speck
        locations and sizes. It will return a mask where all dust motes
        have been marked. The function can be used for both L and M-modes
        as M-modes are shifted 2 pixels to left and their radius is set 
        to 16, except for the first two dust specks which are smaller.
        @summary: Adds dust motes to bad pixel mask. 
        @param mask: array of the same size as the image that is used to mask
        areas such as dust motes that should not be used for fitting.
        @param opt_elem: optical element that was used; L or M -mode
        @return: updated mask, x_centre, y_centre, radius of dust specks
        '''
        # mask indices
        y, x = N.indices(mask.shape)

        #read the dust file       
        dust = N.loadtxt('SMNdust.stis', comments='#')
        xcen = dust[:,0]
        ycen = dust[:,1]

        #first 2 spots on spectrum & are small. cut size
        rad = N.zeros(N.shape(dust)[0]) + 12
        rad[0:2] -= 4
        #; 99jun10 - shift stis medium disp spots left 
        if 'M' in opt_elem:
            #shifting badspots to left
            print'STIS Med resolution grating. Shifting badspots left.'
            xcen -= 2
            rad = rad*0 + 16
            rad[0:2] -= 4     # 1st 2 spots on spectrum & are small. cut size
        
        #update the mask
        for xc, yc, rd in zip(xcen, ycen, rad):
            xm = x - xc
            ym = y - yc
            radius = N.sqrt(xm**2 + ym**2)
            msk = radius < rd
            mask[msk] = 0

        return mask, xcen, ycen, rad    

    def _fitfunc(self, x, ynodes):
        '''
        The function that is being fitted.
        This can be changed to whatever function if needed.
        Note that ynodes can then be a list of parameters.
        k defines the order of the spline fitting, it is hard coded
        to be 3, but could be changed if needed.
        @param x: the x position where to evaluate the B-spline
        @param ynodes: y position of the nodes
        @return: 1-D evaluated B-spline value at x.
        '''
        return I.splev(x, I.splrep(self.xnodes, ynodes, k = 3))

    def _errfunc(self, ynodes, x, y):
        '''
        Error function; simply _fitfunction - ydata
        @param ynodes: y position of the nodes to be evaluated
        @param x: x positions where to evaluate the B-spline
        @param y: y positions 
        @return: Spline evaluated y positions - ydata
        '''
        return self._fitfunc(x, ynodes) - y

    def _splinefitScipy(self, x, y, ynodes, xnodes):
        '''
        Return the point which minimizes the sum of squares of M (non-linear)
        equations in N unknowns given a starting estimate, x0, using a
        modification of the Levenberg-Marquardt algorithm.
        @param x:
        @param y:
        @param ynodes:
        @param xnodes: 
        @return: fitted parameters, error/success message
        '''
        self.xnodes = xnodes
        return O.leastsq(self._errfunc, ynodes, args=(x, y))         
        
    def _cspline(self, x, y, t):
        '''
        Uses interpolation to find the B-spline representation of 1-D curve.
        @param x: x position
        @param y: y position
        @param t: position in which to evaluate the B-spline
        @return: interpolated y position of the B-sline
        '''
        tck = I.splrep(x, y)
        y2 = I.splev(t, tck)
        return y2
    
    def _writeCombinedFits(self, flat, err, dq, head, template, raws, output):
        '''
        Writes the combined flat field FITS to a file.
        Uses old reference files as a template.
        @param flat: flat field array
        @param err: error array
        @param dq: data quality array
        @param head: header dictionary
        @param template: template file to be used
        @param raws: list of raw file names that were used to create the flat
        @param output: name of the output file      
        '''
        #output = self.output + output  
        fh = PF.open(template)
        
        fh[1].data = flat.astype(N.float32)
        fh[2].data = err.astype(N.float32)
        fh[3].data = dq.astype(N.int16)
        
        hdu0 = fh[0].header
        hdr1 = fh[1].header
        hdr2 = fh[2].header
        hdr3 = fh[3].header
        
        #change 0th header keywords DESCRIP to have right length
        for key in head:
            if key == 'DESCRIP':
                #weird CDBS rule of 67 chars... 
                l = len(head[key])
                if l <= 67:
                    pad = '-'*(67 - l)
                    head[key] = head[key] + pad
                else:
                    print 'Problem with DESCRIP keyword, will truncate'
                    head[key] = head[key][:68]
            hdu0.update(key, head[key])

        #hardcoded changes
        hdu0.update('ORIGIN', 'PyFITS %s version' % PF.__version__)
        hdr1.update('ORIGIN', 'PyFITS %s version' % PF.__version__)
        hdr2.update('ORIGIN', 'PyFITS %s version' % PF.__version__)
        hdr3.update('ORIGIN', 'PyFITS %s version' % PF.__version__)
        hdu0.update('FILENAME', output[len(self.output):])
        #the first one makes a default FITS comment, but CDBS wants it with equal sign...
        #hdu0.update('COMMENT', 'Reference file was created by S.-M. Niemi, %s.' % D.datetime.today().strftime('%B %Y'))
        del hdu0['COMMENT']
        hdu0.add_comment('= Reference file was created by S.-M. Niemi, %s.' % D.datetime.today().strftime('%B %Y'),
                                before = 'ORIGIN')
        #fix the date
        date = D.datetime.today().strftime('%d/%m/%y')
        hdu0.update('FITSDATE', date)
        hdu0.update('DATE', date)
        hdr1.update('DATE', date)
        hdr2.update('DATE', date)
        hdr3.update('DATE', date)
        #fix history
        del hdu0['HISTORY']
        del hdu0['COMMENTS']
        hdu0.add_history('Created on %s, using the' % D.datetime.today().strftime('%B %d %Y'))
        hdu0.add_history('Python script STISCCDSpectroscopyFlat.py.')
        hdu0.add_history('')
        hdu0.add_history('The flat field for spectral modes is independent of')
        hdu0.add_history('wavelength but does change with time.  For this reason,')            
        hdu0.add_history('all the L-mode gratings have the same flat field, and all')            
        hdu0.add_history('the M-mode gratings have the same flat field. An average')            
        hdu0.add_history('flat is produced from datawith one to four million')            
        hdu0.add_history('electrons/pixel and is applicable to all CCD first order')           
        hdu0.add_history('modes after the dust motes are replaced by hose mote regions')         
        hdu0.add_history('from separate low or medium dispersion flats. Application of')       
        hdu0.add_history('flat to spectra of standard stars produces an rms residual')             
        hdu0.add_history('noise level as good as ~0.3%, which is comparable to the')               
        hdu0.add_history('residual noise achievable with no flat.')
        hdu0.add_history('New CCD p-flats constructed primarily from G430M spectral')
        hdu0.add_history('flats from program 11852. In L-mode flats, those regions')  
        hdu0.add_history('affected by dust motes were replaced by data from')        
        hdu0.add_history('the older cycle 7 l-flat file k2910262o_pfl.fits.')#k2910262o_pfl.fits 
        hdu0.add_history('The following input files were used:')
        for file in raws:
            hdu0.add_history(file[len(self.output):])
        
        #make the file
        fh.writeto(output)
        fh.close()
        print '%s has been written...' % output
    
    def _writeMakeFITS(self, file, flat, err, eps, sm, i, output):
        '''
        Writes the output to a FITS file. This is an intermediate product
        so the header is not CDBS compatible.
        @param file: the name of the file that is being used as a template
        @param flat: flat field array
        @param err: error array
        @param eps: eps array
        @param sm: total number of images
        @param i: total number of observations
        @param output: name of the output file name  
        '''
        output = self.output + output
        
        ifd = PF.open(file)
        orghdr0 = ifd[0].header
        
        #ofd = PF.HDUList(PF.PrimaryHDU(header = orghdr0))
        ofd = PF.HDUList(PF.PrimaryHDU())
        ifd.close()

        #create a new primary header with flat data
        #hdu = PF.ImageHDU(data=flat, header=ifd[1].header, name='IMAGE')
        hdu = PF.ImageHDU(data=flat, name='IMAGE')
        #update('target', 'NGC1234', 'target name')
        hdu.header.update('OPT_ELEM', orghdr0['OPT_ELEM'])
        #hdu.header.update('MODE_ID', orghdr0['MODE_ID'])
        hdu.header.update('APERTURE', orghdr0['APERTURE'])
        hdu.header.update('CENWAVE', orghdr0['CENWAVE'])
        hdu.header.update('DETECTOR', orghdr0['DETECTOR'])
        hdu.header.update('CCDGAIN', orghdr0['CCDGAIN'])
        hdu.header.update('TOTIMG', sm)
        hdu.header.update('TOTOBS', i)
        #add history section
        hdu.header.add_history('Flat Written by STISCCDSpectrscopyFlat.py')
        hdu.header.add_history('at %s UTC.' % D.datetime.utcnow())
        #checks that the header follows rules
        hdu.verify('fix')
        #appends to the HDUlist
        ofd.append(hdu)

        #create a new extension header with error array
        #hdu2 = PF.ImageHDU(data=err, header=ifd[2].header, name='ERR')
        hdu2 = PF.ImageHDU(data=err, name='ERR')
        hdu2.header.update('OPT_ELEM', orghdr0['OPT_ELEM'])
        #hdu2.header.update('MODE_ID', orghdr0['MODE_ID'])
        hdu2.header.update('APERTURE', orghdr0['APERTURE'])
        hdu2.header.update('CENWAVE', orghdr0['CENWAVE'])
        hdu2.header.update('DETECTOR', orghdr0['DETECTOR'])
        hdu2.header.update('CCDGAIN', orghdr0['CCDGAIN'])
        hdu2.header.update('TOTIMG', sm)
        hdu2.header.update('TOTOBS', i)
        #add history section
        hdu2.header.add_history('Flat Written by STISCCDSpectrscopyFlat.py')
        hdu2.header.add_history('at %s UTC.' % D.datetime.utcnow())
        #checks that the header follows rules
        hdu2.verify('fix')
        #appends to the HDUlist
        ofd.append(hdu2)

        #create a new extension header with eps array
        #hdu3 = PF.ImageHDU(data=eps, header=ifd[3].header, name='EPS')
        hdu3 = PF.ImageHDU(data=eps, name='EPS')
        hdu3.header.update('OPT_ELEM', orghdr0['OPT_ELEM'])
        #hdu3.header.update('MODE_ID', orghdr0['MODE_ID'])
        hdu3.header.update('APERTURE', orghdr0['APERTURE'])
        hdu3.header.update('CENWAVE', orghdr0['CENWAVE'])
        hdu3.header.update('DETECTOR', orghdr0['DETECTOR'])
        hdu3.header.update('CCDGAIN', orghdr0['CCDGAIN'])
        hdu3.header.update('TOTIMG', sm)
        hdu3.header.update('TOTOBS', i)
        #add history section
        hdu3.header.add_history('Flat Written by STISCCDSpectrscopyFlat.py')
        hdu3.header.add_history('at %s UTC.' % D.datetime.utcnow())
        #checks that the header follows rules
        hdu3.verify('fix')
        #appends to the HDUlist
        ofd.append(hdu3)
        
        #writes the file
        try:
            ofd.writeto(output + '.fits')
        except:
            print 'File %s exists...' % (output + '.fits')
            print 'Will write to %s instead!' % (output + 'SMN.fits')
            ofd.writeto(output + 'SMN.fits')
    
    def _doStats(self, data, mode):
        '''
        Calculates and prints out some basic statistics from the given data.
        @param data: data array from which the statistics is being calculated.
        @param mode: a string related to the mode (L/M)s
        '''
        #whole data
        std = N.std(data)
        mean = N.mean(data - 1.)
        rms = N.sqrt(mean**2 + std**2)
        
        #100 x 100 pixels at the centre of the data array
        sh = N.shape(data)
        x , y = sh[0]/2, sh[1]/2
        xmin = x - 50 if x - 50 > 0 else 0
        xmax = x + 50 if x + 50 <= sh[0] else sh[0]
        ymin = y - 50 if y - 50 > 0 else 0
        ymax = y + 50 if y + 50 <= sh[1] else sh[1]
        
        ds = data[ymin:ymax, xmin:xmax]
        stds = N.std(ds)
        means = N.mean(ds - 1)
        rmss = N.sqrt(means**2 + stds**2)
        
        print '-'*15 + 'Statistics of %s' % mode + '-'*15
        print '%15s'*4 % ('ARRAY', 'MEAN', 'STDEV', 'RMS Noise')
        print '%15s%15.5f%16.6f%14.6f' % ('Full', mean + 1., std, rms)
        print '%15s%15.5f%16.6f%14.6f' % ('Centre', means + 1., stds, rmss)
    
    def _fitflat(self, hdr, img, mask, nodes, col = False, nomed = False, file = 'name'):
        '''
        Creates spline fitted flat field array and masked image.
        Uses img for the data and nodes for the number of nodes.
        This function can be used to fit both column and row direction.
        This choice is controlled with the boolean col.
        @param hdr: header
        @param img: flat field image
        @param mask: mask that is being applied and updated
        @param nodes: number of nodes being used for the spline fits
        @param col: boolean, column (True) or row (False, default) fit
        @param nomed: boolean, median (True) or no median filtering (False, default)
        @param file: the name of the plot file 
        @return: Spline fitted data, img / fit, mask
        '''
        
        s = N.shape(img)
        nx = s[0]
        ny = s[1]
        
        det = hdr['DETECTOR'].strip()

        #set up positions of spline nodes
        if col:
            xpx = N.arange(ny, dtype = int)
            xnod = N.arange(nodes)*(ny-1.)/(nodes-1.)   # spaced nodes incl ends
        else:
            xpx = N.arange(nx, dtype = int)
            xnod = N.arange(nodes)*(nx-1.) / (nodes-1.)   #spaced nodes incl ends
                    
        #using array copy
        fit = img.copy() # unfit lines will be unit flats
        tmp = img.copy()

        # initialize for 1-d median filter
        bad = N.where((mask == 0) & (fit == 0.0))
        nbad = len(bad)
        if nbad > 0: fit[bad] = 1.0               #to avoid 0/0 in img/fit for all bad row
     
        if col == False:
            #add extra pt half way btwn first and last pts at ends
            dl = xnod[1] - xnod[0] 
            xnod = N.insert(xnod, 1, dl/2.)
            xnod = N.insert(xnod, -1, (xnod[-1] - dl/2.))
            if nomed == False:
                'Print MEDIAN filtering for row fitting!'
                tmp = SS.medfilt2d(img, 11)  # default for CCDs
     
        loop = ny - 1
        if col: loop = nx - 1
        lenfit = nx
        if col:
            lenfit = ny
        nskip = 0

        for i in range(loop+1):
            if col: #column fitting
                good = mask[:,i] > 0
                ngd = len(mask[good])
                if float(ngd)/lenfit < 0.55:
                    mask[:,i] = -1
                    nskip += 1
                    continue
                if nomed == False:
                    tmp[good, i] = SS.medfilt(img[good, i], 13)

                #this is significantly better initial guess than the one below
                ynod = N.array([N.mean(tmp[x-5:x+5, i]) for x in xnod])
                ynod[N.isnan(ynod)] = N.mean(tmp[good, i])
                #ynod = xnod*0 + N.mean(tmp[good, i])
            
                fitynods, _t = self._splinefitScipy(xpx[good], tmp[good, i], ynod, xnod)
                fit[:,i] = self._cspline(xnod, fitynods, xpx)
                
                if i == 650: self._plotFit(xpx, img, fit, good, i, xnod, ynod, fitynods, tmp, file)
            
            else: #row fitting
                good = mask[i,:] > 0
                ngd = len(mask[good])
                if float(ngd)/lenfit < 0.55:
                    mask[i,:] = -1
                    nskip += 1
                    continue

                #reallocate xnodes esp for STIS tung 52x2 w/ 1st 215 px ignored
                xnod = N.arange(nodes)*(N.max(xpx[good])-xpx[good][0])/(nodes-1) + xpx[good][0]                                           
                ynod = N.array([N.mean(tmp[i, x-5:x+5]) for x in xnod])
                ynod[N.isnan(ynod)] = N.mean(tmp[i, good])
                fitynods, _t = self._splinefitScipy(xpx[good], tmp[i, good], ynod, xnod)
                fit[i,:] = self._cspline(xnod, fitynods, xpx)
                if i == 600: self._plotFit(xpx, img, fit, good, i, xnod, ynod, fitynods, tmp, file, column = False)
       
        print 'FITLAT with %i NODES' % len(xnod)
        print '%i fits were skipped...' % nskip
        
        bad = N.where(fit == 0)
        if len(bad[0]) > 0:
            print bad
            print 'Problem at fit points, will replace with 1.0'
            fit[bad] = 1.0            #to avoid 0/0 in img/fit                                                                                             
        flat = img/fit

        #self._plot50(flat, (0,0), (0,0), (0,0), 'foo')

        return fit, flat, mask
        
        
    def crreject(self, filelist):
        '''
        Runs CalSTIS for each file in the file list.
        Uses default settings.
        @param filelist: list of files being run through CalSTIS.
        '''
        for file in filelist:
            stis.calstis(file)
            
    def combine(self, filelist, output, crsigmas = '20'):
        '''
        Combines all files in filelist using ocrreject PyRAF task.
        @param filelist: filelist being processed 
        @param output:  output list
        @param crsigmas: cosmic ray rejection sigma clipping value
        '''
        stis.ocrreject(filelist, output = output, crsigmas = crsigmas)
        
    def make50CDD(self, files, colnodes = 25, rownodes = 13):
        '''
        Makes a flat field from all files that has been taken with clear
        aperture (50CCD). Each input file will write an output FITS file.
        Makes also plots out from the data that has been fitted and masked
        that can be used to check the results for any failed spline fits, etc.
        @param files: a list of file names that are being used 
        @param colnodes: the number of nodes used of column fits (default = 25)
        @param rownodes: the number of nodes used for row fits (default = 13)  
        @summary: Creates a flat field
        @todo: rewrite away from IDL
        '''
        files = [self.output + x for x in files]
        
        for i, file in enumerate(files):
            #open file and pull out required information
            fh = PF.open(file)
            dcr = fh[1].data
            err = fh[2].data
            eps = fh[3].data
            hdr0 = fh[0].header
            hdr1 = fh[1].header
            fh.close()
        
            lamp = hdr0['SCLAMP'].strip()
            aper = hdr0['APERTURE'].strip()
            mode = hdr0['OPT_ELEM'].strip()
            gain = 'g' + str(hdr0['CCDGAIN'])
            
            if 'M' in mode:
                mode += '-' + str(hdr0['CENWAVE']) + '_'
            if aper == '50CCD': mode += '50CCD'
                     
            eps = 0*eps
            nused = hdr1['NCOMBINE']
            sm = N.max(nused)
            
            ny, nx = N.shape(dcr)

            onemsk = N.ones((nx,ny), dtype = N.int)          #mask of where flat = 1 
            ignmsk = N.ones((nx,ny), dtype = N.int)          #mask of pts to keep, but ignore in flt

            #bad spots to ignmsk
            ignmsk, xcen, ycen, rad = self._badspot(ignmsk, hdr0['OPT_ELEM'].strip())
    
            onemsk[:,0] = 0                   # general STIS bad 1st and last col                                                                                  
            onemsk[:,1023] = 0
            onemsk[994:1024,:] = 0            # "vignetted" at top indep of slit pos.                                                                              
            onemsk[0,:] = 0                   # first row                                                                                                          
            onemsk[0:5,253:259] = 0           # 99feb4 hole made vert stripe at bott.                                                                              
            onemsk[14:16,768:770] = 0         # ... for D2 G230LB, 50CCD        
            
            if aper== '50CCD':
                onemsk[0:15, :] = 0
            
            cenlo = 280
            cenhi = 742                         #  orig fid centers
            
            if 'M' in mode:
                if aper == '50CCD':
                    onemsk[0:38, :] = 0
                    onemsk[975:1024, :] = 0     # top clipped
                cenlo = 304
                cenhi = 766
            
            #fiducial masks
            if aper != '50CCD':
                onemsk[cenlo-14:cenlo+15, :] = 0
                onemsk[cenhi-19:cenhi+20, :] = 0
                                                                                                                           
            err[onemsk == 0] = 0               # err=0 means do not use data                                                                                
            eps[onemsk == 0] = 512             # all px rejected flag                                                                                       
            onemsk[eps > 150] = 0              # keep warm px=150
            
            #fit in col dir first because of glints along L&R edges for 50ccd D2-5216
            cmask = onemsk*ignmsk
            PL.imshow(cmask, origin='lower', interpolation = None)
            PL.savefig(file[:-5]+'_cmask.pdf')
            PL.close()
            
            colfit, flat, cmask = self._fitflat(hdr0, dcr, cmask, colnodes, col = True, file = file[:-5])
    
            if lamp == 'TUNGSTEN' and aper == '52X2':
                print ' Cannot do row fit for ', lamp, aper
                fit = colfit.copy()
                rmask = cmask.copy()
            else:
                #iterate w/ row fits for no em lines
                #ignmsk areas filled w/ the fits
                rmask = onemsk.copy()
                if mode == 'G430M-5216_50CCD':
                    print'Omit rowfit at ends of ', mode
                    rmask[:,0:61] = 0
                    rmask[:,930:1024] = 0
            
                fit, flat, rmask = self._fitflat(hdr0, colfit, rmask, rownodes, nomed = True, file = file[:-5])

                if mode == 'G430M-5216_50CCD':
                    fit[:, 0:61] = colfit[:, 0:61]      # bumps at ends of rows                                                                              
                    fit[:, 930:1024] = colfit[:, 930:1024]
            
            flat = dcr/fit
            
            indx = N.where((cmask == -1) & (rmask == -1))   # neither row or col fit
            if len(indx) > 0: err[indx] = 0         #err=0 means do not use data 
            if len(indx) > 0: eps[indx] = 512       #all px rejected flag

            flat[onemsk == 0] = 1.0
            err = err/fit                             # error in units of flat           
            
            #remove vertical ringing
            yflat = N.ones(1024)
            for iy in range(1024):
                inc = cmask[iy, :] == 1
                if len(flat[iy, inc]) > 0: yflat[iy] = N.mean(flat[iy, inc])
            yflatm = SS.medfilt(yflat, 5)
            for iy in range(1024): flat[iy,:] = flat[iy,:]/yflatm[iy]
            if len(flat[N.isnan(flat)]) > 0:
                print 'ERROR: there are NaNs in the flat:', flat[N.isnan(flat)]

            #make plot
            self._plot50(flat, xcen, ycen, rad, file[:-5])
   
            #create a FITS file
            fname=['ppG430M_50CCD_gain%s_flat' % gain[1:],'ppG430M_50CCD_gain%s_flat' % gain[1:]]
            self._writeMakeFITS(file, flat, err, eps, sm, i, fname[i])       

    def make52X2(self, files, slitpos, colnodes = 13, rownodes = 13):
        '''
        Makes a flat field from all files that has been taken with a long slit
        in the light path (52x2). Each input file will write an output FITS file.
        Makes also plots out from the data that has been fitted and masked
        that can be used to check the results for any failed spline fits, etc.
        @param files: a list of file names that are being used 
        @param slitpos: a list of slit positions that correspond to each file
        @param colnodes: the number of nodes used of column fits (default = 13)
        @param rownodes: the number of nodes used for row fits (default = 13)  
        @summary: Creates a flat field
        @todo: rewrite away from IDL. Get rid off the hard coded file names
        '''
        files = [self.output + x for x in files]
        
        for i, file in enumerate(files):
            #open file and pull out required information
            fh = PF.open(file)
            dcr = fh[1].data
            err = fh[2].data
            eps = fh[3].data
            hdr0 = fh[0].header
            hdr1 = fh[1].header
            fh.close()
        
            lamp = hdr0['SCLAMP'].strip()
            aper = hdr0['APERTURE'].strip()
            mode = hdr0['OPT_ELEM'].strip()
            gain = 'g' + str(hdr0['CCDGAIN'])
            
            if 'M' in mode:
                mode += '-' + str(hdr0['CENWAVE']) + '_'
            if aper == '50CCD': mode += '50CCD'
                      
            eps = 0*eps
            nused = hdr1['NCOMBINE']
            #nused = hdr1['TOTIMG']
            sm = N.max(nused)
            sum='sm%i' % (sm)
            print 'Processing file %s (%s)' % (file, mode+gain+sum)
            
            ny, nx = N.shape(dcr)

            onemsk = N.ones((nx,ny), dtype = N.int)          #mask of where flat = 1 
            ignmsk = N.ones((nx,ny), dtype = N.int)          #mask of pts to keep, but ignore in flt

            #bad spots to ignmsk
            ignmsk, xcen, ycen, rad = self._badspot(ignmsk, hdr0['OPT_ELEM'].strip())
    
            onemsk[:,0] = 0                   # general STIS bad 1st and last col                                                                                  
            onemsk[:,1023] = 0
            onemsk[1013:1024, :] = 0          # "vignetted" at top indep of slit pos.                                                                              
            onemsk[0,:] = 0                   # first row                                                                                                          
            onemsk[0:5,253:259] = 0           # 99feb4 hole made vert stripe at bott.                                                                              
            onemsk[14:16,768:770] = 0         # ... for D2 G230LB, 50CCD        
            
            cenlo = 280 - 0.0141*slitpos[i]
            cenhi = 742 - 0.0141*slitpos[i]   #  orig fid centers
            
            if 'M' in mode:
                cenlo = 286 - 0.0141*slitpos[i]
                cenhi = 748 - 0.0141*slitpos[i]
                botedge = 22 - 0.0141*slitpos[i]
                topedge = 1042 - 0.0141*slitpos[i]
                
                if botedge < 1: botedge = 1
                if topedge > ny - 1: topedge = ny - 1
                
                if '5126' in mode:
                    onemsk[0:botedge+1, :] = 0   # bad at bottom
                    onemsk[topedge:ny, :] = 1   # top OK                                                                                                            
                    cenlo = 304 - 0.0141*slitpos[i]
                    cenhi = 766 - 0.0141*slitpos[i]
                if '6094' in mode:
                    onemsk[1013:1024, :] = 0
                    cenlo = 259 - 0.0141*slitpos[i]
                    cenhi = 721 - 0.0141*slitpos[i]

            #print file, cenlo, cenhi
            cenlo += 18.
            cenhi += 18.
            
            #fiducial masks
            if '52' in aper:                                                                            
                onemsk[cenlo-14:cenlo+15, :] = 0
                onemsk[cenhi-19:cenhi+20, :] = 0
                onemsk[0:botedge+1, :] = 0
                onemsk[topedge:ny, :] = 0
                                                                                                                           
            err[onemsk == 0] = 0               # err=0 means do not use data                                                                                
            eps[onemsk == 0] = 512             # all px rejected flag                                                                                       
            onemsk[eps > 150] = 0              # keep warm px=150
            
            #fit in col dir first because of glints along L&R edges for 50ccd D2-5216
            cmask = onemsk*ignmsk
            PL.imshow(cmask, origin='lower', interpolation = None)
            PL.savefig(file[:-5]+'_cmask.pdf')
            PL.close()
            #PL.imshow(onemsk, origin='lower', interpolation = None)
            #PL.savefig(file[:-5]+'_onemask.pdf')
            #PL.close()
            #PL.imshow(ignmsk, origin='lower', interpolation = None)
            #PL.savefig(file[:-5]+'_ignmask.pdf')
            #PL.close()

            colfit, flat, cmask = self._fitflat(hdr0, dcr, cmask, colnodes, col = True, file = file[:-5])
    
            if lamp == 'TUNGSTEN' and aper == '52X2':
                print ' Cannot do row fit for ', lamp, aper
                fit = colfit.copy()
                rmask = cmask.copy()
            else:
                #iterate w/ row fits for no em lines
                #ignmsk areas filled w/ the fits
                rmask = onemsk.copy()
                if mode == 'G430M-5216_50CCD':
                    print'Omit rowfit at ends of ', mode
                    rmask[:,0:61] = 0
                    rmask[:,930:1024] = 0
            
                fit, flat, rmask = self._fitflat(hdr0, colfit, rmask, rownodes, nomed = True, file = file[:-5])

                if mode == 'G430M-5216_50CCD':
                    fit[:, 0:61] = colfit[:, 0:61]      # bumps at ends of rows                                                                              
                    fit[:, 930:1024] = colfit[:, 930:1024]
            
                flat = dcr/fit
            
            indx = N.where((cmask == -1) & (rmask == -1))   # neither row or col fit
            if len(indx) > 0: err[indx] = 0         #err=0 means do not use data 
            if len(indx) > 0: eps[indx] = 512       #all px rejected flag

            flat[onemsk == 0] = 1.0
            err = err/fit                             # error in units of flat           
            
            #remove vertical ringing
            yflat = N.ones(1024)
            for iy in range(1024):
                inc = cmask[iy, :] == 1
                if len(flat[iy, inc]) > 0:
                    yflat[iy] = N.mean(flat[iy, inc])
                    flat[iy,:] = flat[iy,:]/yflat[iy]
            if len(flat[N.isnan(flat)]) > 0:
                print 'ERROR: there are NaNs in the flat:', flat[N.isnan(flat)]

            #make plot
            self._plot50(flat, xcen, ycen, rad, file[:-5])
   
            #create a FITS file
            fname=['pG430M_52x2_gain4m7300_flat','pG430M_52x2_gain4m3640_flat',
                   'pG430M_52x2_gain4p0000_flat','pG430M_52x2_gain4p3640_flat',
                   'pG430M_52x2_gain4p7300_flat']
            
            self._writeMakeFITS(file, flat, err, eps, sm, i, fname[i])
        
    def CombineFinalFlatS(self, list, headerl, headerm, raws):
        '''
        Combines all idicidual images to form a single combined flat field for 
        each given mode. Handles flux, error and data quality arrays. Images are
        combined using weights for each pixel that are calculated using the error
        arrays. Will take into account the only the pixels that has not been
        flagged in the data quality array.
        This function will also call other functions to calculate some basic
        statistics and to create some plots from the combined image.
        For L-modes the dust have to pasted from another file. Will use the one
        that is in the CDBS: /grp/hst/cdbs/oref/k2910262o_pfl.fits.
        @param list: a list of files to be combined
        @param headerl: a header for the l-mode combined image
        @param headerm: a header for the m-mode combined image
        @param raws: list of raw file names that were used to create the flat
        '''
        #hard coded value
        siglim = 5
        
        nimage = len(list)

        #make zero arrays
        added_flux = N.zeros((1024, 1024))
        added_error = N.zeros((1024, 1024))
        added_dq = N.zeros((1024, 1024))
        weights = N.zeros((1024, 1024))
                
        fluxall = N.zeros((1024, 1024, nimage))
        errorall = N.zeros((1024, 1024, nimage))
        flagsall = N.zeros((1024, 1024, nimage))

        for i, file in enumerate(list):
            fh = PF.open(file)
            fluxin = fh[1].data
            errorin = fh[2].data
            flagsin = fh[3].data
            fh.close()
            
            if i > 1: flagsin[225:801, 180] = flagsin[225:801, 180] + 1024
            
            fluxall[:,:,i] = fluxin.copy()
            errorall[:,:,i] = errorin.copy()
            flagsall[:,:,i] = flagsin.copy()

        for ix in range(1024):
            for iy in range(1024):
                added_dq[iy, ix] = N.min(flagsall[iy, ix, :])
                ig = N.where((flagsall[iy, ix, :] == 0) & (errorall[iy, ix,:] > 0.0))
                if len(ig[0]) <= 0:
                    added_flux[iy, ix] = 1.
                    added_error[iy,ix] = 0.1
                elif len(ig[0]) <= 2:
                    added_flux[iy,ix] = N.sum(fluxall[iy,ix,ig]/errorall[iy,ix,ig]**2)/N.sum(1./errorall[iy,ix,ig]**2)
                    added_error[iy,ix] = N.sqrt(1./N.sum(1./errorall[iy,ix,ig]**2))
                else:
                    center = N.median(fluxall[iy,ix,ig])
                    std = N.max(errorall[iy,ix,ig])
                    igg = N.where(N.abs(fluxall[iy,ix,ig] - center) < siglim*std)
                    if len(igg[0]) >= 1:
                        cov = N.where(((flagsall[iy, ix, :] == 0) & (errorall[iy, ix,:] > 0.0)) & (N.abs(fluxall[iy,ix,:] - center) < siglim*std))
                        added_flux[iy,ix] = N.sum(fluxall[iy,ix,cov]/errorall[iy,ix,cov]**2)/N.sum(1./errorall[iy,ix,cov]**2)
                        added_error[iy,ix] = N.sqrt(1./N.sum(1./errorall[iy,ix,cov]**2))
                    else:
                        added_flux[iy,ix] = center
                        added_error[iy,ix] = std
        
        #fix spurious errors
        added_error[added_error > 0.1] = 0.1
        added_flux[added_flux < 0.0] = 1.
        added_dq[added_flux < 0.0] = 1024
        
        #low and med res copies
        flat_l = added_flux.copy()
        flat_m = added_flux.copy()
        err_l = added_error.copy()
        err_m = added_error.copy()
        dq_l = added_dq.copy()
        dq_m = added_dq.copy()

        # flag and patch dust motes (dq=1024)                                                                                                                                  
        m_mote = N.ones((1024,1024), dtype = N.int)
        l_mote = N.ones((1024,1024), dtype = N.int)
        l_mote, xlcen, ylcen, radl = self._badspot(l_mote, 'G430L')
        m_mote, xmcen, ymcen, radm = self._badspot(m_mote, 'G430M')
        
        # since basic flats are from m mode data, have to also replace area covered by                                                                                         
        # m-mode motes with "good" l mode data to produce l mode pflat.                                                                                                        
        l_mote_ext = l_mote*m_mote

        # flag dust motes with 1024                                                                                                                                            
        dq_l[l_mote_ext == 0] = dq_l[l_mote_ext == 0] + 1024
        dq_m[m_mote == 0] = dq_m[m_mote == 0] + 1024

        # leave m-mode modes alone, but paste into l_mode motes from another file                                                                                                                                                                  
        templ_f = PF.open('/grp/hst/cdbs/oref/k2910262o_pfl.fits')[1].data
        templ_e = PF.open('/grp/hst/cdbs/oref/k2910262o_pfl.fits')[2].data
        l_mote_loc = N.where(l_mote_ext == 0)
        flat_l[l_mote_loc] = templ_f[l_mote_loc]
        err_l[l_mote_loc] = templ_e[l_mote_loc]

        # write individual extensions of low and high disp file
        templ = '/grp/hst/cdbs/oref/n491401ho_pfl.fits' #
        tempm = '/grp/hst/cdbs/oref/n491401ko_pfl.fits' #'n491401eo_pfl.fits'
        self._writeCombinedFits(flat_l, err_l, dq_l, headerl, templ, raws, self.output + 'coadd_comb_reject_l.fits')          
        self._writeCombinedFits(flat_m, err_m, dq_m, headerm, tempm, raws, self.output + 'coadd_comb_reject_m.fits')

        #make some extra plots
        self._plot50(flat_l, xlcen, ylcen, radl, 'coadd_comb_reject_l')
        self._plot50(flat_m, xmcen, ymcen, radm, 'coadd_comb_reject_m')
        
        #print out some information
        self._doStats(flat_l, 'L-mode Flat')
        self._doStats(flat_m, 'M-mode Flat')
    
    def MakeCopies(self):
        '''
        Copies newly created p-flat files over to a new directory and
        names the new files appropriately which are appropriate for CDBS
        delivery.
        '''
        outdir = './final/'

        try:
            os.mkdir(outdir)
        except:
            print 'Final output directory exists'
            pass

        #shutil.copy(src, dst)
        
        l = './out/coadd_comb_reject_l.fits'
        m = './out/coadd_comb_reject_m.fits'
        
        mfiles = ['g230mb_new_pfl.fits', 'g430m_new_pfl.fits', 'g750m_new_pfl.fits']
        lfiles = ['g230lb_new_pfl.fits', 'g430l_new_pfl.fits', 'g750l_new_pfl.fits']

        for file in mfiles:    
            shutil.copy(m, outdir + file)
            fh = PF.open(outdir + file, mode='update')
            hdr0 = fh[0].header
            hdr0['FILENAME'] = file
            hdr0['OPT_ELEM'] = file[:file.find('_')].upper() 
            fh.close()
        for file in lfiles:
            shutil.copy(l, outdir + file)
            fh = PF.open(outdir + file, mode='update')
            hdr0 = fh[0].header
            hdr0['FILENAME'] = file
            hdr0['OPT_ELEM'] = file[:file.find('_')].upper() 
            fh.close()

def process_args(just_print_help = False):
    '''
    Processes and parses the command line arguments.
    Will also print help and the version of the script if requested.
    '''
    from optparse import OptionParser
    
    usage = 'usage: %prog [options]'
    desc = 'This script can be used to generates STIS CCD spectroscopic flat field images.'
    
    parser = OptionParser(usage = usage, version='%prog ' + __version__, description = desc)
         
    parser.add_option('-o', '--output', dest='output', 
                      help='Output directory. If not given, will use ./out/', 
                      metavar='string')
    parser.add_option('-i', '--input', dest='input', 
                      help='Input directory. If not given, will use ./obs/', 
                      metavar='string')
    parser.add_option('-f', '--filelists', action='store_true', dest='filelist',
                      help='Will list each suitable crj file in a file list.')
    parser.add_option('-c', '--crreject', action='store_true', dest='crreject',
                      help='Will run CalSTIS for all raw files.')
    parser.add_option('-b', '--combine', action='store_true', dest='combine',
                      help='Will combine suitable images using ocrreject.')
    parser.add_option('-5', '--50ccd', action='store_true', dest='ccd',
                      help='Will generate flat field images from 50CCD observations.')
    parser.add_option('-s', '--slit', action='store_true', dest='slit',
                      help='Will generate flat field images from 52X2 observations.')    
    parser.add_option('-g', '--generate', action='store_true', dest='generate',
                      help='Will generate the final flat field images.')  
    parser.add_option('-m', '--make', action='store_true', dest='copy',
                      help='Will copy generated files to a new directory.')  
    parser.add_option('--stats', action='store_true', dest='stats',
                      help='Calculates some statistics from coadd_*fits files.')
      
    if just_print_help:
        parser.print_help()
    else:
        return parser.parse_args()

def checkZeroArguments(opts):
    '''
    Checks if no command line arguments were given.
    @param opts: option parser instance. 
    @requires: True or False
    '''
    for x in opts.__dict__:
        if opts.__dict__[x] is not None:
            return True
    return False    

if __name__ == '__main__':
    '''
    The main program starts here.
    '''
    #HARDCODED values:
    slitpos = [-7300, -3640, 0, 3640, 7300]     #slit wheel positions
    
    #option parser
    opts, args = process_args()
    #process zero arguments
    if checkZeroArguments(opts) == False:
        print 'Will do all'
        opts.filelist = True
        opts.crreject = True
        opts.combine = True
        opts.ccd = True
        opts.slit = True
        opts.generate = True
        opts.copy = True
    if opts.output is None:
        output = './out/'
    else:
        output = opts.output
    if opts.input is None:
        input = './obs/'
    else:
        input = opts.input
    
    #test that folders exists
    if os.path.isdir(input) == False: sys.exit('No valid input directory, please specify one!')
    if os.path.isdir(output) == False: os.mkdir(output)
    
    #objects
    F = Findfiles(input, output)
    P = PrepareFiles(input, output)
    M = MakeFlat(input, output)

    #find all raws that match the obs mode
    allRaws = G.glob(input + '*_raw.fits')
    raws = F.obsMode(allRaws)

    if opts.crreject :
        #modify headers and run calstis
        print '\n\nModifying header keywords and running CalSTIS...'
        P.changeKeywords(raws)
        M.crreject(raws)
    
    if opts.filelist:
        print '\n\nGenerating file lists...'
        #find all crj files
        org = os.getcwd()
        os.chdir(input)        
        allCrjs = G.glob('*_crj.fits')
        os.chdir(org)
        #50ccd
        cr = F.apertureFilter(allCrjs, aperture = '50CCD', filter = 'Clear')
        gain1 = F.gain(cr, value = 1)
        gain4 = F.gain(cr, value = 4)
        if len(gain1) == 0 or len(gain4) == 0:
            print 'Did not find find suitable 50CCD Clear files for one of the gain settings...'
        else:
            F.writeToASCIIFile(gain1, 'g430m_50ccd_gain1_crj.txt')
            F.writeToASCIIFile(gain4, 'g430m_50ccd_gain4_crj.txt')
        #52x2
        nominal = 3242355
        a52x2 = F.apertureFilter(allCrjs, aperture = '52X2', filter = 'Clear')
        poss = F.slitwheelPos(a52x2, slitpos, nominal, tolerance = 2)
        for val in poss:
            if val < 0:
                F.writeToASCIIFile(poss[val], 'g430m_52x2m%i_crj.txt' % -val)
            elif val == 0:
               F.writeToASCIIFile(poss[val], 'g430m_52x2_crj.txt')
            else:
                F.writeToASCIIFile(poss[val], 'g430m_52x2p%i_crj.txt' % val)

    if opts.combine:
        #combine similar images
        org = os.getcwd()
        os.chdir(input)
        txts = G.glob('*.txt')
        print '\n\nCombining individual images...'
        for a in txts:
            M.combine('@'+a, a[:-3] + 'fits', crsigmas = '20')
            shutil.move(a[:-3] + 'fits', '../' + output)
        os.chdir(org)
    
    if opts.ccd:
        #Make 50CCD flats
        print '\n\nCreating 50CCD flats'
        ccdFiles = ['g430m_50ccd_gain1_crj.fits', 'g430m_50ccd_gain4_crj.fits']
        #M.make50CDD(ccdFiles, colnodes = 25, rownodes = 13)
        M.make50CDD(ccdFiles, colnodes = 20, rownodes = 13) #colnodes = 20 seems to work better than 25

    if opts.slit:
        #Make 52x2 flats
        print '\n\nCreating 52x2 flats'
        Sfiles_tmp = ['g430m_52x2m7300','g430m_52x2m3640','g430m_52x2','g430m_52x2p3640','g430m_52x2p7300']
        Sfiles = [file + '_crj.fits' for file in Sfiles_tmp]
        M.make52X2(Sfiles, slitpos, colnodes = 13, rownodes = 13)
    
    if opts.generate:
        #Combine to a final flat
        print '\n\nCombining flats'
        toCombine = ['ppG430M_50CCD_gain4_flat.fits',
                     'ppG430M_50CCD_gain1_flat.fits',
                     'pG430M_52x2_gain4m7300_flat.fits',
                     'pG430M_52x2_gain4m3640_flat.fits',
                     'pG430M_52x2_gain4p0000_flat.fits',
                     'pG430M_52x2_gain4p3640_flat.fits',
                     'pG430M_52x2_gain4p7300_flat.fits']
        headerl = {'USEAFTER' : 'May 12 2009 00:00:00',
                   'DESCRIP' : 'REVISED ON-ORBIT STIS SPECTROSCOPIC CCD P-FLAT FOR L-MODES',
                   'PEDIGREE': 'INFLIGHT 16/08/2009 15/12/2009'}
        headerm = {'USEAFTER' : 'May 12 2009 00:00:00',
                   'PEDIGREE': 'INFLIGHT 16/08/2009 15/12/2009',
                    'DESCRIP' : 'REVISED ON-ORBIT STIS SPECTROSCOPIC CCD P-FLAT FOR M-MODES'}
        toCombine = [output + line for line in toCombine]
        M.CombineFinalFlatS(toCombine, headerl, headerm, raws)
    
    if opts.copy:
        print '\n\nMaking copies...'
        M.MakeCopies()
        
    if opts.stats:
        M._doStats(PF.open('./out/coadd_comb_reject_l.fits')[1].data, 'L')
        M._doStats(PF.open('./out/coadd_comb_reject_m.fits')[1].data, 'M')
    
    print '\n\nScript Ends!'
