import matplotlib
matplotlib.use('PS')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.2)
matplotlib.rcParams['legend.fontsize'] = 14
matplotlib.rcParams['legend.handlelength'] = 5
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import pylab as P
import os
import numpy as N
from matplotlib import cm
#Sami's repository
import db.sqlite as sq
import astronomy.hess_plot as h
import astronomy.datamanipulation as dm

def plot_ages(query, xlabel, ylabel, output, out_folder,
              flux = 5, band = 250, title = '$2.0 < z < 4.0$',
              pmin = 0.05, pmax = 1.0,
              xbin = 10, ybin = 15,
              xmin = 7.9, xmax = 11.7, ymin = -1.5, ymax = 1.8,
              scatters = False, mean = False):
    '''
    Plots age versus a given quantity.
    '''
    #get data
    data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

    #observable galaxies
    mask = data[:,1] > flux
    xe = data[:,0][mask]
    ye = N.log10(data[:,1][mask])
    #all galaxies
    xd = data[:,0]
    yd = N.log10(data[:,1])
    mask = yd != N.nan
    xd = xd[mask]
    yd = yd[mask]

    #hess
    sd, sdmin, sdmax = h.hess_plot(xd, yd, N.ones(len(xd)), 
                                   xmin, xmax, xbin, 
                                   ymin, ymax, ybin,
                                   pmax = pmax, pmin = pmin)
    se, semin, semax = h.hess_plot(xe, ye, N.ones(len(xe)), 
                                   xmin, xmax, xbin, 
                                   N.log10(flux), ymax, ybin,
                                   pmax = pmax, pmin = pmin)
    
    #figure
    fig = P.figure()
    fig.suptitle(title)
    f, (ax1, ax2) = P.subplots(1, 2, sharey=True) 
    f.subplots_adjust(wspace = 0.0, hspace = 0.01, left = 0.08, bottom = 0.07,
                      right = 0.97, top = 0.93)

    #contours
    ims = ax1.imshow(sd, vmin = sdmin, vmax = sdmax,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin, xmax, ymin, ymax],
                     aspect = 'auto', alpha = 1)
    ims = ax2.imshow(se, vmin = semin, vmax = semax,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin, xmax, N.log10(flux), ymax],
                     aspect = 'auto', alpha = 1)

    #percentiles
    xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd, yd, xmin, xmax)
    md = (y50d > 0) & (y16d > 0) & (y84d > 0)
    xbin_mide, y50e, y16e, y84e = dm.percentile_bins(xe, ye, xmin, xmax)
    me = (y50e > 0) & (y16e > 0) & (y84e > 0)
    ax1.plot(xbin_midd[md], y50d[md], 'r-')
    ax1.plot(xbin_midd[md], y16d[md], 'r--')
    ax1.plot(xbin_midd[md], y84d[md], 'r--')
    ax2.plot(xbin_mide[me], y50e[me], 'r-')
    ax2.plot(xbin_mide[me], y16e[me], 'r--')
    ax2.plot(xbin_mide[me], y84e[me], 'r--')

    #dots
    if scatters:
        ax1.scatter(xd, yd, c='b', s = 10,
                    marker = 'h', label = 'All galaxies')
        ax2.scatter(xe, ye, c='r', s = 10,
                    marker = 'o', label = r'$S_{%i} > %.1f$ mJy' % (band, flux))

    #hlines
    if mean:
        #mean size
        mean_disk = N.mean(yd)
        mean_early = N.mean(ye)
        ax1.axhline(mean_disk, c = 'b', label = 'Mean')
        ax2.axhline(mean_early, c = 'r', label = 'Mean')

    #add text
    P.text(0.5, 0.95, 'All galaxies',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    P.text(0.5, 0.95, r'$S_{%i} > %.1f$ mJy' % (band, flux),
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax2.transAxes)


    #labels
    ax1.set_xlabel(xlabel)
    ax2.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    #ax2.set_yticks([])

    #limits
    #ax1.set_ylim(ymin, ymax)
    #ax2.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin, xmax)
    ax2.set_xlim(xmin, xmax)

    #yticks
    #ax1.set_yticks(y1ticks)
    #ax2.set_yticks(y2ticks)

    #make grid
    ax1.grid()
    ax2.grid()
    
    #write a legend
    ax1.legend(shadow = True, fancybox = True, 
               numpoints = 1, loc = 'upper left',
               scatterpoints = 1)
    ax2.legend(shadow = True, fancybox = True, 
               numpoints = 1, loc = 'upper left',
               scatterpoints = 1)
    P.savefig(out_folder + output)

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
#    path = hm + '/Dropbox/Research/Herschel/runs/test3/'
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/age/'
    db = 'sams.db'

    query = '''select galprop.tmerge, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.z > 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs > 1e-5 and
                galprop.tmerge > 0.0
                '''

    plot_ages(query, r'$t_{merge} \quad$ [Gyr]', 
              r'$log_{10}(S_{250}$ [mJy]$)$', 'Tmerge2.ps',
              out_folder, pmin = 0.01,
              xmin = 0.0, xmax = 2.5)
    print query
    
    query = '''select galprop.tmerge, FIR.pacs100_obs*1000
                from FIR, galprop where
                FIR.z > 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.pacs100_obs > 1e-5 and
                galprop.tmerge > 0.0
                '''

    plot_ages(query, r'$t_{merge} \quad$ [Gyr]', 
              r'$log_{10}(S_{100}$ [mJy]$)$', 'Tmerge3.ps',
              out_folder, pmin = 0.01, band = 100, flux = 1,
              xmin = 0.0, xmax = 2.5)
    print query
    
    query = '''select galprop.meanage, FIR.pacs100_obs*1000
                from FIR, galprop where
                FIR.z > 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.pacs100_obs > 1e-5
                '''

    plot_ages(query, r'Mean Age [Gyr]', 
              r'$log_{10}(S_{100} \quad$ [mJy])', 'Age.ps',
              out_folder, pmin = 0.01,
              xmin = 0.01, xmax = 1.0)
    print query