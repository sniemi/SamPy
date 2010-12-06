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

def plot_size(query, xlabel, ylabel, output, out_folder,
              bulge = 0.4, title = '$2.0 < z < 4.0$',
              pmin = 0.05, pmax = 1.0,
              xbin = 15, ybin = 15,
              y1ticks = [1, 3, 5, 7, 10],
              y2ticks = [1, 3, 5, 7],
              xmin = 7.9, xmax = 11.7, ymin = 0.1, ymax = 10,
              scatters = False, mean = False):
    '''
    Plots size versus a given quantity.
    '''
    #get data
    data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

    #sphericals
    mask = data[:,2] > bulge
    xe = data[:,0][mask]
    ye = data[:,1][mask]
    # disks
    disks = data[:,2] <= bulge
    xd = data[:,0][disks]
    yd = data[:,1][disks]

    #hess
    sd, sdmin, sdmax = h.hess_plot(xd, yd, N.ones(len(xd)), 
                                   xmin, xmax, xbin, 
                                   ymin, ymax, ybin,
                                   pmax = pmax, pmin = pmin)
    se, semin, semax = h.hess_plot(xe, ye, N.ones(len(xe)), 
                                   xmin, xmax, xbin, 
                                   ymin, ymax, ybin,
                                   pmax = pmax, pmin = pmin)
    
    #figure
#    fig = P.figure(figsize = (12, 12))
    fig = P.figure()
    fig.suptitle(title)
    fig.subplots_adjust(wspace = 0.0, hspace = 0.01, left = 0.08, bottom = 0.07,
                        right = 0.97, top = 0.93)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    #contours
#    ax1.contourf(sd, origin = 'lower', colors = 'b', 
#                 linewidths = 0.8, linestyles = '-',
#                 extent = [xmin, xmax, ymin, ymax],
#                 rightside_up = True, alpha = 0.7)#,
#                 #levels = [0.01, 0.3, 0.6, 0.9])
#    ax2.contourf(se, origin = 'lower', colors = 'r', 
#                 linewidths = 0.8, linestyles = '-',
#                 extent = [xmin, xmax, ymin, ymax],
#                 rightside_up = True, alpha = 0.7)
    ims = ax1.imshow(sd, vmin = sdmin, vmax = sdmax,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin, xmax, ymin, ymax],
                     aspect = 'auto', alpha = 1)
    ims = ax2.imshow(se, vmin = semin, vmax = semax,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin, xmax, ymin, ymax],
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
                    marker = 'h', label = 'Late-type')
        ax2.scatter(xe, ye, c='r', s = 10,
                    marker = 'o', label = 'Early-type')

    #hlines
    if mean:
        #mean size
        mean_disk = N.mean(yd)
        mean_early = N.mean(ye)
        ax1.axhline(mean_disk, c = 'b', label = 'Mean')
        ax2.axhline(mean_early, c = 'r', label = 'Mean')

    #add text
    P.text(0.5, 0.95,'Late-type galaxies',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    P.text(0.5, 0.95,'Early-type galaxies',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax2.transAxes)


    #labels
    ax1.set_xlabel(xlabel)
    ax2.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax2.set_yticks([])

    #limits
    ax1.set_ylim(ymin, ymax)
    ax2.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin, xmax)
    ax2.set_xlim(xmin, xmax)

    #yticks
    ax1.set_yticks(y1ticks)
    ax2.set_yticks(y2ticks)

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
    out_folder = hm + '/Dropbox/Research/Herschel/plots/size/'
    db = 'sams.db'

#    query = '''select galprop.mstar, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
#                from FIR, galprop where
#                FIR.z > 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 5.0e-03 and
#                FIR.spire250_obs < 1e6
#                '''
#
#    plot_size(query, r'$\log(M_{\star}/M_{\odot})$', 
#              r'$R_{\textrm{disk}}$ \quad [kpc]', 'Size.ps',
#              out_folder, xmin = 9.9, xmax = 11.7)
#    print query

    query = '''select galprop.mstar, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
                from FIR, galprop where
                FIR.z > 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                galprop.tmerge > 0.5 and
                FIR.spire250_obs > 1e-9 and
                FIR.spire250_obs < 1e6
                '''
    plot_size(query, r'$\log(M_{\star}/M_{\odot})$', 
              r'$R_{\textrm{disk}}$ \quad [kpc]', 'Size2.ps',
              out_folder, xmin = 8.2, xmax = 11.3,
              pmin = 0.05, xbin = 15, ybin = 14)
    print query

#    query = '''select FIR.spire250_obs*1000, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
#                from FIR, galprop where
#                FIR.z > 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 1e-9 and
#                galprop.tmerge > 0.5
#                '''
#
#    plot_size(query, r'$S_{250}$ [mJy]', 
#              r'$R_{\textrm{disk}}$ \quad [kpc]', 'Size3.ps',
#              out_folder, xmin = 1e-3, xmax = 20)
#    print query

#    query = '''select galprop.mstar, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
#                from FIR, galprop where
#                FIR.z > 2.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                galprop.tmerge > 0.5 and
#                FIR.spire250_obs > 1e-9 and
#                FIR.spire250_obs < 1e7
#                '''
#    plot_size(query, r'$\log(M_{\star}/M_{\odot})$', 
#              r'$R_{\textrm{disk}}$ \quad [kpc]', 'Size4.ps',
#              out_folder, title = r'$z > 2$')
#    print query

#    query = '''select galprop.tmerge, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
#                from FIR, galprop where
#                FIR.z > 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 5.0e-03
#                '''
#
#    plot_size(query, r'$t_{\textrm{merge}} \quad$ [Gyr]', 
#              r'$R_{\textrm{disk}}$ \quad [kpc]', 'Tmerge.ps',
#              out_folder,
#              y1ticks = [1, 3, 5, 7, 10, 15, 20],
#              y2ticks = [1, 3, 5, 7, 10, 15],
#              xmin = 0, xmax = 2.7, ymin = 0, ymax = 20)
#    print query
