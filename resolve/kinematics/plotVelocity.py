"""
Class to plot velocity fields and SDSS images.

:requires: NumPy
:requires: PyFITS
:requires: matplotlib

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
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
    Velocity field.
    """

    def __init__(self, directImage):
        """
        Constructor
        """
        self.info = {}
        self.info['directImage'] = directImage


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


    def plotVelocity(self):
        """

        :Note: there are hard coded values here...
        """
        vel = self.info['data'][:,6]
        msk = vel > 0
        #vel[msk] -= np.mean(vel[msk])

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.imshow(self.info['image'],
                  origin='lower',
                  cmap=cm.gist_gray_r,
                  vmax=0.6,
                  vmin=1e-5)
        ax.scatter(self.info['data'][:,2][msk],
                   self.info['data'][:,3][msk],
                   c=vel[msk],
                   s=20, marker = 's',
                   cmap=cm.jet,
                   edgecolor='none',
                   alpha=0.8)

        #TODO: remove these hard coded values...
        ax.set_xlim(2050, 2201)
        ax.set_ylim(1081, 1250)

        fig.savefig('test.pdf')


    def plotVelocityWCS(self):
        """

        """
        vel = self.info['data'][:,6]
        msk = vel > 0
        #vel[msk] -= np.mean(vel[msk])
        xp = self.info['data'][:,2][msk]
        yp = self.info['data'][:,3][msk]

        f = maputils.FITSimage(self.info['directImage'])
        f.set_limits(pxlim=(630, 770), pylim=(830, 1090))

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


        #better to do this in RA and DEC actually...
        #annim.Marker(x=xp, y=yp, mode='pixels', marker='s', color=vel[msk])

        frame.scatter(xp,
                      yp,
                      c=vel[msk],
                      s=20, marker = 's',
                      cmap=cm.jet,
                      edgecolor='none',
                      alpha=0.8)

        annim.plot()
        plt.savefig('test2.pdf')


if __name__ == '__main__':
    velocity = velocityField('rotated.fits')
    velocity.loadSDSSimage()
    velocity.combineVelocityCoordinates()
    #velocity.plotVelocity()
    velocity.plotVelocityWCS()
