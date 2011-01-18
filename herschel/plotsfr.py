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
import os
import numpy as N
from matplotlib import cm
#Sami's repository
import db.sqlite as sq
import astronomy.hess_plot as h
import astronomy.datamanipulation as dm

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
    fig = P.figure(figsize= (10,10))
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
    db = 'sams.db'

    ylab = r'Fraction  of $M_{\star}$ Created'
    type = '.png'

###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs, galprop.mstar, galprop.mstar_burst
                from FIR, galprop where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs > 1e-18 and
                FIR.spire250_obs < 1e6
                '''
    xlab = r'$\frac{S_{250}}{S_{3.4}}$'
    plotSFRFractions(query, xlab, ylab,'FractionBurstSPIRE250IRAC1'+type,
                     out_folder, xmin = 0.0, xmax = 2500, xbins = 12,
                     logscale = False, ymax = 1.01)
