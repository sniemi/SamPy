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
import sandbox.MyTools as M

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
    data = sq.get_data_sqlitePowerTen(path, db, query)

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

def plot_size2(query, xlabel, ylabel, output, out_folder,
               bulge = 0.4, title = '$2.0 < z < 4.0$',
               pmin = 0.05, pmax = 1.0,
               xbin = 15, ybin = 15,
               xmin = 7.9, xmax = 11.7, ymin = 0.1, ymax = 10):
    '''
    Plots size versus a given quantity.
    '''
    #get data
    data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

    # disks
    disks = data[:,2] <= bulge
    xd = data[:,0][disks]
    yd = data[:,1][disks]

    #hess
    sd, sdmin, sdmax = h.hess_plot(xd, yd, N.ones(len(xd)), 
                                   xmin, xmax, xbin, 
                                   ymin, ymax, ybin,
                                   pmax = pmax, pmin = pmin)

    #figure
    fig = P.figure()
    fig.suptitle(title)
    ax1 = fig.add_subplot(111)


    ims = ax1.imshow(sd, vmin = sdmin, vmax = sdmax,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin, xmax, ymin, ymax],
                     aspect = 'auto', alpha = 1)

    #percentiles
    xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd, yd, xmin, xmax)
    md = (y50d > 0) & (y16d > 0) & (y84d > 0)
    ax1.plot(xbin_midd[md], y50d[md], 'r-')
    ax1.plot(xbin_midd[md], y16d[md], 'r--')
    ax1.plot(xbin_midd[md], y84d[md], 'r--')

    #add text
    P.text(0.5, 0.95,'Late-type galaxies',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)

    #labels
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)

    #limits
    ax1.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin, xmax)

    #yticks
    #ax1.set_yticks(y1ticks)

    #make grid
    ax1.grid()
    
    #write a legend
    ax1.legend(shadow = True, fancybox = True, 
               numpoints = 1, loc = 'upper left',
               scatterpoints = 1)
    P.savefig(out_folder + output)

def plot_size_paper(xd1, xd2, yd1, yd2,
                    xlabel, ylabel, output, out_folder,
                    pmin = 0.05, pmax = 1.0,
                    xbin1 = 15, ybin1 = 15,
                    xbin2 = 15, ybin2 = 15,
                    y1ticks = [1, 3, 5, 7, 9, 12],
                    y2ticks = [1, 3, 5, 7, 9],
                    xmin1 = 7.9, xmax1 = 11.7, 
                    xmin2 = 7.9, xmax2 = 11.7,
                    ymin = 0.1, ymax = 12,
                    scatters = False, mean = False):

    #calculate hess
    sd1, sdmin1, sdmax1 = h.hess_plot(xd1, yd1, N.ones(len(xd1)), 
                                      xmin1, xmax1, xbin1, 
                                      ymin, ymax, ybin1,
                                      pmax = pmax, pmin = pmin)
    sd2, sdmin2, sdmax2 = h.hess_plot(xd2, yd2, N.ones(len(xd2)), 
                                      xmin2, xmax2, xbin2, 
                                      ymin, ymax, ybin2,
                                      pmax = pmax, pmin = pmin)
    
    #load obs data
    file = os.getenv('HOME') + '/Dropbox/Research/Herschel/obs_data/CavaSizesValues.txt'
    data = N.loadtxt(file, comments = '#', usecols = (0,1))
    
    #figure
    fig = P.figure()
    #fig.suptitle('Late-type Galaxies')
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
    
    ax2.scatter(xd2, yd2, s = 1, marker = 'o', color = 'blue',
                label = '$S_{250} > 5$ mJy')

    ax1.scatter(data[:,0], data[:,1], s = 45, marker = 's',
                color = 'green')    
    ax2.scatter(data[:,0], data[:,1], s = 45, marker = 's',
                color = 'green', label = 'Cava et al 2010')

    #percentiles
    xbin_midd1, y50d1, y16d1, y84d1 = dm.percentile_bins(xd1, yd1,
                                                         xmin1, xmax1,
                                                         nxbins = 2*xbin1,
                                                         limit = 25)
    md1 = (y50d1 > 0) & (y16d1 > 0) & (y84d1 > 0)
    xbin_midd2, y50d2, y16d2, y84d2 = dm.percentile_bins(xd2, yd2,
                                                         xmin2, xmax2,
                                                         nxbins = xbin2,
                                                         limit = 12)
    md2 = (y50d2 > 0) | (y16d2 > 0) | (y84d2 > 0)
    ax1.plot(xbin_midd1[md1], y50d1[md1], 'r-')
    ax1.plot(xbin_midd1[md1], y16d1[md1], 'r--')
    ax1.plot(xbin_midd1[md1], y84d1[md1], 'r--')
    ax2.plot(xbin_midd2[md2], y50d2[md2], 'r-')
    ax2.plot(xbin_midd2[md2], y16d2[md2], 'r--')
    ax2.plot(xbin_midd2[md2], y84d2[md2], 'r--')

    #add text
    P.text(0.5, 0.95,'Late-type galaxies\n$2 \leq z < 4$',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
#    P.text(0.5, 0.95,'$S_{250} > 5$ mJy',
#           horizontalalignment='center',
#           verticalalignment='center',
#           transform = ax2.transAxes)

    #labels
    ax1.set_xlabel(xlabel)
    ax2.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    #yticks
    ax2.set_yticks([])
    ax1.set_xticks(ax1.get_xticks()[:-1])
    ax2.set_xticks(ax2.get_xticks()[1:])
    ax1.set_yticks(y1ticks)
    ax2.set_yticks(y2ticks)
    #limits
    ax1.set_ylim(ymin, ymax)
    ax2.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin1, xmax1)
    ax2.set_xlim(xmin2, xmax2)
    #make grid
    ax1.grid()
    ax2.grid()
    #write a legend
    #ax1.legend(shadow = True, fancybox = True, 
    #           numpoints = 1, loc = 'upper left',
    #           scatterpoints = 1)
    ax2.legend(shadow = True, fancybox = True, 
               numpoints = 1, loc = 'upper left',
               scatterpoints = 1, markerscale = 1.5)
    P.savefig(out_folder + output)

def plot_size_paperKDE(xd1, xd2, yd1, yd2,
                       xlabel, ylabel, output, out_folder,
                       xbin1 = 15, ybin1 = 15,
                       xbin2 = 15, ybin2 = 15,
                       y1ticks = [1, 3, 5, 7, 9, 12],
                       y2ticks = [1, 3, 5, 7, 9],
                       xmin1 = 7.9, xmax1 = 11.7, 
                       xmin2 = 7.9, xmax2 = 11.7,
                       ymin = 0.1, ymax = 12,
                       scatters = False, mean = False,
                       lvls = None):

    #calclate KDEs
    mu1 = M.AnaKDE([xd1, yd1])
    x_vec1, y_vec1, zm1, lvls1, d01, d11 = mu1.contour(N.linspace(xmin1, xmax1, xbin1),
                                                       N.linspace(ymin, ymax, ybin1),
                                                       return_data = True)
    mu2 = M.AnaKDE([xd2, yd2])
    x_vec2, y_vec2, zm2, lvls2, d02, d12 = mu2.contour(N.linspace(xmin2, xmax2, xbin2),
                                                       N.linspace(ymin, ymax, ybin2),
                                                       return_data = True)
    #load obs data
    file = os.getenv('HOME') + '/Dropbox/Research/Herschel/obs_data/CavaSizesValues.txt'
    data = N.loadtxt(file, comments = '#', usecols = (0,1))
    
    #make the figure
    fig = P.figure()
    fig.subplots_adjust(wspace = 0.0, hspace = 0.01, left = 0.08, bottom = 0.07,
                        right = 0.97, top = 0.93)
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)
    #make filled contours
    if lvls == None:
        cont = ax1.contourf(x_vec1, y_vec1, zm1,
                            cmap = cm.get_cmap('gist_yarg'))
        cont = ax2.contourf(x_vec2, y_vec2, zm2,
                            cmap = cm.get_cmap('gist_yarg'))
    else:
        cont = ax1.contourf(x_vec1, y_vec1, zm1,
                            cmap = cm.get_cmap('gist_yarg'),
                            levels = lvls)
        cont = ax2.contourf(x_vec2, y_vec2, zm2,
                            cmap = cm.get_cmap('gist_yarg'),
                            levels = lvls)

    #plot scatter
    ax2.scatter(xd2, yd2, s = 0.5   , marker = 'o', color = 'blue',
                label = '$S_{250} > 5$ mJy')
    #plot observed data
    ax1.scatter(data[:,0], data[:,1], s = 45, marker = 's',
                color = 'green')    
    ax2.scatter(data[:,0], data[:,1], s = 45, marker = 's',
                color = 'green', label = 'Cava et al 2010')
    #calculate and plot percentiles
    xbin_midd1, y50d1, y16d1, y84d1 = dm.percentile_bins(xd1, yd1,
                                                         xmin1, xmax1,
                                                         nxbins = 30,
                                                         limit = 20)
    md1 = (y50d1 > 0) & (y16d1 > 0) & (y84d1 > 0)
    xbin_midd2, y50d2, y16d2, y84d2 = dm.percentile_bins(xd2, yd2,
                                                         xmin2, xmax2,
                                                         nxbins = 15,
                                                         limit = 10)
    md2 = (y50d2 > 0) | (y16d2 > 0) | (y84d2 > 0)
    ax1.plot(xbin_midd1[md1], y50d1[md1], 'r-')
    ax1.plot(xbin_midd1[md1], y16d1[md1], 'r--')
    ax1.plot(xbin_midd1[md1], y84d1[md1], 'r--')
    ax2.plot(xbin_midd2[md2], y50d2[md2], 'r-')
    ax2.plot(xbin_midd2[md2], y16d2[md2], 'r--')
    ax2.plot(xbin_midd2[md2], y84d2[md2], 'r--')

    #add text
    P.text(0.5, 0.95,'Late-type galaxies\n$2 \leq z < 4$',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)

    #labels
    ax1.set_xlabel(xlabel)
    ax2.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    #yticks
    ax2.set_yticks([])
    ax1.set_xticks(ax1.get_xticks()[:-1])
    ax2.set_xticks(ax2.get_xticks()[1:])
    ax1.set_yticks(y1ticks)
    ax2.set_yticks(y2ticks)
    #limits
    ax1.set_ylim(ymin, ymax)
    ax2.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin1, xmax1)
    ax2.set_xlim(xmin2, xmax2)
    #make grid
    ax1.grid()
    ax2.grid()
    #write a legend
    ax2.legend(shadow = True, fancybox = True, 
               numpoints = 1, loc = 'upper left',
               scatterpoints = 1, markerscale = 1.5)
    P.savefig(out_folder + output)

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    #path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    path = hm + '/Research/Herschel/runs/big_volume/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/size/big/'
    db = 'sams.db'
    
    #bulge-to-disk ratio
    bulge = 0.4
    
    query1 = '''select galprop.mstar, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
                from FIR, galprop where
                galprop.tmerge > 0.5 and
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.spire250_obs > 1e-15 and
                FIR.spire250_obs < 1e6 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                '''
    query2 = '''select galprop.mstar, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
                from FIR, galprop where
                galprop.tmerge > 0.5 and
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.spire250_obs > 5e-3 and
                FIR.spire250_obs < 1e6 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                '''
    #get data query1
    data = sq.get_data_sqlitePowerTen(path, db, query1)
    # disks
    disks = data[:,2] <= bulge
    xd1 = data[:,0][disks]
    yd1 = data[:,1][disks]
    #get data query1
    data = sq.get_data_sqlitePowerTen(path, db, query2)
    # disks
    disks = data[:,2] <= bulge
    xd2 = data[:,0][disks]
    yd2 = data[:,1][disks]
    #find all galaxies in similar Mstellar range as SPIRE bright
    yd2min = N.min(yd2)
    yd2max = N.max(yd2)
    msk = (yd1 >= yd2min) & (yd1 <= yd2max)
    #print out some info
    print 'Mean size of all galaxies, number of galaxies', N.mean(yd1), len(yd1)
    print 'Mean size of all galaxies with the same stellar mass selection as SPIRE detected', N.mean(yd1[msk]), len(yd1[msk])
    print 'Mean size of SPIRE detected galaxies', N.mean(yd2), len(yd2)

    #star the actual plots
    print 'Begin plotting'
    print 'Input DB: ', path + db
    print 'Output folder: ', out_folder

#    plot_size_paper(xd1, xd2, yd1, yd2,
#                    r'$\log_{10}(M_{\star}/M_{\odot})$', 
#                    r'$R_{\mathrm{disk}} \quad [\mathrm{kpc}]$',
#                    'SizeStellarMass.ps', out_folder,
#                    xmin1 = 8.5, xmax1 = 12.0,
#                    xmin2 = 10.1, xmax2 = 11.7,
#                    pmin = 0.02, xbin1 = 25, ybin1 = 25,
#                    xbin2 = 20, ybin2 = 20)
#
#    plot_size_paper(xd1, xd2, yd1, yd2,
#                    r'$\log_{10}(M_{\star}/M_{\odot})$', 
#                    r'$R_{\mathrm{disk}} \quad [\mathrm{kpc}]$',
#                    'SizeStellarMass2.ps', out_folder,
#                    xmin1 = 8.5, xmax1 = 11.9,
#                    xmin2 = 10.1, xmax2 = 11.7,
#                    pmin = 0.02, xbin1 = 20, ybin1 = 20,
#                    xbin2 = 15, ybin2 = 15)

    plot_size_paperKDE(xd1[::2], xd2, yd1[::2], yd2,
                       r'$\log_{10}(M_{\star}/M_{\odot})$', 
                       r'$R_{\mathrm{disk}} \quad [\mathrm{kpc}]$',
                       'SizeStellarMass3.ps', out_folder,
                       xmin1 = 9.2, xmax1 = 12.0,
                       xmin2 = 10.1, xmax2 = 11.7,
                       xbin1 = 40, ybin1 = 40,
                       xbin2 = 40, ybin2 = 40)

    plot_size_paperKDE(xd1[::2], xd2, yd1[::2], yd2,
                       r'$\log_{10}(M_{\star}/M_{\odot})$', 
                       r'$R_{\mathrm{disk}} \quad [\mathrm{kpc}]$',
                       'SizeStellarMass4.ps', out_folder,
                       xmin1 = 9.2, xmax1 = 12.0,
                       xmin2 = 10.1, xmax2 = 11.7,
                       xbin1 = 80, ybin1 = 80,
                       xbin2 = 80, ybin2 = 80)

    plot_size_paperKDE(xd1[::2], xd2, yd1[::2], yd2,
                       r'$\log_{10}(M_{\star}/M_{\odot})$', 
                       r'$R_{\mathrm{disk}} \quad [\mathrm{kpc}]$',
                       'SizeStellarMass5.ps', out_folder,
                       xmin1 = 9.2, xmax1 = 12.0,
                       xmin2 = 10.1, xmax2 = 11.7,
                       xbin1 = 80, ybin1 = 80,
                       xbin2 = 80, ybin2 = 80,
                       lvls = N.linspace(0, 2, 10))
    
    plot_size_paperKDE(xd1[::2], xd2, yd1[::2], yd2,
                       r'$\log_{10}(M_{\star}/M_{\odot})$', 
                       r'$R_{\mathrm{disk}} \quad [\mathrm{kpc}]$',
                       'SizeStellarMass6.ps', out_folder,
                       xmin1 = 9.2, xmax1 = 12.0,
                       xmin2 = 10.1, xmax2 = 11.7,
                       xbin1 = 80, ybin1 = 80,
                       xbin2 = 80, ybin2 = 80,
                       lvls = N.logspace(0, 2, 10))

    plot_size_paperKDE(xd1[::2], xd2, yd1[::2], yd2,
                       r'$\log_{10}(M_{\star}/M_{\odot})$', 
                       r'$R_{\mathrm{disk}} \quad [\mathrm{kpc}]$',
                       'SizeStellarMass7.ps', out_folder,
                       xmin1 = 9.2, xmax1 = 12.0,
                       xmin2 = 10.1, xmax2 = 11.7,
                       xbin1 = 80, ybin1 = 80,
                       xbin2 = 80, ybin2 = 80,
                       lvls = [0.01, 0.05, 0.1, 0.3, 0.5, 0.7, 0.9])

    
#    query1 = '''select galprop.mstar, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                galprop.tmerge > 0.5 and
#                FIR.spire250_obs > 1e-12 and
#                FIR.spire250_obs < 1e6
#                '''
#    query2 = '''select galprop.mstar, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 5e-3 and
#                FIR.spire250_obs < 1e6
#                '''
#    plot_size_paper(query1, query2, r'$\log(M_{\star}/M_{\odot})$', 
#               r'$R_{\textrm{disk}}$ \quad [kpc]', 'SizeStellarMassMergersIn.ps',
#               out_folder, xmin1 = 8.2, xmax1 = 11.65,
#               xmin2 = 10.1, xmax2 = 11.65,
#               pmin = 0.05, xbin1 = 13, ybin1 = 11,
#               xbin2 = 13, ybin2 = 11)
#
#    query1 = '''select galprop.mstardot, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                galprop.tmerge > 0.5 and
#                FIR.spire250_obs > 1e-12 and
#                FIR.spire250_obs < 1e6
#                '''
#    query2 = '''select galprop.mstardot, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                galprop.tmerge > 0.5 and
#                FIR.spire250_obs > 5e-3 and
#                FIR.spire250_obs < 1e6
#                '''
#    plot_size_paper(query1, query2, r'$\dot{M}_{\star} \ [M_{\odot}yr^{-1}]$', 
#                    r'$R_{\textrm{disk}}$ \quad [kpc]', 'SizeSFR.ps',
#                    out_folder, xmin1 = 0, xmax1 = 200,
#                    xmin2 = 0, xmax2 = 200,
#                    pmin = 0.05, xbin1 = 20, ybin1 = 10,
#                    xbin2 = 20, ybin2 = 10)

###################################################################################################
#OBSOLETE PLOTS
###################################################################################################
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
