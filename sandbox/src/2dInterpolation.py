import numpy, pylab
from scipy import interpolate
from matplotlib import cm

# 2D interpolation example.
def my2d():
     """2D interpolation example.
    
     References:
     http://matplotlib.sourceforge.net/index.html
     http://www.scipy.org/doc/api_docs/SciPy.interpolate.interpolate.interp2d.html
     """
    
     # Scattered data points to be interpolated
     # These are arbitrary numbers for this exercise
     x = numpy.array([0.0, 1767.0, 1767.0, 0.0, -1767.0, -1767.0, -1767.0, 0.0, 1767.0])
     y = numpy.array([0.0, 0.0, 1767.0, 1767.0, 1767.0, 0.0, -1767.0, -1767.0, -1767.0])
     z = numpy.array([27, 16, 0, 12, 69, 128, 292, 332, 298])
    
     # Print the data to screen for checking
     print 'DATA USED FOR INTERPOLATION:'
     for val, tuple in enumerate(zip(x,y,z)):
         print val, ':', tuple[0], tuple[1], tuple[2]
    
     # Coordinates to fill with interpolated data
     xi = numpy.arange(numpy.min(x), numpy.max(x))
     yi = numpy.arange(numpy.min(y), numpy.max(y))
    
     # Perform 2D interpolation
     l = interpolate.interpolate.interp2d(x, y, z)
     im = l(xi, yi)
    
     # Get min/max to use same colorbar on for base and overlay
     pmin = im.min()
     pmax = im.max()
    
     # Show interpolated 2D image
     p = pylab.imshow(im, vmin=pmin, vmax=pmax, cmap = cm.gist_yarg,
                      origin = 'lower', extent=[numpy.min(x), numpy.max(x), numpy.min(y), numpy.max(y)])
    
     c = pylab.contour(im,origin = 'lower', extent=[numpy.min(x), numpy.max(x), numpy.min(y), numpy.max(y)])
    
     pylab.clabel(c, inline=1, fontsize=8)
    
     # Display colobar
     # Optional shrink to make it same width as display
     c = pylab.colorbar(p, orientation='horizontal', shrink=0.7)
     c.set_label('Raw Counts at Dwell Points')
    
     # Plot labels
     pylab.xlabel('Dispersion Offset (mas)')
     pylab.ylabel('Cross-Dispersion Offset (mas)')
     pylab.title('11531 Visit 7 Target Acquisition')
    
     #pylab.show()
     pylab.savefig('2dAcq.pdf')
    # End of my2d()

if __name__ == '__main__':
    my2d()