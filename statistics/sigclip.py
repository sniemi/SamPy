'''
Sigmaclipped standard deviation, mean, and median
'''
import numpy

def stdevclipping(array, lowcut=4, highcut=4, maxnit=50, verbose=False):
    if type(array) in (list, tuple):
        flat = numpy.array(array).ravel()
    else:
        flat = array.ravel()
    n = flat.size
    if n < 3:
        raise RuntimeError("The array must have at least 3 elements")
    niter = 0
    ngood = n
    nreject = 0
    nrej_last = -1

    and_ = numpy.logical_and
    while niter < maxnit and ngood > 3 and nreject != nrej_last:
        nrej_last = nreject
        std = flat.std()
        median = numpy.median(flat)
        mean = (flat - median).sum() / ngood + median
        flat = flat.compress(and_(flat >= median - lowcut * std,
                                  flat <= median + highcut * std))
        niter += 1
        if verbose:
            print "%3d    %4d  %12.3f  %12.3f  %12.3f" % (niter, nreject,
                                                          mean, median, std)
        ngood = flat.size
        nreject = n - ngood

    return std, mean, median, nreject
