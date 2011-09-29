"""
Functions to calculate differential functions.

These functions can be used to calculate for example
luminosity functions, stellar and dark matter halo
functions etc.

:requires: NumPy

:version: 0.17

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu
"""
import numpy as N

def diffFunctionLogBinning(data, column=0, log=False,
                           wgth=None, mmax=15.5, mmin=9.0,
                           nbins=35, h=0.7, volume=250, nvols=1,
                           verbose=False):
    """
    Calculates a differential function from data.
    Uses NumPy to calculate a histogram and then divides.
    each bin value with the length of the bin.
    The log binning refers to 10 based log, i.e. "math"`\\log_{10}(data)`
    """
    #get the number of items in data
    if len(N.shape(data)) == 1:
        ngal = len(data)
    else:
        ngal = len(data[:, column])

    #if wgth is None then make weights based on 
    #the volume and the number of volumes
    if wgth == None:
        weight = N.zeros(ngal) + (1. / (nvols * (float(volume) / h) ** 3))
    else:
        weight = wgth

    #if log have been taken from the data or not
    if not log:
        if len(N.shape(data)) == 1:
            d = N.log10(data)
        else:
            d = N.log10(data[:, column])
        mmin = N.log10(mmin)
        mmax = N.log10(mmax)
    else:
        d = data[:, column]

        #calculate mass functions
    mf, edges = N.histogram(d,
                            nbins,
                            range=(mmin, mmax),
                            weights=weight)
    mbin = (edges[1:] + edges[:-1]) / 2.
    dm = edges[1] - edges[0]

    if verbose:
        print '\nNumber of galaxies = %i' % ngal
        print 'min = %f, max = %f' % (mmin, mmax)
        print 'df =', dm
        print 'h =', h
        print 'Results:\n', mbin
        print mf / dm
    return mbin, mf / dm


def diff_function_log_binning(data, column=0, log=False,
                              wgth=None, mmax=15.5, mmin=9.0,
                              nbins=35, h=0.7, volume=250, nvols=1,
                              verbose=False):
    """
    Calculates a differential function from data.

    :warning: One should not use this, unless the number of
              systems for each bin is used. One should use diffFunctionLogBinning
              instead, which is probably faster as it uses NumPy.histogram
              rather than my own algorithm.
    """
    #get the number of items in data
    if len(N.shape(data)) == 1:
        ngal = len(data)
    else:
        ngal = len(data[:, column])


    #if wgth is None then make weights based on 
    #the volume and the number of volumes
    if wgth == None:
        weight = N.zeros(ngal) + (1. / (nvols * (float(volume) / h) ** 3))
    else:
        weight = wgth

    #if log have been taken from the data or not
    if not log:
        if len(N.shape(data)) == 1:
            d = N.log10(data)
        else:
            d = N.log10(data[:, column])
        mmin = N.log10(mmin)
        mmax = N.log10(mmax)
    else:
        if len(N.shape(data)) == 1:
            d = data
        else:
            d = data[:, column]

    #bins
    dm = (mmax - mmin) / float(nbins)
    mbin = (N.arange(nbins) + 0.5) * dm + mmin
    #one could also use N.linspace(mmin, mmax, nbins)
    #note however that one should then use + dm / 2. 

    if verbose:
        print '\nNumber of galaxies = %i' % ngal
        print 'min = %f, max = %f' % (mmin, mmax)
        print 'df =', dm
        print 'h =', h

    #differential functions function, dummy values are -99
    mf = N.zeros(nbins) - 99.9
    nu = N.zeros(nbins) - 99

    #find out bins
    ibin = N.floor((d - mmin) / dm)

    #make a mask of suitable bins
    mask = (ibin >= 0) & (ibin < nbins)

    #calculate the sum in each bin
    for i in range(nbins):
        mf[i] = N.sum(weight[ibin[mask] == i])
        nu[i] = len(ibin[ibin[mask] == i])

    if verbose:
        print 'Results:\n', mbin
        print mf / dm
        print nu
    return mbin, mf / dm, nu


def mass_function(data, column=0, log=False,
                  wght=None, mmin=9.0, mmax=15.0,
                  nbins=35, h=0.7, volume=250,
                  nvols=1, verbose=False):
    """
    Calculates a mass function from data.
    Returns differential mass function and bins:
    dN / dlnM
    :TODO: add calculating the cumulative mass function.
    """
    #if log have been taken from the data or not
    if not log:
        if len(data.shape) > 1:
            dat = N.log(data[:, column] * h)
        else:
            dat = N.log(data * h)
    else:
        if len(data.shape) > 1:
            dat = data[:, column] * h
        else:
            dat = data * h
    del data
    #number of galaxies
    ngal = len(dat)
    #set weights if None given
    if wght == None:
        wght = N.zeros(ngal) + (1. / (nvols * (float(volume) / h) ** 3))

    #bins, one could also use N.linspace() or N.logscape()
    dm = (mmax - mmin) / float(nbins)
    #mid points
    mbin = (N.arange(nbins) + 0.5) * dm + mmin

    #verbose output
    if verbose:
        print 'Number of galaxies = %i' % ngal
        print 'dlnM =', dm
        print 'h =', h

    mf = N.zeros(nbins)
    #find out in which bins each data point belongs to
    ibin = N.floor((dat - mmin) / dm)
    #make a mask of suitable bins
    mask = (ibin >= 0) & (ibin < nbins)
    #calculate the sum in each bin
    for i in range(nbins):
        mf[i] = N.sum(wght[ibin[mask] == i])
    mf = N.array(mf)

    if not log:
        mbin = N.e ** mbin
        if verbose:
            print '\nResults:', mbin, mf / dm
        return mbin, mf / dm
    else:
        if verbose:
            print '\nResults:', mbin, mf / dm
        return mbin, mf / dm


def stellarMassFunction(data,
                        wght=None, mmin=None, mmax=None,
                        nbins=40, h=0.7, volume=50,
                        nvols=8, verbose=False,
                        early_type_galaxies=0.4,
                        central_galaxy_id=1):
    """
    Calculates a stellar mass function from data. Calculates
    stellar mass functions for all galaxies, early- and late-types
    and central galaxies separately.

    :param data: should in the following format:
                 data['stellar_mass'] = []
                 data['bulge_mass'] = []
                 data['galaxy_id'] = []
    :type data: dictionary

    :return: output
    :rtype: dictionary
    """
    #get number of galaxies
    ngal = len(data['stellar_mass'])

    #set weights if None given
    if wght == None:
        wght = N.zeros(ngal) + (1. / (nvols * (float(volume) / h) ** 3))

    #set minimum and maximum mass if None given
    if mmin == None:
        mmin = N.min(data['stellar_mass'])
    if mmax == None:
        mmax = N.max(data['stellar_mass'])

    #calculate the stepsize
    dm = (mmax - mmin) / float(nbins)
    #mid points
    mbin = (N.arange(nbins) + 0.5) * dm + mmin

    #verbose output
    if verbose:
        print 'Number of galaxies = %i' % ngal
        print 'The least massive galaxy stellar mass', mmin
        print 'The most massive galaxy stellar mass ', mmax
        print 'dM =', dm
        print 'h =', h

    #mass functions
    mf_star = N.zeros(nbins)
    mf_star_central = N.zeros(nbins)
    mf_early = N.zeros(nbins)
    mf_late = N.zeros(nbins)
    mf_bulge = N.zeros(nbins)

    #adapted from IDL, could be done without looping
    btt = 10.0 ** (data['bulge_mass'] - data['stellar_mass'])
    for i in range(ngal):
        ibin = int(N.floor((data['stellar_mass'][i] - mmin) / dm))
        if ibin >= 0 and ibin < nbins:
            mf_star[ibin] += wght[i]
            #stellar mass, by type
            if btt[i] >= early_type_galaxies:
                mf_early[ibin] += wght[i]
            else:
                mf_late[ibin] += wght[i]
                #stellar mass, centrals galaxies only
            if data['galaxy_id'][i] == central_galaxy_id:
                mf_star_central[ibin] += wght[i]

    #Get the log of the mass fuction and divide with dex
    mf_star = N.log10(mf_star / dm)
    mf_early = N.log10(mf_early / dm)
    mf_late = N.log10(mf_late / dm)
    mf_star_central = N.log10(mf_star_central / dm)

    out = {}
    out['mf_stellar_mass'] = mf_star
    out['mf_early_types'] = mf_early
    out['mf_late_types'] = mf_late
    out['mf_central_galaxies'] = mf_star_central
    out['mass_bins'] = mbin
    out['dm'] = dm
    return out
    
    