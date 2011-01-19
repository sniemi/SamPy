'''
Plots luminosity functions at different redshifts.
Pulls data from an sqlite3 database.

@author: Sami Niemi
'''
import matplotlib
matplotlib.use('PS')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 16
matplotlib.rc('xtick', labelsize = 13) 
matplotlib.rc('ytick', labelsize = 13) 
matplotlib.rc('axes', linewidth = 1.2)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import numpy as N
import pylab as P
import re, os
import scipy.stats as SS
#from cosmocalc import cosmocalc
#Sami's repo
import db.sqlite
import astronomy.differentialfunctions as df
import astronomy.conversions as cv

def plot_luminosityfunction(path, database, redshifts,
                            band, out_folder, obs_data,
                            solid_angle = 10*160.,
                            ymin = 10**3, ymax = 2*10**6,
                            xmin = 0.5, xmax = 100,
                            nbins = 15, sigma = 5.0,
                            H0 = 70.0, WM = 0.28,
                            zmax = 6.0):
    '''
    @param solid_angle: area of the sky survey in arcmin**2
                        GOODS = 160, hence 10*160
    @param sigma: sigma level of the errors to be plotted
    @param nbins: number of bins (for simulated data)
    '''
    #fudge factor to handle errors that are way large
    fudge = ymin

    #subplot numbers
    columns = 3
    rows = 3 

    #get data
    query = '''select %s from FIR where %s > 3
               and FIR.spire250_obs < 1e6''' % (band, band)
    total = db.sqlite.get_data_sqlite(path, database, query)

    #make the figure
    fig = P.figure()
    P.subplots_adjust(wspace = 0.0, hspace = 0.0)
    ax = P.subplot(rows, columns, 1)
    
    #get the co-moving volume to the backend
    comovingVol = cv.comovingVolume(solid_angle, 0, zmax,
                                    H0 = H0, WM = WM)

    #weight each galaxy
    wghts = N.zeros(len(total)) + (1./comovingVol)
    #calculate the differential stellar mass function
    #with log binning
    b, n, nu = df.diff_function_log_binning(total,
                                            wgth = wghts, 
                                            mmax = xmax,
                                            mmin = xmin,
                                            nbins = nbins,
                                            log = True)
    #calculate the poisson error
    mask = nu > 0
    err = wghts[0] * N.sqrt(nu[mask]) * sigma
    up = n[mask] + err
    lw = n[mask] - err
    lw[lw < ymin] = ymin
    
    #plot the sigma area
    stot = ax.fill_between(b[mask], up, lw, color = '#728FCE')   
    #plot the knots
    mtot = ax.scatter(b[mask], n[mask], marker = 'o', s = 3, color = 'k')
    
    #add annotation
    ax.annotate('Total', (0.5, 0.87), xycoords='axes fraction',
               ha = 'center')

    #set scale
    ax.set_yscale('log')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xticklabels([])
    ax.set_ylabel(r'$\phi \ [Mpc^{-3} \ dex^{-1}]$')

    ptot = P.Rectangle((0, 0), 1, 1, fc='#728FCE')
    sline = '%i$\sigma$ errors' % sigma
    P.legend((mtot, ptot), ('All Galaxies', sline), loc='lower left',
             scatterpoints = 1, fancybox = True, shadow = True)

    #redshift limited plots
    for i, red in enumerate(redshifts):
        query = '''select %s from FIR where %s > 3 and %s
        and FIR.spire250_obs < 1e6''' % (band, band, red)
        limited = db.sqlite.get_data_sqlite(path, database, query)
        print query, len(limited)
        
        #modify redshift string
        tmp = red.split()
        #rtitle = r'$z = %.0f$' % N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])

        #get a comoving volume
        comovingVol = cv.comovingVolume(solid_angle,
                                        float(tmp[2]),
                                        float(tmp[6]),
                                        H0 = H0,
                                        WM = WM)

        #weights
        wghts = N.zeros(len(limited)) + (1./comovingVol)

        #differential function
        bb, nn, nu =  df.diff_function_log_binning(limited,
                                                   wgth = wghts, 
                                                   mmax = xmax,
                                                   mmin = xmin,
                                                   nbins = nbins,
                                                   log = True)
        #make a subplot
        axs = P.subplot(rows, columns, i+2)

        #calculate the poisson error
        mask = nu > 0
        err = wghts[0] * N.sqrt(nu[mask]) * sigma
        up = nn[mask] + err
        lw = nn[mask] - err
        lw[lw < ymin] = ymin
        #plot the sigma area
        axs.fill_between(bb[mask], up, lw, color = '#728FCE')
        #plot the knots
        axs.scatter(bb[mask], nn[mask], marker = 'o',
                    s = 3, color = 'k')

        #add annotation
        axs.annotate(rtitle, (0.5, 0.87),
                     xycoords='axes fraction',
                     ha = 'center')

        #set scales
        axs.set_yscale('log')
        axs.set_xlim(xmin, xmax)
        axs.set_ylim(ymin, ymax)

        #remove unnecessary ticks and add units
        if i == 0 or i == 1 or i == 3 or i == 4:
            axs.set_yticklabels([])
        if i == 2 or i == 3 or i == 4:
            btmp = re.search('\d\d\d', band).group()
            axs.set_xlabel(r'$\log_{10} (L_{%s} \ [L_{\odot}])$' % btmp)
            #axs.set_xticks(axs.get_xticks()[1:])
        else:
            axs.set_xticklabels([])
        if i == 2:
            axs.set_ylabel(r'$\phi \ [Mpc^{-3} \ dex^{-1}]$')
            #axs.set_xticks(axs.get_xticks()[:-1])
            
    #save figure
    P.savefig(out_folder+'luminosity_function_%s.ps' % band)
    P.close()

def plot_luminosityfunction2(path, database, redshifts,
                             band, out_folder, obs_data,
                             solid_angle = 10*160.,
                             ymin = 10**3, ymax = 2*10**6,
                             xmin = 0.5, xmax = 100,
                             nbins = 15, sigma = 5.0,
                             H0 = 70.0, WM = 0.28,
                             zmax = 6.0):
    '''
    @param solid_angle: area of the sky survey in arcmin**2
                        GOODS = 160, hence 10*160
    @param sigma: sigma level of the errors to be plotted
    @param nbins: number of bins (for simulated data)
    '''
    col = ['black', 'red', 'magenta', 'green', 'blue', 'brown']
    #get data
    query = '''select %s from FIR where %s > 3
               and FIR.spire250_obs < 1e6''' % (band, band)
    total = db.sqlite.get_data_sqlite(path, database, query)

    #make the figure
    fig = P.figure()
    ax = P.subplot(111)
    
    #get the co-moving volume to the backend
    comovingVol = cv.comovingVolume(solid_angle, 0, zmax,
                                    H0 = H0, WM = WM)

    #weight each galaxy
    wghts = N.zeros(len(total)) + (1./comovingVol)
    #calculate the differential stellar mass function
    #with log binning
    b, n, nu = df.diff_function_log_binning(total,
                                            wgth = wghts, 
                                            mmax = xmax,
                                            mmin = xmin,
                                            nbins = nbins,
                                            log = True)
    #calculate the poisson error
    mask = nu > 0
    err = wghts[0] * N.sqrt(nu[mask]) * sigma
    up = n[mask] + err
    lw = n[mask] - err
    lw[lw < ymin] = ymin
    
    #plot the knots
#    mtot = ax.errorbar(b[mask], n[mask], yerr = [err, err],
#                       color = 'k', label = 'Total',
#                       marker = 'None', ls = '-')
    
    #redshift limited plots
    for i, red in enumerate(redshifts):
        query = '''select %s from FIR where %s > 3 and %s
        and FIR.spire250_obs < 1e6''' % (band, band, red)
        limited = db.sqlite.get_data_sqlite(path, database, query)
        print query, len(limited)
        
        #modify redshift string
        tmp = red.split()
        #rtitle = r'$z = %.0f$' % N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])

        #get a comoving volume
        comovingVol = cv.comovingVolume(solid_angle,
                                        float(tmp[2]),
                                        float(tmp[6]),
                                        H0 = H0,
                                        WM = WM)

        #weights
        wghts = N.zeros(len(limited)) + (1./comovingVol)

        #differential function
        bb, nn, nu =  df.diff_function_log_binning(limited,
                                                   wgth = wghts, 
                                                   mmax = xmax,
                                                   mmin = xmin,
                                                   nbins = nbins,
                                                   log = True)

        #calculate the poisson error
        mask = nu > 0
#        err = wghts[0] * N.sqrt(nu[mask]) * sigma
#        up = nn[mask] + err
#        lw = nn[mask] - err
#        lw[lw < ymin] = ymin
        x = bb[mask]
        y = nn[mask]
        #to make sure that the plots go below the area plotted
        x = N.append(x, N.max(x)*1.01)
        y = N.append(y, 1e-10)
        ax.plot(x, y, color = col[i], marker = 'None', ls = '-', label = rtitle)

    #set scales
    ax.set_yscale('log')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_ylabel(r'$\phi \ [\mathrm{Mpc}^{-3} \ \mathrm{dex}^{-1}]$')
    ax.set_xlabel(r'$\log_{10}(L_{%s} \ [L_{\odot}])$' % re.search('\d\d\d', band).group())

    P.legend(scatterpoints = 1, fancybox = True, shadow = True)
    
    #save figure
    P.savefig(out_folder+'luminosity_function2_%s.ps' % band)
    P.close()

def plot_luminosityfunctionKDE(path, database, redshifts,
                               band, out_folder, obs_data,
                               solid_angle = 10*160.,
                               ymin = 10**3, ymax = 2*10**6,
                               xmin = 0.5, xmax = 100,
                               nbins = 15,
                               H0 = 70.0, WM = 0.28,
                               zmax = 6.0):
    '''
    @param solid_angle: area of the sky survey in arcmin**2
                        GOODS = 160, hence 10*160
    @param sigma: sigma level of the errors to be plotted
    @param nbins: number of bins (for simulated data)
    '''
    col = ['black', 'red', 'magenta', 'green', 'blue', 'brown']
    #get data
    query = '''select %s from FIR where %s > 6
               and FIR.spire250_obs < 1e6''' % (band, band)
    total = db.sqlite.get_data_sqlite(path, database, query)[:,0]
    print len(total)
    #get the co-moving volume to the backend
    comovingVol = cv.comovingVolume(solid_angle,
                                    0, zmax,
                                    H0 = H0, WM = WM)
    #normalization
    normalization = float(len(total))/comovingVol*(nbins*7*2)
    #KDE
    mu = SS.gaussian_kde(total)
    #in which points to evaluate
    x = N.linspace(N.min(total), N.max(total), nbins*7)
    
    #make the figure
    fig = P.figure()
    ax = P.subplot(111)
    #plot
    ax.plot(x, mu.evaluate(x)/normalization, color = 'gray', ls='--')
    
    #redshift limited plots
    for i, red in enumerate(redshifts):
        query = '''select %s from FIR where %s > 6 and %s
        and FIR.spire250_obs < 1e6''' % (band, band, red)
        limited = db.sqlite.get_data_sqlite(path, database, query)[:,0]
        print query, len(limited)
        
        #modify redshift string
        tmp = red.split()
        rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])
        #get a comoving volume
        comovingVol = cv.comovingVolume(solid_angle,
                                        float(tmp[2]),
                                        float(tmp[6]),
                                        H0 = H0,
                                        WM = WM)
        #normalization
        normalization = float(len(limited))/comovingVol*(nbins*7*2)
        #KDE
        mu = SS.gaussian_kde(limited)
        #in which points to evaluate
        x = N.linspace(N.min(limited), N.max(limited), nbins*7)

        ax.plot(x, mu.evaluate(x)/normalization, color = col[i],
                marker = 'None', ls = '-', label = rtitle)

    #set scales
    ax.set_yscale('log')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_ylabel(r'$\phi \ [\mathrm{Mpc}^{-3} \ \mathrm{dex}^{-1}]$')
    ax.set_xlabel(r'$\log_{10}(L_{%s} \ [L_{\odot}])$' % re.search('\d\d\d', band).group())

    P.legend(scatterpoints = 1, fancybox = True, shadow = True)
    
    #save figure
    P.savefig(out_folder+'luminosity_functionKDE_%s.ps' % band)
    P.close()

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    database = 'sams.db'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/luminosity_functions/'
    obs_data = hm+'/Dropbox/Research/Herschel/obs_data/'

    redshifts = ['FIR.z >= 0.0 and FIR.z <= 0.5',
                 'FIR.z >= 0.9 and FIR.z <= 1.1',
                 'FIR.z >= 1.9 and FIR.z <= 2.1',
                 'FIR.z >= 2.9 and FIR.z <= 3.1',
                 'FIR.z >= 3.9 and FIR.z <= 4.1',
                 'FIR.z >= 4.9 and FIR.z <= 5.1']

    redshifts = ['FIR.z >= 0.0 and FIR.z <= 0.5',
                 'FIR.z >= 1.9 and FIR.z <= 2.1',
                 'FIR.z >= 3.9 and FIR.z <= 4.1',
                 'FIR.z >= 4.9 and FIR.z <= 5.1']
    
    bands = ['FIR.pacs100',
             'FIR.pacs160',
             'FIR.spire250',
             'FIR.spire350',
             'FIR.spire500']
    
    for b in bands:
        if '100' in b:
            xmin = 8.5
            xmax = 12.3
            nb = 14
        if '160' in b:
            xmin = 8.5
            xmax = 12.0
            nb = 13
        if '250' in b:
            xmin = 8.5
            xmax = 11.5
            nb = 11
        if '350' in b:
            xmin = 8.5
            xmax = 11.5
            nb = 10
        if '500' in b:
            xmin = 8.5
            xmax = 11.5
            nb = 10
            
        print 'Plotting ', b

#        plot_luminosityfunction(path, database, redshifts, b,
#                                out_folder, obs_data,
#                                xmin = xmin, xmax = xmax,
#                                ymin = 10**-5, ymax = 8*10**-2,
#                                nbins = 18, sigma = 5.0)
#
#        plot_luminosityfunction2(path, database, redshifts, b,
#                                 out_folder, obs_data,
#                                 xmin = xmin, xmax = xmax,
#                                 ymin = 10**-5, ymax = 5*10**-2,
#                                 nbins = nb, sigma = 5.0)

        plot_luminosityfunctionKDE(path, database, redshifts, b,
                                   out_folder, obs_data,
                                   xmin = xmin, xmax = xmax,
                                   ymin = 10**-5, ymax = 5*10**-2,
                                   nbins = nb)

#    redshifts = ['FIR.z >= 0.0 and FIR.z < 0.1',
#                 'FIR.z > 0.1 and FIR.z < 0.2',
#                 'FIR.z > 0.2 and FIR.z < 0.3',
#                 'FIR.z > 0.3 and FIR.z < 0.4',
#                 'FIR.z > 0.4 and FIR.z < 0.5']
#
#    print 'Plotting the extra plot...'
#    plot_luminosityfunction(path, database, redshifts, 'FIR.spire250',
#                            out_folder+'spec', obs_data,
#                            xmin = 8.1, xmax = 11.3,
#                            ymin = 10**-5, ymax = 3*10**-1,
#                            nbins = 10, sigma = 5.0)

    print 'All done...'