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
import numpy as N
from matplotlib import cm
import os
#Sami's repository
import db.sqlite as sq
import astronomy.datamanipulation as dm
import astronomy.hess_plot as h
    
def plot_ssfr_paper(query1, query2, out_folder,
                    xmin1 = 7.7, xmax1 = 11.8, xbin1 = 16,
                    ymin1 = -11, ymax1 =-7.5, ybin1 = 16,
                    xmin2 = 9.8, xmax2 = 11.8, xbin2 = 15,
                    ymin2 = -10, ymax2 = -7.5, ybin2 = 15,
                    pmax = 1.0, pmin = 0.01):
    #get data, all galaxies
    data1 = sq.get_data_sqliteSMNfunctions(path, db, query1)
    ssfr1 = N.log10(data1[:,0] / (10**data1[:,1]))
    x1 = data1[:,1]
    #get data, S_250 > 5mJy
    data2 = sq.get_data_sqliteSMNfunctions(path, db, query2)
    ssfr2 = N.log10(data2[:,0] / (10**data2[:,1]))
    x2 = data2[:,1]
    #make hess data
    s1, smin1, smax1 = h.hess_plot(x1, ssfr1,
                                   N.ones(len(x1)), 
                                   xmin1, xmax1, xbin1, 
                                   ymin1, ymax1, ybin1,
                                   pmax, pmin)
    s2, smin2, smax2 = h.hess_plot(x2, ssfr2,
                                   N.ones(len(x2)), 
                                   xmin2, xmax2, xbin2, 
                                   ymin2, ymax2, ybin2,
                                   pmax, pmin)
    
    #make the figure
    fig = P.figure()
    fig.subplots_adjust(wspace = 0.0, hspace = 0.01,
                        bottom = 0.07,
                        right = 0.97, top = 0.93)

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ims = ax1.imshow(s1, vmin = smin1, vmax = smax1,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin1, xmax1, ymin1, ymax1],
                     aspect = 'auto', alpha = 1)
    ims = ax2.imshow(s2, vmin = smin2, vmax = smax2,
                     origin = 'lower', cmap = cm.gray,
                     interpolation = None,
                     extent = [xmin2, xmax2, ymin2, ymax2],
                     aspect = 'auto', alpha = 1)

    #scatter plot
    ax2.scatter(x2, ssfr2, c = 'b', marker = 'o', s = 5)

    #percentiles
    xbin_midd, y50d, y16d, y84d = dm.percentile_bins(x1, ssfr1,
                                                     xmin1, xmax1)
    md = (y50d > -99) | (y16d >  -99) | (y84d >  -99)
    xbin_mide, y50e, y16e, y84e = dm.percentile_bins(x2, ssfr2,
                                                     xmin2, xmax2)
    me = (y50e >  -99) | (y16e >  -99) | (y84e >  -99)
    ax1.plot(xbin_midd[md], y50d[md], 'r-')
    ax1.plot(xbin_midd[md], y16d[md], 'r--')
    ax1.plot(xbin_midd[md], y84d[md], 'r--')
    ax2.plot(xbin_mide[me], y50e[me], 'r-')
    ax2.plot(xbin_mide[me], y16e[me], 'r--')
    ax2.plot(xbin_mide[me], y84e[me], 'r--')

    #labels
    ax1.set_xlabel(r'$\log_{10}(M_{\star} \ [M_{\odot}])$')
    ax2.set_xlabel(r'$\log_{10}(M_{\star} \ [M_{\odot}])$')
    ax1.set_ylabel(r'$\log_{10} \left (\frac{\dot{M}_{\star}}{M_{\star}} \ [\mathrm{yr}^{-1}] \right )$')

    #limits
    ax1.set_ylim(ymin1, ymax1)
    ax2.set_ylim(ymin1, ymax1)
    ax1.set_xlim(xmin1, xmax1)
    ax2.set_xlim(xmin2, xmax2)

    #add text
    P.text(0.5, 0.94,'All galaxies\n$2 \leq z < 4$',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    P.text(0.5, 0.97,'$S_{250} > 5$ mJy',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax2.transAxes)

    #yticks
    ax2.set_yticks(ax1.get_yticks()[1:-1])

    #make grid
    ax1.grid()
    ax2.grid()

    P.savefig(out_folder + 'ssfr.ps')
    P.close()

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/spire_detected/ssfr/'
    db = 'sams.db'

    query2 = '''select galprop.mstardot, galprop.mstar
                from galprop, FIR where
                FIR.z >= 2 and FIR.z < 4 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs > 5.0e-03 and
                FIR.spire250_obs < 1e6
             ''' 
    query1 = '''select galprop.mstardot, galprop.mstar
                from galprop, FIR where
                FIR.z >= 2 and FIR.z < 4 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs < 1e6
             ''' 
    #print query
    plot_ssfr_paper(query1, query2, out_folder)

###############################################################################
#OBSOLETE INFO
#    #5sigma limits derived by Kuang
#    depths = {'pacs100_obs': 1.7e-3,
#              'pacs160_obs': 4.5e-3,
#              'spire250_obs': 5.0e-3,
#              'spire350_obs': 9.0e-3,
#              'spire500_obs': 10.0e-3
#              }
#    FIRbands = ['pacs70_obs',
#                'pacs100_obs',
#                'pacs160_obs',
#                'spire250_obs',
#                'spire350_obs',
#                'spire500_obs']
#
#    galprop = ['mstar', 'mstardot', 'sfr_burst', 'sfr_ave', 'meanage', 'tmerge',
#               'r_disk', 'sigma_bulge', 'mhalo', 'm_strip', 'mcold', 'maccdot',
#               'maccdot_radio', 'Zstar', 'Zcold', 'tau0', 'tmajmerge']
#    galphot = ['f775w', 'f606w', 'f125w', 'f160w']
#    galphotdust = ['f775w', 'f606w', 'f125w', 'f160w']
#
#    t1 = 'galprop'
#    t2 = 'galphot'
#    t3 = 'galphotdust'
#    t4 = 'FIR'
