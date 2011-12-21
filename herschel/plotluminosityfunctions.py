"""
Plots luminosity functions at different redshifts.
Pulls data from an sqlite3 database.

:author: Sam-Matias Niemi
:contact: sammy@sammyniemi.com
"""
import matplotlib
matplotlib.use('PS')
matplotlib.rc('text', usetex=True)
matplotlib.rcParams['font.size'] = 15
matplotlib.rc('xtick', labelsize=13)
matplotlib.rc('ytick', labelsize=13)
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rcParams['legend.fontsize'] = 11
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import numpy as N
import pylab as P
import re, os
import scipy.stats as SS
import SamPy.db.sqlite
import SamPy.astronomy.differentialfunctions as df
import SamPy.astronomy.conversions as cv
import SamPy.astronomy.luminosityFunctions as lf


def plot_luminosityfunction(path, database, redshifts,
                            band, out_folder,
                            solid_angle=10 * 160.,
                            ymin=10 ** 3, ymax=2 * 10 ** 6,
                            xmin=0.5, xmax=100,
                            nbins=15, sigma=5.0,
                            H0=70.0, WM=0.28,
                            zmax=6.0):
    """
    :param solid_angle: area of the sky survey in arcmin**2
                        GOODS = 160, hence 10*160
    :param sigma: sigma level of the errors to be plotted
    :param nbins: number of bins (for simulated data)
    """
    #subplot numbers
    columns = 3
    rows = 3

    #get data
    query = """select %s from FIR where %s > 7
               and FIR.spire250_obs < 1e6""" % (band, band)
    total = SamPy.db.sqlite.get_data_sqlite(path, database, query)

    #make the figure
    fig = P.figure()
    P.subplots_adjust(wspace=0.0, hspace=0.0)
    ax = P.subplot(rows, columns, 1)

    #get the co-moving volume to the backend
    comovingVol = cv.comovingVolume(solid_angle, 0, zmax,
                                    H0=H0, WM=WM)

    #weight each galaxy
    wghts = N.zeros(len(total)) + (1. / comovingVol)
    #calculate the differential stellar mass function
    #with log binning
    b, n, nu = df.diff_function_log_binning(total,
                                            wgth=wghts,
                                            mmax=xmax,
                                            mmin=xmin,
                                            nbins=nbins,
                                            log=True)
    #calculate the poisson error
    mask = nu > 0
    err = wghts[0] * N.sqrt(nu[mask]) * sigma
    up = n[mask] + err
    lw = n[mask] - err
    lw[lw < ymin] = ymin

    #plot the sigma area
    stot = ax.fill_between(b[mask], up, lw, color='#728FCE')
    #plot the knots
    mtot = ax.scatter(b[mask], n[mask], marker='o', s=3, color='k')

    #add annotation
    ax.annotate('Total', (0.5, 0.87), xycoords='axes fraction',
                ha='center')

    #set scale
    ax.set_yscale('log')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xticklabels([])
    ax.set_ylabel(r'$\phi \ [Mpc^{-3} \ dex^{-1}]$')

    ptot = P.Rectangle((0, 0), 1, 1, fc='#728FCE')
    sline = '%i$\sigma$ errors' % sigma
    P.legend((mtot, ptot), ('All Galaxies', sline), loc='lower left',
                         scatterpoints=1, fancybox=True, shadow=True)

    #redshift limited plots
    for i, red in enumerate(redshifts):
        query = '''select %s from FIR where %s > 7 and %s
        and FIR.spire250_obs < 1e6''' % (band, band, red)
        limited = SamPy.db.sqlite.get_data_sqlite(path, database, query)
        print query, len(limited)

        #modify redshift string
        tmp = red.split()
        #rtitle = r'$z = %.0f$' % N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])

        #get a comoving volume
        comovingVol = cv.comovingVolume(solid_angle,
                                        float(tmp[2]),
                                        float(tmp[6]),
                                        H0=H0,
                                        WM=WM)

        #weights
        wghts = N.zeros(len(limited)) + (1. / comovingVol)

        #differential function
        bb, nn, nu = df.diff_function_log_binning(limited,
                                                  wgth=wghts,
                                                  mmax=xmax,
                                                  mmin=xmin,
                                                  nbins=nbins,
                                                  log=True)
        #make a subplot
        axs = P.subplot(rows, columns, i + 2)

        #calculate the poisson error
        mask = nu > 0
        err = wghts[0] * N.sqrt(nu[mask]) * sigma
        up = nn[mask] + err
        lw = nn[mask] - err
        lw[lw < ymin] = ymin
        #plot the sigma area
        axs.fill_between(bb[mask], up, lw, color='#728FCE')
        #plot the knots
        axs.scatter(bb[mask], nn[mask], marker='o',
                    s=3, color='k')

        #add annotation
        axs.annotate(rtitle, (0.5, 0.87),
                     xycoords='axes fraction',
                     ha='center')

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
    P.savefig(out_folder + 'luminosity_function_%s.ps' % band)
    P.close()


def plot_luminosityfunction2(path, database, redshifts,
                             band, out_folder,
                             solid_angle=10 * 160.,
                             ymin=10 ** 3, ymax=2 * 10 ** 6,
                             xmin=0.5, xmax=100,
                             nbins=15, sigma=5.0,
                             H0=70.0, WM=0.28,
                             zmax=6.0):
    """
    :param solid_angle: area of the sky survey in arcmin**2
                        GOODS = 160, hence 10*160
    :param sigma: sigma level of the errors to be plotted
    :param nbins: number of bins (for simulated data)
    """
    col = ['black', 'red', 'magenta', 'green', 'blue', 'brown']
    #get data
    query = '''select %s from FIR where %s > 7
               and FIR.spire250_obs < 1e6''' % (band, band)
    total = SamPy.db.sqlite.get_data_sqlite(path, database, query)

    #make the figure
    fig = P.figure()
    ax = P.subplot(111)

    #get the co-moving volume to the backend
    comovingVol = cv.comovingVolume(solid_angle, 0, zmax,
                                    H0=H0, WM=WM)

    #weight each galaxy
    wghts = N.zeros(len(total)) + (1. / comovingVol)
    #calculate the differential stellar mass function
    #with log binning
    b, n, nu = df.diff_function_log_binning(total,
                                            wgth=wghts,
                                            mmax=xmax,
                                            mmin=xmin,
                                            nbins=nbins,
                                            log=True)
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
        query = '''select %s from FIR where %s > 7 and %s
        and FIR.spire250_obs < 1e6''' % (band, band, red)
        limited = SamPy.db.sqlite.get_data_sqlite(path, database, query)
        print query, len(limited)

        #modify redshift string
        tmp = red.split()
        #rtitle = r'$z = %.0f$' % N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])

        #get a comoving volume
        comovingVol = cv.comovingVolume(solid_angle,
                                        float(tmp[2]),
                                        float(tmp[6]),
                                        H0=H0,
                                        WM=WM)

        #weights
        wghts = N.zeros(len(limited)) + (1. / comovingVol)

        #differential function
        bb, nn, nu = df.diff_function_log_binning(limited,
                                                  wgth=wghts,
                                                  mmax=xmax,
                                                  mmin=xmin,
                                                  nbins=nbins,
                                                  log=True)

        #calculate the poisson error
        mask = nu > 0
        #        err = wghts[0] * N.sqrt(nu[mask]) * sigma
        #        up = nn[mask] + err
        #        lw = nn[mask] - err
        #        lw[lw < ymin] = ymin
        x = bb[mask]
        y = nn[mask]
        #to make sure that the plots go below the area plotted
        x = N.append(x, N.max(x) * 1.01)
        y = N.append(y, 1e-10)
        ax.plot(x, y, color=col[i], marker='None', ls='-', label=rtitle)

    #set scales
    ax.set_yscale('log')
    ax.set_xlim(xmin + 0.2, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_ylabel(r'$\phi \ [\mathrm{Mpc}^{-3} \ \mathrm{dex}^{-1}]$')
    ax.set_xlabel(r'$\log_{10}(L_{%s} \ [L_{\odot}])$' % re.search('\d\d\d', band).group())

    P.legend(scatterpoints=1, fancybox=True, shadow=True)

    #save figure
    P.savefig(out_folder + 'luminosity_function2_%s.ps' % band)
    P.close()


def plot_luminosityfunctionKDE(path, database, redshifts,
                               band, out_folder,
                               solid_angle=10 * 160.,
                               ymin=10 ** 3, ymax=2 * 10 ** 6,
                               xmin=0.5, xmax=100,
                               nbins=15,
                               H0=70.0, WM=0.28,
                               zmax=6.0):
    """
    :param solid_angle: area of the sky survey in arcmin**2
                        GOODS = 160, hence 10*160
    :param sigma: sigma level of the errors to be plotted
    :param nbins: number of bins (for simulated data)
    """
    col = ['black', 'red', 'magenta', 'green', 'blue', 'brown']
    #get data
    query = '''select %s from FIR where %s > 6
               and FIR.spire250_obs < 1e6''' % (band, band)
    total = SamPy.db.sqlite.get_data_sqlite(path, database, query)[:, 0]
    print len(total)
    #get the co-moving volume to the backend
    comovingVol = cv.comovingVolume(solid_angle,
                                    0, zmax,
                                    H0=H0, WM=WM)
    #normalization
    normalization = float(len(total)) / comovingVol * (nbins * 7 * 2)
    #KDE
    mu = SS.gaussian_kde(total)
    #in which points to evaluate
    x = N.linspace(N.min(total), N.max(total), nbins * 7)

    #make the figure
    fig = P.figure()
    ax = P.subplot(111)
    #plot
    ax.plot(x, mu.evaluate(x) / normalization, color='gray', ls='--')

    #redshift limited plots
    for i, red in enumerate(redshifts):
        query = '''select %s from FIR where %s > 6 and %s
        and FIR.spire250_obs < 1e6''' % (band, band, red)
        limited = SamPy.db.sqlite.get_data_sqlite(path, database, query)[:, 0]
        print query, len(limited)

        #modify redshift string
        tmp = red.split()
        rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])
        #get a comoving volume
        comovingVol = cv.comovingVolume(solid_angle,
                                        float(tmp[2]),
                                        float(tmp[6]),
                                        H0=H0,
                                        WM=WM)
        #normalization
        normalization = float(len(limited)) / comovingVol * (nbins * 7 * 2)
        #KDE
        mu = SS.gaussian_kde(limited)
        #in which points to evaluate
        x = N.linspace(N.min(limited), N.max(limited), nbins * 7)

        ax.plot(x, mu.evaluate(x) / normalization, color=col[i],
                marker='None', ls='-', label=rtitle)

    #set scales
    ax.set_yscale('log')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_ylabel(r'$\phi \ [\mathrm{Mpc}^{-3} \ \mathrm{dex}^{-1}]$')
    ax.set_xlabel(r'$\log_{10}(L_{%s} \ [L_{\odot}])$' % re.search('\d\d\d', band).group())

    P.legend(scatterpoints=1, fancybox=True, shadow=True)

    #save figure
    P.savefig(out_folder + 'luminosity_functionKDE_%s.ps' % band)
    P.close()


def plot_luminosityfunctionPaper(path, database, redshifts,
                                 bands, out_folder,
                                 solid_angle=100*160.,
                                 ymin=5e-7, ymax=5*10**-2,
                                 xmin=9.1, xmax=13.1,
                                 H0=70.0, WM=0.28):
    """
    :param solid_angle: area of the sky survey in arcmin**2
                        GOODS = 160, hence 100*160
    """
    col = ['black', 'red', 'magenta', 'green', 'blue']
    lin = [':', '--', '-', '-.', '-']
    #make the figure
    fig = P.figure()
    fig.subplots_adjust(left=0.09, bottom=0.08,
                        right=0.93, top=0.95,
                        wspace=0.0, hspace=0.0)
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    for b in bands:
        if '100' in b: nb = 19
        if '160' in b: nb = 14
        if '250' in b: nb = 14
        if '350' in b: nb = 11

        print '\nPlotting ', b

        #redshift limited plots
        for i, red in enumerate(redshifts):
            query = '''select %s from FIR where %s > 7.7 and %s
            and FIR.spire250_obs < 1e6''' % (b, b, red)
            limited = SamPy.db.sqlite.get_data_sqlite(path, database, query)
            print query, len(limited)

            #modify redshift string
            tmp = red.split()
            #rtitle = r'$z = %.0f$' % N.mean(N.array([float(tmp[2]), float(tmp[6])]))
            rtitle = r'$%s \leq z < %s$' % (tmp[2], tmp[6])

            #get a comoving volume
            comovingVol = cv.comovingVolume(solid_angle,
                                            float(tmp[2]),
                                            float(tmp[6]),
                                            H0=H0,
                                            WM=WM)
            #weights
            wghts = N.zeros(len(limited)) + (1. / comovingVol)
            #differential function
            bb, nn, nu = df.diff_function_log_binning(limited,
                                                      wgth=wghts,
                                                      mmax=xmax,
                                                      mmin=xmin,
                                                      nbins=nb,
                                                      log=True)

            mask = nu > 0
            x = bb[mask]
            y = nn[mask]
            #to make sure that the plots go below the area plotted
            x = N.append(x, N.max(x) * 1.01)
            y = N.append(y, 1e-10)
            if '100' in b:
                ax1.plot(x, N.log10(y), color=col[i], marker='None', ls=lin[i], label=rtitle)
            if '160' in b:
                ax2.plot(x, N.log10(y), color=col[i], marker='None', ls=lin[i], label=rtitle)
            if '250' in b:
                ax3.plot(x, N.log10(y), color=col[i], marker='None', ls=lin[i], label=rtitle)
            if '350' in b:
                ax4.plot(x, N.log10(y), color=col[i], marker='None', ls=lin[i], label=rtitle)

    #plot observational constrains
    mic100 = lf.Herschel100Lapi()
    mic250 = lf.Herschel250Lapi()

    #x values
    x100 = N.log10(mic100['Lsun'])
    x250 = N.log10(mic250['Lsun'])

    #mask out missing values
    msk100z15 = mic100['z1.5'][:, 0] > -6.5
    msk100z22 = mic100['z2.2'][:, 0] > -6.5
    msk100z32 = mic100['z3.2'][:, 0] > -6.5

    msk250z15 = mic250['z1.4'][:, 0] > -6.5
    msk250z22 = mic250['z2.2'][:, 0] > -6.5
    msk250z32 = mic250['z3.2'][:, 0] > -6.5


    #PACS100 plots
    ax1.errorbar(x100[msk100z15], mic100['z1.5'][:, 0][msk100z15],
                 yerr=[-mic100['z1.5'][:, 2][msk100z15], mic100['z1.5'][:, 1][msk100z15]],
                 marker='s', ms=4, ls='None', mfc='r', mec='r', c='r')
    ax1.errorbar(x100[msk100z22], mic100['z2.2'][:, 0][msk100z22],
                 yerr=[-mic100['z2.2'][:, 2][msk100z22], mic100['z2.2'][:, 1][msk100z22]],
                 marker='o', ms=4, ls='None', mfc='m', mec='m', c='m')
    ax1.errorbar(x100[msk100z32], mic100['z3.2'][:, 0][msk100z32],
                 yerr=[-mic100['z3.2'][:, 2][msk100z32], mic100['z3.2'][:, 1][msk100z32]],
                 marker='d', ms=4, ls='None', mfc='g', mec='g', c='g')
    #    ax1.scatter(x100[msk100z15], 10**mic100['z1.5'][:,0][msk100z15],
    #                marker='s', s=10,c='k')
    #    ax1.scatter(x100[msk100z22], 10**mic100['z2.2'][:,0][msk100z22],
    #                marker='o', s=10, c='r')
    #    ax1.scatter(x100[msk100z32], 10**mic100['z3.2'][:,0][msk100z32],
    #                marker='d', s=10, c='m')

    #SPIRE250 plots
    ax3.errorbar(x250[msk250z15], mic250['z1.4'][:, 0][msk250z15],
                 yerr=[-mic250['z1.4'][:, 2][msk250z15], mic250['z1.4'][:, 1][msk250z15]],
                 marker='s', ms=4, ls='None', mfc='r', mec='r', c='r', label=r'$1.2 \leq z < 1.6$')
    ax3.errorbar(x250[msk250z22], mic250['z2.2'][:, 0][msk250z22],
                 yerr=[-mic250['z2.2'][:, 2][msk250z22], mic250['z2.2'][:, 1][msk250z22]],
                 marker='o', ms=4, ls='None', mfc='m', mec='m', c='m',  label=r'$2.0 \leq z < 2.4$')
    ax3.errorbar(x250[msk250z32], mic250['z3.2'][:, 0][msk250z32],
                 yerr=[-mic250['z3.2'][:, 2][msk250z32], mic250['z3.2'][:, 1][msk250z32]],
                 marker='d', ms=4, ls='None', mfc='g', mec='g', c='g', label=r'$2.4 \leq z < 4.0$')
    #    ax3.scatter(x250[msk250z15], 10**mic250['z1.4'][:,0][msk250z15],
    #                marker='s', s=10,c='k')
    #    ax3.scatter(x250[msk250z22], 10**mic250['z2.2'][:,0][msk250z22],
    #                marker='o', s=10, c='r')
    #    ax3.scatter(x250[msk250z32], 10**mic250['z3.2'][:,0][msk250z32],
    #                marker='d', s=10, c='m')


    #labels
    ax4.errorbar([5,], [-10,], yerr=[0.1,],
                 marker='s', ms=4, ls='None', mfc='r', mec='r', c='r', label=r'$1.2 \leq z < 1.6$')
    ax4.errorbar([5,], [-10,], yerr=[0.1,],
                 marker='o', ms=4, ls='None', mfc='m', mec='m', c='m',  label=r'$2.0 \leq z < 2.4$')
    ax4.errorbar([5,], [-10,], yerr=[0.1,],
                 marker='d', ms=4, ls='None', mfc='g', mec='g', c='g', label=r'$2.4 \leq z < 4.0$')

    #set scales
    #    ax1.set_yscale('log')
    #    ax2.set_yscale('log')
    #    ax3.set_yscale('log')
    #    ax4.set_yscale('log')

    #ylabel = r'$\phi \ [\mathrm{Mpc}^{-3} \ \mathrm{dex}^{-1}]$'
    ylabel = r'$\log_{10} \left ( \phi \ [\mathrm{Mpc}^{-3} \ \mathrm{dex}^{-1}] \right )$'

    xlabel = r'$\log_{10}(L \ [L_{\odot}])$'

    #labels
    ax3.set_xlabel(xlabel)
    ax4.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax3.set_ylabel(ylabel)
    ax2.set_yticklabels([])
    ax4.set_yticklabels([])
    ax1.set_xticklabels([])
    ax2.set_xticklabels([])
    #limits
    ymin = N.log10(ymin)
    ymax = N.log10(ymax)
    ax1.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin + 0.2, xmax)
    ax2.set_ylim(ymin, ymax)
    ax2.set_xlim(xmin + 0.2, xmax)
    ax3.set_ylim(ymin, ymax)
    ax3.set_xlim(xmin + 0.2, xmax)
    ax4.set_ylim(ymin, ymax)
    ax4.set_xlim(xmin + 0.2, xmax)

    #add some annotations
    P.text(0.5, 0.94, 'a) PACS 100',
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax1.transAxes)
    P.text(0.5, 0.94, 'b) PACS 160',
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax2.transAxes)
    P.text(0.5, 0.94, 'c) SPIRE 250',
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax3.transAxes)
    P.text(0.5, 0.94, 'd) SPIRE 350',
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax4.transAxes)

    #legend
    ax4.legend(scatterpoints=1, fancybox=True, shadow=True,
               loc='center right')
    #save figure
    P.savefig(out_folder + 'luminosity_functionPaper.ps')
    P.close()


if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Research/Herschel/runs/big_volume/'
    database = 'sams.db'
    out_folder = hm + '/Research/Herschel/plots/luminosity_functions/'
    obs_data = hm + '/Dropbox/Research/Herschel/obs_data/'

    redshifts = ['FIR.z >= 0.0 and FIR.z < 0.3',
                 'FIR.z >= 1.2 and FIR.z < 1.6',
                 'FIR.z >= 2.0 and FIR.z < 2.4',
                 'FIR.z >= 2.4 and FIR.z < 4.0',
                 'FIR.z >= 4.8 and FIR.z < 5.1']

    bands = ['FIR.pacs100',
             'FIR.pacs160',
             'FIR.spire250',
             'FIR.spire350']

    plot_luminosityfunctionPaper(path, database, redshifts, bands, out_folder)

    print 'All done...'