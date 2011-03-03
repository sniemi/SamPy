#! /usr/bin/env python
'''
DESCRIPTION:
Combines the Phase Retrieval software results, produces plots
and calculates focus with and without breathing correction. 

USAGE:
python PhaseRetResults.py

HISTORY:
Created on Dec 17, 2009

@author: Sami-Matias Niemi (niemi@stsci.edu)

@version: 0.91

@todo: maybe introduce sigma clipping to the means?
@todo: how the legend has been implemented is a dirty,
        it should be done better.
'''

import matplotlib
matplotlib.rc('text', usetex = True)
matplotlib.use('PDF')
matplotlib.rcParams['legend.fontsize'] = 9
import pyfits as PF
import pylab as P
import numpy as N
import datetime as D
import scipy.interpolate as I
import glob as G
import time
from matplotlib import cm
from matplotlib.patches import Circle

__author__ = 'Sami-Matias Niemi'
__version__ = '0.91'

class PhaseRetResults():

    def __init__(self, cameras, str):
        self.cameras = cameras
        self.str = str
        
    def _fromJulian(self, j):
        '''
        Converts Modified Julian days to human readable format
        @return: human readable date and time
        '''
        days = j - 40587 # From Jan 1 1900
        sec = days*86400.0
        return time.gmtime(sec)
    
    def readBreathing(self, file):
        jul = []
        flat = []
        for line in open(file).readlines():
            if 'Julian' in line: continue
            else:
                t = line.strip().split()
                jul.append(float(t[0]))
                flat.append(float(t[-1]))
                
        return N.array([N.array(jul), N.array(flat)])
        
    def readResults(self, file):
        '''
        '''
        x, y = -999, -999
        
        fh = open(file)

        out = []
        for line in fh.readlines():
            for camera in self.cameras:
                if camera in line:
                    #print 'Found %s' % camera
                    tmp = line.strip().split()
                    x = tmp[1]
                    y = tmp[2]
                    cam = camera
                    break
            tmp = line.strip().split()
            try:
                out.append([cam, int(x), int(y), tmp[self.str['file']],
                            float(tmp[self.str['mjd']]), float(tmp[self.str['focus']])])
            except:
                pass
        return out
    
    def findFiles(self, data):
        tmp = []
        for line in data:
            new = True
            for x in tmp:
                if line[3] == tmp: new = False
            if new: tmp.append(line[3])
        return tmp    
        
    def plotStars(self, file, ext, xpos, ypos, rad = 25):
        '''
        '''
        if ext == 1: chip = 2
        if ext == 4: chip = 1
        
        #manipulate data
        data = PF.open(file)[ext].data
        data[data <= 1.0] = 1.0
        data = N.log10(data)  
        
        ax = P.subplot(111)
        b = P.gca()
                
        ims = ax.imshow(data,
                        origin='lower',
                        cmap = cm.gray,
                        interpolation = None,
                        vmin = 0.0,
                        vmax = 3.0)
        cb = P.colorbar(ims, orientation='horizontal')
        cb.set_label('$\log_{10}(Counts)$')
        
        #loop over xpos and ypos and ratio and draw circles
        count = 1
        for x, y in zip(xpos, ypos):
            cir = Circle((x+1, y+1), radius = rad, fc = 'none', ec = 'r')
            b.add_patch(cir)
            P.annotate('Star %i' % count,
                        xy = (x, y+70), 
                        horizontalalignment='center',
                        verticalalignment='center',
                        style = 'italic', size = 'xx-small',
                        color='red')
            count += 1
        
        P.title('Focus Stars of %s Chip %i' % (file[:-9], chip))
        
        P.savefig('%sStarsChip%i.pdf' % (file[:-7], chip))       
        P.close()
   
    def _getStats(self, data):
        res = []
        tmp = []
        t = {}
        for line in data:
            diff = True
            for x in tmp:
                if line[0] == x: diff = False
                
            if diff: tmp.append(line[0])

        for x in tmp:
            for line in data:
                if line[0] == x: t.setdefault(x,[]).append(line[1])
            
        for key in t:
            res.append([key, N.mean(t[key]), N.std(t[key]), N.shape(t[key])[0]])
        return res
    
    def plotFocus(self, chip1, chip2, brdata = [], noBreathing = False):
        d = []
        meanACS = []
        meanWFC3 = []
        brA = {}
        brW = {}
        
        obsj = G.glob('j*.fits')[0][:7]
        obsi = G.glob('i*.fits')[0][:7]
        
        #get some data
        for line in chip1:
            d.append(line[4])
            if 'ACS' in line[0]:
                meanACS.append([line[4], line[5]])
            if 'WFC3' in line[0]:
                meanWFC3.append([line[4], line[5]])
        for line in chip2:
            if 'ACS' in line[0]:
                meanACS.append([line[4], line[5]])
            if 'WFC3' in line[0]:
                meanWFC3.append([line[4], line[5]])

        avd = self._fromJulian(N.mean(N.array(d)))

        fig = P.figure()
        ax = fig.add_subplot(111)   
     
        #get stasts
        statACS = self._getStats(meanACS)
        statWFC3 = self._getStats(meanWFC3)
        acsJDs = [line[0] for line in statACS]
        wfcJDs = [line[0] for line in statWFC3]
        #interpolated breathing values
        if noBreathing == False:
            acsBreathing = I.interp1d(brdata[0,:], brdata[1,:], kind = 'linear')
            wfcBreathing = I.interp1d(brdata[0,:], brdata[1,:], kind = 'linear')
            for x in acsJDs :
                brA[x] = acsBreathing(x)
            for x in wfcJDs :
                brW[x] = wfcBreathing(x)
                
            for line in chip1:
                if 'ACS' in line[0]:
                    ac = ax.plot(line[4], line[5] - brA[line[4]], 'bs', zorder = 7)
                if 'WFC3' in line[0]:
                    wf = ax.plot(line[4], line[5] - brW[line[4]], 'ro', zorder = 7)
            for line in chip2:
                if 'ACS' in line[0]:
                    ac2 = ax.plot(line[4], line[5] - brA[line[4]], 'gd', zorder = 7)
                if 'WFC3' in line[0]:
                    wf2 = ax.plot(line[4], line[5] - brW[line[4]], 'mx', zorder = 7)        
            #plot mean values
            acsf = [line[1] - brA[line[0]] for line in statACS]
            wfcf = [line[1] - brW[line[0]] for line in statWFC3]
            eac = ax.errorbar(acsJDs, acsf,
                             yerr = [line[2]/N.sqrt(line[3]) for line in statACS], marker = 'H', mfc = 'yellow',
                             ms = 9, mec='magenta', ls = 'None', mew = 1.3, ecolor = 'magenta', zorder = 50)
            ewf = ax.errorbar(wfcJDs, wfcf,
                             yerr = [line[2]/N.sqrt(line[3]) for line in statWFC3], marker = 'o', mfc = 'cyan',
                             ms = 5, mec='magenta', ls = 'None', mew = 1.3, ecolor = 'magenta', zorder = 50)
            
            print '\nBreathing corrections:\n Camera     MJD               correction'
            for x in acsJDs:
                print 'ACS       %f        %f' % (x, brA[x])
            for x in wfcJDs:
                print 'WFC3      %f        %f' % (x, brW[x])
            
            print '\nBreathing corrected focus:'
            print 'Julian      J-L     focus     error  camera'
            print '%i %9i %9.2f %9.3f %5s' % (int(N.mean(acsJDs)),  (int(N.mean(acsJDs)) - 48005), N.mean(acsf), N.std(acsf)/N.sqrt(len(acsf)), 'ACS')
            print '%i %9i %9.2f %9.3f %6s' % (int(N.mean(wfcJDs)),  (int(N.mean(wfcJDs)) - 48005), N.mean(wfcf), N.std(acsf)/N.sqrt(len(wfcf)), 'WFC3')
            
        else:
            for line in chip1:
                if 'ACS' in line[0]:
                    ac = ax.plot(line[4], line[5], 'bs', zorder = 7)
                if 'WFC3' in line[0]:
                    wf = ax.plot(line[4], line[5], 'ro', zorder = 7)
            for line in chip2:
                if 'ACS' in line[0]:
                    ac2 = ax.plot(line[4], line[5], 'gd', zorder = 7)
                if 'WFC3' in line[0]:
                    wf2 = ax.plot(line[4], line[5], 'mx', zorder = 7)    
            #plot mean values
            acsf = [line[1] for line in statACS]
            wfcf = [line[1] for line in statWFC3]
            eac = ax.errorbar(acsJDs, acsf,
                             yerr = [line[2]/N.sqrt(line[3]) for line in statACS], marker = 'H', mfc = 'yellow',
                             ms = 9, mec='magenta', ls = 'None', mew = 1.3, ecolor = 'magenta', zorder = 50)
            ewf = ax.errorbar(wfcJDs, wfcf,
                             yerr = [line[2]/N.sqrt(line[3]) for line in statWFC3], marker = 'o', mfc = 'cyan',
                             ms = 5, mec='magenta', ls = 'None', mew = 1.3, ecolor = 'magenta', zorder = 50)
            
            print '\nWithout breathing correction:'
            print 'OBS         date       JD    focus    error'
            print '%6s %11s %7i %6.2f %8.3f' % (obsj, time.strftime(('%d/%m/%y'), avd),
                                               int(N.mean(acsJDs)),
                                               N.mean(acsf),
                                               N.std(acsf)/N.sqrt(len(acsf)))
            print '%6s %11s %7i %6.2f %8.3f' % (obsi, time.strftime(('%d/%m/%y'), avd),
                                               int(N.mean(wfcJDs)),
                                               N.mean(wfcf),
                                               N.std(wfcf)/N.sqrt(len(wfcf)))
            
        times = []
        for m in ax.get_xticks():
            x = time.strftime(("%H:%M:%S"), self._fromJulian(m))
            times.append(x)
        ax.set_xticklabels(times)

        #zero focus line
        ax.axhline(0, color='k', ls = '--', lw = 0.8)

        if noBreathing:
            P.title('Focus Measurement (No breathing correction)')                
        else:
            P.title('Focus Measurement (breathing corrected)')

        try:     
            P.legend((ac[0], wf[0], ac2[0], wf2[0], eac[0], ewf[0]),
                     ['ACS chip 1', 'WFC3 chip 1', 'ACS chip 2', 'WFC3 chip 2', 'ACS Mean', 'WFC3 Mean'],
                     fancybox = True, shadow = True, numpoints  = 1)
        except:
            P.legend((ac[0], ac2[0], wf2[0], eac[0], ewf[0]),
                     ['ACS chip 1', 'ACS chip 2', 'WFC3 chip 2', 'ACS Mean', 'WFC3 Mean'],
                     fancybox = True, shadow = True, numpoints  = 1)

        P.xlabel('%s' % time.strftime(('%d %b %Y'), avd))
        P.ylabel('Defocus [SM $\mu$m]')
        if noBreathing:
            P.savefig('FullFocusNoBreathing.pdf')
        else:
            P.savefig('FullFocus.pdf')
        print '\n\n'
        
if __name__ == '__main__':
    #define some variables
    str = {'file': 0,
           'target': 1,
           'mjd' : 2,
           'date': 3,
           'time': 4,
           'focus':6}
    cameras = ['ACS', 'WFC3'] 
    
    PR = PhaseRetResults(cameras, str)
    
    #Read the stuff in
    c1 = PR.readResults('resultsChip1.txt') #chip 1
    c2 = PR.readResults('resultsChip2.txt') #chip 2
    #read breathing values
    brdata = PR.readBreathing('breathing.txt')

    #make a plot without breathing correction
    PR.plotFocus(c1, c2, noBreathing = True)    
    #make a plot with breathing correction
    PR.plotFocus(c1, c2, brdata)

    #plot stars
    f1 = PR.findFiles(c1)
    f2 = PR.findFiles(c2)
    
    for file in f1:
        x = []
        y = []
        for line in c1:
            if line[3] == file:
                x.append(line[1])
                y.append(line[2])    
        PR.plotStars(file+'_flt.fits', 4, x, y)
    for file in f2:
        x = []
        y = []
        for line in c2:
            if line[3] == file:
                x.append(line[1])
                y.append(line[2])    
        PR.plotStars(file+'_flt.fits', 1, x, y)
        