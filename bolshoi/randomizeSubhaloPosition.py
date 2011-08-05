'''
Randomizes a subhalo galaxy position (RA and DEC)
'''
import matplotlib.pyplot as plt
import numpy as np
from astLib import astCoords
from cosmocalc import cosmocalc
# from Sami's repo
import SamPy.astronomy.randomizers as rand
import SamPy.astronomy.conversions as conv

__author__ = 'Sami-Matias Niemi'

def plotRandomization():
    #number of random points
    points = 1000
    # get the random values
    rds = rand.randomUnitSphere(points)
    # convert them to Cartesian coord
    rd = conv.convertSphericalToCartesian(1,
                                          rds['theta'],
                                          rds['phi'])

    #set figure limits
    min = -1.3
    max = 1.3

    #make a figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    #generate a sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    #plot it as a wire frame
    ax.plot_wireframe(x, y, z,
                      rstride=4,
                      cstride=4,
                      color='k')

    #plot the random points
    ax.scatter(rd['x'], rd['y'], rd['z'],
               color = 'red')
    #project them on the bottom
    ax.scatter(rd['x'], rd['y'],
               zs=min, zdir='z')
    #project them on the left
    ax.scatter(rd['y'], rd['z'],
               min, zdir='x')

    ax.set_xlim3d(min, max)
    ax.set_ylim3d(min, max)
    ax.set_zlim3d(min, max)

    plt.show()

def plotTestRandmizer(size,
                      rds,
                      fudge=1.1):

    rd = conv.convertSphericalToCartesian(size,
                                          rds['theta'],
                                          rds['phi'])
    #make a figure
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.view_init(22, -19)

    #generate a sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = size*np.outer(np.cos(u), np.sin(v))
    y = size*np.outer(np.sin(u), np.sin(v))
    z = size*np.outer(np.ones(np.size(u)), np.cos(v))
    #plot it as a wire frame
    ax.plot_wireframe(x, y, z,
                      rstride=6,
                      cstride=6,
                      color='k')

    #plot main galaxy
    ax.scatter([0,], [0,], [0,], color = 'magenta',
               label = 'Main Galaxy')
    #plot the random points
    ax.scatter(rd['x'], rd['y'], rd['z'],
               color = 'red',
               label = 'Subhalo Galaxy')
    #project them on the bottom
    ax.scatter(rd['x'], rd['y'],
               zs=-size*fudge, zdir='z',
               label = 'Projection')
    #project them on the back
    ax.scatter(rd['x'], rd['z'],
               size*fudge, zdir='y',
               label = 'Projection')
    #project them on the left
    ax.scatter(rd['y'], rd['z'],
               -size*fudge, zdir='x',
               label = 'Projection')

    ax.set_xlim3d(-size*fudge, size*fudge)
    ax.set_ylim3d(-size*fudge, size*fudge)
    ax.set_zlim3d(-size*fudge, size*fudge)

    ax.set_xlabel('x = line-of-sight [kpc]')
    ax.set_ylabel('y = X = -RA [kpc]')
    ax.set_zlabel('z = Y = DEC [kpc]')

    ax.legend()

    plt.show()


def testRandomizer():

    #calculate a test case
    conversion = 0.000277777778 # degree to arcsecond
    #random distance between z = 0 and 5
    z = np.random.rand() * 5.0
    #random separation of the main galaxy and the subhalo
    physical_distance = np.random.rand() * 1e3 #in kpc
    #get the angular diameter distance to the galaxy
    dd1 = cosmocalc(z, 71.0, 0.28)['PS_kpc'] #in kpc / arc seconds
    dd = (physical_distance / dd1) * conversion # to degrees
    # RA and DEC of the main galaxy, first one in GOODS south
    ra_main = 52.904892 #in degrees
    dec_main = -27.757082 #in degrees
    # get the random position
    rds = rand.randomUnitSphere(points=1)
    # convert the position to Cartesian coord
    # when dd is the radius of the sphere coordinates
    # the dd is in units of degrees here so the results
    # are also in degrees.
    rd = conv.convertSphericalToCartesian(dd,
                                          rds['theta'],
                                          rds['phi'])


    # Make the assumption that x is towards the observer
    # z is north and y is west. Now if we assume that our z and y
    # are Standard Coordinates, i.e., the projection of the RA and DEC
    # of an object onto the tangent plane of the sky. We can now
    # assume that the y coordinate is aligned with RA and the z coordinate
    # is aligned with DEC. The origin of this system is at the tangent point
    # in the dark matter halo.
    # Poor man's solution to the problem would be:
    new_ra = ra_main - (rd['y'][0]/np.cos(rd['z'][0]))
    new_dec = dec_main + rd['z'][0]
    # However, this only works if one is away from the pole.
    # More general solution can be derived using spherical geometry:
    data = {}
    data['CD'] = np.matrix('-1 0; 0 1')
    data['RA'] = ra_main
    data['DEC'] = dec_main
    data['X'] = rd['y'][0]
    data['Y'] = rd['z'][0]
    result = conv.RAandDECfromStandardCoordinates(data)


    #print the output
    print 'Redshift of the galaxy is %.3f while the subhaloes distance is %0.2f kpc'% (z, physical_distance)
    print '\nCoordinates of the main halo galaxy are (RA and DEC):'
    print '%.7f  %.7f' % (ra_main, dec_main)
    print astCoords.decimal2hms(ra_main, ':'), astCoords.decimal2dms(dec_main, ':')
    print '\nCoordinates for the subhalo galaxy are (RA and DEC):'
    print '%.7f  %.7f' % (new_ra, new_dec)
    print astCoords.decimal2hms(new_ra, ':'), astCoords.decimal2dms(new_dec, ':')
    print 'or when using more accurate technique'
    print '%.7f  %.7f' % (result['RA'], result['DEC'])
    print astCoords.decimal2hms(result['RA'], ':'), astCoords.decimal2dms(result['DEC'], ':')
    #print 'Shift in RA and DEC [degrees]:'
    #print  rd['y'][0], (rd['z'][0]/np.cos(rd['z'][0]))
    print '\nShift in RA and DEC [seconds]:'
    print  -rd['y'][0]/np.cos(rd['z'][0])/conversion, rd['z'][0]/conversion
    print 'or again with the better method:'
    print (result['RA'] - ra_main)/conversion, (result['DEC'] - dec_main)/conversion
    #print '\nDistance inferred from the coordinates vs the real distance vs x'
    #print np.sqrt((rd['y'][0]/conversion)**2 + ((rd['z'][0]/np.cos(rd['z'][0]))/conversion)**2) * dd1, \
    #      physical_distance, rd['x'][0]


    plotTestRandmizer(physical_distance, rds)

if __name__ == '__main__':

    #plotRandomization()

    testRandomizer()