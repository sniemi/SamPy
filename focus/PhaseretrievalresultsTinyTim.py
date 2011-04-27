'''
HISTORY:
Created on March 3, 2011

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu

:version: 0.1
'''
import matplotlib
matplotlib.use('PDF')
import pylab as P
import glob as G
import numpy as N
import os
from matplotlib import cm
#from my repo
import focus.phaseretrievalresults as ph

__author__ = 'Sami-Matias Niemi'
__version__ = '0.1'

class TinyTimResults(ph.PhaseRetResults):
    '''
    Expansion to PhaseRetResults class
    '''

    def findRealFocus(self, file):
        parms = './' + os.path.dirname(file) + '/complete_results/parameters.txt'
        tmp = open(parms).readlines()
        for line in tmp:
            if 'Focus' in line:
                fcs = float(line.split('|')[1].split()[0].strip())
        return fcs

    def plotFocusDifference(self, input, title, abs = False):
        fig = P.figure()
        ax = fig.add_subplot(111)
        
        tmp1 = []
        tmp2 = []
        tmp3 = []
        tmp4 = []
        for key in input:
            data = input[key]
            if abs:
                tmp1.append(N.abs(data[1][0]-data[0]))
                tmp2.append(N.abs(data[1][1]-data[0]))
                tmp3.append(N.abs(data[1][2]-data[0]))
                tmp4.append(N.abs(data[1][3]-data[0]))
                x1 = ax.plot(N.abs(data[1][0]), N.abs(data[0]), 'bo')
                x2 = ax.plot(N.abs(data[1][1]), N.abs(data[0]), 'rs')
                x3 = ax.plot(N.abs(data[1][2]), N.abs(data[0]), 'mD')
                x4 = ax.plot(N.abs(data[1][2]), N.abs(data[0]), 'g*')
            else:
                tmp1.append(data[1][0]-data[0])
                tmp2.append(data[1][1]-data[0])
                tmp3.append(data[1][2]-data[0])
                tmp4.append(data[1][3]-data[0])
                x1 = ax.plot(data[1][0], data[0], 'bo')
                x2 = ax.plot(data[1][1], data[0], 'rs')
                x3 = ax.plot(data[1][2], data[0], 'mD')
                x4 = ax.plot(data[1][2], data[0], 'g*')

        
        ax.plot([-15,15],[-15,15], 'k:')
        if abs:
            ax.set_xlim(0, 7.5)
            ax.set_ylim(0, 7.5)
        else:
            ax.set_xlim(-7.5, 7.5)
            ax.set_ylim(-7.5, 7.5)
        
        P.text(0.5, 1.05, title,
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax.transAxes)

        ax.set_xlabel('Phase Retrieval Result [Secondary mirror despace]')
        ax.set_ylabel('TinyTim Focus Offset [Secondary mirror despace]')

        ax.legend([x1, x2, x3, x4],
                  ['Nominal setup', 'Fixed Blur Kernel', 'Spherical = 0, fixed', 'sph = 0, fixed Blur'],
                  shadow = True, fancybox = True, numpoints  = 1,
                  loc = 'best')

        if abs:
            P.savefig('FocusAbsolute.pdf')
        else:
            P.savefig('Focus.pdf')
        
        #print out statistics
        tmp1 = N.array(tmp1)
        tmp2 = N.array(tmp2)
        tmp3 = N.array(tmp3)
        tmp4 = N.array(tmp4)
        print 'Average offset (PR - TT) for nominal method is %.2f' % N.mean(tmp1)
        print 'while STD is %.3f' % N.std(tmp1)
        print
        print 'Average offset (PR - TT) for fixed blur kernel is %.2f' % N.mean(tmp2)
        print 'while STD is %.3f' % N.std(tmp2)
        print
        print 'Average offset (PR - TT) for fixed spherical = 0 is %.2f' % N.mean(tmp3)
        print 'while STD is %.3f' % N.std(tmp3)
        print
        print 'Average offset (PR - TT) for fixed blur and sph = 0 is %.2f' % N.mean(tmp4)
        print 'while STD is %.3f' % N.std(tmp4)    
    
    def plotFocusFieldPosition(self, input, title):
        fig = P.figure()
        ax = fig.add_subplot(111)

        c1, x1, y1 = [], [], []
        for key in input:
            data = input[key]
            c1.append(data[0]-data[1][0][5])
            x1.append(data[1][0][1])
            y1.append(data[1][0][2])

        x1 = ax.scatter(x1, y1, c = c1,
                        marker='o',
                        cmap = cm.get_cmap('jet'),
                        edgecolor = 'none')

        c1 = fig.colorbar(x1, ax = ax, shrink = 0.7, fraction = 0.05)
        c1.set_label('TinyTim Focus Offset - Phase Retrieval Measurement')

        ax.set_xlim(0, 4096)
        ax.set_ylim(0, 2051)

        P.text(0.5, 1.05, title,
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax.transAxes)

        P.savefig('FocusFieldPos.pdf')

        
if __name__ == '__main__':
    #define some variables
    str = {'file': 0,
           'target': 0,
           'mjd' : 1,
           'date': 2,
           'time': 3,
           'focus':5}

    cameras = ['WFC3'] 

    t1 = 'UVIS1, PSF diameter = 3.0 arcsec, Filter F410M, G5V star, variable field positions'
    t2 = 'UVIS1, PSF diameter = 3.0 arcsec, Filter F410M, G5V star'

    PR = TinyTimResults(cameras, str)

    #find all data files
    results = G.glob('t*/results.txt')
    
    #loop over the data files and find the focus info
    out = {}
    out2 = {}
    for file in results:
        print 'processing %s' % file
        res = PR.readResults(file)
        #get the observed values
        tmp = []
        for x in res:
            tmp.append(x[str['focus']])
        #find the true focus
        trueFocus = PR.findRealFocus(file)
        #output values
        out[file] = [trueFocus, tmp]
        out2[file] = [trueFocus, res]
    
    #generate a plot
    PR.plotFocusDifference(out, t1)
    PR.plotFocusDifference(out, t1, abs = True)
    PR.plotFocusFieldPosition(out2, t2)
    