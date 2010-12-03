import scipy
import scipy.optimize
import numpy as N

def FitExponent(xcorr, ycorr, initials):
    '''
    Fits an exponential to data.
    '''
    fitfunc = lambda p, x: p[0] + p[1]*scipy.exp(-x*p[2])
    errfunc = lambda p, x, y: fitfunc(p,x) - y
    
    # fit
    p1, success = scipy.optimize.leastsq(errfunc, initials, args=(xcorr, ycorr))

    # compute the best fit function from the best fit parameters
    corrfit = fitfunc(p1, xcorr)
    return corrfit, p1

def doubleExponent(x, p, yshift):
    return yshift + p[0] + p[1]*scipy.exp(-x/p[2]) + p[3]*scipy.exp(-x/p[4])

def singleExponent(x, p, yshift):
    return yshift  + p[0] + p[1]*scipy.exp(-x*p[2])

def FitDoubleExponent(xcorr, ycorr, initials):
    '''
    Fits a double exponential to data.
    @return: corrfit
    '''
    fitfunc = lambda p, x: p[0] + p[1]*scipy.exp(-x/p[2]) + p[3]*scipy.exp(-x/p[4])
    errfunc = lambda p, x, y: fitfunc(p,x) - y
    
    # fit
    p1, success = scipy.optimize.leastsq(errfunc, initials, args=(xcorr, ycorr))

    print 'Double exponent fit:'
    print 'p[0] + p[1]*scipy.exp(-x/p[2]) + p[3]*scipy.exp(-x/p[4])'
    print p1
    if success != 1: print success
    print 

    # compute the best fit function from the best fit parameters
    corrfit = fitfunc(p1, xcorr)
    return corrfit, p1

def FindZeroDoubleExp(p, x0, yshift = 0.0):
    roots = scipy.optimize.fsolve(doubleExponent, x0, args = (p, yshift))
    return roots

def FindZeroSingleExp(p, x0, yshift = 0.0):
    roots = scipy.optimize.fsolve(singleExponent, x0, args = (p, yshift))
    return roots

def PolyFit(x, y, order = 1):
    '''
    Fits a polynomial to the data.
    @return: 
    fitted y values, error of the fit
    '''
    (ar,br) = N.polyfit(y, x, order)
    yr = N.polyval([ar,br], y)
    err = N.sqrt(sum((yr - y)**2.)/len(yr))   
    return yr, err
