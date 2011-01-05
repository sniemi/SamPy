'''
Some functions to calculate differential functions. These
can be used to calculate luminosity functions, stellar and
dark matter halo functions etc.

@requires: NumPy

@version: 0.11

@author: Sami Niemi
@contact: niemi@stsci.edu
'''
import numpy as N

def diff_function_log_binning(data, column = 0, log = False,
                              wgth = None, mmax = 15.5, mmin = 9.0,
                              nbins = 35, h = 0.7, volume = 250, nvols = 1,
                              physical_units = False, verbose = False):
    '''
    Calculates a differential function from data.
    @todo: rewrite this, it's not very well done...
    '''
    #number of galaxies
    one = False
    if len(N.shape(data)) == 1:
        ngal = len(data)
        one = True
    else:
        ngal = len(data[:,column])
    
    #if data are in physical units or not, use h
    if not physical_units:
        h = 1.0
    
    #if wgth is None then make weights based on the volume etc.
    if wgth == None:
        weight = N.zeros(ngal) + (1./(nvols*(float(volume)/h)**3))
    else:
        weight = wgth

    #if log have been taken from the data or not
    if not log:
        if len(N.shape(data)) == 1:
            d = N.log10(data)
        else:
            d = N.log10(data[:,column])
        mmin = N.log10(mmin)
        mmax = N.log10(mmax)
    else:
        d = data[:,column]   

    #bins 
    dm = (mmax - mmin) / float(nbins)
    mbin = (N.arange(nbins)+0.5)*dm + mmin
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
    ibin = N.floor((d - mmin)/dm)

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


def mass_function(data, column = 0, log = False,
                  wght = None, mmin = 9.0, mmax = 15.0, 
                  nbins = 35, h = 0.7, volume = 250,
                  nvols = 1, verbose = False):
    '''
    Calculates a mass function from data.
    Returns differential mass function and bins:
    dN / dlnM
    @TODO: add calculating the cumulative mass function.
    '''
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
            dat = data *h
    del data
    #number of galaxies
    ngal = len(dat)
    #set weights if None given
    if wght == None:
        wght = N.zeros(ngal) + (1./(nvols*(float(volume)/h)**3))

    #bins, one could also use N.linspace() or N.logscape()
    dm = (mmax - mmin) / float(nbins)
    #mid points
    mbin = (N.arange(nbins)+0.5)*dm + mmin

    #verbose output
    if verbose:
        print 'Number of galaxies = %i' % ngal
        print 'dlnM =', dm
        print 'h =', h

    mf = N.zeros(nbins)
    #find out in which bins each data point belongs to
    ibin = N.floor((dat - mmin)/dm)
    #make a mask of suitable bins
    mask = (ibin >= 0) & (ibin < nbins)
    #calculate the sum in each bin
    for i in range(nbins):
        mf[i] = N.sum(wght[ibin[mask] == i])
    mf = N.array(mf)
    
    if not log:
        mbin = N.e**mbin
        if verbose:
            print '\nResults:', mbin, mf/dm
        return mbin, mf/dm
    else:
        if verbose:
            print '\nResults:', mbin, mf/dm
        return mbin, mf/dm