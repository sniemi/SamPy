import matplotlib
#matplotlib.use('PS')
matplotlib.use('Agg')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.1)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 3
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import pylab as P
import numpy as N
import scipy.stats as SS
from matplotlib import cm
import os
#Sami's repository
import db.sqlite as sq
import astronomy.datamanipulation as dm
import sandbox.MyTools as M

def plotFIRLbolvsSFR(query, path, database,
                     output, out_folder,
                     xbins = 90, ybins = 90):
    '''
    Plots star formation rate as a function of total IR luminosity.
    Uses KDE to plot contours using the probability density function. 
    '''
    #get data
    data = sq.get_data_sqlite(path, database, query)
    print len(data[:,0])
    #KDE
    x = M.AnaKDE([data[:,0], N.log10(data[:,1])])
    x_vec, y_vec, zm, lvls, d0, d1 = x.contour(N.linspace(7.0, 13.0, xbins),
                                               N.linspace(-5, 2.5, ybins),
                                               return_data = True)
    #check the highest value and that the KDE integrates to 1
   #print N.max(zm), abs(x.kde.integrate_box([6.5,-5],[13.5,3]))
    #make plot
#    fig = P.figure()
    fig = P.figure(figsize=(10,10))    
    fig.subplots_adjust(left = 0.09, bottom = 0.07,
                        right = 0.97, top = 0.93)
    ax1 = fig.add_subplot(111)
    #scatter plot
    ax1.scatter(data[:,0], N.log10(data[:,1]), s = 0.1, color = 'r')
    #make filled contours
    cont = ax1.contourf(x_vec, y_vec, zm,
                        cmap = cm.get_cmap('gist_yarg'),
                        alpha = 0.9)
    #cbar = fig.colorbar(cont)
    #show image
#    img = ax1.imshow(zm,extent=(6.5,13.5,-5,3),
#                     cmap=cm.get_cmap('gist_yarg'),
#                     alpha = 0.95, vmin = 0.1, vmax = 1.1,
#                     interpolate=None)
    #labels
    ax1.set_xlabel('$\log_{10}(L_{\mathrm{IR}} \ [M_{\odot}])$')
    ax1.set_ylabel('$\log_{10}(\dot{M}_{\star} \ [M_{\odot} \ \mathrm{yr}^{-1}])$')
    #scale
    ax1.set_ylim(-5, 2.5)
    ax1.set_xlim(7.0, 13.0)
    #save figure
    P.savefig(out_folder + output)

def plotSFRFractions(query,
                     xlabel, ylabel,
                     output, out_folder,
                     xmin = 8.0,
                     xmax = 11.5,
                     xbins = 15,
                     ymin = -0.01,
                     ymax = 1.01,
                     logscale = False):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x = data[:,0]
    mstar = data[:,1]
    burst = data[:,2]

    mids, fract = dm.binAndReturnFractions(x,
                                           burst,
                                           mstar,
                                           xmin,
                                           xmax,
                                           xbins,
                                           logscale = False)
    print mids, fract
    #make the figure
#    fig = P.figure()
    fig = P.figure(figsize=(10,10))
    fig.subplots_adjust(left = 0.08, bottom = 0.07,
                        right = 0.97, top = 0.93)
    ax1 = fig.add_subplot(111)
    #draw lines
    ax1.plot(mids, fract, 'k-', lw = 2.6, label = 'In Bursts')


    #labels
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    #limits
    ax1.set_ylim(ymin, ymax)
    #add annotate
    P.text(0.5, 0.93,'All galaxies\n$2 \leq z < 4$',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    #make grid
    ax1.grid()
    #legend and save
    P.legend(loc = 'upper right')
    P.savefig(out_folder + output)

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/sfr/'
    database = 'sams.db'

    ylab = r'Fraction  of $M_{\star}$ Created'
    type = '.png'

###############################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs, galprop.mstar, galprop.mstar_burst
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs > 1e-18 and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$\frac{S_{250}}{S_{3.4}}$'
#    plotSFRFractions(query, xlab, ylab,'FractionBurstSPIRE250IRAC1'+type,
#                     out_folder, xmin = 0.0, xmax = 2500, xbins = 12,
#                     logscale = False, ymax = 1.01)
###############################################################################
    #query
    query = '''select FIR.L_bol, galprop.mstardot from FIR, galprop
    where FIR.z >= 1.9 and FIR.z <= 2.1 and FIR.spire250_obs < 1e6 and
    galprop.halo_id = FIR.halo_id and galprop.gal_id = FIR.gal_id and
    FIR.L_bol < 100 and galprop.mstardot > 1e-5 and FIR.L_bol > 7'''
    plotFIRLbolvsSFR(query, path, database,'LIRSFRz2'+type, out_folder,
                     xbins = 90, ybins = 90)
###############################################################################        
    query = '''select FIR.L_bol, galprop.mstardot from FIR, galprop
    where FIR.z >= 2.0 and FIR.z < 4.0 and FIR.spire250_obs < 1e6 and
    galprop.halo_id = FIR.halo_id and galprop.gal_id = FIR.gal_id and
    FIR.L_bol < 100 and galprop.mstardot > 1e-5 and FIR.L_bol > 7'''
    plotFIRLbolvsSFR(query, path, database,'LIRSFR'+type, out_folder,
                     xbins = 60, ybins = 60)
###############################################################################
