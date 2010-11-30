import matplotlib
matplotlib.rc('text', usetex = False)
matplotlib.rc('xtick', labelsize=12) 
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rc('lines', markeredgewidth=2.0)
matplotlib.rcParams['lines.linewidth'] = 1.8
matplotlib.rcParams['legend.fontsize'] = 9
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
#matplotlib.use('PDF')
matplotlib.use('Agg')

import numpy as N
import pylab as P
import re, os
import db.sqlite

def diff_function(data, column = 0, log = False,
                  wgth = None, mmax = 15.5, mmin = 9.0,
                  nbins = 35, h = 0.7, volume = 250, nvols = 1,
                  physical_units = False, verbose = False):
    '''
    Calculates a differential function from data.
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
        d = N.log10(data[:,column])
        mmin = N.log10(mmin)
        mmax = N.log10(mmax)
    else:
        d = data[:,column]   

    #bins 
    dm = (mmax - mmin) / float(nbins)
    mbin = (N.arange(nbins)+0.5)*dm + mmin

    if verbose:
        print '\nNumber of galaxies = %i' % ngal
        print 'min = %f, max = %f' % (mmin, mmax)
        print 'df =', dm
        print 'h =', h

    #mass function
    mf = N.zeros(nbins)
    nu = N.zeros(nbins)
    
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
 
def plot_number_counts(path, database, band, redshifts,
                       out_folder, obs_data,
                       area = 2.25,
                       ymin = 10**3, ymax = 2*10**6,
                       xmin = 0.5, xmax = 100,
                       nbins = 15, sigma = 3.0):
    '''
    160 (arcminutes squared) = 0.0444444444 square degrees
    Simulation was 10 times the GOODS realization, so
    area = 0.44444444, thus, the weighting is 1/0.44444444
    i.e. 2.25.
    @param sigma: sigma level of the errors to be plotted
    @param nbins: number of bins (for simulated data)
    @param area: actually 1 / area, used to weight galaxies
    '''
    #fudge factor to handle errors that are way large
    fudge = ymin

    #The 10-5 square degrees number of rows in the plot
    columns = 2
    rows = 3 #len(band) / columns

    try:
        wave = re.search('\d\d\d', band).group()
    except:
        #pacs 70 has only two digits
        wave = re.search('\d\d', band).group()

    #get data and convert to mJy
    query = '''select FIR.%s from FIR
where FIR.%s < 10000 and FIR.%s > 1e-15''' % (band, band, band)
    fluxes = db.sqlite.get_data_sqlite(path, database, query)*10**3

    #weight each galaxy
    wghts = N.zeros(len(fluxes)) + area

    #make the figure
    fig = P.figure(figsize = (10, 10))
    P.subplots_adjust(wspace = 0.0, hspace = 0.0)
    ax = P.subplot(rows, columns, 1)

    #calculate the differential number density
    #with log binning
    b, n, nu =  diff_function(fluxes,
                              wgth = wghts, 
                              mmax = xmax,
                              mmin = xmin,
                              nbins = nbins)
    #get the knots
    x = 10**b
    #chain rule swap to dN/dS
    #d/dS[ log_10(S)] = d/dS[ ln(S) / ln(10)]
    # = 1 / (S*ln(10)) 
    swap = 1. / (N.log(10)*x)
    #Euclidean-normalization S**2.5
    y = n*swap*(x**2.5)
    
    #plot the knots
    z0 = ax.plot(x, y, 'ko')

    #poisson error
    mask = nu > 0
    err = swap[mask] * (x[mask]**2.5) * area * N.sqrt(nu[mask]) * sigma
    up = y[mask] + err
    lw = y[mask] - err
    lw[lw < ymin] = ymin
    s0 = ax.fill_between(x[mask], up, lw, alpha = 0.2)

    #add annotation
    ax.annotate('Total', (0.5, 0.9), xycoords='axes fraction',
               ha = 'center')

    #plot observational contrains
    if 'pacs100' in band:
        d = N.loadtxt(obs_data+'BertaResults', comments = '#', usecols = (0,1,2))
        b0 = ax.errorbar(d[:,0], d[:,1], yerr = d[:,1]*d[:,2], ls = 'None',
                         marker = '*', mec = 'r', c = 'red')
        a = N.loadtxt(obs_data+'Altieri100', comments = '#', usecols = (0,1,2,3))
        x = a[:,0]
        y = a[:,1]
        high = a[:,2] - y
        low = N.abs(a[:,3] - y)
        #yerr = [how much to take away from the y, how much to add to y]
        a0 = ax.errorbar(x, y, yerr = [low, high], c='green', marker = 'D',
                         ls = 'None', mec = 'green', lw = 1.3, ms = 3, mew = 1.3)
    if 'pacs160' in band:
        d = N.loadtxt(obs_data+'BertaResults', comments = '#', usecols = (0,3,4))
        b0 = ax.errorbar(d[:,0], d[:,1], yerr = d[:,1]*d[:,2], ls = 'None',
                         marker = '*', mec = 'r', c = 'red')
        a = N.loadtxt(obs_data+'Altieri160', comments = '#', usecols = (0,1,2,3))
        x = a[:,0]
        y = a[:,1]
        high = a[:,2] - y
        low = N.abs(a[:,3] - y)
        a0 = ax.errorbar(x, y, yerr = [low, high], c='green', marker = 'D',
                         ls = 'None', mec = 'green', lw = 1.3, ms = 3, mew = 1.3)
    if 'spire250' in band:
        #Glenn et al results
        d = N.loadtxt(obs_data+'GlennResults250', comments = '#', usecols = (0,1,2,3))
        x = d[:,0]
        y = 10**d[:,1] * x**2.5 * 10**-3
        yp = 10**(d[:,2] + d[:,1]) * x**2.5 * 10**-3
        yl = 10**(d[:,1] - d[:,3]) * x**2.5 * 10**-3
        g0 = ax.errorbar(x, y, yerr = [y-yl, yp-y], ls = 'None',
                         marker = '*', mec = 'r', c='red')    
        #Clements et al results
        g = N.loadtxt(obs_data+'Clements250', comments = '#', usecols = (0, 5, 6))
        x = g[:,0]
        y = g[:,1]*(10**3)**1.5 / (180/N.pi)**2
        err = g[:,2]*(10**3)**1.5 / (180/N.pi)**2
        c0 = ax.errorbar(x, y, yerr = [err, err], ls = 'None',
                         marker = 'D', mec = 'm', c='magenta',
                         lw = 0.9, ms = 3, mew = 0.9)    
    if 'spire350' in band:
        d = N.loadtxt(obs_data+'GlennResults350', comments = '#', usecols = (0,1,2,3))
        x = d[:,0]
        y = 10**d[:,1] * x**2.5 * 10**-3
        yp = 10**(d[:,2] + d[:,1]) * x**2.5 * 10**-3
        yl = 10**(d[:,1] - d[:,3]) * x**2.5 * 10**-3
        g0 = ax.errorbar(x, y, yerr = [y-yl, yp-y], ls = 'None',
                         marker = '*', mec = 'r', c='red')
        #Clements et al results
        g = N.loadtxt(obs_data+'Clements350', comments = '#', usecols = (0, 5, 6))
        x = g[:,0]
        y = g[:,1]*(10**3)**1.5 / (180/N.pi)**2
        err = g[:,2]*(10**3)**1.5 / (180/N.pi)**2
        c0 = ax.errorbar(x, y, yerr = [err, err], ls = 'None',
                         marker = 'D', mec = 'm', c='magenta',
                         lw = 0.9, ms = 3, mew = 0.9)    
    if 'spire500' in band:
        d = N.loadtxt(obs_data+'GlennResults500', comments = '#', usecols = (0,1,2,3))
        x = d[:,0]
        y = 10**d[:,1] * x**2.5 * 10**-3
        yp = 10**(d[:,2] + d[:,1]) * x**2.5 * 10**-3
        yl = 10**(d[:,1] - d[:,3]) * x**2.5 * 10**-3
        g0 = ax.errorbar(x, y, yerr = [y-yl, yp-y], ls = 'None',
                         marker = '*', mec = 'r', c='red')
        #Clements et al results
        g = N.loadtxt(obs_data+'Clements500', comments = '#', usecols = (0, 5, 6))
        x = g[:,0]
        y = g[:,1]*(10**3)**1.5 / (180/N.pi)**2
        err = g[:,2]*(10**3)**1.5 / (180/N.pi)**2
        c0 =  ax.errorbar(x, y, yerr = [err, err], ls = 'None',
                          marker = 'D', mec = 'm', c='magenta',
                          lw = 0.9, ms = 3, mew = 0.9)    

    #set scale
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xticklabels([])

    #legend
    if 'pacs100' in band or 'pacs160' in band:
        #NOTE: hardcoded sigma limits because legend does not support % !!!
        p = P.Rectangle((0, 0), 1, 1, fc='blue', alpha = 0.2)
        sline = '%i$\sigma$ errors' % sigma
        P.legend((z0, p, b0[0], a0), 
                 ('Our Model', sline, 'Berta et al. 2010', 'Altieri et al. 2010'), 
                  'lower left')
    if 'spire' in band:
        p = P.Rectangle((0, 0), 1, 1, fc='blue', alpha = 0.2)
        sline = '%i$\sigma$ errors' % sigma
        P.legend((z0, p, g0[0], c0), 
                 ('Our Model', sline, 'Glenn et al. 2010', 'Clements et al. 2010'), 
                  'lower left')

    #redshift limited plots
    for i, red in enumerate(redshifts):
        #get data and convert to mJy
        query = '''select FIR.%s from FIR 
where %s and FIR.%s < 10000 and FIR.%s > 1e-15''' % (band, red, band, band)
        fluxes = db.sqlite.get_data_sqlite(path, database, query)*10**3

        #modify redshift string
        tmp = red.split()
        rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])

        #weights
        wghts = N.zeros(len(fluxes)) + area

        #make a subplot
        axs = P.subplot(rows, columns, i+2)

        #make a histogram
        b, n, nu =  diff_function(fluxes,
                                  wgth = wghts, 
                                  mmax = xmax,
                                  mmin = xmin,
                                  nbins = nbins)
        #knots in mjy, no log
        x = 10**b
        #chain rule swap
        #d/dS[ log_10(S)] = d/dS[ ln(S) / ln(10)]
        # = 1 / (S*ln(10)) 
        swap = 1. / (N.log(10)*x)
        #Euclidean normalization, S**2.5
        y = n*swap*(x**2.5)
        
        #plot the knots
        axs.plot(x, y, 'ko')
        
        #poisson error
        mask = nu > 0
        err = swap[mask] * (x[mask]**2.5) * area * N.sqrt(nu[mask]) * sigma
        up = y[mask] + err
        lw = y[mask] - err
        lw[lw < ymin] = ymin
        axs.fill_between(x[mask], up, lw, alpha = 0.2)

        #add annotation
        axs.annotate(rtitle, (0.5, 0.9), xycoords='axes fraction',
                     ha = 'center')

        #add observational constrains
        if 'pacs100' in band:
            fl = obs_data+'data_100um_4_Sami_Niemi_20101126.txt'
            if i == 0:
                data = N.loadtxt(fl, usecols=(0, 1, 2, 3), comments = '#')
                x = 10**data[:,0]
                y = 10**data[:,1]
                up = y*data[:,3]
                msk = data[:,2] < -10.0
                data[:,2][msk] = 0.999
                lw = y*data[:,2]
                axs.errorbar(x, y, yerr=[lw, up], ls = 'None',
                             marker = '*', mec = 'r', c='red')
            if i == 1:
                data = N.loadtxt(fl, usecols=(0, 4, 5, 6), comments = '#')
                x = 10**data[:,0]
                y = 10**data[:,1]
                up = y*data[:,3]
                msk = data[:,2] < -10.0
                data[:,2][msk] = 0.999
                lw = y*data[:,2]
                axs.errorbar(x, y, yerr=[lw, up], ls = 'None',
                             marker = '*', mec = 'r', c='red')
            if i == 2:
                data = N.loadtxt(fl, usecols=(0, 7, 8, 9), comments = '#')
                x = 10**data[:,0]
                y = 10**data[:,1]
                up = y*data[:,3]
                msk = data[:,2] < -10.0
                data[:,2][msk] = 0.999
                lw = y*data[:,2]
                axs.errorbar(x, y, yerr=[lw, up], ls = 'None',
                             marker = '*', mec = 'r', c='red')
            if i == 3:
                data = N.loadtxt(fl, usecols=(0, 10, 11, 12), comments = '#')
                x = 10**data[:,0]
                y = 10**data[:,1]
                up = y*data[:,3]
                msk = data[:,2] < -10.0
                data[:,2][msk] = 0.999
                lw = y*data[:,2]
                axs.errorbar(x, y, yerr=[lw, up], ls = 'None',
                             marker = '*', mec = 'r', c='red')
        if 'pacs160' in band:
            fl = obs_data+'data_160um_4_Sami_Niemi_20101126.txt'
            if i == 0:
                data = N.loadtxt(fl, usecols=(0, 1, 2, 3), comments = '#')
                x = 10**data[:,0]
                y = 10**data[:,1]
                up = y*data[:,3]
                msk = data[:,2] < -10.0
                data[:,2][msk] = 0.999
                lw = y*data[:,2]
                axs.errorbar(x, y, yerr=[lw, up], ls = 'None',
                             marker = '*', mec = 'r', c='red')
            if i == 1:
                data = N.loadtxt(fl, usecols=(0, 4, 5, 6), comments = '#')
                x = 10**data[:,0]
                y = 10**data[:,1]
                up = y*data[:,3]
                msk = data[:,2] < -10.0
                data[:,2][msk] = 0.999
                lw = y*data[:,2]
                axs.errorbar(x, y, yerr=[lw, up], ls = 'None',
                            marker = '*', mec = 'r', c='red')
            if i == 2:
                data = N.loadtxt(fl, usecols=(0, 7, 8, 9), comments = '#')
                x = 10**data[:,0]
                y = 10**data[:,1]
                up = y*data[:,3]
                msk = data[:,2] < -10.0
                data[:,2][msk] = 0.999
                lw = y*data[:,2]
                axs.errorbar(x, y, yerr=[lw, up], ls = 'None',
                             marker = '*', mec = 'r', c='red')
            if i == 3:
                data = N.loadtxt(fl, usecols=(0, 10, 11, 12), comments = '#')
                x = 10**data[:,0]
                y = 10**data[:,1]
                up = y*data[:,3]
                msk = data[:,2] < -10.0
                data[:,2][msk] = 0.999
                lw = y*data[:,2]
                axs.errorbar(x, y, yerr=[lw, up], ls = 'None',
                             marker = '*', mec = 'r', c='red')
        
        #set scales
        axs.set_xscale('log')
        axs.set_yscale('log')
        axs.set_xlim(xmin, xmax)
        axs.set_ylim(ymin, ymax)

        #remove unecessary ticks and add units
        if i % 2 == 0:
            axs.set_yticklabels([])
        if i == 2 or i == 3:
            axs.set_xlabel(r'$S(%s \mu m)$ [mJy]' % wave)
        else:
            axs.set_xticklabels([])
        if i == 1:
            axs.set_ylabel(r'$\frac{dN(S_{%s})}{dS_{%s}} \times S_{%s}^{2.5} \quad [$deg$^{-2}$ mJy$^{1.5}]$' % (wave, wave, wave))
            
    #save figure
    P.savefig(out_folder+'numbercounts_%s.png' % band)
    P.close()

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero/'
    database = 'sams.db'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/number_counts/'
    obs_data = hm+'/Dropbox/Research/Herschel/obs_data/'

    #5sigma limits derived by Kuang
    depths = {'pacs100_obs': 1.7,
              'pacs160_obs': 4.5,
              'spire250_obs': 5.0,
              'spire350_obs': 9.0,
              'spire500_obs': 10.0
              }

    #passbands to be plotted
    bands = ['pacs70_obs',
             'pacs100_obs',
             'pacs160_obs',
             'spire250_obs',
             'spire350_obs',
             'spire500_obs']

    pacs = ['pacs70_obs',
            'pacs100_obs',
            'pacs160_obs']

    redshifts = ['FIR.z >= 0.0 and FIR.z <= 0.5',
                 'FIR.z > 0.5 and FIR.z <= 1.0',
                 'FIR.z > 1.0 and FIR.z <= 2.0',
                 'FIR.z > 2.0 and FIR.z <= 5.0']

#    redshifts = ['FIR.z >= 2.0 and FIR.z <= 3.0',
#                 'FIR.z > 3.0 and FIR.z <= 3.5',
#                 'FIR.z > 3.5 and FIR.z <= 4.5',
#                 'FIR.z > 4.5 and FIR.z <= 6.0']
    
    #plot the number counts
    for bd in bands:
        if 'pacs' in bd:
            print 'plotting ', bd
            plot_number_counts(path, database, bd, redshifts,
                               out_folder, obs_data,
                               xmin = 0.1, xmax = 500,
                               ymin = 1.5*10**2, ymax = 6*10**5,
                               nbins = 23, sigma = 5.0)
        if 'spire' in bd:
            print 'plotting ', bd
            plot_number_counts(path, database, bd, redshifts,
                               out_folder, obs_data,
                               xmin = 0.1, xmax = 1600,
                               ymin = 10**2, ymax = 3*10**6,
                               nbins = 16, sigma = 5.0)

    print 'All done...'