'''
A random collection of functions for data manipulation.

@requires: NumPy, SciPy

@version: 0.1

@author: Sami Niemi
'''
import numpy as N
import scipy.stats as ss

def percentile_bins(xdata, ydata, xmin, xmax,
                    nxbins = 15, log = False,
                    limit = 6):
    '''
    Computes median and 16 and 84 percentiles of y-data in bins in x
    @param xdata: numpy array of xdata
    @param ydata: numpy arrya of ydata
    @param xmax: maximumx value of x that data are binned to
    @param xmin: minimum value of x that data are binned to
    @param nxbins: number of bins in x
    @param log: if True, xbins are logarithmically spaced, else linearly
    @param limit: the minimum number of values in a bin for which the
                median and percentiles are returned for.
    @return: mid points of the bins, median, 16 per cent percentile, and
    84 per cent percentile.
    '''
    if log:
        xbin = N.logspace(xmin, xmax, nxbins)
    else:
        xbin = N.linspace(xmin, xmax, nxbins)
    nbin = len(xbin) - 1
    xbin_mid = N.zeros(nbin)
    y50 = N.zeros(nbin) - 99.
    y16 = N.zeros(nbin) - 99.
    y84 = N.zeros(nbin) - 99.

    for i in range(nbin):
        xbin_mid[i] = xbin[i] + 0.5*(xbin[i+1] - xbin[i])
        mask = (xdata > xbin[i]) & (xdata <= xbin[i+1])
        if len(ydata[mask]) >= limit:
            y50[i] = ss.scoreatpercentile(ydata[mask], 50)
            y16[i] = ss.scoreatpercentile(ydata[mask], 16)
            y84[i] = ss.scoreatpercentile(ydata[mask], 84)
    return xbin_mid, y50, y16, y84

def average_bins(xdata, ydata, xmin, xmax, nxbins = 15):
    '''
    Computes mean and 16 and 84 percentiles of y-data in bins in x
    @param xdata: numpy array of xdata
    @param ydata: numpy arrya of ydata
    @param xmax: maximumx value of x that data are binned to
    @param xmin: minimum value of x that data are binned to
    @param nxbins: number of bins in x     
    @return: mid points of the bins, mean, 16 per cent percentile, and
    84 per cent percentile.
    '''
    xbin = N.linspace(xmin, xmax, nxbins)
    nbin = len(xbin) - 1
    xbin_mid = N.zeros(nbin)
    y50 = N.zeros(nbin) - 99.
    y16 = N.zeros(nbin) - 99.
    y84 = N.zeros(nbin) - 99.

    for i in range(nbin):
        xbin_mid[i] = xbin[i] + 0.5*(xbin[i+1] - xbin[i])
        mask = (xdata > xbin[i]) & (xdata <= xbin[i+1])
        if len(ydata[mask]) >= 10:
            y50[i] = N.mean(ydata[mask])
            y16[i] = ss.scoreatpercentile(ydata[mask], 16)
            y84[i] = ss.scoreatpercentile(ydata[mask], 84)
    return xbin_mid, y50, y16, y84

def binned_average(xdata, ydata, xbins, step):
    x = []
    y = []
    yerr = []
    std = []
    for a in xbins:
        mask = (xdata >= a) & (xdata < a + step)
        mean = N.mean(ydata[mask])
        error = N.std(ydata[mask]) / N.sqrt(len(ydata[mask]))
        x.append(a + step/2.)
        y.append(mean)
        yerr.append(error)
        std.append(N.std(ydata[mask]))
        del mask
    return x, y, yerr, std
