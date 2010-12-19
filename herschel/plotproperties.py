import matplotlib
matplotlib.use('PSs')
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

def plot_properties(query, xlabel, ylabel, output, out_folder,
                    flux = 5, band = 250,
                    pmin = 0.1, pmax = 1.0,
                    xbin = 15, ybin = 11,
                    xmin = 7.9, xmax = 11.7,
                    ymin = 0, ymax = 50):
    '''
    Plots 
    '''
    
    #get data
    data = sq.get_data_sqlitePowerTen(path, db, query)

    #set 1: all galaxies
    xd = data[:,0]
    yd = data[:,1]

    #set 2
    mask = data[:,1] > flux
    xe = data[:,0][mask]
    ye = data[:,1][mask]
    #x limits for the right hand (scatter) plot
    secxmin, secxmax = 0.99*N.min(xe), 1.005*N.max(xe)
    if 'mstardot' in query:
        secxmax = 1200.
    if 'burst' in query:
        secxmax = 1500.

    #hess
    sd, sdmin, sdmax = h.hess_plot(xd, yd, N.ones(len(xd)), 
                                   xmin, xmax, xbin, 
                                   ymin, ymax, ybin,
                                   pmax = pmax, pmin = pmin)
    se, semin, semax = h.hess_plot(xe, ye, N.ones(len(xe)), 
                                   secxmin, secxmax, xbin-4, 
                                   flux, ymax, ybin-1,
                                   pmax = pmax, pmin = pmin)
    
    #figure
#    f, (ax1, ax2) = P.subplots(1, 2, sharey=True) 
    f, (ax1, ax2) = P.subplots(1, 2, figsize=(10,10)) 
    f.subplots_adjust(wspace = 0.0, hspace = 0.01, left = 0.08, bottom = 0.07,
                      right = 0.97, top = 0.93)

    #hess plots
    ims = ax1.imshow(sd, vmin = sdmin, vmax = sdmax,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin, xmax, ymin, ymax],
                     aspect = 'auto', alpha = 1)
    ims = ax2.imshow(se, vmin = semin, vmax = semax,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [secxmin, secxmax, flux, ymax],
                     aspect = 'auto', alpha = 1)
    #flux limit lines
    ax1.axhline(flux, color = 'green', ls = '--')
    ax2.axhline(flux, color = 'green', ls = '--')
    #scatter to the second plot
    ax2.scatter(xe, ye, s = 6, color = 'b')
    #percentiles
    xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd, yd,
                                                     xmin, xmax)
    md = (y50d > 0) | (y16d > 0) | (y84d > 0)
    xbin_mide, y50e, y16e, y84e = dm.percentile_bins(xe, ye,
                                                     secxmin, secxmax)
    me = (y50e > 0) | (y16e > 0) | (y84e > 0)
    ax1.plot(xbin_midd[md], y50d[md], 'r-')
    ax1.plot(xbin_midd[md], y16d[md], 'r--')
    ax1.plot(xbin_midd[md], y84d[md], 'r--')
    ax2.plot(xbin_mide[me], y50e[me], 'r-')
    ax2.plot(xbin_mide[me], y16e[me], 'r--')
    ax2.plot(xbin_mide[me], y84e[me], 'r--')
    

    #add text
    P.text(0.5, 0.95, 'All galaxies',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    P.text(0.5, 0.95, r'%s > %.1f $ mJy' % (ylabel.split()[0], flux),
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax2.transAxes)


    #labels
    ax1.set_xlabel(xlabel)
    ax2.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    #y tick positions
#    ax1.set_yticks(yticks)
    #ax2.set_yticks(yticks[1:-2])

    #limits
    ax1.set_xlim(xmin, xmax)
    ax2.set_xlim(secxmin, secxmax)

    ax1.set_ylim(ymin, ymax)
    ax2.set_ylim(ymin, ymax)

    ax2.set_yticks(ax2.get_yticks()[1:-1])
#    ax2.set_xticks(ax2.get_xticks()[1:])
    
    #make grid
    ax1.grid()
    ax2.grid()

    P.savefig(out_folder + output)

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
#    path = hm + '/Dropbox/Research/Herschel/runs/test3/'
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/props/'
    db = 'sams.db'

    query = '''select galprop.mstar, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs < 1e5 and
                FIR.z >= 2 and FIR.z < 4
                '''
    plot_properties(query, r'$\log_{10}(M_{\star} / M_{\odot})$', 
                    r'$S_{250} \quad [$mJy$]$', 'mstar.ps',
                    out_folder, pmin = 0.05,
                    xmin = 8.7, xmax = 11.7,
                    ymin = 0.01, ymax = 45)
    print query

    query = '''select galprop.mcold, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs < 1e5 and
                FIR.z >= 2 and FIR.z < 4
                '''
    plot_properties(query, r'$\log_{10}(M_{coldgas} / M_{\odot})$', 
                    r'$S_{250} \quad [$mJy$]$', 'gasmass.ps',
                    out_folder, pmin = 0.05,
                    xmin = 8.5, xmax = 11.8,
                    ymin = 0.001, ymax = 40)
    print query

    query = '''select galprop.mcold - galprop.mstar, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs < 1e5 and
                FIR.z >= 2 and FIR.z < 4
                '''
    plot_properties(query, r'$\log_{10} \left ( \frac{M_{coldgas} / M_{\odot}}{M_{\star} / M_{\odot}} \right )$', 
                    r'$S_{250} \quad [$mJy$]$', 'massratio.ps',
                    out_folder, pmin = 0.05,
                    xmin = -1.5, xmax = 1.5,
                    ymin = 0.001, ymax = 45)
    print query

    query = '''select galprop.mstardot, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs < 1e5 and
                FIR.z >= 2 and FIR.z < 4
                '''
    plot_properties(query, r'$\dot{M_{\star}} \quad [\frac{M_{\odot}}{yr}]$', 
                    r'$S_{250} \quad [$mJy$]$', 'sfr.ps',
                    out_folder, pmin = 0.05,
                    xmin = 0, xmax = 380, xbin = 12,
                    ymin = 0.001, ymax = 45)
    print query    

    query = '''select galprop.sfr_burst, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs < 1e5 and
                FIR.z >= 2 and FIR.z < 4
                '''
    plot_properties(query, r'$\dot{M}_{burst} \quad [\frac{M_{\odot}}{yr}]$', 
                    r'$S_{250} \quad [$mJy$]$', 'sfrburst.ps',
                    out_folder, pmin = 0.05,
                    xmin = 0, xmax = 260,
                    ymin = 0.001, ymax = 45)
    print query 

#PACS 160

    query = '''select galprop.mstar, FIR.pacs160_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.pacs160_obs < 1e5 and
                FIR.z >= 2 and FIR.z < 4
                '''
    plot_properties(query, r'$\log_{10}(M_{\star} / M_{\odot})$', 
                    r'$S_{160} \quad [$mJy$]$', 'mstar2.ps',
                    out_folder, pmin = 0.05,
                    xmin = 9.6, xmax = 11.8,
                    ymin = 0.001, ymax = 45, flux = 4.5)
    print query

    query = '''select galprop.mcold, FIR.pacs160_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.pacs160_obs < 1e5 and
                FIR.z >= 2 and FIR.z < 4
                '''
    plot_properties(query, r'$\log_{10}(M_{coldgas} / M_{\odot})$', 
                    r'$S_{160} \quad [$mJy$]$', 'gasmass2.ps',
                    out_folder, pmin = 0.05,
                    xmin = 8.3, xmax = 11.8,
                    ymin = 0.001, ymax = 45, flux = 4.5)
    print query

    query = '''select galprop.mcold - galprop.mstar, FIR.pacs160_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.pacs160_obs < 1e5 and
                FIR.z >= 2 and FIR.z < 4
                '''
    plot_properties(query, r'$\log_{10} \left ( \frac{M_{coldgas} / M_{\odot}}{M_{\star} / M_{\odot}} \right )$', 
                    r'$S_{160} \quad [$mJy$]$', 'massratio2.ps',
                    out_folder, pmin = 0.05,
                    xmin = -5, xmax = 1,
                    ymin = 0.001, ymax = 45, flux = 4.5)
    print query

    query = '''select galprop.mstardot, FIR.pacs160_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.pacs160_obs < 1e5 and
                FIR.z >= 2 and FIR.z < 4
                '''
    plot_properties(query, r'$\dot{M_{\star}} \quad [\frac{M_{\odot}}{yr}]$', 
                    r'$S_{160} \quad [$mJy$]$', 'sfr2.ps',
                    out_folder, pmin = 0.05,
                    xmin = 0, xmax = 380, xbin = 10,
                    ymin = 0.001, ymax = 45, flux = 4.5)
    print query    

    query = '''select galprop.sfr_burst, FIR.pacs160_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.pacs160_obs < 1e5 and
                FIR.z >= 2 and FIR.z < 4
                '''
    plot_properties(query, r'$\dot{M}_{burst} \quad [\frac{M_{\odot}}{yr}]$', 
                    r'$S_{250} \quad [$mJy$]$', 'sfrburst.ps',
                    out_folder, pmin = 0.05,
                    xmin = 0, xmax = 260,
                    ymin = 0.001, ymax = 45, flux = 5.0)
    print query 
