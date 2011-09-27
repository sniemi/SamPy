"""
Class to plot velocity fields and SDSS images.

:requires: NumPy
:requires: PyFITS
:requires: matplotlib
:requires: Kapteyn Python package
:requires: SamPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.3
"""
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
    Velocity field plotting class.
    """

    def __init__(self, directImage):
        """
        Class constructor.
        """
        self.info = {'directImage': directImage}


    def combineVelocityCoordinates(self,
                                   vel='velocity.pk',
                                   coord='coordinates.pk'):
        """
        Combine velocity file and coordinate files.

        :param vel: pickled velocity information
        :type vel: str
        :param coord: pickled coordinate information
        :type coord: str
        """
        #load in data
        coords = read.cPickledData(coord)
        vel = read.cPickledData(vel)

        #output
        out = []
        low = []
        mid = []
        up = []

        #find matches
        for val in vel:
            pos = ''
            ycoord = int(val[1])

            if 's1' in val[0]:
                data = coords['low']
                pos = 'low'
            elif 's2' in val[0]:
                data = coords['mid']
                pos = 'mid'
            else:
                data = coords['up']
                pos = 'up'

            for line in data:
                if line[1] == ycoord:
                    #list so we can add them together, which is more like append...
                    tmp = line + [float(val[2]), float(val[3]), float(val[4]), float(val[5]),
                                  float(val[6]), float(val[7])]
                    out.append(tmp)

                    #this is not very efficient way...
                    if pos == 'low':
                        low.append(tmp)
                    elif pos == 'mid':
                        mid.append(tmp)
                    else:
                        up.append(tmp)

        self.info['coordinates'] = coords
        self.info['velocities'] = vel
        self.info['data'] = np.asarray(out)
        self.info['low'] = np.asarray(low)
        self.info['mid'] = np.asarray(mid)
        self.info['up'] = np.asarray(up)


    def loadSDSSimage(self, ext=0):
        """
        Loads SDSS image and header.

        :param ext: FITS extension
        :type ext: int
        """
        fh = pf.open(self.info['directImage'])
        self.info['image'] = fh[ext].data
        self.info['hdr'] = fh[0].header
        fh.close()
        #set WCS
        self.info['WCS'] = pywcs.WCS(self.info['hdr'])


    def plotVelocityWCS(self, xlims=(630, 770), ylims=(830, 1090), clipmin=1e-4, clipmax=0.7):
        """
        Generates a plot with SDSS file on the background and the slicer velocities on the top.
        will also plot the centre slit velocity curve.

        :param xlims: a tuple of xmin and xmax
        :type xlims: tuple
        :param ylims: a tuple of ymin and ymax
        :type ylims: tuple
        :param yclipmin: a minimum value to be used to clip the background image
        :type yclipmin: float
        :param yclipmax: a maximum value to be used to clip the background image
        :type yclipmax: float

        :return: None
        """
        yshift = -2

        #data manipulation
        vel = self.info['data'][:, 6]
        msk = vel > 0
        #vel[msk] -= np.mean(vel[msk])
        xp = self.info['data'][:, 2][msk]
        yp = self.info['data'][:, 3][msk]
        #only mid
        midmsk = self.info['mid'][:, 6] > 0

        #settings
        cbfontsize = 7

        f = maputils.FITSimage(self.info['directImage'])
        f.set_limits(pxlim=xlims, pylim=ylims)

        fig = plt.figure(figsize=(10, 10))
        gs = gridspec.GridSpec(1, 2, width_ratios=[4, 1])
        ax1 = plt.subplot(gs[0])
        ax2 = plt.subplot(gs[1], title='Centre Slit')
        gs.update(wspace=0.01, hspace=0.01, left=0.02, right=0.94, top=0.92, bottom=0.07)
        #old method
        #[left, bottom, width, height]
        #rect_img = [0.0, 0.06, 0.8, 0.85]
        #rect_sct = [0.80, 0.06, 0.15, 0.85]
        #ax1 = plt.axes(rect_img)
        #ax2 = plt.axes(rect_sct)

        annim = f.Annotatedimage(ax1, cmap='binary', clipmin=clipmin, clipmax=clipmax)
        annim.Image(alpha=0.95)
        #cont = annim.Contours(levels=np.arange(1e-4, 1, 1e-1))

        #colour bar
        inset_axes2 = inset_locator.inset_axes(ax1, width='45%', height='1%', loc=2)
        units = r'flux (nanomaggies)'
        colbar = annim.Colorbar(frame=inset_axes2, fontsize=cbfontsize, orientation='horizontal')
        colbar.set_label(label=units)#, fontsize=13)

        grat = annim.Graticule()
        grat.setp_gratline(wcsaxis=0, linestyle=':', zorder=1)
        grat.setp_gratline(wcsaxis=1, linestyle=':', zorder=1)
        #grat.setp_ticklabel(rotation=30)
        grat.setp_tick(fontsize=12)
        grat.set_tickmode(plotaxis=['bottom','left'], mode="Switch")
        grat.setp_ticklabel(plotaxis=['top','right'], visible=False)

        #add ruler
        #ymid = np.mean(self.info['mid'][:, 3][midmsk])
        #xmid = np.mean(self.info['mid'][:, 2][midmsk])
        #ysize = (ylims[1] - ylims[0]) / 2.35
        xmid = xlims[1]-6
        #ruler1 = annim.Ruler(x1=xmid+1, y1=ymid-ysize,
        #                     x2=xmid+1, y2=ymid+ysize,
        #                     mscale=0.8, fliplabelside=True,
        #                     lambda0=0.0, step=5.0/3600.)
        ruler1 = annim.Ruler(x1=xmid+1, y1=ylims[0] + 17,
                             x2=xmid+1, y2=ylims[1] - 17,
                             mscale=0.8, fliplabelside=True,
                             lambda0=0.0, step=5.0/3600.)

        ruler1.setp_line(color='k', lw=1.5)
        ruler1.setp_label(color='k', fontsize=11)

        annim.plot()
        
        #overplot image slicer velocity field
        s = ax1.scatter(xp,
                        yp+yshift,
                        c=vel[msk],
                        s=30,
                        marker='s',
                        cmap=cm.jet,
                        edgecolor='none',
                        alpha=0.8)

        #set colour bar and modify font sizes
        inset_axes = inset_locator.inset_axes(ax1, width='45%', height='1%', loc=1)
        c1 = plt.colorbar(s, cax=inset_axes, orientation='horizontal')
        #inset_axes.xaxis.set_ticks_position('top')
        c1.set_label('Velocity (km s$^{-1}$)')
        t = c1.ax.get_xticklabels()
        for j in t:
            j.set_fontsize(cbfontsize)

        #the second plot
        ax2.errorbar(self.info['mid'][:, 6][midmsk],
                     self.info['mid'][:, 3][midmsk]+yshift,
                     xerr=self.info['mid'][:, 7][midmsk],
                     marker='o', ms=4, ls='None')


        #set limits
        ax2.set_ylim(ylims[0], ylims[1])
        ax2.set_xlim(np.min(self.info['mid'][:, 6][midmsk]) * 0.985,
                     np.max(self.info['mid'][:, 6][midmsk]) * 1.015)

        #modify ticks
        ax2.set_yticklabels([])
        ax2.set_yticks([])
        ax2.set_xticks(ax2.get_xticks()[::2])

        ax2.set_xlabel('Velocity (km s$^{-1}$)')

        plt.savefig('VelocityField.pdf')


if __name__ == '__main__':
    #change these
    inputfile = 'rotated.fits'
    xlims = (625, 770)
    ylims = (860, 1085)

    #velocity instance
    velocity = velocityField(inputfile)
    velocity.loadSDSSimage()
    velocity.combineVelocityCoordinates()
    velocity.plotVelocityWCS(xlims=xlims, ylims=ylims)