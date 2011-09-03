'''
Plots stellar to dark matter halo mass ratios from Bolshoi and compares the results to Peter's curves.

:author: Sami-Matias Niemi
'''
import matplotlib

matplotlib.rc('text', usetex=True)
matplotlib.rcParams['font.size'] = 15
matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rcParams['legend.fontsize'] = 7
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
matplotlib.use('PDF')
from matplotlib.ticker import MultipleLocator, NullFormatter
import numpy as N
import pylab as P
import os, logging
import glob as g
#From Sami's Repo
import db.sqlite
import astronomy.datamanipulation as dm
import plot.tools as pt

def stellarHaloMFRatio(path, database, redshifts,
                       output_folder, outfile,
                       xmin=10.0, xmax=14.4,
                       ymin=-3, ymax=-1,
                       nbins=15, h=0.7):
    '''
    Plots stellar to dark matter halo mass ratios as a function of redshift.
    '''
    #get Behroozi et al. fits
    BFits = g.glob('/Users/niemi/Dropbox/Research/Observations/behroozi/results/*.dat')

    #get a colour scheme
    cols = pt.give_colours()

    #scale the SAM's output masses with this factor
    multiply = 1e9

    #make the figure and axes instance
    fig = P.figure()
    ax = fig.add_subplot(111)

    #plot the different redshifts
    for ii, redshift in enumerate(redshifts):
        #get redshift, add 0.1 so that int/floor returns the closest int
        tmp = redshift.split()
        rd = int(float(tmp[2]) + 0.1)

        #generate the SQL query
        query = '''select mstar_disk, mbulge, mhalo from galpropz where ''' + redshift
        query += ' and mstar_disk >= 0.0 and mbulge >= 0.0'
        query += ' and mstar_disk + mbulge > 0.0'
        query += ' and gal_id = 1'

        #load Behroozi et al fit data
        BF = N.loadtxt(BFits[ii + 1])
        ax.plot(BF[:, 0], # - N.log10(h),
                BF[:, 1],
                color=cols[ii],
                ls='--',
                label='Behroozi et al.: $z \sim %s$' % (BFits[ii + 1].split('z')[2][:4]))

        logging.debug(BFits[ii + 1])

        #get data from the SQLite3 db
        dat = db.sqlite.get_data_sqlite(path, database, query)

        #rename data and calculate the ratio
        mstar = dat[:, 0] + dat[:, 1]
        mhalo = dat[:, 2]
        ratio = N.log10(mstar / mhalo)
        mhalo = N.log10(mhalo * multiply)
        #print ratio, N.min(ratio), N.max(ratio)

        #debug output
        ngal = len(mstar)
        logging.debug('%i galaxies found at z = %i\n' % (ngal, rd))

        #bin the data
        xbin_mid, y50, y16, y84 = dm.percentile_bins(mhalo,
                                                     ratio,
                                                     xmin,
                                                     xmax,
                                                     nxbins=nbins)
        msk = y50 > -10
        #plot the binned data
        #        ax.errorbar(xbin_mid[msk],
        #                    y50[msk],
        #                    yerr = [y50[msk]-y16[msk], y84[msk]-y50[msk]],
        #                    color = cols[ii],
        #                    label = 'Bolshoi+SAM: $z \sim %i$' % rd)
        ax.plot(xbin_mid[msk],
                y50[msk],
                color=cols[ii],
                ms='o',
                ls='-',
                label='Bolshoi+SAM: $z \sim %i$' % rd)



    #set axes scales and labels
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel(r'$\log_{10} \left ( M_{\mathrm{dm}} \ [\mathrm{M}_{\odot}] \right )$')
    ax.set_ylabel(r'$\log_{10} \left (\frac{M_{\star}}{M_{\mathrm{dm}}} \right )$')
    #set small ticks
    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m / 5.)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m / 5.)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(output_folder + outfile + '.pdf')
    P.close()


def stellarHaloMFRatioMultiPanel(path, database, redshifts,
                                 output_folder, outfile,
                                 xmin=10.0, xmax=14.4,
                                 ymin=-3, ymax=-1,
                                 nbins=15):
    '''
    Plots stellar to dark matter halo mass ratios as a function of redshift.
    '''
    #get Behroozi et al. fits
    BFits = g.glob(hm + '/Dropbox/Research/Observations/behroozi/results/*.dat')

    #get a colour scheme
    cols = pt.give_colours()

    #scale the SAM's output masses with this factor
    multiply = 1e9

    #make the figure and axes instance
    fig = P.figure()
    P.subplots_adjust(left=0.13,
                      bottom=0.1,
                      wspace=0.0,
                      hspace=0.0)

    #plot the different redshifts
    for ii, redshift in enumerate(redshifts):
        #get redshift, add 0.1 so that int/floor returns the closest int
        tmp = redshift.split()
        rd = int(float(tmp[2]) + 0.1)

        #generate the SQL query
        query = '''select mstar_disk, mbulge, mhalo from galpropz where ''' + redshift
        query += ' and mstar_disk >= 0.0 and mbulge >= 0.0'
        query += ' and mstar_disk + mbulge > 0.0'
        query += ' and gal_id = 1'

        if ii < 6:
            ax = fig.add_subplot(2, 3, ii + 1)

        #get data from the SQLite3 db
        dat = db.sqlite.get_data_sqlite(path, database, query)

        #rename data and calculate the ratio
        mstar = dat[:, 0] + dat[:, 1]
        mhalo = dat[:, 2]
        ratio = N.log10(mstar / mhalo)
        mhalo = N.log10(mhalo * multiply)
        #print ratio, N.min(ratio), N.max(ratio)

        #debug output
        ngal = len(mstar)
        logging.debug('%i galaxies found at z = %i\n' % (ngal, rd))

        #bin the data
        xbin_mid, y50, y16, y84 = dm.percentile_bins(mhalo,
                                                     ratio,
                                                     xmin,
                                                     xmax,
                                                     nxbins=nbins)
        msk = y50 > -10
        #plot the binned data
        if ii == 6:
            ax.plot(xbin_mid[msk],
                    y50[msk],
                    'k--',
                    label='Bolshoi+SAM')
        else:
            ax.errorbar(xbin_mid[msk],
                        y50[msk],
                        yerr=[y50[msk] - y16[msk], y84[msk] - y50[msk]],
                        color='k',
                        label='Bolshoi+SAM')

        #load Behroozi et al fit data
        BF = N.loadtxt(BFits[ii + 1])
        #plot Behroozi data
        if ii == 6:
            ax.plot(BF[:, 0],
                    BF[:, 1],
                    color='r',
                    ls='--',
                    label='Behroozi et al.')
        else:
            ax.plot(BF[:, 0],
                    BF[:, 1],
                    color='r',
                    ls='-',
                    label='Behroozi et al.')

        #output some information
        logging.debug(BFits[ii + 1])

        #mark the redshift
        if ii < 5:
            P.text(0.5, 0.93,
                   r'$ z \sim %.1f $' % (rd),
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   fontsize=12)
        elif ii == 5:
            P.text(0.5, 0.93,
                   r'$z \sim %.1f (s)\ \& \ %.1f (d)$' % (rd, rd + 1),
                   horizontalalignment='center',
                   verticalalignment='center',
                   transform=ax.transAxes,
                   fontsize=12)

        #set axes scales and labels
        ax.set_xlim(xmin - 0.1, xmax)
        ax.set_ylim(ymin, ymax)

        #set small ticks
        m = ax.get_yticks()[1] - ax.get_yticks()[0]
        yminorLocator = MultipleLocator(m / 5.)
        yminorFormattor = NullFormatter()
        ax.yaxis.set_minor_locator(yminorLocator)
        ax.yaxis.set_minor_formatter(yminorFormattor)
        m = ax.get_xticks()[1] - ax.get_xticks()[0]
        xminorLocator = MultipleLocator(m / 5.)
        xminorFormattor = NullFormatter()
        ax.xaxis.set_minor_locator(xminorLocator)
        ax.xaxis.set_minor_formatter(xminorFormattor)

        #set legend
        if ii == 4:
            ax.legend(shadow=True,
                      fancybox=True,
                      numpoints=1,
                      loc='lower right')

        #set ylabel
        if ii == 0 or ii == 3:
            ax.set_ylabel(r'$\log_{10} \left (\frac{M_{\star}}{M_{\mathrm{dm}}} \right )$')

        #set xlabel
        if ii == 4: # or ii == 3 or ii == 5:
            ax.set_xlabel(r'$\log_{10} \left ( M_{\mathrm{dm}} \ [\mathrm{M}_{\odot}] \right )$')

        #remove some y ticks
        if ii == 0 or ii == 3:
            ax.set_yticks(ax.get_yticks()[:-1])
        else:
            ax.set_yticklabels([])

        #remove some x ticks
        if ii == 3 or ii == 4 or ii == 5:
            #ax.set_xticks(ax.get_xticks()[:-1])
            continue
        elif ii == 6:
            continue
        else:
            ax.set_xticklabels([])

    P.savefig(output_folder + outfile + 'Multi.pdf')
    P.close()


def main(redshifts, path, database, output_folder, outfile):
    '''
    Driver function, call this with a path to the data,
    and label you wish to use for the files.
    '''
    #    stellarHaloMFRatio(path,
    #                       database,
    #                       redshifts,
    #                       output_folder,
    #                       outfile)

    stellarHaloMFRatioMultiPanel(path,
                                 database,
                                 redshifts,
                                 output_folder,
                                 outfile)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #path1 = hm + '/Dropbox/Research/Bolshoi/run/trial2/'
    path2 = hm + '/Desktop/Research/run/newtree1/'
    database = 'sams.db'
    outpath = hm + '/Dropbox/Research/Bolshoi/MassRatioPlots/'

    logging.debug('Making the first plot')
    redshifts1 = ['galpropz.zgal > 0.9 and galpropz.zgal <= 1.1',
                  'galpropz.zgal > 1.9 and galpropz.zgal <= 2.1',
                  'galpropz.zgal > 2.9 and galpropz.zgal <= 3.1',
                  'galpropz.zgal > 3.9 and galpropz.zgal <= 4.1',
                  'galpropz.zgal > 4.9 and galpropz.zgal <= 5.1',
                  'galpropz.zgal > 5.9 and galpropz.zgal <= 6.1',
                  'galpropz.zgal > 6.9 and galpropz.zgal <= 7.1']
    #    redshifts2 = ['galpropz.zgal > 0.9 and galpropz.zgal <= 1.1',
    #                  'galpropz.zgal > 1.9 and galpropz.zgal <= 2.1',
    #                  'galpropz.zgal > 2.9 and galpropz.zgal <= 3.1',
    #                  'galpropz.zgal > 3.9 and galpropz.zgal <= 4.1',
    #                  'galpropz.zgal > 4.9 and galpropz.zgal <= 5.2']

    #main(redshifts1, path1, database, outpath, 'RatioMFs1')
    main(redshifts1, path2, database, outpath, 'RatioMFsNew')

#    logging.debug('Making the second plot')
#    redshifts = ['galpropz.zgal >= 0.9 and galpropz.zgal <= 1.3',
#                 'galpropz.zgal >= 1.9 and galpropz.zgal <= 2.5',
#                 'galpropz.zgal >= 2.9 and galpropz.zgal <= 3.5',
#                 'galpropz.zgal >= 3.5 and galpropz.zgal <= 4.1']
#    main(redshifts, path, database, outpath, 'stellarmf2')
