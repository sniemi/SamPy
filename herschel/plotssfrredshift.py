import matplotlib
matplotlib.use('PS')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.2)
matplotlib.rcParams['legend.fontsize'] = 11
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import pylab as P
import numpy as N
from matplotlib import cm
import os
#Sami's repository
import db.sqlite as sq
import astronomy.datamanipulation as dm
import astronomy.hess_plot as h

def plot(query, xlabel, ylabel, output, out_folder,
        bulge = 0.4, xbin = 10, ybin = 10, xmin = -0.1, xmax = 6):
    
    #get data
    data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

    #sphericals
    mask = (data[:,2] > bulge) & (data[:,3] > 0.5)
    xe = data[:,0][mask]
    ye = data[:,1][mask]
    # disks
    disks = (data[:,2] <= bulge) & (data[:,3] > 0.5)
    xd = data[:,0][disks]
    yd = data[:,1][disks]
    #IR bright
    mask = data[:,4] > 1e-3
    xir = data[:,0][mask]
    yir = data[:,1][mask]
    
    #calculate means and percentiles
    xmd, y50d, y16d, y84d = dm.average_bins(xd, yd, xmin, xmax, nxbins = 20)
    xmt, y50t, y16t, y84t = dm.average_bins(data[:,0], data[:,1], xmin, xmax, nxbins = 20)
    xme, y50e, y16e, y84e = dm.average_bins(xe, ye, xmin, xmax, nxbins = 20)
    xmir, y50ir, y16ir, y84ir = dm.average_bins(xir, yir, xmin, xmax, nxbins = 20)

    #figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)
    #plots
#    ax1.errorbar(xmt, y50t, yerr = [y50t, y84t], label = 'Total',
#                 c = 'k')
#    ax1.errorbar(xmd, y50d, yerr = [y50d, y84d], label = 'Late-types',
#                 c = 'b', ls = '--')
#    ax1.errorbar(xme, y50e, yerr = [y16e, y84e-y50e], label = 'Early-types',
#                 c = 'r', ls = '-.')
    ax1.errorbar(xmir, y50ir, yerr = [y16ir, y84ir], label = '$S_{250} > 1$ mJy',
                 c = 'm', ls = ':')
    ax1.plot(xmt, y50t, 'k-', label = 'Total')
    ax1.plot(xmd, y50d, 'b--', label = 'Late-types')
    ax1.plot(xme, y50e, 'r-.', label = 'Early-types')
#    ax1.fill_between(xmt, y16t, y50t, label = 'Total')
#    ax1.fill_between(xmd, y16d, y50d, label = 'Late-type')
#    ax1.fill_between(xme, y16e, y50e, label = 'Early-type')
#    ax1.fill_between(xmir, y16ir, y50ir, label = '$S_{250} > 5$ mJy')
    
    #limits and labels
    ax1.set_xlim(0.0, xmax-.3)
    ax1.set_ylim(1e-3, 100.0)
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_yscale('log')
    #legend
    ax1.legend(shadow = True, fancybox = True, loc = 'lower right')
    #save and close
    P.savefig(out_folder + output)
    P.close()

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/sfrs/'
    db = 'sams.db'

    query = '''select FIR.z, galprop.mstardot/galprop.mstar, Pow10(galprop.mbulge - galprop.mstar),
               galprop.tmerge, FIR.spire250_obs
               from FIR, galprop where
               FIR.gal_id = galprop.gal_id and FIR.halo_id = galprop.halo_id'''

    plot(query, r'$z$', r'sSFR $\quad [Gyr^{-1}]$', 'ssfrvsz.ps', out_folder)
    print query