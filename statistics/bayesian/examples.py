import pymc

def pymc_linear_fit_withoutliers(data1, data2, data1err=None, data2err=None,
                                 print_results=False, intercept=True, nsample=5000, burn=1000,
                                 thin=10, return_MC=False, guess=None, verbose=0):
    """
    Use pymc to fit a line to data with outliers assuming outliers
    come from a broad, uniform distribution that cover all the data
    """
    if guess is None:
        guess = (0, 0)

    xmu = pymc.distributions.Uninformative(name='x_observed', value=0)
    if data1err is None:
        xdata = pymc.distributions.Normal('x', mu=xmu, observed=True,
            value=data1, tau=1, trace=False)
    else:
        xtau = pymc.distributions.Uninformative(name='x_tau',
            value=1.0 / data1err ** 2, observed=True, trace=False)
        xdata = pymc.distributions.Normal('x', mu=xmu, observed=True,
            value=data1, tau=xtau, trace=False)

    d = {'slope': pymc.distributions.Uninformative(name='slope', value=guess[0]),
         'badvals': pymc.distributions.DiscreteUniform('bad', 0, 1, value=[False] * len(data2)),
         'bady': pymc.distributions.Uniform('bady', min(data2 - data2err), max(data2 + data2err), value=data2),
    }
    if intercept:
        d['intercept'] = pymc.distributions.Uninformative(name='intercept',
            value=guess[1])

        @pymc.deterministic(trace=False)
        def model(x=xdata, slope=d['slope'], intercept=d['intercept'],
                  badvals=d['badvals'], bady=d['bady']):
            return (x * slope + intercept) * (True - badvals) + badvals * bady

    else:
        @pymc.deterministic(trace=False)
        def model(x=xdata, slope=d['slope'], badvals=d['badvals'], bady=d['bady']):
            return x * slope * (True - badvals) + badvals * bady

    d['f'] = model

    if data2err is None:
        ydata = pymc.distributions.Normal('y', mu=model, observed=True,
            value=data2, tau=1, trace=False)
    else:
        ytau = pymc.distributions.Uninformative(name='y_tau',
            value=1.0 / data2err ** 2, observed=True, trace=False)
        ydata = pymc.distributions.Normal('y', mu=model, observed=True,
            value=data2, tau=ytau, trace=False)
    d['y'] = ydata

    MC = pymc.MCMC(d)
    MC.sample(nsample, burn=burn, thin=thin, verbose=verbose)

    MCs = MC.stats()
    m, em = MCs['slope']['mean'], MCs['slope']['standard deviation']
    if intercept:
        b, eb = MCs['intercept']['mean'], MCs['intercept']['standard deviation']

    if print_results:
        print "MCMC Best fit y = %g x" % (m),
        if intercept:
            print " + %g" % (b)
        else:
            print ""
        print "m = %g +/- %g" % (m, em)
        if intercept:
            print "b = %g +/- %g" % (b, eb)
        print "Chi^2 = %g, N = %i" % (((data2 - (data1 * m)) ** 2).sum(), data1.shape[0] - 1)

    if return_MC:
        return MC
    if intercept:
        return m, b
    else:
        return m


if __name__ == "__main__":
    import numpy as np
    import matplotlib.pyplot as plt

    data = np.array([[1, 201, 592, 61, 9, -0.84],
                     [2, 244, 401, 25, 4, 0.31],
                     [3, 47, 583, 38, 11, 0.64],
                     [4, 287, 402, 15, 7, -0.27],
                     [5, 203, 495, 21, 5, -0.33],
                     [6, 58, 173, 15, 9, 0.67],
                     [7, 210, 479, 27, 4, -0.02],
                     [8, 202, 504, 14, 4, -0.05],
                     [9, 198, 510, 30, 11, -0.84],
                     [10, 158, 416, 16, 7, -0.69],
                     [11, 165, 393, 14, 5, 0.30],
                     [12, 201, 442, 25, 5, -0.46],
                     [13, 157, 317, 52, 5, -0.03],
                     [14, 131, 311, 16, 6, 0.50],
                     [15, 166, 400, 34, 6, 0.73],
                     [16, 160, 337, 31, 5, -0.52],
                     [17, 186, 423, 42, 9, 0.90],
                     [18, 125, 334, 26, 8, 0.40],
                     [19, 218, 533, 16, 6, -0.78],
                     [20, 146, 344, 22, 5, -0.56],])
    
    xdata, ydata = data[:, 1], data[:, 2]
    xerr, yerr = data[:, 4], data[:, 3]

    #MCMC
    MC = pymc_linear_fit_withoutliers(xdata, ydata, data1err=xerr, data2err=yerr, return_MC=True)
    MC.sample(500000, burn=10000, verbose=3)

    mmean = MC.stats()['slope']['mean']
    bmean = MC.stats()['intercept']['mean']

    #plot the results
    plt.plot(np.linspace(0,300), np.linspace(0,300)*mmean+bmean,color='k',linewidth=2)

    for m,b in zip(MC.trace('slope')[-100:],MC.trace('intercept')[-100:]):
        plt.plot(np.linspace(0,300), np.linspace(0,300)*m+b, color='k', alpha=0.05)

    plt.scatter(xdata, ydata, color='b', label='data')

    plt.scatter(xdata[MC.badvals.value.astype('bool')],
               ydata[MC.badvals.value.astype('bool')], color='r', label='likely outliers')

    plt.legend(shadow=True, fancybox=True, numpoints=1, loc='upperleft')
    plt.savefig('test.pdf')
