"""
A (random) collection of functions for data manipulation.

:requires: NumPy
:requires: SciPy

:version: 0.2

:author: Sami-Matias Niemi
:contact: sammy@sammyniemi.com
"""
import numpy as N
import scipy.stats as ss

def percentile_bins(xdata, ydata, xmin, xmax,
                    nxbins=15, log=False,
                    limit=6):
    """
    Computes median and 16 and 84 percentiles of y-data in bins in x.

    :param xdata: numpy array of xdata
    :param ydata: numpy arrya of ydata
    :param xmax: maximum value of x that data are binned to
    :param xmin: minimum value of x that data are binned to
    :param nxbins: number of bins in x
    :param log: if True, xbins are logarithmically spaced, else linearly
    :param limit: the minimum number of values in a bin for which the
                  median and percentiles are returned for.

    :return: mid points of the bins, median, 16 per cent percentile, and 84 per cent percentile.
    """
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
        xbin_mid[i] = xbin[i] + 0.5 * (xbin[i + 1] - xbin[i])
        mask = (xdata > xbin[i]) & (xdata <= xbin[i + 1])
        if len(ydata[mask]) >= limit:
            y50[i] = ss.scoreatpercentile(ydata[mask], 50)
            y16[i] = ss.scoreatpercentile(ydata[mask], 16)
            y84[i] = ss.scoreatpercentile(ydata[mask], 84)
    return xbin_mid, y50, y16, y84


def average_bins(xdata, ydata, xmin, xmax, nxbins=15):
    """
    Computes mean and 16 and 84 percentiles of y-data in bins in x

    :param xdata: numpy array of xdata
    :param ydata: numpy arrya of ydata
    :param xmax: maximumx value of x that data are binned to
    :param xmin: minimum value of x that data are binned to
    :param nxbins: number of bins in x

    :return: mid points of the bins, mean, 16 per cent percentile, and 84 per cent percentile.
    """
    xbin = N.linspace(xmin, xmax, nxbins)
    nbin = len(xbin) - 1
    xbin_mid = N.zeros(nbin)
    y50 = N.zeros(nbin) - 99.
    y16 = N.zeros(nbin) - 99.
    y84 = N.zeros(nbin) - 99.

    for i in range(nbin):
        xbin_mid[i] = xbin[i] + 0.5 * (xbin[i + 1] - xbin[i])
        mask = (xdata > xbin[i]) & (xdata <= xbin[i + 1])
        if len(ydata[mask]) >= 10:
            y50[i] = N.mean(ydata[mask])
            y16[i] = ss.scoreatpercentile(ydata[mask], 16)
            y84[i] = ss.scoreatpercentile(ydata[mask], 84)
    return xbin_mid, y50, y16, y84


def binned_average(xdata, ydata, xbins, step):
    """
    Calculates a binned average from data

    :param xdata: x vector
    :param ydata: y vector
    :param xbins: a vector of x bins
    :param step: size of the step

    :return: binned average values
    """
    x = []
    y = []
    yerr = []
    std = []
    for a in xbins:
        mask = (xdata >= a) & (xdata < a + step)
        mean = N.mean(ydata[mask])
        error = N.std(ydata[mask]) / N.sqrt(len(ydata[mask]))
        x.append(a + step / 2.)
        y.append(mean)
        yerr.append(error)
        std.append(N.std(ydata[mask]))
        del mask
    return x, y, yerr, std


def binAndReturnMergerFractions(mstar,
                                nomerge,
                                mergers,
                                majors,
                                mstarmin=9,
                                mstarmax=11.5,
                                mbins=10,
                                logscale=False):
    """
    Bin the data and return different merger fractions.
    """
    out = []
    #bins
    if logscale:
        mb = N.logspace(N.log10(mstarmin), N.log10(mstarmax), mbins)
        mids = rollingAverage(mb)
    else:
        mb = N.linspace(mstarmin, mstarmax, mbins)
        mids = mb[:-1] + (mb[1] - mb[0]) / 2.
        #check the mergers
    for i, low in enumerate(mb):
        if i < mbins - 1:
            msk = (mstar >= low) & (mstar < mb[i + 1])
            tmp1 = len(mstar[msk])
            tmp2 = len(mstar[msk & nomerge])
            tmp3 = len(mstar[msk & mergers])
            tmp4 = len(mstar[msk & majors])
            out.append([tmp1, tmp2, tmp3, tmp4])
    return mids, out


def binAndReturnMergerFractions2(mstar,
                                 nomerge,
                                 mergers,
                                 majors,
                                 mergers2,
                                 majors2,
                                 mstarmin=9,
                                 mstarmax=11.5,
                                 mbins=10,
                                 logscale=False):
    """
    Bin the data and return different merger fractions.
    """
    out = []
    #bins
    if logscale:
        mb = N.logspace(N.log10(mstarmin), N.log10(mstarmax), mbins)
        mids = rollingAverage(mb)
    else:
        mb = N.linspace(mstarmin, mstarmax, mbins)
        mids = mb[:-1] + (mb[1] - mb[0]) / 2.
        #check the mergers
    for i, low in enumerate(mb):
        if i < mbins - 1:
            msk = (mstar >= low) & (mstar < mb[i + 1])
            tmp1 = len(mstar[msk])
            tmp2 = len(mstar[msk & nomerge])
            tmp3 = len(mstar[msk & mergers])
            tmp4 = len(mstar[msk & majors])
            tmp5 = len(mstar[msk & mergers2])
            tmp6 = len(mstar[msk & majors2])
            out.append([tmp1, tmp2, tmp3, tmp4, tmp5, tmp6])
    return mids, out


def binAndReturnFractions(x,
                          y1,
                          y2,
                          xmin=9,
                          xmax=11.5,
                          xbins=10,
                          logscale=False):
    """
    Bin the data and return different merger fractions.
    """
    out = []
    #bins
    if logscale:
        mb = N.logspace(N.log10(xmin), N.log10(xmax), xbins)
        mids = rollingAverage(mb)
    else:
        mb = N.linspace(xmin, xmax, xbins)
        mids = mb[:-1] + (mb[1] - mb[0]) / 2.
        #check the mergers
    for i, low in enumerate(mb):
        if i < xbins - 1:
            msk = (x >= low) & (x < mb[i + 1])
            tmp = float(len(y1[msk])) / len(y2[msk])
            out.append(tmp)
    return mids, out


def rollingAverage(x):
    """
    Returns the average between the cells of a list.

    :param x: a Python list of values

    :return: a NumPy array of averages
    """
    out = []
    for i, a in enumerate(x):
        if i < len(x) - 1:
            tmp = (float(a) + x[i + 1]) / 2.
            out.append(tmp)
    return N.array(out)


def movingAverage(x, n, type='simple'):
    """
    compute an n period moving average, type is 'simple' | 'exponential'
    """
    x = N.asarray(x)
    if type == 'simple':
        weights = N.ones(n)
    else:
        weights = N.exp(N.linspace(-1., 0., n))
    weights /= weights.sum()
    a = N.convolve(x, weights, mode='full')[:len(x)]
    a[:n] = a[n]
    return a