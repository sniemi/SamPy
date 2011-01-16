import matplotlib
matplotlib.use('PS')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.2)
matplotlib.rcParams['legend.fontsize'] = 12
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

def plot_tmerge(query1, query2,
                xlabel, ylabel,
                output, out_folder,
                pmin = 0.05, pmax = 1.0,
                xbin1 = 15, ybin1 = 15,
                xbin2 = 15, ybin2 = 15,
                y1ticks = [0, .4, .8, 1.2, 1.6, 2.0, 2.5, 3],
                y2ticks = [.4, .8, 1.2, 1.6, 2.0, 2.5],
                xmin1 = 7.9, xmax1 = 11.7, 
                xmin2 = 7.9, xmax2 = 11.7,
                ymin = 0.0, ymax = 3.0,
                scatters = False, mean = False):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query1)
    xd1 = data[:,0]
    yd1 = data[:,1]
    #get data, S_250 > 5 mJy
    data = sq.get_data_sqliteSMNfunctions(path, db, query2)
    xd2 = data[:,0]
    yd2 = data[:,1]

    #the fraction of no mergers?
    nm1 = len(yd1[yd1 < 0.0]) / float(len(yd1)) * 100.
    nm2 = len(yd2[yd2 < 0.0]) / float(len(yd2)) * 100.

    #print out some statistics
    print len(yd2)
    print 'Mean tmerge of all galaxies', N.mean(yd1[yd1 > 0.0])
    print 'Mean tmerge of SPIRE detected galaxies', N.mean(yd2[yd2 > 0.0])
    print
    print 'Max tmerge of all galaxies', N.max(yd1[yd1 > 0.0])
    print 'Max tmerge of SPIRE detected galaxies', N.max(yd2[yd2 > 0.0])
    print
    print 'Fraction of all galaxies that have experienced a merger', 100.-nm1 
    print 'Fraction of SPIRE that have experienced a merger', 100.-nm2

    #calculate 2D probability fields
    sd1, sdmin1, sdmax1 = h.hess_plot(xd1, yd1, N.ones(len(xd1)), 
                                      xmin1, xmax1, xbin1, 
                                      ymin, ymax, ybin1,
                                      pmax = pmax, pmin = pmin)
    sd2, sdmin2, sdmax2 = h.hess_plot(xd2, yd2, N.ones(len(xd2)), 
                                      xmin2, xmax2, xbin2, 
                                      ymin, ymax, ybin2,
                                      pmax = pmax, pmin = pmin)
        
    #make the figure
    fig = P.figure()
    fig.subplots_adjust(wspace = 0.0, hspace = 0.01, left = 0.08, bottom = 0.07,
                        right = 0.97, top = 0.93)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ims = ax1.imshow(sd1, vmin = sdmin1, vmax = sdmax1,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin1, xmax1, ymin, ymax],
                     aspect = 'auto', alpha = 1)
    ims = ax2.imshow(sd2, vmin = sdmin2, vmax = sdmax2,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin2, xmax2, ymin, ymax],
                     aspect = 'auto', alpha = 1)
    
    ax2.scatter(xd2, yd2, s = 7, marker = 'o',
                color = 'blue')

    #percentiles
    xbin_midd1, y50d1, y16d1, y84d1 = dm.percentile_bins(xd1,
                                                         yd1,
                                                         xmin1,
                                                         xmax1,
                                                         nxbins = xbin1)
    md1 = (y50d1 >= 0) & (y16d1 >= 0) & (y84d1 >= 0)
    xbin_midd2, y50d2, y16d2, y84d2 = dm.percentile_bins(xd2,
                                                         yd2,
                                                         xmin2,
                                                         xmax2,
                                                         nxbins = xbin2)
    md2 = (y50d2 >= 0) | (y16d2 >= 0) | (y84d2 >= 0)
    ax1.plot(xbin_midd1[md1], y50d1[md1], 'r-')
    ax1.plot(xbin_midd1[md1], y16d1[md1], 'r--')
    ax1.plot(xbin_midd1[md1], y84d1[md1], 'r--')
    ax2.plot(xbin_midd2[md2], y50d2[md2], 'r-')
    ax2.plot(xbin_midd2[md2], y16d2[md2], 'r--')
    ax2.plot(xbin_midd2[md2], y84d2[md2], 'r--')

    #add text
    P.text(0.5, 0.93,'All galaxies\n$2 \leq z < 4$',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    P.text(0.5, 0.96,'$S_{250} > 5$ mJy',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax2.transAxes)

    #labels
    ax1.set_xlabel(xlabel)
    ax2.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)

    #limits
    ax1.set_ylim(ymin, ymax)
    ax2.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin1, xmax1)
    ax2.set_xlim(xmin2, xmax2)

    #yticks
    ax2.set_yticks([])
    ax2.set_xticks(ax2.get_xticks()[1:])
    ax1.set_yticks(y1ticks)
    ax2.set_yticks(y2ticks)

    #make grid
    ax1.grid()
    ax2.grid()

    P.savefig(out_folder + output)

def plot_tmerge_bluest(query1, query2,
                        xlabel, ylabel,
                        output, out_folder,
                        pmin = 0.05, pmax = 1.0,
                        xbin1 = 15, ybin1 = 15,
                        xbin2 = 15, ybin2 = 15,
                        y1ticks = [0, .4, .8, 1.2, 1.6, 2.0],
                        y2ticks = [0.02,  0.04,  0.06,  0.08],
                        xmin1 = 7.9, xmax1 = 11.7, 
                        xmin2 = 7.9, xmax2 = 11.7,
                        ymin1 = 0.0, ymax1 = 2.0,
                        ymin2 = 0.0, ymax2 = 0.1,
                        scatters = False, mean = False):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query1)
    xd1 = data[:,0]
    yd1 = data[:,1]
    #get data, S_250 > 5 mJy
    data = sq.get_data_sqliteSMNfunctions(path, db, query2)
    xd2 = data[:,0]
    yd2 = data[:,1]

    #the fraction of no mergers?
    nm1 = len(yd1[yd1 < 0.0]) / float(len(yd1)) * 100.
    nm2 = len(yd2[yd2 < 0.0]) / float(len(yd2)) * 100.

    #print out some statistics
    print len(yd2)
    print 'Mean tmerge of all galaxies', N.mean(yd1[yd1 > 0.0])
    print 'Mean tmerge of SPIRE detected galaxies', N.mean(yd2[yd2 > 0.0])
    print
    print 'Max tmerge of all galaxies', N.max(yd1[yd1 > 0.0])
    print 'Max tmerge of SPIRE detected galaxies', N.max(yd2[yd2 > 0.0])
    print
    print 'Fraction of all galaxies that have experienced a merger', 100.-nm1 
    print 'Fraction of SPIRE that have experienced a merger', 100.-nm2

    #calculate 2D probability fields
    sd1, sdmin1, sdmax1 = h.hess_plot(xd1, yd1, N.ones(len(xd1)), 
                                      xmin1, xmax1, xbin1, 
                                      ymin1, ymax1, ybin1,
                                      pmax = pmax, pmin = pmin)
    sd2, sdmin2, sdmax2 = h.hess_plot(xd2, yd2, N.ones(len(xd2)), 
                                      xmin2, xmax2, xbin2, 
                                      ymin2, ymax2, ybin2,
                                      pmax = pmax, pmin = pmin)
        
    #make the figure
    fig = P.figure()
    fig.subplots_adjust(wspace = 0.15, hspace = 0.01, left = 0.08, bottom = 0.07,
                        right = 0.97, top = 0.93)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ims = ax1.imshow(sd1, vmin = sdmin1, vmax = sdmax1,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin1, xmax1, ymin1, ymax1],
                     aspect = 'auto', alpha = 1)
    ims = ax2.imshow(sd2, vmin = sdmin2, vmax = sdmax2,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin2, xmax2, ymin2, ymax2],
                     aspect = 'auto', alpha = 1)
    
    ax2.scatter(xd2, yd2, s = 7, marker = 'o',
                color = 'blue')

    #percentiles
    xbin_midd1, y50d1, y16d1, y84d1 = dm.percentile_bins(xd1,
                                                         yd1,
                                                         xmin1,
                                                         xmax1,
                                                         nxbins = xbin1)
    md1 = (y50d1 >= -10) & (y16d1 >= -10) & (y84d1 >= -10)
    xbin_midd2, y50d2, y16d2, y84d2 = dm.percentile_bins(xd2,
                                                         yd2,
                                                         -0.45,
                                                         0.4,
                                                         nxbins = 8)
#                                                        nxbins = xbin2)
    md2 = (y50d2 >= -10) | (y16d2 >= -10) | (y84d2 >= -10)
    ax1.plot(xbin_midd1[md1], y50d1[md1], 'r-')
    ax1.plot(xbin_midd1[md1], y16d1[md1], 'r--')
    ax1.plot(xbin_midd1[md1], y84d1[md1], 'r--')
    ax2.plot(xbin_midd2[md2], y50d2[md2], 'r-')
    ax2.plot(xbin_midd2[md2], y16d2[md2], 'r--')
    ax2.plot(xbin_midd2[md2], y84d2[md2], 'r--')

    #add text
    P.text(0.5, 0.93,'All galaxies\n$2 \leq z < 4$',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    P.text(0.5, 0.93,'$S_{250} > 5$ mJy\n$F775W - F850lp < -0.1$',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax2.transAxes)

    #labels
    ax1.set_xlabel(xlabel)
    ax2.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)

    #limits
    ax1.set_ylim(ymin1, ymax1)
    ax2.set_ylim(ymin2, ymax2)
    ax1.set_xlim(xmin1, xmax1)
    ax2.set_xlim(xmin2, xmax2)

    #yticks
    ax2.set_xticks(ax2.get_xticks()[1:])
    ax1.set_yticks(y1ticks)
    ax2.set_yticks(y2ticks)

    #make grid
    ax1.grid()
    ax2.grid()

    P.savefig(out_folder + output)

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/mergers/'
    db = 'sams.db'

#    query1 = '''select galprop.mstar, galprop.tmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 1e-18 and
#                FIR.spire250_obs < 1e6
#                '''
#    query2 = '''select galprop.mstar, galprop.tmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 5e-3 and
#                FIR.spire250_obs < 1e6
#                '''
#    plot_tmerge(query1, query2, r'$\log(M_{\star}/M_{\odot})$', 
#               '$T_{\mathrm{merge}}$ \quad [Gyr]', 'TmergeStellarMass.ps',
#                out_folder, xmin1 = 8.2, xmax1 = 11.8,
#                xmin2 = 10.1, xmax2 = 11.65,
#                pmin = 0.05,
#                xbin1 = 12, ybin1 = 10,
#                xbin2 = 10, ybin2 = 10)
#    
###############################
    query1 = '''select galprop.mcold - galprop.mstar, galprop.tmerge
                from FIR, galprop where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs > 1e-18 and
                FIR.spire250_obs < 1e6
                '''
    query2 = '''select galprop.mcold - galprop.mstar, galprop.tmerge
                from FIR, galprop where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs > 5e-3 and
                FIR.spire250_obs < 1e6
                '''
                
    xlab = r'$\log_{10} \left( \frac{M_{\star}}{M_{\mathrm{coldgas}}} \right )$'
    plot_tmerge(query1, query2, xlab, 
               '$T_{\mathrm{merge}} \quad [\mathrm{Gyr}]$', 'TmergeMassFraction.ps',
                out_folder,
                xmin1 = -6, xmax1 = 1.9,
                xmin2 = -0.9, xmax2 = .8,
                pmin = 0.05,
                xbin1 = 11, ybin1 = 10,
                xbin2 = 9, ybin2 = 9)
    
###############################
#    query1 = '''select galprop.mstardot, galprop.tmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 1e-18 and
#                FIR.spire250_obs < 1e6
#                '''
#    query2 = '''select galprop.mstardot, galprop.tmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 5e-3 and
#                FIR.spire250_obs < 1e6
#                '''
#                
#    xlab = r'$\dot{M}_{\star}$ [$M_{\odot}$ Gyr$^{-1}$]'
#    plot_tmerge(query1, query2, xlab, 
#               '$T_{\mathrm{merge}}$ \quad [Gyr]', 'TmergeSFR.ps',
#                out_folder,
#                xmin1 = 0., xmax1 = 1000.,
#                xmin2 = 0., xmax2 = 1000.,
#                pmin = 0.05,
#                xbin1 = 10, ybin1 = 10,
#                xbin2 = 9, ybin2 = 9)
#
###############################
#    query1 = '''select SSFR(galprop.mstardot, galprop.mstar), galprop.tmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 1e-18 and
#                FIR.spire250_obs < 1e6
#                '''
#    query2 = '''select SSFR(galprop.mstardot, galprop.mstar), galprop.tmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 5e-3 and
#                FIR.spire250_obs < 1e6
#                '''
#                
#    xlab = r'$\frac{\dot{M}_{\star}}{M_{\star}}$ [Gyr$^{-1}$]'
#    plot_tmerge(query1, query2, xlab, 
#               '$T_{\mathrm{merge}}$ \quad [Gyr]', 'TmergeSSFR.ps',
#                out_folder,
#                xmin1 = -10., xmax1 = -7,
#                xmin2 = -10, xmax2 = -7.5,
#                pmin = 0.05,
#                xbin1 = 10, ybin1 = 10,
#                xbin2 = 9, ybin2 = 9)
#
############
#    print '\nMoving to Major mergers...\n'
#    query1 = '''select galprop.mstar, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 1e-18 and
#                FIR.spire250_obs < 1e6
#                '''
#    query2 = '''select galprop.mstar, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 5e-3 and
#                FIR.spire250_obs < 1e6
#                '''
#    plot_tmerge(query1, query2, r'$\log(M_{\star}/M_{\odot})$', 
#               '$T_{\mathrm{majormerge}}$ \quad [Gyr]', 'TmajmergeStellarMass.ps',
#                out_folder, xmin1 = 8.2, xmax1 = 11.8,
#                xmin2 = 10.1, xmax2 = 11.65,
#                pmin = 0.05,
#                xbin1 = 10, ybin1 = 10,
#                xbin2 = 10, ybin2 = 10)
#    
###############################
#    query1 = '''select galprop.mcold - galprop.mstar, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 1e-18 and
#                FIR.spire250_obs < 1e6
#                '''
#    query2 = '''select galprop.mcold - galprop.mstar, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 5e-3 and
#                FIR.spire250_obs < 1e6
#                '''
#                
#    xlab = r'$\log_{10} \left( \frac{M_{\star}}{M_{\mathrm{coldgas}}} \right )$'
#    plot_tmerge(query1, query2, xlab, 
#               '$T_{\mathrm{majormerge}}$ \quad [Gyr]', 'TmajmergeMassFraction.ps',
#                out_folder,
#                xmin1 = -6, xmax1 = 1.5,
#                xmin2 = -0.9, xmax2 = 1.,
#                pmin = 0.05,
#                xbin1 = 10, ybin1 = 10,
#                xbin2 = 9, ybin2 = 9)
#    
###############################
#    query1 = '''select galprop.mstardot, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 1e-18 and
#                FIR.spire250_obs < 1e6
#                '''
#    query2 = '''select galprop.mstardot, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 5e-3 and
#                FIR.spire250_obs < 1e6
#                '''
#                
#    xlab = r'$\dot{M}_{\star}$ [$M_{\odot}$ Gyr$^{-1}$]'
#    plot_tmerge(query1, query2, xlab, 
#               '$T_{\mathrm{majormerge}}$ \quad [Gyr]', 'TmajmergeSFR.ps',
#                out_folder,
#                xmin1 = 0., xmax1 = 1000.,
#                xmin2 = 0., xmax2 = 1000.,
#                pmin = 0.05,
#                xbin1 = 10, ybin1 = 10,
#                xbin2 = 9, ybin2 = 9)
###############################
#    query1 = '''select SSFR(galprop.mstardot, galprop.mstar), galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 1e-18 and
#                FIR.spire250_obs < 1e6
#                '''
#    query2 = '''select SSFR(galprop.mstardot, galprop.mstar), galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 5e-3 and
#                FIR.spire250_obs < 1e6
#                '''
#                
#    xlab = r'$\frac{\dot{M}_{\star}}{M_{\star}}$ [Gyr$^{-1}$]'
#    plot_tmerge(query1, query2, xlab, 
#               '$T_{\mathrm{majormerge}}$ \quad [Gyr]', 'TmajmergeSSFR.ps',
#                out_folder,
#                xmin1 = -10., xmax1 = -7,
#                xmin2 = -10, xmax2 = -7.5,
#                pmin = 0.05,
#                xbin1 = 10, ybin1 = 10,
#                xbin2 = 9, ybin2 = 9)

##############################
#bluest galaxies
##############################
    print '\nMoving on to bluest galaxies\n'
    query1 = '''select galprop.mcold - galprop.mstar, galprop.tmerge
                from FIR, galprop where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs > 1e-18 and
                FIR.spire250_obs < 1e6
                '''
    query2 = '''select galprop.mcold - galprop.mstar, galprop.tmerge
                from FIR, galprop, galphot where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphot.gal_id and
                FIR.halo_id = galphot.halo_id and
                FIR.spire250_obs > 5e-3 and
                FIR.spire250_obs < 1e6 and
                galphot.f775w - galphot.f850lp < -0.1
                '''
                
    xlab = r'$\log_{10} \left( \frac{M_{\star}}{M_{\mathrm{coldgas}}} \right )$'
    plot_tmerge_bluest(query1, query2, xlab,
                       '$T_{\mathrm{merge}} \quad [\mathrm{Gyr}]$',
                       'TmergeBlueestMassFraction.ps',
                        out_folder,
                        xmin1 = -6, xmax1 = 1.5,
                        xmin2 = -0.6, xmax2 = .7,
                        pmin = 0.05,
                        xbin1 = 10, ybin1 = 10,
                        xbin2 = 8, ybin2 = 7)
##############################
#    query1 = '''select galprop.mcold - galprop.mstar, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 1e-18 and
#                FIR.spire250_obs < 1e6
#                '''
#    query2 = '''select galprop.mcold - galprop.mstar, galprop.tmajmerge
#                from FIR, galprop, galphot where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs > 5e-3 and
#                FIR.spire250_obs < 1e6 and
#                galphot.f775w - galphot.f850lp < -0.1
#                '''
#                
#    xlab = r'$\log_{10} \left( \frac{M_{\star}}{M_{\mathrm{coldgas}}} \right )$'
#    plot_tmerge_bluest(query1, query2, xlab,
#                       '$T_{\mathrm{majormerge}}$ \quad [Gyr]',
#                       'TmergeBlueestMassFractionMajor.ps',
#                        out_folder,
#                        xmin1 = -6, xmax1 = 1.5,
#                        xmin2 = -0.6, xmax2 = .7,
#                        pmin = 0.05,
#                        xbin1 = 10, ybin1 = 10,
#                        xbin2 = 8, ybin2 = 7)
##############################
#    query1 = '''select galprop.mcold - galprop.mstar, galprop.tmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 1e-18 and
#                FIR.spire250_obs < 1e6
#                '''
#    query2 = '''select galprop.mcold - galprop.mstar, galprop.tmerge
#                from FIR, galprop, galphot where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphot.f775w - galphot.f850lp < -0.16
#                '''
#                
#    xlab = r'$\log_{10} \left( \frac{M_{\star}}{M_{\mathrm{coldgas}}} \right )$'
#    plot_tmerge_bluest(query1, query2, xlab,
#                       '$T_{\mathrm{merge}}$ \quad [Gyr]',
#                       'TmergeBlueestMassFraction2.ps',
#                        out_folder,
#                        xmin1 = -6, xmax1 = 1.5,
#                        xmin2 = -0.6, xmax2 = .7,
#                        pmin = 0.05,
#                        xbin1 = 10, ybin1 = 10,
#                        xbin2 = 7, ybin2 = 7)
