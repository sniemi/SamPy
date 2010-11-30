#! /usr/bin/env python
'''
ABOUT:
A script to visualize extraction and background box locations
respect to the spectral strip. Creates PDF files from given
FITS files.

Works with counts and flt COS FUV files.

DEPENDS:
Python 2.5 or later, but not 3.x
NumPy
PyFITS
matplotlib

TESTED:
Python 2.5.1
NumPy: 1.4.0.dev7576
PyFITS: 2.2.2
matplotlib 1.0.svn

USAGE:
python PlotExtractionBox.py [*file_name*]
where
[*filename*] is an optional keyword that can be either a single
file or string that contains wild cards e.g. "*_counts_*"
If no filename given program will search for all files that
contain string _counts_.

HISTORY:
Created on October 22, 2009

VERSION:
0.2: test release (SMN)

@author: Sami-Matias Niemi (niemi@stsci.edu)
'''

import matplotlib
try:
    matplotlib.use('PDF')
except:
    pass
matplotlib.rcParams['legend.fontsize'] = 7
matplotlib.rcParams['xtick.major.size'] = 3
matplotlib.rcParams['ytick.major.size'] = 3
matplotlib.rc('text', usetex = True)
from matplotlib import cm
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, NullFormatter, LogLocator
import pyfits as PF
import pylab as P
import numpy as N
import glob as G
import sys

__author__ = 'Sami-Matias Niemi'
__version__ = '0.2'

def FixFilename(string):
    fname = ''
    for x in string:
        if x == '_':
            fname += '\_'
        else:
            fname += x
    return fname

def WavelengthFromPixel(segment, grating, cenwave, fppos, pixel):
    '''
    For FUV.
    '''
    
    cdbs = '/grp/hst/cdbs/lref/'
    file = 't9e1307kl_disp.fits'
    
    wave = -1.0
    
    data = PF.open(cdbs+file)[1].data
    for line in data:
        if line[0].strip() == segment.strip() and \
           line[1].strip() == grating.strip() and \
           line[2].strip() == 'PSA' and \
           line[3] == cenwave: #and  \
           #line[4] == fppos:
            wave = line[5][0] + (pixel*line[5][1]) + (pixel*pixel*line[5][2])
    
    return wave

def makeFUVPlot(filename, data, hdr0, hdr, DQ, outputFolder):
    '''
    FUV plotting function
    '''

    max = N.max(data)
    min = N.min(data)
    
    factor = hdr['EXPTIME'] 
   
    fig = P.figure()
    ax = fig.add_subplot(111)
        
    xmax = N.shape(data)[1]
    x = N.array([0, xmax])
    
    #FUV slope zero point
    FUVxzero = 8192

    if hdr0['SEGMENT'] == 'FUVA':
        #extraction box
        boxstartyL = (0-FUVxzero)*hdr['SP_SLP_A'] + hdr['SP_LOC_A'] - (0.5*hdr['SP_HGT'])
        boxstopyL = (xmax-FUVxzero)*hdr['SP_SLP_A'] - 0.5*hdr['SP_HGT'] + hdr['SP_LOC_A']
        boxstartyH = (0-FUVxzero)*hdr['SP_SLP_A'] + hdr['SP_LOC_A'] + (0.5*hdr['SP_HGT'])
        boxstopyH = (xmax-FUVxzero)*hdr['SP_SLP_A'] + 0.5*hdr['SP_HGT'] + hdr['SP_LOC_A']
        boxL = N.array([boxstartyL, boxstopyL])
        boxH = N.array([boxstartyH, boxstopyH])
        
        #backgrounds
        back1startyL = (0-FUVxzero)*hdr['SP_SLP_A'] + hdr['B_BKG1_A'] - (0.5*hdr['B_HGT1_A'])
        back1stopyL = (xmax-FUVxzero)*hdr['SP_SLP_A'] - 0.5*hdr['B_HGT1_A'] + hdr['B_BKG1_A']
        back1startyH = (0-FUVxzero)*hdr['SP_SLP_A'] + hdr['B_BKG1_A'] + (0.5*hdr['B_HGT1_A'])
        back1stopyH = (xmax-FUVxzero)*hdr['SP_SLP_A'] + 0.5*hdr['B_HGT1_A'] + hdr['B_BKG1_A']
        back1L = N.array([back1startyL, back1stopyL])
        back1H = N.array([back1startyH, back1stopyH])
        back2startyL = (0-FUVxzero)*hdr['SP_SLP_A'] + hdr['B_BKG2_A'] - (0.5*hdr['B_HGT2_A'])
        back2stopyL = (xmax-FUVxzero)*hdr['SP_SLP_A'] - 0.5*hdr['B_HGT2_A'] + hdr['B_BKG2_A']
        back2startyH = (0-FUVxzero)*hdr['SP_SLP_A'] + hdr['B_BKG2_A'] + (0.5*hdr['B_HGT2_A'])
        back2stopyH = (xmax-FUVxzero)*hdr['SP_SLP_A'] + 0.5*hdr['B_HGT2_A'] + hdr['B_BKG2_A']
        back2L = N.array([back2startyL, back2stopyL])
        back2H = N.array([back2startyH, back2stopyH])
        
        #extraction plot
        ax.plot(x, boxL, 'r-', lw = 1.5, label = 'Extraction Box')
        ax.plot(x, boxH, 'r-', lw = 1.5)
        #background plot
        ax.plot(x, back1L, 'b--', label = 'Background 1')
        ax.plot(x, back1H, 'b--')
        
        ax.plot(x, back2L, 'b--', label = 'Background 2')
        ax.plot(x, back2H, 'b--')    
        
        #shaded areas
        ax.fill_between(x, boxL, boxH, where = boxL < boxH, facecolor='red', alpha=0.08, label = 'Extraction Box')
        ax.fill_between(x, back1L, back1H, where = back1L < back1H, facecolor='blue', alpha=0.1, label = 'Background 1')
        ax.fill_between(x, back2L, back2H, where = back2L < back2H, facecolor='blue', alpha=0.1, label = 'Background 2')

    if hdr0['SEGMENT'] == 'FUVB':
        #extraction box
        boxstartyL = (0-FUVxzero)*hdr['SP_SLP_B'] + hdr['SP_LOC_B'] - (0.5*hdr['SP_HGT'])
        boxstopyL = (xmax-FUVxzero)*hdr['SP_SLP_B'] - 0.5*hdr['SP_HGT'] + hdr['SP_LOC_B']
        boxstartyH = (0-FUVxzero)*hdr['SP_SLP_B'] + hdr['SP_LOC_B'] + (0.5*hdr['SP_HGT'])
        boxstopyH = (xmax-FUVxzero)*hdr['SP_SLP_B'] + 0.5*hdr['SP_HGT'] + hdr['SP_LOC_B']
        boxL = N.array([boxstartyL, boxstopyL])
        boxH = N.array([boxstartyH, boxstopyH])
        
        #backgrounds
        back1startyL = (0-FUVxzero)*hdr['SP_SLP_B'] + hdr['B_BKG1_B'] - (0.5*hdr['B_HGT1_B'])
        back1stopyL = (xmax-FUVxzero)*hdr['SP_SLP_B'] - 0.5*hdr['B_HGT1_B'] + hdr['B_BKG1_B']
        back1startyH = (0-FUVxzero)*hdr['SP_SLP_B'] + hdr['B_BKG1_B'] + (0.5*hdr['B_HGT1_B'])
        back1stopyH = (xmax-FUVxzero)*hdr['SP_SLP_B'] + 0.5*hdr['B_HGT1_B'] + hdr['B_BKG1_B']
        back1L = N.array([back1startyL, back1stopyL])
        back1H = N.array([back1startyH, back1stopyH])
        
        back2startyL = (0-FUVxzero)*hdr['SP_SLP_B'] + hdr['B_BKG2_B'] - (0.5*hdr['B_HGT2_B'])
        back2stopyL = (xmax-FUVxzero)*hdr['SP_SLP_B'] - 0.5*hdr['B_HGT2_B'] + hdr['B_BKG2_B']
        back2startyH = (0-FUVxzero)*hdr['SP_SLP_B'] + hdr['B_BKG2_B'] + (0.5*hdr['B_HGT2_B'])
        back2stopyH = (xmax-FUVxzero)*hdr['SP_SLP_B'] + 0.5*hdr['B_HGT2_B'] + hdr['B_BKG2_B']
        back2L = N.array([back2startyL, back2stopyL])
        back2H = N.array([back2startyH, back2stopyH]) 
        
        #extraction plot
        ax.plot(x, boxL, 'r-', lw = 1.5, label = 'Extraction Box')
        ax.plot(x, boxH, 'r-', lw = 1.5)
        #background plot
        ax.plot(x, back1L, 'b--', label = 'Background 1')
        ax.plot(x, back1H, 'b--')
        
        ax.plot(x, back2L, 'b--', label = 'Background 2')
        ax.plot(x, back2H, 'b--')    
        
        #shaded areas
        ax.fill_between(x, boxL, boxH, where = boxL < boxH, facecolor='red', alpha=0.05, label = 'Extraction Box')
        ax.fill_between(x, back1L, back1H, where = back1L < back1H, facecolor='blue', alpha=0.05, label = 'Background 1')
        ax.fill_between(x, back2L, back2H, where = back2L < back2H, facecolor='blue', alpha=0.05, label = 'Background 2')

    #imshow
    cax = ax.imshow(data,
                    cmap=cm.gist_yarg,
                    vmin = min, 
                    vmax = max/factor,
                    origin = 'lower',
                    aspect = 'auto',
                    zorder = 10,
                    interpolation = None)
    #ax.set_title('Extraction boxes for %s' % filename)

    ax.set_xlabel('X (pixels)')
    ax.set_ylabel('Y (pixels)')
   
    #limits
    ax.set_ylim(back1L[0]*0.96, back2H[0]*1.07)
    ax.set_xlim(0, xmax)

    #colour bar
    cbar = fig.colorbar(cax, ticks=[min, max/factor/2., max/factor], orientation='horizontal')
    cbar.ax.set_xticklabels(['%3.2f' % min, '%3.2f' % (max/2.), '%3.2f' % (max)])
    cbar.ax.set_title('Pixel Values (counts s$^{-1}$)')
    
    #add some info
    annosize = 'x-small'
    P.annotate('Extraction boxes for %s' % FixFilename(filename),
               xy = (0.5, 0.08), 
               horizontalalignment='center',
               verticalalignment='center',
               size = annosize,
               xycoords='figure fraction')

    P.annotate('SEGMENT = ' + hdr0['SEGMENT'] + ', OPT\_ELEM = ' +
               hdr0['OPT_ELEM'] + ', FP-POS = %i' % hdr0['FPPOS'] +
               ', CENWAVE = %i' % hdr0['CENWAVE'] + ', EXPTIME = %i s' % hdr['EXPTIME'],
               xy = (0.5, 0.06), 
               horizontalalignment='center',
               verticalalignment='center',
               size = annosize,
               xycoords='figure fraction')

    #Duplicate axis so we can manipulate wavelength to upper x axis
    ax2 = ax.twiny()
    ax2.set_xlabel('Wavelength (\AA)')
    ax2.set_ylim(back1L[0]*0.96, back2H[0]*1.07)
    ax2.set_xlim(0, xmax)
    m = ax2.get_xticks()[1] - ax2.get_xticks()[0]
    xminorLocator = MultipleLocator(m/5)
    xminorFormattor = NullFormatter()
    ax2.xaxis.set_minor_locator(xminorLocator)
    ax2.xaxis.set_minor_formatter(xminorFormattor) 
    
    waves = []
    for m in ax.get_xticks():
        x = WavelengthFromPixel(hdr0['SEGMENT'],
                                hdr0['OPT_ELEM'],
                                hdr0['CENWAVE'],
                                hdr0['FPPOS'],
                                m)
        waves.append(int(x))
    ax2.set_xticklabels(waves)    
    
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m/5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor) 

    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m/5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    
    try:
        ax.legend(shadow = True, fancybox = True)
    except:
        ax.legend(shadow = True)
    
    P.savefig(outputFolder + filename[:-4] + 'pdf')
    P.close()

def makeNUVPlot(filename, data, hdr0, hdr, DQ, outputFolder):
    '''
    NUV plotting function
    '''
    #exposure time
    factor = hdr['EXPTIME'] 

    max = N.max(data)
    min = N.min(data)
   
    fig = P.figure()
    ax = fig.add_subplot(111)
        
    xmax = N.shape(data)[1]
    x = N.array([0, xmax])
    
    #FUV slope zero point
    NUVxzero = 637
    
    #extraction boxes
    box1startyL = (0-NUVxzero)*hdr['SP_SLP_A'] + hdr['SP_LOC_A'] - (0.5*hdr['SP_HGT'])
    box1stopyL = (xmax-NUVxzero)*hdr['SP_SLP_A'] - 0.5*hdr['SP_HGT'] + hdr['SP_LOC_A']
    box1startyH = (0-NUVxzero)*hdr['SP_SLP_A'] + hdr['SP_LOC_A'] + (0.5*hdr['SP_HGT'])
    box1stopyH = (xmax-NUVxzero)*hdr['SP_SLP_A'] + 0.5*hdr['SP_HGT'] + hdr['SP_LOC_A']
    box1L = N.array([box1startyL, box1stopyL])
    box1H = N.array([box1startyH, box1stopyH])
    
    box2startyL = (0-NUVxzero)*hdr['SP_SLP_B'] + hdr['SP_LOC_B'] - (0.5*hdr['SP_HGT'])
    box2stopyL = (xmax-NUVxzero)*hdr['SP_SLP_B'] - 0.5*hdr['SP_HGT'] + hdr['SP_LOC_B']
    box2startyH = (0-NUVxzero)*hdr['SP_SLP_B'] + hdr['SP_LOC_B'] + (0.5*hdr['SP_HGT'])
    box2stopyH = (xmax-NUVxzero)*hdr['SP_SLP_B'] + 0.5*hdr['SP_HGT'] + hdr['SP_LOC_B']
    box2L = N.array([box2startyL, box2stopyL])
    box2H = N.array([box2startyH, box2stopyH])
    
    box3startyL = (0-NUVxzero)*hdr['SP_SLP_C'] + hdr['SP_LOC_C'] - (0.5*hdr['SP_HGT'])
    box3stopyL = (xmax-NUVxzero)*hdr['SP_SLP_C'] - 0.5*hdr['SP_HGT'] + hdr['SP_LOC_C']
    box3startyH = (0-NUVxzero)*hdr['SP_SLP_C'] + hdr['SP_LOC_C'] + (0.5*hdr['SP_HGT'])
    box3stopyH = (xmax-NUVxzero)*hdr['SP_SLP_C'] + 0.5*hdr['SP_HGT'] + hdr['SP_LOC_C']
    box3L = N.array([box3startyL, box3stopyL])
    box3H = N.array([box3startyH, box3stopyH])    
    
    #backgrounds
    #A
    back1AstartyL = (0-NUVxzero)*hdr['SP_SLP_A'] + hdr['B_BKG1_A'] - (0.5*hdr['B_HGT1_A'])
    back1AstopyL = (xmax-NUVxzero)*hdr['SP_SLP_A'] - 0.5*hdr['B_HGT1_A'] + hdr['B_BKG1_A']
    back1AstartyH =  (0-NUVxzero)*hdr['SP_SLP_A'] + hdr['B_BKG1_A'] + (0.5*hdr['B_HGT1_A'])
    back1AstopyH = (xmax-NUVxzero)*hdr['SP_SLP_A'] + 0.5*hdr['B_HGT1_A'] + hdr['B_BKG1_A']
    back1AL = N.array([back1AstartyL, back1AstopyL])
    back1AH = N.array([back1AstartyH, back1AstopyH])
    back2AstartyL = (0-NUVxzero)*hdr['SP_SLP_A'] + hdr['B_BKG2_A'] - (0.5*hdr['B_HGT2_A'])
    back2AstopyL = (xmax-NUVxzero)*hdr['SP_SLP_A'] - 0.5*hdr['B_HGT2_A'] + hdr['B_BKG2_A']
    back2AstartyH = (0-NUVxzero)*hdr['SP_SLP_A'] + hdr['B_BKG2_A'] + (0.5*hdr['B_HGT2_A'])
    back2AstopyH = (xmax-NUVxzero)*hdr['SP_SLP_A'] + 0.5*hdr['B_HGT2_A'] + hdr['B_BKG2_A']
    back2AL = N.array([back2AstartyL, back2AstopyL])
    back2AH = N.array([back2AstartyH, back2AstopyH])
    #B
    back1BstartyL = (0-NUVxzero)*hdr['SP_SLP_B'] + hdr['B_BKG1_B'] - (0.5*hdr['B_HGT1_B'])
    back1BstopyL = (xmax-NUVxzero)*hdr['SP_SLP_B'] - 0.5*hdr['B_HGT1_B'] + hdr['B_BKG1_B']
    back1BstartyH =  (0-NUVxzero)*hdr['SP_SLP_B'] + hdr['B_BKG1_B'] + (0.5*hdr['B_HGT1_B'])
    back1BstopyH = (xmax-NUVxzero)*hdr['SP_SLP_B'] + 0.5*hdr['B_HGT1_B'] + hdr['B_BKG1_B']
    back1BL = N.array([back1BstartyL, back1BstopyL])
    back1BH = N.array([back1BstartyH, back1BstopyH])
    back2BstartyL = (0-NUVxzero)*hdr['SP_SLP_B'] + hdr['B_BKG2_B'] - (0.5*hdr['B_HGT2_B'])
    back2BstopyL = (xmax-NUVxzero)*hdr['SP_SLP_B'] - 0.5*hdr['B_HGT2_B'] + hdr['B_BKG2_B']
    back2BstartyH = (0-NUVxzero)*hdr['SP_SLP_B'] + hdr['B_BKG2_B'] + (0.5*hdr['B_HGT2_B'])
    back2BstopyH = (xmax-NUVxzero)*hdr['SP_SLP_B'] + 0.5*hdr['B_HGT2_B'] + hdr['B_BKG2_B']
    back2BL = N.array([back2BstartyL, back2BstopyL])
    back2BH = N.array([back2BstartyH, back2BstopyH])
    #C
    back1CstartyL = (0-NUVxzero)*hdr['SP_SLP_C'] + hdr['B_BKG1_C'] - (0.5*hdr['B_HGT1_C'])
    back1CstopyL = (xmax-NUVxzero)*hdr['SP_SLP_C'] - 0.5*hdr['B_HGT1_C'] + hdr['B_BKG1_C']
    back1CstartyH =  (0-NUVxzero)*hdr['SP_SLP_C'] + hdr['B_BKG1_C'] + (0.5*hdr['B_HGT1_C'])
    back1CstopyH = (xmax-NUVxzero)*hdr['SP_SLP_C'] + 0.5*hdr['B_HGT1_C'] + hdr['B_BKG1_C']
    back1CL = N.array([back1CstartyL, back1CstopyL])
    back1CH = N.array([back1CstartyH, back1CstopyH])
    back2CstartyL = (0-NUVxzero)*hdr['SP_SLP_C'] + hdr['B_BKG2_C'] - (0.5*hdr['B_HGT2_C'])
    back2CstopyL = (xmax-NUVxzero)*hdr['SP_SLP_C'] - 0.5*hdr['B_HGT2_C'] + hdr['B_BKG2_C']
    back2CstartyH = (0-NUVxzero)*hdr['SP_SLP_C'] + hdr['B_BKG2_C'] + (0.5*hdr['B_HGT2_C'])
    back2CstopyH = (xmax-NUVxzero)*hdr['SP_SLP_C'] + 0.5*hdr['B_HGT2_C'] + hdr['B_BKG2_C']
    back2CL = N.array([back2CstartyL, back2CstopyL])
    back2CH = N.array([back2CstartyH, back2CstopyH])
    
    #extraction plot
    ax.plot(x, box1L, 'r-', lw = 1.5, label = 'Extraction Boxes')
    ax.plot(x, box1H, 'r-', lw = 1.5)
    ax.plot(x, box2L, 'r-', lw = 1.5)#, label = 'Extraction Box')
    ax.plot(x, box2H, 'r-', lw = 1.5)
    ax.plot(x, box3L, 'r-', lw = 1.5)#, label = 'Extraction Box')
    ax.plot(x, box3H, 'r-', lw = 1.5)
    #background plot
    ax.plot(x, back1AL, 'b--', label = 'Background 1A')
    ax.plot(x, back1AH, 'b--')
    ax.plot(x, back2AL, 'b--', label = 'Background 2A')
    ax.plot(x, back2AH, 'b--')    
    
    ax.plot(x, back1BL, 'g:', label = 'Background 1B')
    ax.plot(x, back1BH, 'g:')
    ax.plot(x, back2BL, 'g:', label = 'Background 2B')
    ax.plot(x, back2BH, 'g:')
    
    ax.plot(x, back1CL, 'y-.', label = 'Background 1C')
    ax.plot(x, back1CH, 'y-.')
    ax.plot(x, back2CL, 'y-.', label = 'Background 2C')
    ax.plot(x, back2CH, 'y-.')
    
    #shaded areas
    ax.fill_between(x, box1L, box1H, where = box1L < box1H, facecolor='red', alpha=0.08, label = 'Extraction Box 1')
    ax.fill_between(x, box2L, box2H, where = box2L < box2H, facecolor='red', alpha=0.08, label = 'Extraction Box 2')
    ax.fill_between(x, box3L, box3H, where = box3L < box3H, facecolor='red', alpha=0.08, label = 'Extraction Box 3')
    ax.fill_between(x, back1AL, back1AH, where = back1AL < back1AH, facecolor='blue', alpha=0.1, label = 'Background 1')
    ax.fill_between(x, back2AL, back2AH, where = back2AL < back2AH, facecolor='blue', alpha=0.1, label = 'Background 2')

    #DQ array    
    #dax = ax.imshow(DQ,
    #                vmin = 0,
    #                vmax = 256,
    #                cmap=cm.Reds,
    #                origin = 'lower',
    #                aspect = 'auto',
    #                interpolation = None,
    #                alpha = 1.0,
    #                label = 'DQ') 
    #Image
    cax = ax.imshow(data,
                    cmap=cm.gist_yarg,
                    vmin = min,
                    vmax = max/factor,
                    origin = 'lower',
                    aspect = 'auto',
                    interpolation = None)
    
    ax.set_title('Extraction boxes for %s' % FixFilename(filename))
    
    ax.set_xlabel('X (pixels)')
    ax.set_ylabel('Y (pixels)')
   
    #y limits
    ax.set_ylim(back2AL[1]*0.83, back1AH[0]*1.25)
    ax.set_xlim(0, xmax+100)
        
    cbar = fig.colorbar(cax, ticks=[min, max/factor/2., max/factor], orientation='horizontal')
    cbar.ax.set_xticklabels(['%3.2f' % min, '%3.2f' % (max/2.), '%3.2f' % (max)])
    cbar.ax.set_title('Pixel Values (counts/sec)')
    
    #add some info
    annosize = 'x-small'
    P.annotate('DETECTOR = ' + hdr0['DETECTOR'] + ', OPT\_ELEM = ' +
               hdr0['OPT_ELEM'] + ', FP-POS = %i' % hdr0['FPPOS'] +
               ', CENWAVE = %i' % hdr0['CENWAVE'] + ', EXPTIME = %i sec' % hdr['EXPTIME'],
               xy = (0.5, 0.05), 
               horizontalalignment='center',
               verticalalignment='center',
               size = annosize,
               xycoords='figure fraction')
    
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m/5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor) 

    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m/5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    
    try:
        ax.legend(shadow = True, fancybox = True)
    except:
        ax.legend(shadow = True)
    
    P.savefig(outputFolder + filename[:-4] + 'pdf')
    P.close()

if __name__ == '__main__':
    '''
    Main program
    '''
    
    outputFolder = '/Users/niemi/tmp/imgs/'
    #outputFolder = './'

    if len(sys.argv) > 1:
        name = sys.argv[1]
    else:
        name = '*_counts*'  
    
    files = G.glob(name)

    for file in files:
        if 'counts' in file or 'flt' in file:
            hdr = PF.open(file)[0].header
            #try:
            if 'FUV' in hdr['SEGMENT']:
                makeFUVPlot(file,
                          PF.open(file)[1].data,
                          hdr,
                          PF.open(file)[1].header,
                          PF.open(file)[3].data,
                          outputFolder
                         )
                print 'file %s plotted' % file
            #except:
            #    pass
            #try:
            if 'NUV' in hdr['DETECTOR']:
                makeNUVPlot(file,
                          PF.open(file)[1].data,
                          hdr,
                          PF.open(file)[1].header,
                          PF.open(file)[3].data,
                          outputFolder
                         )
                print 'file %s plotted' % file
            #except:
            #    pass

        if 'corrtag' in file:
            print 'to be done...'