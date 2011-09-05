"""
Basic functions that are related to statistics.

:requires: NumPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import numpy as np

def chiSquare(model, obs):
    """
    Simple :math:`\\chi^{2}` calculation.

    .. math::

        \\Sigma \\frac{(observedFrequency - expectedTheoreticalFrequency)^{2}}{theoreticalExpectedFrequency}

    calculation

    :param model: model data
    :param obs: observed data

    :return: :math:`\\chi^{2}`
    :rtype: float
    """
    r = np.sum((obs - model) ** 2 / model)
    return r


def stdevclipping(array, lowcut=4, highcut=4, maxnit=50, verbose=False):
    """
    Sigmaclipped standard deviation, mean, and median.

    :param array: data
    :type array: list or ndarray
    :param lowcut: lower cut limit
    :type lowcut: int or float
    :param highcut: higher cut limit
    :type highcut: int or float
    :param maxnit: maximum number of iterations
    :type maxnit: int
    :param verbose: whether to print out the information on screen or not
    :type verbose: boolean

    :return: std, mean, median, nreject
    :rtype: list
    """
    if type(array) in (list, tuple):
        flat = np.array(array).ravel()
    else:
        flat = array.ravel()
    n = flat.size
    if n < 3:
        raise RuntimeError("The array must have at least 3 elements")
    niter = 0
    ngood = n
    nreject = 0
    nrej_last = -1

    and_ = np.logical_and
    while niter < maxnit and ngood > 3 and nreject != nrej_last:
        nrej_last = nreject
        std = flat.std()
        median = np.median(flat)
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
