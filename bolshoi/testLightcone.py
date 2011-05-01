'''
Generates some test plots from a lightcone that has been
generated using Rachel's SAM.

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu
'''
import matplotlib
matplotlib.use('Agg')
matplotlib.rc('text', usetex=True)
matplotlib.rcParams['font.size'] = 16
matplotlib.rc('xtick', labelsize=13)
matplotlib.rc('ytick', labelsize=13)
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rcParams['legend.fontsize'] = 11
matplotlib.rcParams['legend.handlelength'] = 1
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import matplotlib.pyplot as plt
import numpy as np
import pylab as P
import re, os
import scipy.stats as SS
from matplotlib import cm
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, NullFormatter, LogLocator
#Sami's repo
import db.sqlite
import astronomy.differentialfunctions as df
import astronomy.conversions as cv
import sandbox.MyTools as M


def plot_luminosityfunction(path, database, redshifts,
                            band, out_folder,
                            solid_angle=1638.0,
                            ymin=10 ** 3, ymax=2 * 10 ** 6,
                            xmin=0.5, xmax=100,
                            nbins=10, sigma=5.0,
                            H0=70.0, WM=0.28,
                            zmax=9.0):
    '''
    :param solid_angle: area of the sky survey in arcmin**2
                        GOODS = 160
    :param sigma: sigma level of the errors to be plotted
    :param nbins: number of bins (for simulated data)
    '''
    #subplot numbers
    columns = 3
    rows = 3

    #get data
    query = '''select %s from FIR where %s > 7
               and FIR.spire250_obs < 1e6''' % (band, band)
    total = db.sqlite.get_data_sqlite(path, database, query)

    #make the figure
    fig = P.figure()
    P.subplots_adjust(wspace=0.0, hspace=0.0)
    ax = P.subplot(rows, columns, 1)

    #get the co-moving volume to the backend
    comovingVol = cv.comovingVolume(solid_angle, 0, zmax,
                                    H0=H0, WM=WM)

    #weight each galaxy
    wghts = np.zeros(len(total)) + (1. / comovingVol)
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
    err = wghts[0] * np.sqrt(nu[mask]) * sigma
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
        limited = db.sqlite.get_data_sqlite(path, database, query)
        print query, len(limited)

        #modify redshift string
        tmp = red.split()
        #rtitle = r'$z = %.0f$' % np.mean(np.array([float(tmp[2]), float(tmp[6])]))
        rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])

        #get a comoving volume
        comovingVol = cv.comovingVolume(solid_angle,
                                        float(tmp[2]),
                                        float(tmp[6]),
                                        H0=H0,
                                        WM=WM)

        #weights
        wghts = np.zeros(len(limited)) + (1. / comovingVol)

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
        err = wghts[0] * np.sqrt(nu[mask]) * sigma
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
    P.savefig(out_folder + 'luminosity_function_%s.pdf' % band)
    P.close()


def plot_luminosityfunctionPaper(path, database, redshifts,
                                 bands, out_folder,
                                 solid_angle=1638.0,
                                 ymin=1e-5, ymax=5 * 10 ** -2,
                                 xmin=8.0, xmax=12.3,
                                 H0=70.0, WM=0.28):
    '''
    :param solid_angle: area of the sky survey in arcmin**2, GOODS = 160
    '''
    col = ['black', 'red', 'magenta', 'green', 'blue', 'brown']
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
        if '100' in b: nb = 15
        if '160' in b: nb = 11
        if '250' in b: nb = 11
        if '350' in b: nb = 9

        print '\nPlotting ', b

        #redshift limited plots
        for i, red in enumerate(redshifts):
            query = '''select %s from FIR where %s > 7.7 and %s
            and FIR.spire250_obs < 1e6''' % (b, b, red)
            limited = db.sqlite.get_data_sqlite(path, database, query)
            print query, len(limited)

            #modify redshift string
            tmp = red.split()
            #rtitle = r'$z = %.0f$' % np.mean(np.array([float(tmp[2]), float(tmp[6])]))
            rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])

            #get a comoving volume
            comovingVol = cv.comovingVolume(solid_angle,
                                            float(tmp[2]),
                                            float(tmp[6]),
                                            H0=H0,
                                            WM=WM)
            #weights
            wghts = np.zeros(len(limited)) + (1. / comovingVol)
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
            x = np.append(x, np.max(x) * 1.01)
            y = np.append(y, 1e-10)
            if '100' in b:
                ax1.plot(x, y, color=col[i], marker='None', ls='-', label=rtitle)
            if '160' in b:
                ax2.plot(x, y, color=col[i], marker='None', ls='-', label=rtitle)
            if '250' in b:
                ax3.plot(x, y, color=col[i], marker='None', ls='-', label=rtitle)
            if '350' in b:
                ax4.plot(x, y, color=col[i], marker='None', ls='-', label=rtitle)


    #set scales
    ax1.set_yscale('log')
    ax2.set_yscale('log')
    ax3.set_yscale('log')
    ax4.set_yscale('log')

    ylabel = r'$\phi \ [\mathrm{Mpc}^{-3} \ \mathrm{dex}^{-1}]$'
    #xlabel = r'$\log_{10}(L_{%s} \ [L_{\odot}])$' % re.search('\d\d\d', band).group()
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
    #make grid
    #ax1.grid()
    #ax2.grid()
    #ax3.grid()
    #ax4.grid()
    #legend
    ax4.legend(scatterpoints=1, fancybox=True, shadow=True,
               loc='center right')
    #save figure
    P.savefig(out_folder + 'luminosity_functionCombined.pdf')
    P.close()


def plotAllLuminosityFunctions(path, database, out_folder):
    redshifts = ['FIR.z >= 0.0 and FIR.z <= 0.5',
                 'FIR.z >= 1.9 and FIR.z <= 2.1',
                 'FIR.z >= 3.9 and FIR.z <= 4.1',
                 'FIR.z >= 4.9 and FIR.z <= 5.1']

    bands = ['FIR.pacs100',
             'FIR.pacs160',
             'FIR.spire250',
             'FIR.spire350',
             'FIR.spire500']

    plot_luminosityfunctionPaper(path, database, redshifts, bands, out_folder)

    for b in bands:
        if '100' in b:
            xmin = 8.5
            xmax = 12.3
        if '160' in b:
            xmin = 8.5
            xmax = 12.0
        if '250' in b:
            xmin = 8.5
            xmax = 11.5
        if '350' in b:
            xmin = 8.5
            xmax = 11.5
        if '500' in b:
            xmin = 8.5
            xmax = 11.5

        print 'Plotting ', b

        plot_luminosityfunction(path, database, redshifts, b,
                                out_folder,
                                xmin=xmin, xmax=xmax,
                                ymin=10 ** -5, ymax=8 * 10 ** -2,
                                nbins=10, sigma=1.0,
                                solid_angle=1638.0)

    redshifts = ['FIR.z >= 0.0 and FIR.z < 0.1',
                 'FIR.z > 0.1 and FIR.z < 0.2',
                 'FIR.z > 0.2 and FIR.z < 0.3',
                 'FIR.z > 0.3 and FIR.z < 0.4',
                 'FIR.z > 0.4 and FIR.z < 0.5']

    print 'Plotting the extra plot...'
    plot_luminosityfunction(path, database, redshifts, 'FIR.spire250',
                            out_folder + 'spec',
                            xmin=8.1, xmax=11.3,
                            ymin=10 ** -5, ymax=3 * 10 ** -1,
                            nbins=10, sigma=1.0)

    print 'All done...'


def scatterHistograms(xdata,
                      ydata,
                      xlabel,
                      ylabel,
                      output,
                      solid_angle=1638.0):
    '''
    This functions generates a scatter plot and
    projected histograms to both axes.
    '''
    #constants
    xmin = 0.0
    xmax = 9.0
    ymin = -2.05
    ymax = 2.0
    H0 = 70.0
    WM = 0.28

    #xbins and ybins
    xbins = np.linspace(xmin, xmax, 30)
    ybins = np.linspace(ymin, ymax, 20)
    dfx = xbins[1] - xbins[0]
    dfy = ybins[1] - ybins[0]

    #calculate volume
    comovingVol = cv.comovingVolume(solid_angle,
                                    xmin,
                                    xmax,
                                    H0=H0,
                                    WM=WM)

    #weight each galaxy
    wghtsx = (np.zeros(len(xdata)) + (1. / comovingVol)) / dfx
    wghtsy = (np.zeros(len(ydata)) + (1. / comovingVol)) / dfy

    #no labels, null formatter
    nullfmt = NullFormatter()

    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]

    #make a figure
    fig = plt.figure(figsize=(12, 12))

    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)

    #no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    #the scatter plot
    axScatter.scatter(xdata, ydata,
                      marker='o',
                      s=0.5,
                      c='k')

    #KDE
    x = M.AnaKDE([xdata, ydata])
    x_vec, y_vec, zm, lvls, d0, d1 = x.contour(np.linspace(xmin - 0.1, xmax + 0.1, 50),
                                               np.linspace(ymin - 0.1, ymax + 0.1, 50),
                                               return_data=True)
    axScatter.contourf(x_vec, y_vec, zm,
                       levels=np.linspace(0.01, 0.92 * np.max(zm), 10),
                       cmap=cm.get_cmap('gist_yarg'),
                       alpha=0.8)

    #draw a line to the detection limit, 5mJy (at 250)
    axScatter.axhline(np.log10(5),
                      color='green',
                      ls='--',
                      lw=1.8)

    #scatter labels
    axScatter.set_xlabel(xlabel)
    axScatter.set_ylabel(ylabel)

    #set scatter limits
    axScatter.set_xlim(xmin, xmax)
    axScatter.set_ylim(ymin, ymax)

    #make x histogram
    x1 = axHistx.hist(xdata,
                      bins=xbins,
                      weights=wghtsx,
                      log=True,
                      color='gray')
    x2 = axHistx.hist(xdata[ydata > np.log10(5)],
                      bins=xbins,
                      weights=wghtsx[ydata > np.log10(5)],
                      log=True,
                      color='gray',
                      hatch='x')
    #set legend of x histogram
    plt.legend((x1[2][0], x2[2][0]),
               ('All Galaxies', r'$S_{250}> 5\ \mathrm{mJy}$'),
               shadow=False,
               fancybox=False,
               bbox_to_anchor=(0.01, 1.34),
               loc=2,
               borderaxespad=0.)
    #make y histogram
    axHisty.hist(ydata,
                 bins=ybins,
                 orientation='horizontal',
                 weights=wghtsy,
                 log=True,
                 color='gray')

    #set histogram limits
    axHistx.set_xlim(axScatter.get_xlim())
    axHistx.set_ylim(1e-7, 1e0)
    axHisty.set_ylim(axScatter.get_ylim())
    axHisty.set_xlim(4e-9, 1e-1)

    #set histogram labels
    axHistx.set_ylabel(r'$\frac{\mathrm{d}N}{\mathrm{d}z} \quad [\mathrm{Mpc}^{-3} \  \mathrm{dex}^{-1}]$')
    axHisty.set_xlabel(r'$\frac{\mathrm{d}N}{\mathrm{d}S} \quad [\mathrm{Mpc}^{-3} \  \mathrm{dex}^{-1}]$')

    #remove the lowest ticks from the histogram plots
    #axHistx.set_yticks(axHistx.get_yticks()[:-1])
    #axHisty.set_xticks(axHisty.get_xticks()[:-1])

    #set minor ticks
    axScatter.xaxis.set_minor_locator(MultipleLocator(0.5 / 5.))
    axScatter.xaxis.set_minor_formatter(NullFormatter())
    axScatter.yaxis.set_minor_locator(MultipleLocator(1. / 5.))
    axScatter.yaxis.set_minor_formatter(NullFormatter())
    #xhist
    axHistx.xaxis.set_minor_locator(MultipleLocator(0.5 / 5.))
    axHistx.xaxis.set_minor_formatter(NullFormatter())
    #yhist
    axHisty.yaxis.set_minor_locator(MultipleLocator(1. / 5.))
    axHisty.yaxis.set_minor_formatter(NullFormatter())

    plt.savefig(output)


def plotFluxRedshiftDistribution(path,
                                 database,
                                 out_folder):
    query = '''select FIR.spire250_obs, FIR.z
    from FIR where
    FIR.spire250_obs > 1e-6 and
    FIR.spire250_obs < 1e5
    '''
    #get data
    data = db.sqlite.get_data_sqlite(path, database, query)
    #convert fluxes to mJy
    flux = np.log10(data[:, 0] * 1e3) # log of mJy
    redshift = data[:, 1]

    #xlabels
    xlabel = r'$z$'
    ylabel = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'

    #output folder and file name
    output = "{0:>s}FluxRedshiftDist.png".format(out_folder)

    #generate the plot
    scatterHistograms(redshift,
                      flux,
                      xlabel,
                      ylabel,
                      output)


def diff_function(data, column=0, log=False,
                  wgth=None, mmax=15.5, mmin=9.0,
                  nbins=35, h=0.7, volume=250, nvols=1,
                  physical_units=False, verbose=False):
    '''
    Calculates a differential function from data.
    '''
    #number of galaxies
    if len(np.shape(data)) == 1:
        ngal = len(data)
    else:
        ngal = len(data[:, column])

    #if data are in physical units or not, use h
    if not physical_units:
        h = 1.0

    #if wgth is None then make weights based on the volume etc.
    if wgth == None:
        weight = np.zeros(ngal) + (1. / (nvols * (float(volume) / h) ** 3))
    else:
        weight = wgth

    #if log have been taken from the data or not
    if not log:
        if len(np.shape(data)) == 1:
            d = np.log10(data)
        else:
            d = np.log10(data[:, column])
        mmin = np.log10(mmin)
        mmax = np.log10(mmax)
    else:
        if len(np.shape(data)) == 1:
            d = data
        else:
            d = data[:, column]

    #bins
    dm = (mmax - mmin) / float(nbins)
    mbin = (np.arange(nbins) + 0.5) * dm + mmin

    if verbose:
        print '\nNumber of galaxies = %i' % ngal
        print 'min = %f, max = %f' % (mmin, mmax)
        print 'df =', dm
        print 'h =', h

    #mass function
    mf = np.zeros(nbins)
    nu = np.zeros(nbins)

    #find out bins
    ibin = np.floor((d - mmin) / dm)

    #make a mask of suitable bins
    mask = (ibin >= 0) & (ibin < nbins)

    #calculate the sum in each bin
    for i in range(nbins):
        mf[i] = np.sum(weight[ibin[mask] == i])
        nu[i] = len(ibin[ibin[mask] == i])

    if verbose:
        print 'Results:\n', mbin
        print mf / dm
        print nu
    return mbin, mf / dm, nu


def plot_number_counts(path, database, band, redshifts,
                       out_folder, obs_data,
                       area=2.1978021978021975,
                       ymin=10 ** 3, ymax=2 * 10 ** 6,
                       xmin=0.5, xmax=100,
                       nbins=15, sigma=3.0,
                       write_out=False):
    '''
    160 (arcminutes squared) = 0.0444444444 square degrees,
    thus, the weighting is 1/0.044444444 i.e. 22.5.

    :param sigma: sigma level of the errors to be plotted
    :param nbins: number of bins (for simulated data)
    :param area: actually 1 / area, used to weight galaxies
    '''

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
    fluxes = db.sqlite.get_data_sqlite(path, database, query) * 10 ** 3

    #weight each galaxy
    wghts = np.zeros(len(fluxes)) + area

    #make the figure
    fig = P.figure()
    fig.subplots_adjust(wspace=0.0, hspace=0.0,
                        left=0.09, bottom=0.03,
                        right=0.98, top=0.99)
    ax = P.subplot(rows, columns, 1)

    #calculate the differential number density
    #with log binning
    b, n, nu = diff_function(fluxes,
                             wgth=wghts,
                             mmax=xmax,
                             mmin=xmin,
                             nbins=nbins)
    #get the knots
    x = 10 ** b
    #chain rule swap to dN/dS
    #d/dS[ log_10(S)] = d/dS[ ln(S) / ln(10)]
    # = 1 / (S*ln(10))
    swap = 1. / (np.log(10) * x)
    #Euclidean-normalization S**2.5
    y = n * swap * (x ** 2.5)

    #plot the knots
    z0 = ax.plot(x, y, 'ko')

    #poisson error
    mask = nu > 0
    err = swap[mask] * (x[mask] ** 2.5) * area * np.sqrt(nu[mask]) * sigma
    up = y[mask] + err
    lw = y[mask] - err
    lw[lw < ymin] = ymin
    #    s0 = ax.fill_between(x[mask], up, lw, alpha = 0.2)
    s0 = ax.fill_between(x[mask], up, lw, color='#728FCE')

    #write to the file if needed, using appending so might get long...
    if write_out:
        fh = open(out_folder + 'outputTotal.txt', 'a')
        fh.write('#' + band + '\n')
        fh.write('#S[mjy]     dN/dSxS**2.5[deg**-2 mJy**1.5] high low\n')
        for aa, bb, cc, dd in zip(x[mask], y[mask], up, lw):
            fh.write('%e %e %e %e\n' % (aa, bb, cc, dd))
        fh.close()

    #add annotation
    ax.annotate('Total', (0.5, 0.9), xycoords='axes fraction',
                ha='center')

    #plot observational contrains
    if 'pacs100' in band:
        d = np.loadtxt(obs_data + 'BertaResults', comments='#', usecols=(0, 1, 2))
        b0 = ax.errorbar(d[:, 0], d[:, 1], yerr=d[:, 1] * d[:, 2], ls='None',
                         marker='*', mec='r', c='red')
        a = np.loadtxt(obs_data + 'Altieri100', comments='#', usecols=(0, 1, 2, 3))
        x = a[:, 0]
        y = a[:, 1]
        high = a[:, 2] - y
        low = np.abs(a[:, 3] - y)
        #yerr = [how much to take away from the y, how much to add to y]
        a0 = ax.errorbar(x, y, yerr=[low, high], c='green', marker='D',
                         ls='None', mec='green', lw=1.3, ms=3, mew=1.3)
    if 'pacs160' in band:
        d = np.loadtxt(obs_data + 'BertaResults', comments='#', usecols=(0, 3, 4))
        b0 = ax.errorbar(d[:, 0], d[:, 1], yerr=d[:, 1] * d[:, 2], ls='None',
                         marker='*', mec='r', c='red')
        a = np.loadtxt(obs_data + 'Altieri160', comments='#', usecols=(0, 1, 2, 3))
        x = a[:, 0]
        y = a[:, 1]
        high = a[:, 2] - y
        low = np.abs(a[:, 3] - y)
        a0 = ax.errorbar(x, y, yerr=[low, high], c='green', marker='D',
                         ls='None', mec='green', lw=1.3, ms=3, mew=1.3)
    if 'spire250' in band:
        #Glenn et al results
        d = np.loadtxt(obs_data + 'GlennResults250', comments='#', usecols=(0, 1, 2, 3))
        x = d[:, 0]
        y = 10 ** d[:, 1] * x ** 2.5 * 10 ** -3
        yp = 10 ** (d[:, 2] + d[:, 1]) * x ** 2.5 * 10 ** -3
        yl = 10 ** (d[:, 1] - d[:, 3]) * x ** 2.5 * 10 ** -3
        g0 = ax.errorbar(x, y, yerr=[y - yl, yp - y], ls='None',
                         marker='*', mec='r', c='red')
        #Clements et al results
        g = np.loadtxt(obs_data + 'Clements250', comments='#', usecols=(0, 5, 6))
        x = g[:, 0]
        y = g[:, 1] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        err = g[:, 2] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        c0 = ax.errorbar(x, y, yerr=[err, err], ls='None',
                         marker='D', mec='m', c='magenta',
                         lw=0.9, ms=3, mew=0.9)
    if 'spire350' in band:
        d = np.loadtxt(obs_data + 'GlennResults350', comments='#', usecols=(0, 1, 2, 3))
        x = d[:, 0]
        y = 10 ** d[:, 1] * x ** 2.5 * 10 ** -3
        yp = 10 ** (d[:, 2] + d[:, 1]) * x ** 2.5 * 10 ** -3
        yl = 10 ** (d[:, 1] - d[:, 3]) * x ** 2.5 * 10 ** -3
        g0 = ax.errorbar(x, y, yerr=[y - yl, yp - y], ls='None',
                         marker='*', mec='r', c='red')
        #Clements et al results
        g = np.loadtxt(obs_data + 'Clements350', comments='#', usecols=(0, 5, 6))
        x = g[:, 0]
        y = g[:, 1] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        err = g[:, 2] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        c0 = ax.errorbar(x, y, yerr=[err, err], ls='None',
                         marker='D', mec='m', c='magenta',
                         lw=0.9, ms=3, mew=0.9)
    if 'spire500' in band:
        d = np.loadtxt(obs_data + 'GlennResults500', comments='#', usecols=(0, 1, 2, 3))
        x = d[:, 0]
        y = 10 ** d[:, 1] * x ** 2.5 * 10 ** -3
        yp = 10 ** (d[:, 2] + d[:, 1]) * x ** 2.5 * 10 ** -3
        yl = 10 ** (d[:, 1] - d[:, 3]) * x ** 2.5 * 10 ** -3
        g0 = ax.errorbar(x, y, yerr=[y - yl, yp - y], ls='None',
                         marker='*', mec='r', c='red')
        #Clements et al results
        g = np.loadtxt(obs_data + 'Clements500', comments='#', usecols=(0, 5, 6))
        x = g[:, 0]
        y = g[:, 1] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        err = g[:, 2] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        c0 = ax.errorbar(x, y, yerr=[err, err], ls='None',
                         marker='D', mec='m', c='magenta',
                         lw=0.9, ms=3, mew=0.9)

    #set scale
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xticklabels([])

    #legend
    if 'pacs100' in band or 'pacs160' in band:
        p = P.Rectangle((0, 0), 1, 1, fc='#728FCE', alpha=0.2)
        sline = '%i$\sigma$ errors' % sigma
        P.legend((z0, p, b0[0], a0),
                 ('Our Model', sline, 'Berta et al. 2010', 'Altieri et al. 2010'),
                 'lower left')
    if 'spire' in band:
        p = P.Rectangle((0, 0), 1, 1, fc='#728FCE', alpha=0.2)
        sline = '%i$\sigma$ errors' % sigma
        P.legend((z0, p, g0[0], c0),
                 ('Our Model', sline, 'Glenn et al. 2010', 'Clements et al. 2010'),
                 'lower left')

    #redshift limited plots
    for i, red in enumerate(redshifts):
        #get data and convert to mJy
        query = '''select FIR.%s from FIR
                   where %s and FIR.%s < 10000 and FIR.%s > 1e-15''' % (band, red, band, band)
        fluxes = db.sqlite.get_data_sqlite(path, database, query) * 10 ** 3

        #modify redshift string
        tmp = red.split()
        rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])

        #weights
        wghts = np.zeros(len(fluxes)) + area

        #make a subplot
        axs = P.subplot(rows, columns, i + 2)

        #make a histogram
        b, n, nu = diff_function(fluxes,
                                 wgth=wghts,
                                 mmax=xmax,
                                 mmin=xmin,
                                 nbins=nbins)
        #knots in mjy, no log
        x = 10 ** b
        #chain rule swap
        #d/dS[ log_10(S)] = d/dS[ ln(S) / ln(10)]
        # = 1 / (S*ln(10))
        swap = 1. / (np.log(10) * x)
        #Euclidean normalization, S**2.5
        y = n * swap * (x ** 2.5)

        #plot the knots
        axs.plot(x, y, 'ko')

        #poisson error
        mask = nu > 0
        err = swap[mask] * (x[mask] ** 2.5) * area * np.sqrt(nu[mask]) * sigma
        up = y[mask] + err
        lw = y[mask] - err
        lw[lw < ymin] = ymin
        #        axs.fill_between(x[mask], up, lw, alpha = 0.2)
        axs.fill_between(x[mask], up, lw, color='#728FCE')


        #write to output
        if write_out:
            fh = open(out_folder + 'outputredshiftbin%i.txt' % i, 'a')
            fh.write('#' + band + ': ' + rtitle + '\n')
            fh.write('#S[mjy] dN/dS xS**2.5 [deg**-2 mJy**1.5] high low\n')
            for aa, bb, cc, dd in zip(x[mask], y[mask], up, lw):
                fh.write('%e %e %e %e\n' % (aa, bb, cc, dd))
            fh.close()

        #add annotation
        axs.annotate(rtitle, (0.5, 0.9), xycoords='axes fraction',
                     ha='center')

        #add observational constrains
        if 'pacs100' in band:
            fl = obs_data + 'data_100um_4_Sami_Niemi_20101126.txt'
            if i == 0:
                data = np.loadtxt(fl, usecols=(0, 1, 2, 3), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 1:
                data = np.loadtxt(fl, usecols=(0, 4, 5, 6), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 2:
                data = np.loadtxt(fl, usecols=(0, 7, 8, 9), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 3:
                data = np.loadtxt(fl, usecols=(0, 10, 11, 12), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
        if 'pacs160' in band:
            fl = obs_data + 'data_160um_4_Sami_Niemi_20101126.txt'
            if i == 0:
                data = np.loadtxt(fl, usecols=(0, 1, 2, 3), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 1:
                data = np.loadtxt(fl, usecols=(0, 4, 5, 6), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 2:
                data = np.loadtxt(fl, usecols=(0, 7, 8, 9), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 3:
                data = np.loadtxt(fl, usecols=(0, 10, 11, 12), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')

        #set scales
        axs.set_xscale('log')
        axs.set_yscale('log')
        axs.set_xlim(xmin, xmax)
        axs.set_ylim(ymin, ymax)

        #remove unnecessary ticks and add units
        if i % 2 == 0:
            axs.set_yticklabels([])
            axs.set_xticks(axs.get_xticks()[1:])
        if i == 2 or i == 3:
            axs.set_xlabel(r'$S_{%s} \ [\mathrm{mJy}]$' % wave)
        else:
            axs.set_xticklabels([])
        if i == 1:
            axs.set_ylabel(
                r'$\frac{\mathrm{d}N(S_{%s})}{\mathrm{d}S_{%s}} \times S_{%s}^{2.5} \quad [\mathrm{deg}^{-2} \ \mathrm{mJy}^{1.5}]$' % (
                wave, wave, wave))

    #save figure
    P.savefig(out_folder + 'numbercounts_%s.pdf' % band)
    P.close()


def plot_number_counts2(path, database, band, redshifts,
                        out_folder, obs_data, goods,
                        area=2.1978021978021975,
                        ymin=10 ** 3, ymax=2 * 10 ** 6,
                        xmin=0.5, xmax=100,
                        nbins=15, sigma=3.0,
                        write_out=False):
    '''
    160 (arcminutes squared) = 0.0444444444 square degrees,
    thus, the weighting is 1/0.044444444 i.e. 22.5.
    :param sigma: sigma level of the errors to be plotted
    :param nbins: number of bins (for simulated data)
    :param area: actually 1 / area, used to weight galaxies
    '''
    #fudge factor to handle errors that are way large
    fudge = ymin

    #The 10-5 square degrees number of rows in the plot
    columns = 2
    rows = 2

    try:
        wave = re.search('\d\d\d', band).group()
    except:
        #pacs 70 has only two digits
        wave = re.search('\d\d', band).group()

    #get data and convert to mJy
    query = '''select FIR.%s from FIR
               where FIR.%s < 10000 and FIR.%s > 1e-15''' % (band, band, band)
    fluxes = db.sqlite.get_data_sqlite(path, database, query) * 10 ** 3

    #weight each galaxy
    wghts = np.zeros(len(fluxes)) + area

    #make the figure
    fig = P.figure()
    fig.subplots_adjust(wspace=0.0, hspace=0.0,
                        left=0.09, bottom=0.03,
                        right=0.98, top=0.99)
    ax = P.subplot(rows, columns, 1)

    #calculate the differential number density
    #with log binning
    b, n, nu = diff_function(fluxes,
                             wgth=wghts,
                             mmax=xmax,
                             mmin=xmin,
                             nbins=nbins)
    #get the knots
    x = 10 ** b
    #chain rule swap to dN/dS
    #d/dS[ log_10(S)] = d/dS[ ln(S) / ln(10)]
    # = 1 / (S*ln(10))
    swap = 1. / (np.log(10) * x)
    #Euclidean-normalization S**2.5
    y = n * swap * (x ** 2.5)

    #plot the knots
    z0 = ax.plot(x, y, 'ko')

    #poisson error
    mask = nu > 0
    err = swap[mask] * (x[mask] ** 2.5) * area * np.sqrt(nu[mask]) * sigma
    up = y[mask] + err
    lw = y[mask] - err
    lw[lw < ymin] = ymin
    #    s0 = ax.fill_between(x[mask], up, lw, alpha = 0.2)
    s0 = ax.fill_between(x[mask], up, lw, color='#728FCE')

    #write to the file if needed, using appending so might get long...
    if write_out:
        fh = open(out_folder + 'outputTotal.txt', 'a')
        fh.write('#' + band + '\n')
        fh.write('#S[mjy]     dN/dSxS**2.5[deg**-2 mJy**1.5] high low\n')
        for aa, bb, cc, dd in zip(x[mask], y[mask], up, lw):
            fh.write('%e %e %e %e\n' % (aa, bb, cc, dd))
        fh.close()

    #add annotation
    ax.annotate('Total', (0.5, 0.9), xycoords='axes fraction',
                ha='center')

    #plot observational contrains
    if 'pacs100' in band:
        d = np.loadtxt(obs_data + 'BertaResults', comments='#', usecols=(0, 1, 2))
        b0 = ax.errorbar(d[:, 0], d[:, 1], yerr=d[:, 1] * d[:, 2], ls='None',
                         marker='*', mec='r', c='red')
        a = np.loadtxt(obs_data + 'Altieri100', comments='#', usecols=(0, 1, 2, 3))
        x = a[:, 0]
        y = a[:, 1]
        high = a[:, 2] - y
        low = np.abs(a[:, 3] - y)
        #yerr = [how much to take away from the y, how much to add to y]
        a0 = ax.errorbar(x, y, yerr=[low, high], c='green', marker='D',
                         ls='None', mec='green', lw=1.3, ms=3, mew=1.3)
    if 'pacs160' in band:
        d = np.loadtxt(obs_data + 'BertaResults', comments='#', usecols=(0, 3, 4))
        b0 = ax.errorbar(d[:, 0], d[:, 1], yerr=d[:, 1] * d[:, 2], ls='None',
                         marker='*', mec='r', c='red')
        a = np.loadtxt(obs_data + 'Altieri160', comments='#', usecols=(0, 1, 2, 3))
        x = a[:, 0]
        y = a[:, 1]
        high = a[:, 2] - y
        low = np.abs(a[:, 3] - y)
        a0 = ax.errorbar(x, y, yerr=[low, high], c='green', marker='D',
                         ls='None', mec='green', lw=1.3, ms=3, mew=1.3)
    if 'spire250' in band:
        #Glenn et al results
        d = np.loadtxt(obs_data + 'GlennResults250', comments='#', usecols=(0, 1, 2, 3))
        x = d[:, 0]
        y = 10 ** d[:, 1] * x ** 2.5 * 10 ** -3
        yp = 10 ** (d[:, 2] + d[:, 1]) * x ** 2.5 * 10 ** -3
        yl = 10 ** (d[:, 1] - d[:, 3]) * x ** 2.5 * 10 ** -3
        g0 = ax.errorbar(x, y, yerr=[y - yl, yp - y], ls='None',
                         marker='*', mec='r', c='red')
        #Clements et al results
        g = np.loadtxt(obs_data + 'Clements250', comments='#', usecols=(0, 5, 6))
        x = g[:, 0]
        y = g[:, 1] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        err = g[:, 2] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        c0 = ax.errorbar(x, y, yerr=[err, err], ls='None',
                         marker='D', mec='m', c='magenta',
                         lw=0.9, ms=3, mew=0.9)
    if 'spire350' in band:
        d = np.loadtxt(obs_data + 'GlennResults350', comments='#', usecols=(0, 1, 2, 3))
        x = d[:, 0]
        y = 10 ** d[:, 1] * x ** 2.5 * 10 ** -3
        yp = 10 ** (d[:, 2] + d[:, 1]) * x ** 2.5 * 10 ** -3
        yl = 10 ** (d[:, 1] - d[:, 3]) * x ** 2.5 * 10 ** -3
        g0 = ax.errorbar(x, y, yerr=[y - yl, yp - y], ls='None',
                         marker='*', mec='r', c='red')
        #Clements et al results
        g = np.loadtxt(obs_data + 'Clements350', comments='#', usecols=(0, 5, 6))
        x = g[:, 0]
        y = g[:, 1] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        err = g[:, 2] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        c0 = ax.errorbar(x, y, yerr=[err, err], ls='None',
                         marker='D', mec='m', c='magenta',
                         lw=0.9, ms=3, mew=0.9)
    if 'spire500' in band:
        d = np.loadtxt(obs_data + 'GlennResults500', comments='#', usecols=(0, 1, 2, 3))
        x = d[:, 0]
        y = 10 ** d[:, 1] * x ** 2.5 * 10 ** -3
        yp = 10 ** (d[:, 2] + d[:, 1]) * x ** 2.5 * 10 ** -3
        yl = 10 ** (d[:, 1] - d[:, 3]) * x ** 2.5 * 10 ** -3
        g0 = ax.errorbar(x, y, yerr=[y - yl, yp - y], ls='None',
                         marker='*', mec='r', c='red')
        #Clements et al results
        g = np.loadtxt(obs_data + 'Clements500', comments='#', usecols=(0, 5, 6))
        x = g[:, 0]
        y = g[:, 1] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        err = g[:, 2] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
        c0 = ax.errorbar(x, y, yerr=[err, err], ls='None',
                         marker='D', mec='m', c='magenta',
                         lw=0.9, ms=3, mew=0.9)

    #set scale
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xticklabels([])
    #legend
    if 'pacs100' in band or 'pacs160' in band:
        p = P.Rectangle((0, 0), 1, 1, fc='#728FCE', alpha=0.2)
        sline = '%i$\sigma$ errors' % sigma
        P.legend((z0, p, b0[0], a0),
                 ('Our Model', sline, 'Berta et al. 2010', 'Altieri et al. 2010'),
                 'lower left')
    if 'spire' in band:
        p = P.Rectangle((0, 0), 1, 1, fc='#728FCE', alpha=0.2)
        sline = '%i$\sigma$ errors' % sigma
        P.legend((z0, p, g0[0], c0),
                 ('Our Model', sline, 'Glenn et al. 2010', 'Clements et al. 2010'),
                 'lower left')

    #redshift limited plots
    for i, red in enumerate(redshifts):
        #get data and convert to mJy
        query = '''select FIR.%s from FIR
                   where %s and FIR.%s < 1e6 and FIR.%s > 1e-15''' % (band, red, band, band)
        fluxes = db.sqlite.get_data_sqlite(path, database, query) * 10 ** 3
        #modify redshift string
        tmp = red.split()
        rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])
        #weights
        wghts = np.zeros(len(fluxes)) + area
        #make a subplot
        axs = P.subplot(rows, columns, i + 2)
        #make a histogram
        b, n, nu = diff_function(fluxes,
                                 wgth=wghts,
                                 mmax=xmax,
                                 mmin=xmin,
                                 nbins=nbins)
        #knots in mjy, no log
        x = 10 ** b
        #chain rule swap
        #d/dS[ log_10(S)] = d/dS[ ln(S) / ln(10)]
        # = 1 / (S*ln(10))
        swap = 1. / (np.log(10) * x)
        #Euclidean normalization, S**2.5
        y = n * swap * (x ** 2.5)

        #plot the knots
        axs.plot(x, y, 'ko')

        #poisson error
        mask = nu > 0
        err = swap[mask] * (x[mask] ** 2.5) * area * np.sqrt(nu[mask]) * sigma
        up = y[mask] + err
        lw = y[mask] - err
        lw[lw < ymin] = ymin
        #        axs.fill_between(x[mask], up, lw, alpha = 0.2)
        axs.fill_between(x[mask], up, lw, color='#728FCE')

        #write to output
        if write_out:
            fh = open(out_folder + 'outputredshiftbin%i.txt' % i, 'a')
            fh.write('#' + band + ': ' + rtitle + '\n')
            fh.write('#S[mjy] dN/dS xS**2.5 [deg**-2 mJy**1.5] high low\n')
            for aa, bb, cc, dd in zip(x[mask], y[mask], up, lw):
                fh.write('%e %e %e %e\n' % (aa, bb, cc, dd))
            fh.close()
            #add annotation
        axs.annotate(rtitle, (0.5, 0.9), xycoords='axes fraction',
                     ha='center')

        #add observational constrains
        if 'pacs100' in band:
            fl = obs_data + 'data_100um_4_Sami_Niemi_20101126.txt'
            if i == 0:
                data = np.loadtxt(fl, usecols=(0, 1, 2, 3), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 1:
                data = np.loadtxt(fl, usecols=(0, 4, 5, 6), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 2:
                data = np.loadtxt(fl, usecols=(0, 7, 8, 9), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 3:
                data = np.loadtxt(fl, usecols=(0, 10, 11, 12), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
        if 'pacs160' in band:
            fl = obs_data + 'data_160um_4_Sami_Niemi_20101126.txt'
            if i == 0:
                data = np.loadtxt(fl, usecols=(0, 1, 2, 3), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 1:
                data = np.loadtxt(fl, usecols=(0, 4, 5, 6), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 2:
                data = np.loadtxt(fl, usecols=(0, 7, 8, 9), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
            if i == 3:
                data = np.loadtxt(fl, usecols=(0, 10, 11, 12), comments='#')
                x = 10 ** data[:, 0]
                y = 10 ** data[:, 1]
                up = y * data[:, 3]
                msk = data[:, 2] < -10.0
                data[:, 2][msk] = 0.999
                lw = y * data[:, 2]
                axs.errorbar(x, y, yerr=[lw, up], ls='None',
                             marker='*', mec='r', c='red')
        if 'spire250' in band and i == 2:
            #get the GOODS results
            obsGOODS = sex.se_catalog(goods)
            msk = obsGOODS.f250_mjy > -1
            print len(obsGOODS.f250_mjy[msk])
            wghtsGOODS = np.zeros(len(obsGOODS.f250_mjy)) + 22.5
            bGOODS, nGOODS, nuGOODS = diff_function(obsGOODS.f250_mjy[msk],
                                                    wgth=wghtsGOODS[msk],
                                                    mmax=40.0,
                                                    mmin=4.0,
                                                    nbins=5)
            xGOODS = 10 ** bGOODS
            swp = 1. / (np.log(10) * xGOODS)
            yGOODS = nGOODS * swp * (xGOODS ** 2.5)
            msk = nuGOODS > 0
            errGOODS = swp[msk] * (xGOODS[msk] ** 2.5) * 22.5 * np.sqrt(nuGOODS[msk]) * sigma
            upGOODS = yGOODS[msk] + errGOODS
            lwGOODS = yGOODS[msk] - errGOODS
            #plot GOODS
            print xGOODS, yGOODS
            gds = axs.errorbar(xGOODS, yGOODS, yerr=[lwGOODS, upGOODS],
                               ls='None', mec='black',
                               c='black', marker='D')


        #set scales
        axs.set_xscale('log')
        axs.set_yscale('log')
        axs.set_xlim(xmin, xmax)
        axs.set_ylim(ymin, ymax)
        #remove unnecessary ticks and add units
        if i == 0 or i == 2:
            axs.set_yticklabels([])
            #axs.set_xticks(axs.get_xticks()[1:])
        if i == 1 or i == 2:
            axs.set_xlabel(r'$S_{%s} \ [\mathrm{mJy}]$' % wave)
        else:
            axs.set_xticklabels([])
        if i == 1:
            axs.set_ylabel(
                r'$\frac{\mathrm{d}N(S_{%s})}{\mathrm{d}S_{%s}} \times S_{%s}^{2.5} \quad [\mathrm{deg}^{-2} \ \mathrm{mJy}^{1.5}]$' % (
                wave, wave, wave))
            axs.yaxis.set_label_coords(-0.11, 1.0)
        #save figure
    P.savefig(out_folder + 'numbercounts_%s.pdf' % band)
    P.close()

def plotTemplateComparison(band, redshifts,
                           ymin=10 ** 3, ymax=2 * 10 ** 6,
                           xmin=0.5, xmax=100,
                           nbins=15, sigma=3.0):
    hm = os.getenv('HOME')
    #constants
    path = [hm + '/Dropbox/Research/Herschel/runs/ce01/',
            hm + '/Dropbox/Research/Herschel/runs/cp11/',
            hm + '/Desktop/CANDELS/lightConeRuns/goodss/']
    dbs = ['sams.db',
           'sams.db',
           'goodss.db']
    out_folder = hm + '/Desktop/CANDELS/lightConeTesting/'
    ar = [2.25, #10 times goods
          2.25, #10 times goods
          2.1978021978021975] #simu

    #obs data
    obs_data = hm + '/Dropbox/Research/Herschel/obs_data/'

    #The 10-5 square degrees number of rows in the plot
    if 'pacs' in band:
        columns = 2
        rows = 3 #len(band) / columns
    else:
        columns = 2
        rows = 2

    try:
        wave = re.search('\d\d\d', band).group()
    except:
        #pacs 70 has only two digits
        wave = re.search('\d\d', band).group()

    #make the figure
    fig = P.figure()
    fig.subplots_adjust(wspace=0.0, hspace=0.0,
                        left=0.10, bottom=0.1,
                        right=0.97, top=0.98)
    ax = P.subplot(rows, columns, 1)

    #add annotation
    ax.annotate('Total', (0.25, 0.88),
                xycoords='axes fraction',
                ha='center')

    ttle = []
    sss = []
    #loop over the models
    for d, p, area, color in zip(dbs, path, ar, ['r', 'b', 'g']):
        print p
        #get data and convert to mJy
        query = '''select FIR.%s from FIR
                   where FIR.%s < 1e4 and FIR.%s > 1e-15''' % (band, band, band)
        fluxes = db.sqlite.get_data_sqlite(p, d, query) * 1e3

        #weight each galaxy
        wghts = np.zeros(len(fluxes)) + area

        #calculate the differential number density
        #with log binning
        b, n, nu = diff_function(fluxes,
                                 wgth=wghts,
                                 mmax=xmax,
                                 mmin=xmin,
                                 nbins=nbins)
        #get the knots
        x = 10 ** b
        #chain rule swap to dN/dS
        #d/dS[ log_10(S)] = d/dS[ ln(S) / ln(10)]
        # = 1 / (S*ln(10))
        swap = 1. / (np.log(10) * x)
        #Euclidean-normalization S**2.5
        y = n * swap * (x ** 2.5)

        #plot the knots
        z0 = ax.plot(x, y, color=color, ls='None', marker='o')

        #poisson error
        mask = nu > 0
        err = swap[mask] * (x[mask] ** 2.5) * area * np.sqrt(nu[mask]) * sigma
        up = y[mask] + err
        lw = y[mask] - err
        lw[lw < ymin] = ymin
        s0 = ax.fill_between(x[mask], up, lw, alpha=0.2,
                             color=color)

        #plot observational contrains
        if 'pacs100' in band:
            d = np.loadtxt(obs_data + 'BertaResults', comments='#', usecols=(0, 1, 2))
            b0 = ax.errorbar(d[:, 0], d[:, 1], yerr=d[:, 1] * d[:, 2], ls='None',
                             marker='*', mec='c', c='c')
            a = np.loadtxt(obs_data + 'Altieri100', comments='#', usecols=(0, 1, 2, 3))
            x = a[:, 0]
            y = a[:, 1]
            high = a[:, 2] - y
            low = np.abs(a[:, 3] - y)
            #yerr = [how much to take away from the y, how much to add to y]
            a0 = ax.errorbar(x, y, yerr=[low, high], c='m', marker='D',
                             ls='None', mec='m', lw=1.3, ms=3, mew=1.3)
        if 'pacs160' in band:
            d = np.loadtxt(obs_data + 'BertaResults', comments='#', usecols=(0, 3, 4))
            b0 = ax.errorbar(d[:, 0], d[:, 1], yerr=d[:, 1] * d[:, 2], ls='None',
                             marker='*', mec='c', c='c')
            a = np.loadtxt(obs_data + 'Altieri160', comments='#', usecols=(0, 1, 2, 3))
            x = a[:, 0]
            y = a[:, 1]
            high = a[:, 2] - y
            low = np.abs(a[:, 3] - y)
            a0 = ax.errorbar(x, y, yerr=[low, high], c='m', marker='D',
                             ls='None', mec='m', lw=1.3, ms=3, mew=1.3)
        if 'spire250' in band:
            #Glenn et al results
            d = np.loadtxt(obs_data + 'GlennResults250', comments='#', usecols=(0, 1, 2, 3))
            x = d[:, 0]
            y = 10 ** d[:, 1] * x ** 2.5 * 10 ** -3
            yp = 10 ** (d[:, 2] + d[:, 1]) * x ** 2.5 * 10 ** -3
            yl = 10 ** (d[:, 1] - d[:, 3]) * x ** 2.5 * 10 ** -3
            g0 = ax.errorbar(x, y, yerr=[y - yl, yp - y], ls='None',
                             marker='*', mec='c', c='c')
            #Clements et al results
            g = np.loadtxt(obs_data + 'Clements250', comments='#', usecols=(0, 5, 6))
            x = g[:, 0]
            y = g[:, 1] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
            err = g[:, 2] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
            c0 = ax.errorbar(x, y, yerr=[err, err], ls='None',
                             marker='D', mec='m', c='magenta',
                             lw=0.9, ms=3, mew=0.9)
        if 'spire350' in band:
            d = np.loadtxt(obs_data + 'GlennResults350', comments='#', usecols=(0, 1, 2, 3))
            x = d[:, 0]
            y = 10 ** d[:, 1] * x ** 2.5 * 10 ** -3
            yp = 10 ** (d[:, 2] + d[:, 1]) * x ** 2.5 * 10 ** -3
            yl = 10 ** (d[:, 1] - d[:, 3]) * x ** 2.5 * 10 ** -3
            g0 = ax.errorbar(x, y, yerr=[y - yl, yp - y], ls='None',
                             marker='*', mec='c', c='c')
            #Clements et al results
            g = np.loadtxt(obs_data + 'Clements350', comments='#', usecols=(0, 5, 6))
            x = g[:, 0]
            y = g[:, 1] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
            err = g[:, 2] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
            c0 = ax.errorbar(x, y, yerr=[err, err], ls='None',
                             marker='D', mec='m', c='magenta',
                             lw=0.9, ms=3, mew=0.9)
        if 'spire500' in band:
            d = np.loadtxt(obs_data + 'GlennResults500', comments='#', usecols=(0, 1, 2, 3))
            x = d[:, 0]
            y = 10 ** d[:, 1] * x ** 2.5 * 10 ** -3
            yp = 10 ** (d[:, 2] + d[:, 1]) * x ** 2.5 * 10 ** -3
            yl = 10 ** (d[:, 1] - d[:, 3]) * x ** 2.5 * 10 ** -3
            g0 = ax.errorbar(x, y, yerr=[y - yl, yp - y], ls='None',
                             marker='*', mec='c', c='c')
            #Clements et al results
            g = np.loadtxt(obs_data + 'Clements500', comments='#', usecols=(0, 5, 6))
            x = g[:, 0]
            y = g[:, 1] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
            err = g[:, 2] * (10 ** 3) ** 1.5 / (180 / np.pi) ** 2
            c0 = ax.errorbar(x, y, yerr=[err, err], ls='None',
                             marker='D', mec='m', c='magenta',
                             lw=0.9, ms=3, mew=0.9)

        #set scale
        ax.set_xscale('log')
        ax.set_yscale('log')
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        ax.set_xticklabels([])

        sss.append(P.Rectangle((0, 0), 1, 1, fc=color, alpha=0.2))
        #legend
        if 'ce01' in p:
            ttle.append('CE01')
        elif 'cp11' in p:
            ttle.append('CP11')
        else:
            ttle.append('R09')

        #redshift limited plots
        for i, red in enumerate(redshifts):
            #get data and convert to mJy
            query = '''select FIR.%s from FIR
                       where %s and FIR.%s < 1e6 and FIR.%s > 1e-10''' % (band, red, band, band)
            fluxes = db.sqlite.get_data_sqlite(p, d, query) * 1e3

            #modify redshift string
            tmp = red.split()
            rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])

            #weights
            wghts = np.zeros(len(fluxes)) + area

            #make a subplot
            axs = P.subplot(rows, columns, i + 2)

            #make a histogram
            b, n, nu = diff_function(fluxes,
                                     wgth=wghts,
                                     mmax=xmax,
                                     mmin=xmin,
                                     nbins=nbins)
            #knots in mjy, no log
            x = 10 ** b
            #chain rule swap
            #d/dS[ log_10(S)] = d/dS[ ln(S) / ln(10)]
            # = 1 / (S*ln(10))
            swap = 1. / (np.log(10) * x)
            #Euclidean normalization, S**2.5
            y = n * swap * (x ** 2.5)

            #plot the knots
            axs.plot(x, y, color=color, ls='None', marker='o')

            #poisson error
            mask = nu > 0
            err = swap[mask] * (x[mask] ** 2.5) * area * np.sqrt(nu[mask]) * sigma
            up = y[mask] + err
            lw = y[mask] - err
            lw[lw < ymin] = ymin
            axs.fill_between(x[mask], up, lw, alpha=0.2,
                             color=color)

            #add annotation
            axs.annotate(rtitle, (0.25, 0.88), xycoords='axes fraction',
                         ha='center')

            #add observational constrains
            if 'pacs100' in band:
                fl = obs_data + 'data_100um_4_Sami_Niemi_20101126.txt'
                if i == 0:
                    data = np.loadtxt(fl, usecols=(0, 1, 2, 3), comments='#')
                    x = 10 ** data[:, 0]
                    y = 10 ** data[:, 1]
                    up = y * data[:, 3]
                    msk = data[:, 2] < -10.0
                    data[:, 2][msk] = 0.999
                    lw = y * data[:, 2]
                    axs.errorbar(x, y, yerr=[lw, up], ls='None',
                                 marker='*', mec='c', c='c')
                if i == 1:
                    data = np.loadtxt(fl, usecols=(0, 4, 5, 6), comments='#')
                    x = 10 ** data[:, 0]
                    y = 10 ** data[:, 1]
                    up = y * data[:, 3]
                    msk = data[:, 2] < -10.0
                    data[:, 2][msk] = 0.999
                    lw = y * data[:, 2]
                    axs.errorbar(x, y, yerr=[lw, up], ls='None',
                                 marker='*', mec='c', c='c')
                if i == 2:
                    data = np.loadtxt(fl, usecols=(0, 7, 8, 9), comments='#')
                    x = 10 ** data[:, 0]
                    y = 10 ** data[:, 1]
                    up = y * data[:, 3]
                    msk = data[:, 2] < -10.0
                    data[:, 2][msk] = 0.999
                    lw = y * data[:, 2]
                    axs.errorbar(x, y, yerr=[lw, up], ls='None',
                                 marker='*', mec='c', c='c')
                if i == 3:
                    data = np.loadtxt(fl, usecols=(0, 10, 11, 12), comments='#')
                    x = 10 ** data[:, 0]
                    y = 10 ** data[:, 1]
                    up = y * data[:, 3]
                    msk = data[:, 2] < -10.0
                    data[:, 2][msk] = 0.999
                    lw = y * data[:, 2]
                    axs.errorbar(x, y, yerr=[lw, up], ls='None',
                                 marker='*', mec='c', c='c')

            if 'pacs160' in band:
                fl = obs_data + 'data_160um_4_Sami_Niemi_20101126.txt'
                if i == 0:
                    data = np.loadtxt(fl, usecols=(0, 1, 2, 3), comments='#')
                    x = 10 ** data[:, 0]
                    y = 10 ** data[:, 1]
                    up = y * data[:, 3]
                    msk = data[:, 2] < -10.0
                    data[:, 2][msk] = 0.999
                    lw = y * data[:, 2]
                    axs.errorbar(x, y, yerr=[lw, up], ls='None',
                                 marker='*', mec='c', c='c')
                if i == 1:
                    data = np.loadtxt(fl, usecols=(0, 4, 5, 6), comments='#')
                    x = 10 ** data[:, 0]
                    y = 10 ** data[:, 1]
                    up = y * data[:, 3]
                    msk = data[:, 2] < -10.0
                    data[:, 2][msk] = 0.999
                    lw = y * data[:, 2]
                    axs.errorbar(x, y, yerr=[lw, up], ls='None',
                                 marker='*', mec='c', c='c')
                if i == 2:
                    data = np.loadtxt(fl, usecols=(0, 7, 8, 9), comments='#')
                    x = 10 ** data[:, 0]
                    y = 10 ** data[:, 1]
                    up = y * data[:, 3]
                    msk = data[:, 2] < -10.0
                    data[:, 2][msk] = 0.999
                    lw = y * data[:, 2]
                    axs.errorbar(x, y, yerr=[lw, up], ls='None',
                                 marker='*', mec='c', c='c')
                if i == 3:
                    data = np.loadtxt(fl, usecols=(0, 10, 11, 12), comments='#')
                    x = 10 ** data[:, 0]
                    y = 10 ** data[:, 1]
                    up = y * data[:, 3]
                    msk = data[:, 2] < -10.0
                    data[:, 2][msk] = 0.999
                    lw = y * data[:, 2]
                    axs.errorbar(x, y, yerr=[lw, up], ls='None',
                                 marker='*', mec='c', c='c')

            #set scales
            axs.set_xscale('log')
            axs.set_yscale('log')
            axs.set_xlim(xmin, xmax)
            axs.set_ylim(ymin, ymax)

            if 'pacs' in band:
                #remove unnecessary ticks and add units
                if i % 2 == 0:
                    axs.set_yticklabels([])
                    axs.set_xticks(axs.get_xticks()[1:])
                if i == 2 or i == 3:
                    axs.set_xlabel(r'$S_{%s} \ [\mathrm{mJy}]$' % wave)
                else:
                    axs.set_xticklabels([])
                if i == 1:
                    axs.set_ylabel(
                        r'$\frac{\mathrm{d}N(S_{%s})}{\mathrm{d}S_{%s}} \times S_{%s}^{2.5} \quad [\mathrm{deg}^{-2} \ \mathrm{mJy}^{1.5}]$' % (
                        wave, wave, wave))

            if 'spire' in band:
                #remove unnecessary ticks and add units
                if i == 0 or i == 2:
                    axs.set_yticklabels([])
                    #axs.set_xticks(axs.get_xticks()[1:])
                if i == 1 or i == 2:
                    axs.set_xlabel(r'$S_{%s} \ [\mathrm{mJy}]$' % wave)
                else:
                    axs.set_xticklabels([])
                if i == 1:
                    axs.set_ylabel(
                        r'$\frac{\mathrm{d}N(S_{%s})}{\mathrm{d}S_{%s}} \times S_{%s}^{2.5} \quad [\mathrm{deg}^{-2} \ \mathrm{mJy}^{1.5}]$' % (
                        wave, wave, wave))
                    axs.yaxis.set_label_coords(-0.11, 1.0)

        if p == path[-1]:
            if 'pacs100' in band or 'pacs160' in band:
                sline = '%i$\sigma$ errors' % sigma
                P.legend((sss[0], sss[1], sss[2], b0[0], a0[0]), #, gds),
                         (ttle[0], ttle[1], ttle[2], 'Berta et al. 2010', 'Altieri et al. 2010'), #, 'GOODS-N'),
                         'upper right', shadow=True, fancybox=True, numpoints=1)
            if 'spire' in band:
                sline = '%i$\sigma$ errors' % sigma
                P.legend((sss[0], sss[1], sss[2], g0[0], c0[0]), #, gds),
                         (ttle[0], ttle[1], ttle[2], 'Glenn et al. 2010', 'Clements et al. 2010'), #, 'GOODS-N'),
                         'upper right', shadow=True, fancybox=True, numpoints=1)

    #save figure
    P.savefig(out_folder + 'numbercountComparison_%s.pdf' % band)
    P.close()


def plotNumberCounts(path, database, out_folder):
    area = 1. / (39./60*42./60.) # area of the simulation

    obs_data = os.getenv('HOME') + '/Dropbox/Research/Herschel/obs_data/'
    goods = hm + '/Dropbox/Research/Herschel/obs_data/goodsh_goodsn_allbands_z2-4.cat'

    #passbands to be plotted
    bands = ['pacs70_obs',
             'pacs100_obs',
             'pacs160_obs',
             'spire250_obs',
             'spire350_obs',
             'spire500_obs']

    #redshift ranges, 2 for SPIRE
    redshifts = ['FIR.z >= 0.0 and FIR.z <= 0.5',
                 'FIR.z > 0.5 and FIR.z <= 1.0',
                 'FIR.z > 1.0 and FIR.z <= 2.0',
                 'FIR.z > 2.0 and FIR.z <= 5.0']
    redshifts2 = ['FIR.z >= 0.0 and FIR.z <= 1.0',
                  'FIR.z > 1.0 and FIR.z <= 2.0',
                  'FIR.z > 2.0 and FIR.z <= 4.0']

    print 'Begin plotting'
    print 'Input DB: ', path + database
    print 'Output folder: ', out_folder

    #plot the number counts
    for bd in bands:
        if 'pacs' in bd:
            print 'plotting ', bd
            plot_number_counts(path, database, bd, redshifts,
                               out_folder, obs_data,
                               xmin=0.1, xmax=500,
                               ymin=1.5 * 10 ** 2, ymax=6 * 10 ** 5,
                               nbins=11, sigma=1.0, area=area)
            plotTemplateComparison(bd, redshifts,
                                   xmin=0.5, xmax=500,
                                   ymin=2e2, ymax=5 * 10 ** 5,
                                   nbins=11, sigma=1.0)
        if 'spire' in bd:
            print 'plotting ', bd
            plot_number_counts2(path, database, bd, redshifts2,
                                out_folder, obs_data, goods,
                                xmin=0.11, xmax=1800,
                                ymin=10 ** 2, ymax=3 * 10 ** 6,
                                nbins=11, sigma=1.0, area=area)
            plotTemplateComparison(bd, redshifts2,
                                   xmin=0.5, xmax=1800,
                                   ymin=7e2, ymax=8e5,
                                   nbins=11, sigma=1.0)
    print 'All done...'

if __name__ == '__main__':
    #find the home directory
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Desktop/CANDELS/lightConeRuns/goodss/'
    database = 'goodss.db'
    out_folder = hm + '/Desktop/CANDELS/lightConeTesting/'

    #call drivers
    #plotAllLuminosityFunctions(path, database, out_folder)
    #plotFluxRedshiftDistribution(path, database, out_folder)
    plotNumberCounts(path, database, out_folder)