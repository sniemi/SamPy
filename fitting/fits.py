'''
Various functions can be fit to give data.

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:requires: NumPy
:requires: SciPy

:version: 0.1
'''
import scipy
import scipy.optimize
import numpy as np

def Gaussian(ydata, xdata=None, initials=None):
    '''
    Fits a single Gaussian to a given data.
    Uses scipy.optimize.leastsq for fitting.

    :param: ydata, to which a Gaussian will be fitted to.
    :param: xdata, if not given uses np.arange
    :param: initials, initial guess for Gaussian parameters
            in order [amplitude, mean, sigma]

    :return: coefficients, best fit params, success
    :rtype: dictionary
    '''
    # define a gaussian fitting function where
    # p[0] = amplitude
    # p[1] = mean
    # p[2] = sigma
    fitfunc = lambda p, x: p[0] * scipy.exp(-(x - p[1])**2 / (2.0 * p[2]**2))
    errfunc = lambda p, x, y: fitfunc(p, x) - y

    if initials is None:
        initials = scipy.c_[np.max(ydata), np.argmax(ydata), 5][0]

    if xdata is None:
        xdata = np.arange(len(ydata))

    # fit a gaussian to the correlation function
    p1, success = scipy.optimize.leastsq(errfunc, initials[:],\
                                         args=(xdata, ydata))

    # compute the best fit function from the best fit parameters
    corrfit = fitfunc(p1, xdata)

    out={}
    out['fit'] = corrfit
    out['parameters'] = p1
    out['amplitude'] = p1[0]
    out['mean'] = p1[1]
    out['sigma'] = p1[2]
    out['fwhm'] = 2 * np.sqrt(2*np.log(2)) * out['sigma']
    out['success'] = success

    return out


def linearregression(x, y,
                     confidence_level=95,
                     show_plots=False,
                     report=False):
    '''
    A function to calculate simple linear regression
    inputs: x,y-data pairs and a confidence level (in percent)
    outputs: slope = b1, intercept = b0 its confidence intervals
    and R (+squared)
    '''
    #Basic statistics
    x_average = np.mean(x)
    x_stdev = np.std(x)
    y_average = np.mean(y)
    y_stdev = np.std(y)
    n = len(x)

    if n == 2:
        #print 'Only 2 degrees of freedom, cannot calculate errors...'
        return 0, 0, 0

    # calculate linear regression coefficients
    b1 = np.sum((x - x_average) * (y - y_average)) / np.sum((x - x_average) ** 2)
    b0 = y_average - b1 * x_average

    # calculate residuals (observed - predicted)
    TotSS = np.sum((y - y_average) ** 2)   # Total Sum of Squares
    y_hat = b1 * x + b0               # fitted values
    ResSS = np.sum((y - y_hat) ** 2)       # Residual Sum of Squares

    # calculate standard deviations of fit params
    b1_stdev = np.sqrt((ResSS / (n - 2)) / np.sum((x - x_average) ** 2))
    b0_stdev = b1_stdev * np.sqrt(np.sum(x ** 2) / n)

    # compute the mean square error (variance) and standard error (root of var), R2 and R
    mserr = ResSS / (n - 2)
    sterr = np.sqrt(mserr)
    R2 = 1 - ResSS / TotSS
    R = np.sqrt(R2)

    ## calculate confidence interval
    alpha = 1. - (confidence_level * 1. / 100.)
    # degrees of freedom (2 lost by estimates of slope and intercept)
    DF = n - 2
    # critical value (from t table)
    cv = 2.01
    # Margin of error = Critical value x Standard error of the statistic 
    moe_b1 = cv * b1_stdev
    moe_b0 = cv * b0_stdev
    lower_b1 = b1 - moe_b1
    upper_b1 = b1 + moe_b1
    lower_b0 = b0 - moe_b0
    upper_b0 = b0 + moe_b0

    if report:
        print 'Report of linear regression:'
        print np.polyfit(x, y, 1)
        print 'Slope = %.6f +/- %.4f, Intercept = %.4f +/- %.4f' % (b1, moe_b1, b0, moe_b0)
        print '%g percent confidence interval for slope: %.4f to %.4f' % (confidence_level, lower_b1, upper_b1)
        print '%g percent confidence interval for intercept: %.4f to %.4f' % (confidence_level, lower_b0, upper_b0)

    # compute confidence lines for plot
    lower = upper_b1 * x + lower_b0
    upper = lower_b1 * x + upper_b0

    if show_plots:
        P.figure(1000)
        P.title('My Linear Regression')
        P.xlabel('x')
        P.ylabel('y')
        P.grid()
        P.plot(x, y, 'bo', label='data')
        P.plot(x, y_hat, 'r.-', label='linear fit')
        P.plot(x, lower, 'c-')
        P.plot(x, upper, 'c-')
        P.legend(loc='best', numpoints=3)
        # are the residuals normally distributed?
        P.figure(1001)
        P.title('Residuals of fit')
        P.xlabel('x')
        P.ylabel('Residuals')
        P.grid()
        P.plot(x, y - y_hat, 'mo')
        P.show()
    return b1, moe_b1, b0, lower_b1, upper_b1, lower_b0, upper_b0, R2, R


def FitExponent(xcorr, ycorr, initials):
    '''
    Fits an exponential to data.
    '''
    fitfunc = lambda p, x: p[0] + p[1] * scipy.exp(-x * p[2])
    errfunc = lambda p, x, y: fitfunc(p, x) - y

    # fit
    p1, success = scipy.optimize.leastsq(errfunc, initials, args=(xcorr, ycorr))

    # compute the best fit function from the best fit parameters
    corrfit = fitfunc(p1, xcorr)
    return corrfit, p1


def doubleExponent(x, p, yshift):
    return yshift + p[0] + p[1] * scipy.exp(-x / p[2]) + p[3] * scipy.exp(-x / p[4])


def singleExponent(x, p, yshift):
    return yshift + p[0] + p[1] * scipy.exp(-x * p[2])


def FitDoubleExponent(xcorr, ycorr, initials):
    '''
    Fits a double exponential to data.

    :return: best fit, fit parameters
    '''
    fitfunc = lambda p, x: p[0] + p[1] * scipy.exp(-x / p[2]) + p[3] * scipy.exp(-x / p[4])
    errfunc = lambda p, x, y: fitfunc(p, x) - y

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


def FindZeroDoubleExp(p, x0, yshift=0.0):
    roots = scipy.optimize.fsolve(doubleExponent, x0, args=(p, yshift))
    return roots


def FindZeroSingleExp(p, x0, yshift=0.0):
    roots = scipy.optimize.fsolve(singleExponent, x0, args=(p, yshift))
    return roots


def PolyFit(x, y, order=1):
    '''
    Fits a polynomial to the data.

    :return: fitted y values, error of the fit
    '''
    (ar, br) = np.polyfit(y, x, order)
    yr = np.polyval([ar, br], y)
    err = np.sqrt(sum((yr - y) ** 2.) / len(yr))
    return yr, err
