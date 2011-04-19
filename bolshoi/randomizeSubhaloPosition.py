from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
# from Sami's repo
import astronomy.randomizers as rd
import astronomy.conversions as conv

__author__ = 'Sami-Matias Niemi'


if __name__ == '__main__':
    #number of random points
    points = 1000
    # get the random values
    rds = rd.randomUnitSphere(points)
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