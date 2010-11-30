
def AutoCorr(X, lag):
    # Note that we subtract the mean over the entire time series,
    # rather than subtracting the mean from the first and last N-lag
    # points separately. This is discussed further in Jenkins & Watts,
    # Spectral Analysis and its Applications, 1968. In short, the use
    # of separate means for each portion is not recommended, as it is
    # not a satisfactory estimate when a several autocorrelations at
    # different lags are required.
    
    import numpy as N
    import math
    
    #removes mean
    data = N.array(X) - N.mean(X)

    #Compute Autocovariance.
    M = N.abs(lag)
    auto = []
    for index in range(len(lag)):
        auto.append(N.sum(data[0: len(data) - M[index]] * data[M[index]:]))
        
    #divide by variance for covariance?
    #auto = auto / N.var(data)
    auto = auto / N.sum(data**2)
    return auto

def GaussianFit(xcorr, ycorr, initials):
    import scipy
    import scipy.optimize

    # define a gaussian fitting function where
    # p[0] = amplitude
    # p[1] = mean
    # p[2] = sigma
    fitfunc = lambda p, x: p[0]*scipy.exp(-(x-p[1])**2/(2.0*p[2]**2))
    errfunc = lambda p, x, y: fitfunc(p,x)-y
    
    # fit a gaussian to the correlation function
    p1, success = scipy.optimize.leastsq(errfunc, initials, \
                                         args=(xcorr,ycorr))

    # compute the best fit function from the best fit parameters
    corrfit = fitfunc(p1, xcorr)

    return corrfit


if __name__ == '__main__':
    import glob as G
    import matplotlib
    matplotlib.use('PDF')
    import pylab as P
    import scipy, math
    import numpy as N
    
    #CHANGE THESE
    maxlag = 2001 #301
    lag = N.arange(maxlag) - maxlag/2
    
    #limits the spectrum
    sg130a = 11200 #4500  #11200  
    eg130a = 15500 #10000 #15500
    sg130b = 2000 #12400 #2000
    eg130b = 7000 #15200 #7000
    
    sg160a = 7000 #1600 # 7000
    eg160a = 15000 #6700 # 15000
    sg160b = 3000  #
    sg160e = 10000 #
    
    path = '/smov/cos/Analysis/11484/'
    visits = ['VIS93_G130M_SEGB/', 'VIS94_G130M_SEGA/', 'VIS95_G160M/']
    id = '*pix.dat'
    
    explista = '/smov/cos/Analysis/11484/VIS94_G130M_SEGA/exposures_list.txt'
    explistb = '/smov/cos/Analysis/11484/VIS93_G130M_SEGB/exposures_list.txt'
    
    exposa = open(explista).readlines()
    exposb = open(explistb).readlines()
    
    G130MB = G.glob(path+visits[0]+id)
    G130MA = G.glob(path+visits[1]+id)
    G160M = G.glob(path+visits[2]+id)
    
    G130Mdata = []
    for a,b in zip(G130MA,G130MB):
        G130Mdata.append([N.loadtxt(a, comments=';', usecols=(1,)), N.loadtxt(b, comments=';', usecols=(1,))])

    G160Mdata = []
    for file in G160M:
        G160Mdata.append(N.loadtxt(file, comments=';', usecols=(1,)))
    
    resa = []
    resb = []
    for value, counts in enumerate(G130Mdata):
        
        corra = AutoCorr(counts[0], lag)
        corrb = AutoCorr(counts[1], lag)
                
        #autocorr1 = P.acorr(counts[0][sg130a:eg130a], maxlags=maxlag, lw=2, ls='-', marker='None', label='G130M Seg A Autocorr')
        #autocorr2 = P.acorr(counts[1][sg130b:eg130b], maxlags=maxlag, lw=2, ls='-.', marker='None', label='G130M Seg B Autocorr')
        #G130Mauto.append([autocorr1, autocorr2])
        #lag = autocorr2[0]
        #corr = autocorr2[1]
        #lets edit a bit

        widtha = 0
        for x, y in zip(lag, corra):
            if y > 0.5:
                widtha = x
                break

        widthb = 0
        for x, y in zip(lag, corrb):
            if y > 0.5:
                widthb = x
                break

        div = 5
        corrafit = corra[(len(lag)/2-len(lag)/div):(len(lag)/2+len(lag)/div)]
        corrbfit = corrb[(len(lag)/2-len(lag)/div):(len(lag)/2+len(lag)/div)]
        lagfit = lag[(len(lag)/2-len(lag)/div):(len(lag)/2+len(lag)/div)]
        
        #gaussian fitting
        guessa = scipy.c_[max(corrafit), scipy.where(corrafit==max(corrafit))[0], 5]
        fita = GaussianFit(lagfit, corrafit, guessa[0])
        guessb = scipy.c_[max(corrbfit), scipy.where(corrbfit==max(corrbfit))[0], 5]
        fitb = GaussianFit(lagfit, corrbfit, guessb[0])

        P.plot(lag, corra, lw=2, ls='-', label='G130M Seg A Autocorr')
        P.plot(lag, corrb, lw=2, ls='-.', label='G130M Seg B Autocorr')

        P.plot(lagfit, fita, lw=2.5, ls=':', label='Gaussian Fit to Seg A')
        P.plot(lagfit, fitb, lw=2.5, ls='-.',label='Gaussian Fit to Seg B')
        P.xlabel('Lag')
        P.ylim(0.0, 1.01)
        P.ylabel('Normalised Autocorrelation')
        P.legend(shadow=True, loc=0)

        filea = G130MA[value][G130MA[value].find('labo'):G130MA[value].find('_corr')]
        fileb = G130MB[value][G130MB[value].find('labo'):G130MB[value].find('_corr')]
        P.savefig(filea + fileb + '_GaussianFit.pdf')
        P.close()
        
        focoffa = 0
        roota = ''
        focoffb = 0
        rootb = ''
        for line in exposa:
            if line.split()[0] in filea:
                focoffa = line.split()[1]
                roota = line.split()[0]
                break
        for line in exposb:
            if line.split()[0] in fileb:
                focoffb = line.split()[1]
                rootb = line.split()[0]
                break
 
        resb.append([float(focoffb), math.fabs(widthb*2.)])
        resa.append([float(focoffa), math.fabs(widtha*2.)])
 
        print 'Width of %s (A seg) is %f taken with focus offset %s' % (roota, math.fabs(widtha*2.), focoffa)
        print 'Width of %s (B seg) is %f taken with focus offset %s' % (rootb, math.fabs(widthb*2.), focoffb)

        
    #P.scatter([x[0] for x in resa], [x[1] for x in resa], label='G130M Seg A')
    #P.scatter([x[0] for x in resb], [x[1] for x in resb], label='G130M Seg B')
    resa.sort()
    resb.sort()
    
    P.plot([x[0] for x in resa], [x[1]/2. for x in resa], label='G130M Seg A')
    P.plot([x[0] for x in resb], [x[1]/2. for x in resb], label='G130M Seg B')    
    P.title('FOCUS G130M')
    P.ylabel('Width of the autocorrelation function')
    P.xlabel('Focus Offset')
    
    P.savefig('FocusCurveG130M.pdf')