import matplotlib
#matplotlib.use('PS')
matplotlib.use('Agg')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.1)
matplotlib.rcParams['legend.fontsize'] = 11
matplotlib.rcParams['legend.handlelength'] = 3
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import pylab as P
import os
from matplotlib import cm
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
                         title = ''):
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
################################################################################
    query = '''select FIR.spire250_obs, galphot.f775w, FIR.spire250_obs,
                FIR.z
                from FIR, galphot where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galphot.gal_id and
                FIR.halo_id = galphot.halo_id and
                FIR.spire250_obs < 1e6 and
                galphot.f775w < 60 and
                FIR.spire250_obs > 1e-19
                '''
    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
    plotColourProperties(query, xlab, ylab,'ColorSPIRE'+type,  out_folder)
###############################################################################
    query = '''select FIR.spire250_obs, galphot.f775w, FIR.spire250_obs,
                FIR.z
                from FIR, galphot where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galphot.gal_id and
                FIR.halo_id = galphot.halo_id and
                FIR.spire250_obs < 1e6 and
                galphot.f775w < 33 and
                FIR.spire250_obs > 1e-7
                '''
    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
    plotColourProperties(query, xlab, ylab,'ColorSPIRE2'+type, out_folder,
                         xmin = 0.0, xmax = 3.5, ymin = -4.0, ymax = 1.2,
                         title = '$S_{250} > 10^{-7}\ \mathrm{Jy} \ \mathrm{and} \ \mathrm{F775W} < 33$')
###############################################################################
    query = '''select FIR.spire250_obs, galphot.f775w, FIR.spire250_obs,
                FIR.z
                from FIR, galphot where
                FIR.gal_id = galphot.gal_id and
                FIR.halo_id = galphot.halo_id and
                FIR.spire250_obs < 1e6 and
                galphot.f775w < 33 and
                FIR.spire250_obs > 1e-7
                '''
    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
    ylab = r'$\log_{10} ( S_{250} \ [\mathrm{mJy}] )$'
    plotColourProperties(query, xlab, ylab,'ColorSPIRE3'+type, out_folder,
                         xmin = 0.0, xmax = 3.5, ymin = -4.0, ymax = 1.2,
                         title = '$S_{250} > 10^{-7}\ \mathrm{Jy} \ \mathrm{and} \ \mathrm{F775W} < 33$')
###############################################################################
    print 'Plotting physical properties'
###############################################################################
    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mstar,
                FIR.z
                from FIR, galprop, galphot where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphot.gal_id and
                FIR.halo_id = galphot.halo_id and
                FIR.spire250_obs < 1e6 and
                FIR.spire250_obs > 1e-19
                '''
    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
    ylab = r'$\log_{10}(M_{\star} \ [M_{\odot}])$'
    plotColourProperties2(query, xlab, ylab,'ColorMstellar'+type, out_folder,
                          xmin = -1.4, xmax = 3.1, ymin = 7.0, ymax = 11.5)
###############################################################################
    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mstar,
                FIR.z
                from FIR, galprop, galphot where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphot.gal_id and
                FIR.halo_id = galphot.halo_id and
                FIR.spire250_obs < 1e6 and
                FIR.spire250_obs > 1e-19
                '''
    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
    ylab = r'$\log_{10}(M_{\star} \ [M_{\odot}])$'
    plotColourProperties2(query, xlab, ylab,'ColorMstellar2'+type, out_folder,
                          xmin = -1.4, xmax = 3.1, ymin = 7.0, ymax = 11.5)
###############################################################################
    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mhalo,
                FIR.z
                from FIR, galprop, galphot where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphot.gal_id and
                FIR.halo_id = galphot.halo_id and
                FIR.spire250_obs < 1e6 and
                FIR.spire250_obs > 1e-19
                '''
    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
    ylab = r'$\log_{10}(M_{\mathrm{DM}} \ [M_{\odot}])$'
    plotColourProperties2(query, xlab, ylab,'ColorMhalo'+type, out_folder,
                          xmin = -1.4, xmax = 3.1, ymin = 9.5, ymax = 13.5)
###############################################################################
    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mhalo,
                FIR.z
                from FIR, galprop, galphot where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphot.gal_id and
                FIR.halo_id = galphot.halo_id and
                FIR.spire250_obs < 1e6 and
                FIR.spire250_obs > 1e-19
                '''
    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
    ylab = r'$\log_{10}(M_{\mathrm{DM}} \ [M_{\odot}])$'
    plotColourProperties2(query, xlab, ylab,'ColorMhalo2'+type, out_folder,
                          xmin = -1.4, xmax = 3.1, ymin = 9.5, ymax = 13.5)
##############################################################################
    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mstardot,
                FIR.z
                from FIR, galprop, galphot where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphot.gal_id and
                FIR.halo_id = galphot.halo_id and
                FIR.spire250_obs < 1e6 and
                FIR.spire250_obs > 1e-19
                '''
    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
    ylab = r'$\log_{10}(\dot{M}_{\star} \ [M_{\odot}])$'
    plotColourProperties2(query, xlab, ylab,'ColorSFR'+type, out_folder,
                          xmin = -1.4, xmax = 3.1, ymin = -4, ymax = 3.0,
                          ylog = True)
###############################################################################
    query = '''select FIR.spire250_obs, galphot.f850lp, galprop.mstardot,
                FIR.z
                from FIR, galprop, galphot where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphot.gal_id and
                FIR.halo_id = galphot.halo_id and
                FIR.spire250_obs < 1e6 and
                FIR.spire250_obs > 1e-19
                '''
    xlab = r'$\log_{10} \left ( \frac{S_{250}}{S_{F775W}} \right )$'
    ylab = r'$\log_{10}(\dot{M}_{\star} \ [M_{\odot}])$'
    plotColourProperties2(query, xlab, ylab,'ColorSFR2'+type, out_folder,
                          xmin = -1.4, xmax = 3.1, ymin = -4, ymax = 3.0,
                          ylog = True)
###############################################################################
    print 'All done'
