"""
Randomizes a subhalo galaxy position (RA and DEC)

:Author: Sami-Matias Niemi
:contact: sammy@sammyniemi.com
"""
import matplotlib
matplotlib.use('PDF')
matplotlib.rc('text', usetex=True)
matplotlib.rcParams['font.size'] = 11
matplotlib.rc('xtick', labelsize=12)
matplotlib.rc('axes', linewidth=1.1)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 3
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
from astLib import astCoords
import astLib.astCoords as Coords
from cosmocalc import cosmocalc
import SamPy.astronomy.randomizers as rand
import SamPy.astronomy.conversions as conv


def quickPlot(galaxies=170, rvir=0.105):
    """
    A single halo test

    :param galaxies: number of subhalo galaxies
    :param rvir: radius of the main halo [Mpc]
    """
    conversion = 0.000277777778 # degree to arcsecond

    #redshift
    z = 4.477
    #get the angular diameter distance to the galaxy
    dd = cosmocalc(z, 71.0, 0.28)['PS_kpc'] #in kpc / arc seconds

    #position of the main galaxy
    RADeg1 = 189.41432
    decDeg1 = 62.166702

    # get the random values
    rds = rand.randomUnitSphere(galaxies)
    # convert them to Cartesian coord
    rd = conv.convertSphericalToCartesian(rvir/dd/2., rds['theta'], rds['phi'])

    data = {'CD': np.matrix('-1 0; 0 1'), 'RA': RADeg1, 'DEC': decDeg1, 'X': rd['y'], 'Y': rd['z']}

    result = conv.RAandDECfromStandardCoordinates(data)

    RADeg2 = result['RA']
    decDeg2 = result['DEC']

    #calculate the angular separation on the sky
    sep = Coords.calcAngSepDeg(RADeg1, decDeg1, RADeg2, decDeg2) / 2.
    physical_distance = sep * dd / conversion

    text = r'Random Positions, z={0:.2f}, radius of the halo = {1:.0f} kpc'.format(z, 1e3 * rvir)

    #make a figure
    fig = plt.figure(figsize=(12,12))

    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    rect = fig.add_subplot(224, visible=False).get_position()
    ax4 = Axes3D(fig, rect)

    ax1.hist(sep * 1e4, bins=12)
    ax2.hist(physical_distance, bins=12)
    ax3.scatter(0, 0, c='k', s=120, marker='s')
    ax3.scatter((RADeg2 - RADeg1) * 1e4, (decDeg2 - decDeg1) * 1e4, c='b', s=50, marker='o', alpha=0.45)

    #generate a sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = np.outer(np.cos(u), np.sin(v))
    y = np.outer(np.sin(u), np.sin(v))
    z = np.outer(np.ones(np.size(u)), np.cos(v))
    #plot it as a wire frame
    ax4.plot_wireframe(x*1e4*rvir/dd, y*1e4*rvir/dd, z*1e4*rvir/dd,
                       rstride=10, cstride=10, color='0.5', alpha=0.7)

    #plot the random points
    ax4.scatter(rd['x']*2e4, rd['y']*2e4, rd['z']*2e4, color='b', s=30, alpha=0.8)

    ax1.set_xlabel(r'Projected Separation [$10^{-4}$ deg]')
    ax2.set_xlabel(r'Projected Distance [kpc]')
    ax3.set_xlabel(r'$\Delta$RA [$10^{-4}$ deg]')
    #ax4.set_xlabel(r'$\Delta$RA [$10^{-4}$ deg]')
    ax3.set_ylabel(r'$\Delta$DEC [$10^{-4}$ deg]')
    #ax4.set_ylabel(r'$\Delta$DEC [$10^{-4}$ deg]')

    ax3.set_xlim(-200, 200)
    ax3.set_ylim(-100, 100)
    ax4.set_xlim3d(-150, 150)
    ax4.set_ylim3d(-150, 150)
    ax4.set_zlim3d(-150, 150)

    plt.annotate(text, (0.5, 0.95), xycoords='figure fraction', ha='center', va='center', fontsize=12)

    plt.savefig('RandomHalo.pdf')


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
    ax = Axes3D(fig)

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
        color='red')
    #project them on the bottom
    ax.scatter(rd['x'], rd['y'],
        zs=min, zdir='z')
    #project them on the left
    ax.scatter(rd['y'], rd['z'],
        min, zdir='x')

    ax.set_xlim3d(min, max)
    ax.set_ylim3d(min, max)
    ax.set_zlim3d(min, max)

    plt.savefig('RandomTest1.pdf')


def plotTestRandmizer(size,
                      rds,
                      fudge=1.1):
    rd = conv.convertSphericalToCartesian(size,
        rds['theta'],
        rds['phi'])
    #make a figure
    fig = plt.figure()
    ax = Axes3D(fig)
    ax.view_init(22, -19)

    #generate a sphere
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)
    x = size * np.outer(np.cos(u), np.sin(v))
    y = size * np.outer(np.sin(u), np.sin(v))
    z = size * np.outer(np.ones(np.size(u)), np.cos(v))
    #plot it as a wire frame
    ax.plot_wireframe(x, y, z,
        rstride=6,
        cstride=6,
        color='k')

    #plot main galaxy
    ax.scatter([0, ], [0, ], [0, ], color='magenta',
        label='Main Galaxy')
    #plot the random points
    ax.scatter(rd['x'], rd['y'], rd['z'],
        color='red',
        label='Subhalo Galaxy')
    #project them on the bottom
    ax.scatter(rd['x'], rd['y'],
        zs=-size * fudge, zdir='z',
        label='Projection')
    #project them on the back
    ax.scatter(rd['x'], rd['z'],
        size * fudge, zdir='y',
        label='Projection')
    #project them on the left
    ax.scatter(rd['y'], rd['z'],
        -size * fudge, zdir='x',
        label='Projection')

    ax.set_xlim3d(-size * fudge, size * fudge)
    ax.set_ylim3d(-size * fudge, size * fudge)
    ax.set_zlim3d(-size * fudge, size * fudge)

    ax.set_xlabel('x = line-of-sight [kpc]')
    ax.set_ylabel('y = X = -RA [kpc]')
    ax.set_zlabel('z = Y = DEC [kpc]')

    ax.legend()

    plt.savefig('RandomTest2.pdf')


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
    new_ra = ra_main - (rd['y'][0] / np.cos(rd['z'][0]))
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
    print 'Redshift of the galaxy is %.3f while the subhaloes distance is %0.2f kpc' % (z, physical_distance)
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
    print  -rd['y'][0] / np.cos(rd['z'][0]) / conversion, rd['z'][0] / conversion
    print 'or again with the better method:'
    print (result['RA'] - ra_main) / conversion, (result['DEC'] - dec_main) / conversion
    #print '\nDistance inferred from the coordinates vs the real distance vs x'
    #print np.sqrt((rd['y'][0]/conversion)**2 + ((rd['z'][0]/np.cos(rd['z'][0]))/conversion)**2) * dd1, \
    #      physical_distance, rd['x'][0]


if __name__ == '__main__':
    quickPlot()
    #plotRandomization()
    #testRandomizer()
