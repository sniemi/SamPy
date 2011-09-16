"""
Class to plot velocity fields and SDSS images.

:requires: NumPy
:requires: PyFITS
:requires: matplotlib

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.2
"""
import numpy as np
import pyfits as pf
import pywcs
from matplotlib import pyplot as plt
from matplotlib import cm
import SamPy.smnIO.read as read

from kapteyn import maputils, tabarray


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

        #find matches
        for val in vel:
            ycoord = int(val[1])

            if 's1' in val[0]:
                data = coords['low']
            elif 's2' in val[0]:
                data = coords['mid']
            else:
                data = coords['up']

            for line in data:
                if line[1] == ycoord:
                    #list so we can add them together, which is more like append...
                    tmp = line + [float(val[2]), float(val[3]), float(val[4]), float(val[5]),
                                  float(val[6]), float(val[7])]
                    out.append(tmp)

        self.info['coordinates'] = coords
        self.info['velocities'] = vel
        self.info['data'] = np.asarray(out)


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


    def plotVelocityWCS(self, xlims=(630, 770), ylims=(830, 1090)):
        """
        Generates a plot with SDSS file on the background and the slicer velocities on the top.

        :param xlims: a tuple of xmin and xmax
        :type xlims: tuple
        :param ylims: a tuple of ymin and ymax
        :type ylims: tuple

        :return: None
        """
        vel = self.info['data'][:,6]
        msk = vel > 0
        #vel[msk] -= np.mean(vel[msk])
        xp = self.info['data'][:,2][msk]
        yp = self.info['data'][:,3][msk]

        f = maputils.FITSimage(self.info['directImage'])
        f.set_limits(pxlim=xlims, pylim=ylims)

        fig = plt.figure()
        frame = fig.add_subplot(1,1,1)

        annim = f.Annotatedimage(frame, cmap='binary', clipmin=1e-4, clipmax=0.7)
        annim.Image(alpha=0.9)
        #cont = annim.Contours(levels=np.arange(1e-4, 1, 1e-1))

        units = r'nanomaggies'
        colbar = annim.Colorbar(fontsize=6)
        colbar.set_label(label=units, fontsize=13)

        grat = annim.Graticule()
        grat.setp_gratline(wcsaxis=0, linestyle=':')
        grat.setp_gratline(wcsaxis=1, linestyle=':')
        grat.setp_ticklabel(rotation=30)

        s = frame.scatter(xp,
                          yp,
                          c=vel[msk],
                          s=15, marker = 's',
                          cmap=cm.jet,
                          edgecolor='none',
                          alpha=0.7)
        c1 = fig.colorbar(s, ax=frame, shrink=0.7, fraction=0.05)
        c1.set_label('Velocity [km/s]')

        annim.plot()
        plt.savefig('VelocityOverplotted.pdf')


if __name__ == '__main__':
    #change these
    inputfile = 'rotated.fits'
    xlims = (100, 300)
    ylims = (100, 300)

    #velocity instance
    velocity = velocityField(inputfile)
    velocity.loadSDSSimage()
    velocity.combineVelocityCoordinates()
    velocity.plotVelocityWCS(xlims=xlims, ylims=ylims)