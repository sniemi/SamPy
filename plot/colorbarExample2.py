import pylab as P
import numpy
from mpl_toolkits.axes_grid import make_axes_locatable
import  matplotlib.axes as maxes
from matplotlib import cm

if __name__ == '__main__':

    fig = P.figure(figsize=(10,10))
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    s1 = ax1.scatter(numpy.random.rand(10),
                     numpy.random.rand(10),
                     c=numpy.random.rand(10))
    divider = make_axes_locatable(ax1)
    cax1 = divider.new_horizontal('5%', pad=0.0, axes_class=maxes.Axes)
    fig.add_axes(cax1)
    c1 = fig.colorbar(s1, cax = cax1,orientation = 'horizontal')

    s2 = ax2.scatter(numpy.random.rand(10),
                     numpy.random.rand(10),
                     c=numpy.random.rand(10),
                     cmap = cm.get_cmap('jet'))
    divider = make_axes_locatable(ax2)
    cax2 = divider.append_axes('right', 0.1, pad=0.1)
    c2 = fig.colorbar(s2, cax = cax2)
    #p =  matplotlib.patches.Patch(color=cm.get_cmap('jet'))
    #ax2.legend([p],['Test'])

    s3 = ax3.scatter(numpy.random.rand(10),
                     numpy.random.rand(10),
                     c=numpy.random.rand(10))
    cax3 = fig.add_axes([0.2, 0.4, 0.1, 0.01])  #[left, bottom, width, height]
    c3 = fig.colorbar(s3, cax = cax3, orientation = 'horizontal',
                      ticks=[0.15, 0.5, 0.85])

    s4 = ax4.scatter(numpy.random.rand(10),
                     numpy.random.rand(10),
                     c=numpy.random.rand(10))
    divider = make_axes_locatable(ax4)
    cax4 = fig.add_axes([0.55, 0.25, 0.05, 0.2])
    c4 = fig.colorbar(s4, cax = cax4)

    P.show()
