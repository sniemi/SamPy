#! /usr/bin/env python
'''
DESCRIPTION:

USAGE:

HISTORY:
Created on Dec 7, 2009

@author: Sami-Matias Niemi
'''

import matplotlib
matplotlib.rc('text', usetex = True)
matplotlib.use('PDF')
import pyfits as PF
import pylab as P
import glob as G
import numpy as N
#from mpl_toolkits.axes_grid.inset_locator import zoomed_inset_axes
#from mpl_toolkits.axes_grid.inset_locator import mark_inset

__author__ = 'Sami-Matias Niemi'
__version__ = '0.1'

new = 'coadd_comb_reject_m.fits'
oref = '/grp/hst/cdbs/oref/'
oldfile = 'n491401eo_pfl.fits'
old = oref + oldfile

def RMS(data):
    return N.sqrt(N.mean(data)**2 + N.std(data)**2)
    

x1ds = G.glob('*x1d*fits')
x2ds = G.glob('*x2d*fits')

###########################################
newd = PF.open(new)[1].data
oldd = PF.open(old)[1].data

ims = P.imshow(newd/oldd, origin='lower',
                interpolation = None,
                vmin = 0.98,
                vmax = 1.02)
cb = P.colorbar(ims, orientation='vertical')
cb.set_label('New Flat / Old Flat')

P.annotate('New Flat vs. Old Flat (%s)' % oldfile.replace('_', '\_'),
           xy = (0.5, 0.97), 
           horizontalalignment='center',
           verticalalignment='center',
           xycoords='figure fraction')
P.savefig('OldVsNewFlat.pdf')
P.close()

###########################################
newe = PF.open(new)[2].data
olde = PF.open(old)[2].data

ims = P.imshow(newe/olde, origin='lower',
                interpolation = None,
                vmin = 0.85,
                vmax = 1.15)
cb = P.colorbar(ims, orientation='vertical')
cb.set_label('New Error / Old Error')

P.annotate('New Error vs. Old Error (%s)' % oldfile.replace('_', '\_'), xy = (0.5, 0.97), 
           horizontalalignment='center',
           verticalalignment='center',
           xycoords='figure fraction')
P.savefig('OldVsNewFlatError.pdf')
P.close()

############################################
fg = P.figure(1)
as1 = fg.add_subplot(211)
as2 = fg.add_subplot(212)
refflux = PF.open(x1ds[0])[1].data.field('FLUX')
reffluxo = PF.open('./pipeline/' + x1ds[0])[1].data.field('FLUX')
c = 0
for file in x1ds:
    if c > 5 : break
    fh = PF.open(file)
    wave1 = fh[1].data.field('WAVELENGTH')
    flux1 = fh[1].data.field('FLUX')
    fh.close()
    
    fh = PF.open('./pipeline/' + file)
    wave2 = fh[1].data.field('WAVELENGTH')
    flux2 = fh[1].data.field('FLUX')
    fh.close()
    
    resnew = flux1[0] / refflux[0]
    resold = flux2[0] / reffluxo[0]

    as1.plot(wave1[0], resnew, label='New Flat')
    as2.plot(wave2[0], resold, label='Old Flat')
    print 'Mean of residual new %f vs. old %f' % (N.mean(resnew-1), N.mean(resold-1))
    print 'X1d residual: std new %e vs old %e i.e. %f per cent smaller with new flat' % (N.std(resnew-1), N.std(resold-1), 100. - N.std(resnew-1)/N.std(resold-1)*100.)
    c += 1

as2.set_xlabel('Wavelength (\AA)')
as1.set_ylabel('first / rest')
as2.set_ylabel('first / rest')
as1.axhline(1.02)
as1.axhline(0.98)
as2.axhline(1.02)
as2.axhline(0.98)
as1.set_ylim(0.95, 1.05)
as2.set_ylim(0.95, 1.05)
P.title('With new flat top, with old flat below')
P.savefig('X1dsResiduals.pdf')
P.close()
############################################

############################################
fg = P.figure(6)
as1 = fg.add_subplot(311)
as2 = fg.add_subplot(312)
as3 = fg.add_subplot(313)
refwave = PF.open(x1ds[0])[1].data.field('WAVELENGTH') 
refwaveo = PF.open('./pipeline/' + x1ds[0])[1].data.field('WAVELENGTH') 
refflux = PF.open(x1ds[0])[1].data.field('FLUX')
reffluxo = PF.open('./pipeline/' + x1ds[0])[1].data.field('FLUX')
c = 0
for file in x1ds:
    if c > 5 : break
    fh = PF.open(file)
    wave1 = fh[1].data.field('WAVELENGTH')
    flux1 = fh[1].data.field('FLUX')
    fh.close()
    
    fh = PF.open('./pipeline/' + file)
    wave2 = fh[1].data.field('WAVELENGTH')
    flux2 = fh[1].data.field('FLUX')
    fh.close()
    #interpolate to the same wavelength scale
    intf1 = N.interp(refwave[0], wave1[0], flux1[0])
    intf2 = N.interp(refwaveo[0], wave2[0], flux2[0])

    resnew = intf1 / refflux[0]
    resold = intf2 / reffluxo[0]

    as1.plot(refwave[0], resnew, label='New Flat')
    as2.plot(refwaveo[0], resold, label='Old Flat')
    as3.plot(refwave[0], N.abs(resnew-1) - N.abs(resold-1))
    print 'Interpret X1d residual: std new %e vs old %e i.e. %f per cent smaller with new flat' % (N.std(resnew-1), N.std(resold-1), 100. - N.std(resnew-1)/N.std(resold-1)*100.)
    c += 1

as3.set_xlabel('Wavelength (\AA)')
as1.set_ylabel('first / rest')
as2.set_ylabel('first / rest')
as3.set_ylabel('Abs. Res. (N - O)')
as1.axhline(1.01)
as1.axhline(0.99)
as2.axhline(1.01)
as2.axhline(0.99)
as3.axhline(0.0)
as1.set_ylim(0.97, 1.03)
as2.set_ylim(0.97, 1.03)
as3.set_ylim(-0.015, 0.015)
P.annotate('With new flat top, with old flat in the middle, diff at the bottom (Wave interpr.)',
           xy = (0.5, 0.95),
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction')
P.savefig('X1dsResidualsInterpret.pdf')
P.close()

############################################
fg = P.figure(2)
axs1 = fg.add_subplot(211)
axs2 = fg.add_subplot(212)
for file in x1ds:
    fh = PF.open(file)
    wave1 = fh[1].data.field('WAVELENGTH')
    flux1 = fh[1].data.field('FLUX')
    fh.close()
    
    fh = PF.open('./pipeline/' + file)
    wave2 = fh[1].data.field('WAVELENGTH')
    flux2 = fh[1].data.field('FLUX')
    fh.close()

    fig = P.figure()
    
    left, width = 0.1, 0.8
    rect1 = [left, 0.3, width, 0.65]
    rect2 = [left, 0.1, width, 0.2]

    ax1 = fig.add_axes(rect2)  #left, bottom, width, height
    ax2 = fig.add_axes(rect1)        

    for value, wave in enumerate(wave2):
        ax2.plot(wave, flux2[value], label='Old flat')
    for value, wave in enumerate(wave1):
        ax2.plot(wave, flux1[value], label='New Flat')    
    for value, wave in enumerate(wave1):
        ax1.plot(wave, flux1[value] / flux2[value], label = 'Residual' )
    
    ax1.set_xlabel('Wavelength (\AA)')
    ax2.set_ylabel('Flux')
    ax1.set_ylabel('New Flux / Old')
    
    ax1.axhline(1)
    
    ax2.set_xticklabels([])
    ax2.set_yticks(ax2.get_yticks()[1:])
    ax1.set_yticks(ax1.get_yticks()[::2])
 
    P.annotate(file.replace('_', '\_'), xy = (0.5, 0.97), 
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction')
    
    P.legend(shadow=True, fancybox = True)
    P.savefig(file[:-5] + '.pdf')
    P.close()

    #interpolate to the same wavelength scale
    intf1 = N.interp(refwave[0], wave1[0], flux1[0])
    intf2 = N.interp(refwaveo[0], wave2[0], flux2[0])
    #axs1.plot(wave1[0], flux1[0], label='New Flat')
    #axs2.plot(wave2[0], flux2[0], label='Old Flat')
    #another fig
    axs1.plot(refwave[0], intf1, label='New Flat')
    axs2.plot(refwaveo[0], intf2, label='Old Flat')

P.title('With new flat top, with old flat below')
#P.legend()
axs1.set_ylim(ymax = 5.3*10**-9)
axs2.set_ylim(ymax = 5.3*10**-9)
axs2.set_xlabel('Wavelength (\AA)')
axs1.set_ylabel('Flux')
axs2.set_ylabel('Flux')
P.savefig('X1ds.pdf')
#second
axs1.set_xlim(1990, 2005)
axs2.set_xlim(1990, 2005)
axs1.set_ylim(ymax = 5*10**-9)
axs2.set_ylim(ymax = 5*10**-9)
P.savefig('X1dsLim.pdf')
#third
axs1.set_xlim(2025, 2035)
axs2.set_xlim(2025, 2035)
axs1.set_ylim(ymax = 5*10**-9)
axs2.set_ylim(ymax = 5*10**-9)
P.savefig('X1dsLim2.pdf')
P.close()

##
print ' '*45 + 'Old vs New'
print '%25s%22s%19s%17s' % ('File', 'Mean', 'Stdev', 'RMS')
for file in x2ds:
    dataNew = PF.open(file)[1].data
    dataOld = PF.open('./pipeline/' + file)[1].data
    
    ims = P.imshow(dataNew/dataOld, origin='lower',
                    interpolation = None,
                    vmin = 0.95,
                    vmax = 1.05)
    cb = P.colorbar(ims, orientation='vertical')
    cb.set_label('New Flat / Old Flat')

    P.annotate(file.replace('_', '\_'), xy = (0.5, 0.97), 
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction')

    P.savefig(file[:-5] + '.pdf')
    P.close()
    n = dataNew[dataNew > 0.]
    o = dataOld[dataOld > 0.]
    print '%30s%20.4e%18.7e%18.7e' % (file, N.mean(n), N.std(n), RMS(n))
    print '%30s%20.4e%18.7e%18.7e' % ('./pipeline/' + file, N.mean(o), N.std(o), RMS(o))
    print '%30s%20.4f%18.7f%18.7f\n' % ('Ratio (New/Old):', N.mean(n)/N.mean(o), N.std(n)/N.std(o), RMS(n)/RMS(o))

