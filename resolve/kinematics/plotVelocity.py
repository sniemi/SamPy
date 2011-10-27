"""
Class to plot velocity fields and SDSS images.

:requires: NumPy
:requires: PyFITS
:requires: matplotlib
:requires: Kapteyn Python package
:requires: SamPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.6
"""
import matplotlib
matplotlib.rcParams['font.size'] = 16
import numpy as np
import pyfits as pf
import pywcs
import SamPy.smnIO.read as read
from matplotlib import pyplot as plt
from matplotlib import cm
import mpl_toolkits.axes_grid.inset_locator as inset_locator
import matplotlib.gridspec as gridspec
from kapteyn import maputils


class velocityField():
    """
    Class to plot velocity fields.
    """

    def __init__(self, directImage):
        """
        Class constructor.
        """
        self.info = {'directImage': directImage}


    def loadVelocityField(self, input='velocityField.pk'):
        """
        Loads velocity field information from the pickled velocityField.pk
        file. This file is created by processVelocities.py so if that script
        was not run it won't be present and one cannot use this script to
        do the plot.
        """
        self.info['data'] = np.array(read.cPickledData(input)['data'])


    def loadSDSSimage(self, ext=0):
        """
        Loads SDSS image and header.

        :param ext: FITS extension, default = 0
        :type ext: int
        """
        fh = pf.open(self.info['directImage'])
        self.info['image'] = fh[ext].data
        self.info['hdr'] = fh[0].header
        fh.close()
        #set WCS
        self.info['WCS'] = pywcs.WCS(self.info['hdr'])


    def plotVelocityWCS(self):
        """
        Generates a plot with SDSS file on the background and the slicer velocities on the top.
        will also plot the centre slit velocity curve.

        :return: None
        """
        #shift y values by one, because of indexing difference between IRAF and Python
        yshift = -1

        #data manipulation
        vel = self.info['data'][:, 6].astype(np.float)
        err = self.info['data'][:, 7].astype(np.float)
        xp = self.info['data'][:, 2].astype(np.float)
        yp = self.info['data'][:, 3].astype(np.float) + yshift
        #finds the middle slit based on the header information and SLICE keyword
        #does not consider offset position
        files = self.info['data'][:, 12]
        slices = np.array([pf.open(file)[0].header['SLICE'] for file in files if 'off' not in file])
        midmsk = slices == 2

        #tries to figure out good limits automatically, this step might fail
        #depending on the galaxy
        ylims = (np.min(yp) * 0.93, np.max(yp) * 1.07)
        xlims = (np.min(xp) * 0.85, np.max(xp) * 1.15)
        tmpdata = pf.open(self.info['directImage'], memmap=1)[0].data
        tmp = tmpdata[int(np.floor(ylims[0]) * 1.1):int(np.ceil(ylims[1]) * .9),
              int(np.floor(xlims[0]) * 1.1):int(np.ceil(xlims[1]) * .9)]
        clipmin = np.min(tmp) * 0.05 #the multiplier is rather arbitrary
        clipmax = np.max(tmp) * 0.45 #the multiplier is rather arbitrary
        ticks = np.linspace(clipmin, clipmax, 4)
        ticks = [np.round(tick, 1) for tick in ticks]

        #font settings
        cbfontsize = 10

        #opens the FITS file and sets limits
        f = maputils.FITSimage(self.info['directImage'])
        f.set_limits(pxlim=xlims, pylim=ylims)

        #creates a figure and generates two subplots (grids)
        fig = plt.figure(figsize=(10, 8))
        gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1], title='Center Slit')
        gs.update(wspace=0.0, hspace=0.0, top=0.96, bottom=0.07)

        #plots the background SDSS image
        annim = f.Annotatedimage(ax1, cmap='binary', clipmin=clipmin, clipmax=clipmax)
        annim.Image(alpha=0.95)
        #cont = annim.Contours(levels=np.arange(1e-4, 1, 1e-1))

        #colour bar 1: this is the SDSS background image in nanomaggies
        inset_axes2 = inset_locator.inset_axes(ax1, width='43%', height='1.5%', loc=2)
        colbar = annim.Colorbar(frame=inset_axes2, fontsize=cbfontsize,
                                orientation='horizontal',ticks=ticks)
        colbar.set_label(label=r'flux (nanomaggies)')

        #modifies the axis labels
        grat = annim.Graticule()
        grat.setp_gratline(wcsaxis=0, linestyle=':', zorder=1)
        grat.setp_gratline(wcsaxis=1, linestyle=':', zorder=1)
        #grat.setp_ticklabel(rotation=30)
        grat.setp_tick(fontsize=16)
        grat.setp_axislabel(fontsize=16)
        #grat.set_tickmode(plotaxis=['bottom','left'], mode="Switch")
        grat.setp_ticklabel(plotaxis=['top', 'right'], visible=False)
        #grat.setp_ticklabel(plotaxis=['right'], visible=False)

        #adds a ruler
        ymid = np.mean(yp[midmsk])
        ysize = (np.max(yp) - np.min(yp)) * 0.7
        xpos = xlims[1] - 5
        ruler1 = annim.Ruler(x1=xpos, y1=ymid - ysize,
                             x2=xpos, y2=ymid + ysize,
                             mscale=0.8, fliplabelside=True,
                             lambda0=0.0, step=5.0 / 3600.)
        ruler1.setp_line(color='k', lw=1.3)
        ruler1.setp_label(color='k', fontsize=12)

        annim.plot()

        #overplot image slicer velocity field
        s = ax1.scatter(xp, yp, c=vel, s=30, marker='s', cmap=cm.jet, edgecolor='none', alpha=0.9)

        #set colour bar and modify font sizes
        inset_axes = inset_locator.inset_axes(ax1, width='43%', height='1.5%', loc=1)
        c1 = plt.colorbar(s, cax=inset_axes, orientation='horizontal')
        #inset_axes.xaxis.set_ticks_position('top')
        c1.set_label('Velocity (km s$^{-1}$)')
        ticks = np.linspace(int(np.ceil(np.min(vel))), int(np.floor(np.max(vel))), 4)
        ticks = [int(tick) for tick in ticks]
        c1.set_ticks(ticks)
        for j in c1.ax.get_xticklabels():
            j.set_fontsize(cbfontsize)

        #the second plot
        ax2.errorbar(vel[midmsk], yp[midmsk], xerr=err[midmsk],
                     marker='o', ms=4, ls='None')

        #set limits
        ax2.set_ylim(ylims[0], ylims[1])
        ax2.set_xlim(np.min(vel[midmsk]) * 0.985,
                     np.max(vel[midmsk]) * 1.015)

        #modify ticks, plot only every second on x and remove y ticks
        ax2.set_yticklabels([])
        ax2.set_yticks([])
        ax2.set_xticks(ax2.get_xticks()[::2])

        #set label on x
        ax2.set_xlabel('Velocity (km s$^{-1}$)')

        #save figure
        plt.savefig('VelocityField.pdf')


if __name__ == '__main__':
    #input file to read, change if needed
    #however, roated.fits is the default because it has been
    #oriented so that the major axis of the galaxy is vertical
    inputfile = 'rotated.fits'

    #velocity instance, do the actualy plot
    velocity = velocityField(inputfile)
    velocity.loadVelocityField()
    velocity.loadSDSSimage()
    velocity.plotVelocityWCS()
