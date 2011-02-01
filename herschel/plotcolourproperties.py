import matplotlib
#matplotlib.use('PS')
matplotlib.use('Agg')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 15
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.1)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import pylab as P
import os
from matplotlib import cm
from mpl_toolkits.axes_grid import make_axes_locatable 
import  matplotlib.axes as maxes
import numpy as N
#Sami's repository
import db.sqlite as sq
import sandbox.MyTools as M
import astronomy.conversions as co

def plotColourProperties(query,
                         xlabel, ylabel,
                         output, out_folder,
                         ymin = -12, ymax = 2,
                         xmin = -6, xmax = 3.2,
                         title = '',
                         clabel = '$\mathrm{Redshift}$'):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x1 = data[:,0]
    x2 = co.ABMagnitudeToJansky(data[:,1])
    x = N.log10(x1 / x2)
    y = N.log10(data[:,2] * 1e3)
    z = data[:,3]
    #make the figure
#    fig = P.figure()
    fig = P.figure(figsize= (10,10))
    fig.subplots_adjust(left = 0.09, bottom = 0.08,
                        right = 0.92, top = 0.94)
    ax1 = fig.add_subplot(111)
    #plot scatters
    s1 = ax1.scatter(x, y, s = 0.5, marker = 'o',
                     c=z, cmap = cm.get_cmap('jet'), alpha = 0.25,
                     edgecolor = 'none')
    s1 = ax1.scatter(x, y, s = 0.1, marker = 'o',
                     c=z, cmap = cm.get_cmap('jet'),
                     edgecolor = 'none', visible = False)
    c1 = fig.colorbar(s1, ax = ax1, shrink = 0.7, fraction = 0.05, pad = 0.01)
    c1.set_label(clabel)
    #labels
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    #limits
    ax1.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin, xmax)
    #add annotate
    P.text(0.5, 1.03,title,
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    #make grid
    ax1.grid()
    #legend and save
    #P.legend(loc = 'upper left', scatterpoints = 1)
    P.savefig(out_folder + output)

def plotColourProperties2(query,
                          xlabel, ylabel,
                          output, out_folder,
                          ymin = -13, ymax = 2,
                          xmin = -8, xmax = 4,
                          title = '', ylog = False):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x1 = data[:,0]
    x2 = co.ABMagnitudeToJansky(data[:,1])
    x = N.log10(x1 / x2)
    if ylog:
        y = N.log10(data[:,2])
    else:
        y = data[:,2]
    z = data[:,3]
    #make the figure
#    fig = P.figure()
    fig = P.figure(figsize= (10,10))
    fig.subplots_adjust(left = 0.09, bottom = 0.08,
                        right = 0.92, top = 0.94)
    ax1 = fig.add_subplot(111)
    #plot scatters
    s1 = ax1.scatter(x, y, s = 0.6, marker = 'o',
                     c=z, cmap = cm.get_cmap('jet'), alpha = 0.25,
                     edgecolor = 'none')
    s1 = ax1.scatter(x, y, s = 0.1, marker = 'o',
                     c=z, cmap = cm.get_cmap('jet'),
                     edgecolor = 'none', visible = False)
    c1 = fig.colorbar(s1, ax = ax1, shrink = 0.7, fraction = 0.05)
    c1.set_label('$\mathrm{Redshift}$')
    #labels
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    #limits
    ax1.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin, xmax)
    #add annotate
    P.text(0.5, 1.03,title,
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    #make grid
    ax1.grid()
    #legend and save
    #P.legend(loc = 'upper left', scatterpoints = 1)
    P.savefig(out_folder + output)

def plotColourProperties3(query,
                          xlabel, ylabel,
                          output, out_folder,
                          ymin = -12, ymax = 2,
                          xmin = -6, xmax = 3.2,
                          title = ''):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x1 = data[:,0]
    x2 = data[:,1]
    x = N.log10(x1 / x2)
    y = N.log10(data[:,2] * 1e3)
    z = data[:,3]
    #make the figure
#    fig = P.figure()
    fig = P.figure(figsize= (10,10))
    fig.subplots_adjust(left = 0.09, bottom = 0.08,
                        right = 0.92, top = 0.94)
    ax1 = fig.add_subplot(111)
    #plot scatters
    s1 = ax1.scatter(x, y, s = 0.5, marker = 'o',
                     c=z, cmap = cm.get_cmap('jet'), alpha = 0.25,
                     edgecolor = 'none')
    s1 = ax1.scatter(x, y, s = 0.1, marker = 'o',
                     c=z, cmap = cm.get_cmap('jet'),
                     edgecolor = 'none', visible = False)
    c1 = fig.colorbar(s1, ax = ax1, shrink = 0.7, fraction = 0.05)
    c1.set_label('$\mathrm{Redshift}$')
    #labels
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    #limits
    ax1.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin, xmax)
    #add annotate
    P.text(0.5, 1.03,title,
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    #make grid
    ax1.grid()
    #legend and save
    #P.legend(loc = 'upper left', scatterpoints = 1)
    P.savefig(out_folder + output)

def plotColourProperties4(query, output, out_folder):
    #get data, all galaxies
    #FIR.spire250_obs, FIR.irac_ch4_obs, galprop.mstardot,
    #galprop.sfr_burst, galprop.sfr_ave, FIR.z, galprop.tmerge
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x1 = data[:,0]
    x2 = data[:,1]
    x = N.log10(x1 / x2)
    sfr = data[:,2]
    burst = data[:,3]
    avera = data[:,4]
    z = data[:,5]
    tmerge = data[:,6]
    #masks
    noMerge = tmerge < 0.0
    recent = (tmerge < 0.25) & (tmerge > 0.0)
    mergers = tmerge > 0.0
    #make the figure
#    fig = P.figure()
    fig = P.figure(figsize= (10,10))
    fig.subplots_adjust(left = 0.085, bottom = 0.08,
                        right = 0.99, top = 0.99,
                        wspace = 0.21, hspace = 0.0)
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    #plot scatters
    s1 = ax1.scatter(x[noMerge], N.log10(sfr[noMerge]), s = 3.5, marker = '<',
                     c=z[noMerge], cmap = cm.get_cmap('jet'),
                     alpha = 0.15, edgecolor = 'none',
                     label = 'Never Merged')
    s1 = ax1.scatter(x[noMerge], N.log10(sfr[noMerge]), s = 1.0, marker = '<',
                     c=z[noMerge], cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     visible = False)
    s2 = ax2.scatter(x[recent], N.log10(sfr[recent]), s = 3.5, marker = '>',
                     c=z[recent], cmap = cm.get_cmap('jet'),
                     alpha = 0.15, edgecolor = 'none',
                     label = 'Recent Mergers $T_{\mathrm{merge}} < 250$ Myr')
    s2 = ax2.scatter(x[recent], N.log10(sfr[recent]), s = 1.0, marker = '>',
                     c=z[recent], cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     visible = False)
    s3 = ax3.scatter(x[recent], N.log10(burst[recent]), s = 3.5, marker = '>',
                     c=z[recent], cmap = cm.get_cmap('jet'),
                     alpha = 0.15, edgecolor = 'none',
                     label = 'Recent Mergers $T_{\mathrm{merge}} < 250$ Myr')
    s3 = ax3.scatter(x[recent], N.log10(burst[recent]), s = 1.0, marker = '>',
                     c=z[recent], cmap = cm.get_cmap('jet'), edgecolor = 'none',
                    visible = False)
    s6 = ax4.scatter(x[noMerge], N.log10(avera[noMerge]), s = 0.5, marker = 'o',
                     c='red', alpha = 0.1, edgecolor = 'none',
                     label = 'Never Merged')
    s7 = ax4.scatter(x[recent], N.log10(avera[recent]), s = 0.5, marker = 's',
                     c='blue', alpha = 0.1, edgecolor = 'none',
                     label = 'Recent Mergers $T_{\mathrm{merge}} < 250$ Myr')    
    s6 = ax4.scatter(x[noMerge], N.log10(avera[noMerge]), s = 2.0, marker = 'o',
                     c='red', edgecolor = 'none', visible = False)
    s7 = ax4.scatter(x[recent], N.log10(avera[recent]), s = 2.0, marker = 's',
                     c='blue', edgecolor = 'none', visible = False)    
    #colorbars
    cax1 = fig.add_axes([0.11, 0.93, 0.15, 0.15/12.])#[left, bottom, width, height]
    c1 = fig.colorbar(s1, cax = cax1, orientation = 'horizontal',
                      ticks=[2,2.6,3.4,4])
    c1.set_label('$\mathrm{Redshift}$', size = 13)
    cax2 = fig.add_axes([0.6, 0.93, 0.15, 0.15/12.])
    c2 = fig.colorbar(s2, cax = cax2, orientation = 'horizontal',
                      ticks=[2,2.6,3.4,4])
    c2.set_label('$\mathrm{Redshift}$', size = 13)
    cax3 = fig.add_axes([0.11, 0.475, 0.15, 0.15/12.])
    c3 = fig.colorbar(s3, cax = cax3, orientation = 'horizontal',
                      ticks=[2,2.6,3.4,4])
    c3.set_label('$\mathrm{Redshift}$', size = 13)

    #labels
    xlabel = r'$\log_{10} \left ( \frac{S_{250}}{S_{8.0}} \right )$'
    ylabel1 = r'$\log_{10}(\dot{M}_{\star} \ [M_{\odot} \ \mathrm{yr}^{-1}])$'
    ylabel3 = r'$\log_{10}(\dot{M}_{\mathrm{BURST}} \ [M_{\odot} \ \mathrm{yr}^{-1}])$'
    ylabel4 = r'$\log_{10}(< \dot{M}_{\star} > \ [M_{\odot} \ \mathrm{yr}^{-1}])$'
    ax1.set_xticklabels([])
    ax1.set_ylabel(ylabel1)
    ax2.set_xticklabels([])
    ax2.set_ylabel(ylabel1)
    ax3.set_xlabel(xlabel)
    ax3.set_ylabel(ylabel3)
    ax4.set_xlabel(xlabel)
    ax4.set_ylabel(ylabel4)
    #limits
    xmin = -1.5 
    xmax = 3.3
    ymin = -3.8
    ymax = 3.2
    ax1.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin, xmax)
    ax2.set_ylim(ymin, ymax)
    ax2.set_xlim(xmin, xmax)
    ax3.set_ylim(ymin, ymax)
    ax3.set_xlim(xmin, xmax)
    ax4.set_ylim(ymin, ymax)
    ax4.set_xlim(xmin, xmax)
    #make grid
    ax1.grid()
    ax2.grid()
    ax3.grid()
    ax4.grid()
    #legends and save
    ax1.legend(loc = 'upper left', scatterpoints = 1, markerscale=7)
    ax2.legend(loc = 'upper left', scatterpoints = 1, markerscale=7)
    ax2.legend(loc = 'upper left', scatterpoints = 1, markerscale=7)
    ax3.legend(loc = 'upper left', scatterpoints = 1, markerscale=7)
    ax4.legend(loc = 'upper left', scatterpoints = 1, markerscale=18)
    P.savefig(out_folder + output)


if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/colours/'
    db = 'sams.db'

    type = '.png'

    print 'Begin plotting'
#################################################################################
#    query = '''select FIR.spire250_obs, galphot.f775w, FIR.spire250_obs,
#                FIR.z
#                from FIR, galphot where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphot.f775w < 60 and
#                FIR.spire250_obs > 1e-19
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
#    plotColourProperties(query, xlab, ylab,'ColorSPIRE'+type,  out_folder)
#################################################################################
#    query = '''select FIR.spire250_obs, galphot.f775w, FIR.spire250_obs,
#                FIR.z
#                from FIR, galphot where
#                FIR.z >= 2.0 and
#                FIR.z < 2.2 and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphot.f775w < 60 and
#                FIR.spire250_obs > 1e-19
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
#    plotColourProperties(query, xlab, ylab,'ColorSPIREz2'+type,  out_folder)
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f775w, FIR.spire250_obs,
#                FIR.z
#                from FIR, galphot, galprop where
#                FIR.z >= 3.0 and
#                FIR.z < 3.3 and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphot.f775w < 60 and
#                FIR.spire250_obs > 1e-19 and
#                galprop.tmajmerge  > 0 and
#                galprop.tmajmerge < 0.25
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
#    plotColourProperties(query, xlab, ylab,'ColorSPIREz3OnlyRecentMajorMergers'+type,  out_folder)
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f160w, FIR.spire250_obs,
#                galprop.mcold
#                from FIR, galphot, galprop where
#                FIR.z >= 3.0 and
#                FIR.z < 3.3 and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-19 and
#                galprop.mcold > 6
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F160W}} \right )$'
#    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
#    clabel = 'mcold'
#    plotColourProperties(query, xlab, ylab,'ColorSPIREz3Special16'+type, out_folder,
#                         clabel=clabel)
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f775w, FIR.spire250_obs,
#                FIR.z
#                from FIR, galphot where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphot.f775w < 33 and
#                FIR.spire250_obs > 1e-7
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
#    plotColourProperties(query, xlab, ylab,'ColorSPIRE2'+type, out_folder,
#                         xmin = 0.0, xmax = 3.5, ymin = -4.0, ymax = 1.2,
#                         title = '$S_{250} > 10^{-7}\ \mathrm{Jy} \ \mathrm{and} \ \mathrm{F775W} < 33$')
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f775w, FIR.spire250_obs,
#                FIR.z
#                from FIR, galphot where
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphot.f775w < 33 and
#                FIR.spire250_obs > 1e-7
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
#    plotColourProperties(query, xlab, ylab,'ColorSPIRE3'+type, out_folder,
#                         xmin = 0.0, xmax = 3.5, ymin = -4.0, ymax = 1.2,
#                         title = '$S_{250} > 10^{-7}\ \mathrm{Jy} \ \mathrm{and} \ \mathrm{F775W} < 33$')
################################################################################
#    print 'plot no subhaloes'
##################################################################################
#    query = '''select FIR.spire250_obs, galphot.f775w, FIR.spire250_obs,
#                FIR.z
#                from FIR, galphot, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphot.f775w < 60 and
#                FIR.spire250_obs > 1e-19 and
#                galprop.t_sat > 99
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
#    plotColourProperties(query, xlab, ylab,'ColorSPIRENoSub'+type,  out_folder)
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f775w, FIR.spire250_obs,
#                FIR.z
#                from FIR, galphot, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphot.f775w < 60 and
#                FIR.spire250_obs > 1e-7 and
#                galprop.t_sat > 99
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
#    plotColourProperties(query, xlab, ylab,'ColorSPIRE2NoSub'+type, out_folder,
#                         xmin = 0.0, xmax = 3.5, ymin = -4.0, ymax = 1.2,
#                         title = '$S_{250} > 10^{-7}\ \mathrm{Jy} \ \mathrm{and} \ \mathrm{F775W} < 33$')
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f775w, FIR.spire250_obs,
#                FIR.z
#                from FIR, galphot, galprop where
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galprop.t_sat > 99 and 
#                galphot.f775w < 33 and
#                FIR.spire250_obs > 1e-7
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
#    plotColourProperties(query, xlab, ylab,'ColorSPIRE3NoSub'+type, out_folder,
#                         xmin = 0.0, xmax = 3.5, ymin = -4.0, ymax = 1.2,
#                         title = '$S_{250} > 10^{-7}\ \mathrm{Jy} \ \mathrm{and} \ \mathrm{F775W} < 33$')
#################################################################################
#    print 'Plotting IRAC props'
#################################################################################
#    query = '''select FIR.spire250_obs, FIR.irac_ch4_obs, FIR.spire250_obs,
#                FIR.z
#                from FIR where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.spire250_obs < 1e7
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{8.0}} \right )$'
#    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
#    plotColourProperties3(query, xlab, ylab,'ColorIRACSPIRE'+type,  out_folder)
################################################################################
#    query = '''select FIR.spire250_obs, FIR.irac_ch4_obs, FIR.spire250_obs,
#                FIR.z
#                from FIR where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.spire250_obs < 1e6 and
#                FIR.irac_ch4_obs > 1e-7 and
#                FIR.spire250_obs > 1e-7
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{8.0}} \right )$'
#    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
#    plotColourProperties3(query, xlab, ylab,'ColorIRACSPIRE2'+type, out_folder,
#                          xmin = 0.0, ymin = -4.0, ymax = 1.2,
#                          title = '$S_{250} > 10^{-7}\ \mathrm{Jy} \ \mathrm{and} \ S_{8.0} > 10^{-7}\ \mathrm{Jy}$')
#################################################################################
#    print 'Plotting physical properties'
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mstar,
#                FIR.z
#                from FIR, galprop, galphot where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-19
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10}(M_{\star} \ [M_{\odot}])$'
#    plotColourProperties2(query, xlab, ylab,'ColorMstellar'+type, out_folder,
#                          xmin = -1.4, xmax = 3.1, ymin = 7.0, ymax = 11.5)
#################################################################################
#    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.Zstar,
#                FIR.z
#                from FIR, galprop, galphot where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-19
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10}(Z_{\star})$'
#    plotColourProperties2(query, xlab, ylab,'ColorZstellar'+type, out_folder,
#                          xmin = -1.4, xmax = 3.1, ymin = -1.8, ymax = 0.5,
#                          ylog = True)
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.Zstar,
#                FIR.z
#                from FIR, galprop, galphot where
#                FIR.z >= 2.0 and
#                FIR.z < 2.4 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-19
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10}(Z_{\star})$'
#    plotColourProperties2(query, xlab, ylab,'ColorZstellarLowZ'+type, out_folder,
#                          xmin = -1.4, xmax = 3.1, ymin = -1.8, ymax = 0.5,
#                          ylog = True)
#################################################################################
#    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.Zcold,
#                FIR.z
#                from FIR, galprop, galphot where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-19
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10}(Z_{\mathrm{COLDGAS}})$'
#    plotColourProperties2(query, xlab, ylab,'ColorZcoldgas'+type, out_folder,
#                          xmin = -1.4, xmax = 3.1, ymin = -1.6, ymax = 0.5,
#                          ylog = True)
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mstar,
#                FIR.z
#                from FIR, galprop, galphot where
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-19
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10}(M_{\star} \ [M_{\odot}])$'
#    plotColourProperties2(query, xlab, ylab,'ColorMstellar2'+type, out_folder,
#                          xmin = -1.4, xmax = 3.1, ymin = 7.0, ymax = 11.5)
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mhalo,
#                FIR.z
#                from FIR, galprop, galphot where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-19
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10}(M_{\mathrm{DM}} \ [M_{\odot}])$'
#    plotColourProperties2(query, xlab, ylab,'ColorMhalo'+type, out_folder,
#                          xmin = -1.4, xmax = 3.1, ymin = 9.5, ymax = 13.5)
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mhalo,
#                FIR.z
#                from FIR, galprop, galphot where
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-19
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10}(M_{\mathrm{DM}} \ [M_{\odot}])$'
#    plotColourProperties2(query, xlab, ylab,'ColorMhalo2'+type, out_folder,
#                          xmin = -1.4, xmax = 3.1, ymin = 9.5, ymax = 13.5)
###############################################################################
#    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mstardot,
#                FIR.z
#                from FIR, galprop, galphot where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-19
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10}(\dot{M}_{\star} \ [M_{\odot}])$'
#    plotColourProperties2(query, xlab, ylab,'ColorSFR'+type, out_folder,
#                          xmin = -1.4, xmax = 3.1, ymin = -4, ymax = 3.0,
#                          ylog = True)
################################################################################
#    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mstardot,
#                FIR.z
#                from FIR, galprop, galphot where
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphot.gal_id and
#                FIR.halo_id = galphot.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-19
#                '''
#    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
#    ylab = r'$\log_{10}(\dot{M}_{\star} \ [M_{\odot}])$'
#    plotColourProperties2(query, xlab, ylab,'ColorSFR2'+type, out_folder,
#                          xmin = -1.4, xmax = 3.1, ymin = -4, ymax = 3.0,
#                          ylog = True)
#################################################################################
#    print 'plot SFRs'
#################################################################################
#    query = '''select FIR.spire250_obs, FIR.irac_ch4_obs, galprop.mstardot,
#                galprop.sfr_burst, galprop.sfr_ave, FIR.z, galprop.tmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-19 and
#                galprop.mstardot > 0
#                '''
#    plotColourProperties4(query,'ColorSFRBurst'+type, out_folder)
###############################################################################

    print 'All done'
