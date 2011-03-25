import matplotlib
#matplotlib.use('Cairo')
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
import numpy as N
from matplotlib import cm
#Sami's repository
import db.sqlite as sq
import sandbox.MyTools as M
import smnIO.sextutils as sex
import astronomy.conversions as cv

def plotMergerFractionsMultiplot(query, xlabel, ylabel,
                                 output, out_folder, obs,
                                 mergetimelimit = 0.25,
                                 ymin = -0.2, ymax = 1.5,
                                 xmin = -1.9, xmax = 4.15,
                                 xbins = 80, ybins = 80,
                                 title = 'Simulated Galaxies',
                                 size = 4.5, alpha = 0.2, ch = 1):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x = data[:,0]
    f775w = data[:,1]
    f850lp = data[:,2]
    uvcolor = f775w - f850lp
    tmerge = data[:,3]
    tmajor = data[:,4]
    #get observed
    observed = sex.se_catalog(obs)
    xobs = (observed.f250_mjy*1e3) / eval('observed.ch%i_flux_ujy' % ch)
    yobs = cv.janskyToMagnitude(observed.i_flux_ujy) - cv.janskyToMagnitude(observed.z_flux_ujy)
    #masks for simulated galaxies
    nomergeMask = tmerge < 0.0
    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
    majorsMask2 = (tmajor > mergetimelimit)
    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) & \
                  (majorsMask == False) & (majorsMask2 == False)
    mergersMask2 = (nomergeMask == False) & (majorsMask == False) & \
                   (mergersMask == False) & (majorsMask2 == False)

    #KDE
    mu = M.AnaKDE([N.log10(x[nomergeMask]), uvcolor[nomergeMask]])
    x_vec, y_vec, zm, lvls, d0, d1 = mu.contour(N.linspace(xmin, xmax, xbins),
                                                N.linspace(ymin, ymax, ybins),
                                                return_data = True)
    #make the figure
    #fig = P.figure()
    fig = P.figure(figsize= (10,10))
    fig.subplots_adjust(left = 0.09, bottom = 0.08,
                        right = 0.93, top = 0.95,
                        wspace = 0.0, hspace = 0.0)
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    #make contours
    #lv = N.linspace(0.01, N.max(zm), 4)
#    cont = ax1.contour(x_vec, y_vec, zm, linewidths  = 0.9,
#                       levels = lv, colors = 'black')
#    cont = ax2.contour(x_vec, y_vec, zm, linewidths  = 0.9,
#                       levels = lv, colors = 'black')
#    cont = ax3.contour(x_vec, y_vec, zm, linewidths  = 0.9,
#                       levels = lv, colors = 'black')
#    cont = ax4.contour(x_vec, y_vec, zm, linewidths  = 0.9,
#                       levels = lv, colors = 'black')
    cont = ax1.contour(x_vec, y_vec, zm, linewidths  = 0.9,
                       colors = 'black', linestyles = 'dashed')
    cont = ax2.contour(x_vec, y_vec, zm, linewidths  = 0.9,
                       colors = 'black', linestyles = 'dashed')
    cont = ax3.contour(x_vec, y_vec, zm, linewidths  = 0.9,
                       colors = 'black', linestyles = 'dashed')
    cont = ax4.contour(x_vec, y_vec, zm, linewidths  = 0.9,
                       colors = 'black', linestyles = 'dashed')

    #plot scatters
    s2 = ax2.scatter(N.log10(x[majorsMask]), uvcolor[majorsMask],
                     s=size, c=1000.*tmajor[majorsMask], marker='o',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     label = 'Major Merger: $T \leq %.0f$ Myr' % (mergetimelimit*1000.),
                     alpha = alpha)
    s2 = ax2.scatter(N.log10(x[majorsMask]), uvcolor[majorsMask],
                     s=size, c=1000.*tmajor[majorsMask], marker='o',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     visible = False)
    s4 = ax4.scatter(N.log10(x[mergersMask]), uvcolor[mergersMask],
                     s=size*1.8, c=1000.*tmerge[mergersMask], marker='^',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     label = 'Minor Merger: $T \leq %.0f$ Myr' % (mergetimelimit*1000.),
                     alpha = alpha)
    s4 = ax4.scatter(N.log10(x[mergersMask]), uvcolor[mergersMask],
                     s=size*1.8, c=1000.*tmerge[mergersMask], marker='^',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     visible = False)
    #Observed
    s1 = ax1.scatter(N.log10(xobs), yobs, marker='o', s=20, alpha = 0.45, label = 'Observations')
    s3 = ax3.scatter(N.log10(xobs), yobs, marker='o', s=20, alpha = 0.45, label = 'Observations')
    #color bars
    c1 = fig.colorbar(s2, ax = ax2, shrink = 0.7, fraction = 0.05)
    c2 = fig.colorbar(s4, ax = ax4, shrink = 0.7, fraction = 0.05)
    c1.set_label('Time since latest merger [Myr]')
    c2.set_label('Time since latest merger [Myr]')
    #plot dividing line
    # y = x - 2.5
    x = N.array([2.0, 2.5, 3.0, 4.0])
    y = x - 2.7
    ax1.plot(x, y, 'g--')
    ax2.plot(x, y, 'g--')
    ax3.plot(x, y, 'g--')
    ax4.plot(x, y, 'g--')
    
    #add annotate
    P.text(0.5, 1.04, title,
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax2.transAxes)
    P.text(0.5, 1.04,'Observed Galaxies',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    #labels
    ax3.set_xlabel(xlabel)
    ax4.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax3.set_ylabel(ylabel)
    ax2.set_yticklabels([])
    ax4.set_yticklabels([])
    ax1.set_xticklabels([])
    ax2.set_xticklabels([])
    #limits
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
    #legend and save
    ax1.legend(loc = 'upper left', scatterpoints = 1,
               shadow = True, fancybox = True, markerscale=1.5)
    ax2.legend(loc = 'upper left', scatterpoints = 1,
               shadow = True, fancybox = True, markerscale=1.5)
    ax3.legend(loc = 'upper left', scatterpoints = 1,
               shadow = True, fancybox = True, markerscale=1.5)
    ax4.legend(loc = 'upper left', scatterpoints = 1,
               shadow = True, fancybox = True, markerscale=1.5)
    P.savefig(out_folder + output)

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    #path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    path = hm +  '/Research/Herschel/runs/big_volume/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/mergers/big/'
    db = 'sams.db'
    obs = hm + '/Dropbox/Research/Herschel/obs_data/goodsh_goodsn_allbands_z2-4.cat'

    type = '.png'

    print 'Begin plotting'
    print 'Input DB: ', path + db
    print 'Output folder: ', out_folder
###############################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs,
#                galphotdust.f775w, galphotdust.f850lp,
#                galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop, galphotdust where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphotdust.gal_id and
#                FIR.halo_id = galphotdust.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphotdust.f775w < 33 and
#                galphotdust.f850lp < 33 and
#                FIR.spire250_obs > 1e-15 and
#                FIR.irac_ch1_obs > 1e-15
#
#                '''
#    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{3.4}} \right )$'
#    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
#    plotMergerFractionsMultiplot(query, xlab, ylab,'ColorMergerPaper1'+type,
#                                 out_folder, obs)
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs,
#                galphotdust.f775w, galphotdust.f850lp,
#                galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop, galphotdust where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphotdust.gal_id and
#                FIR.halo_id = galphotdust.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphotdust.f775w < 30 and
#                galphotdust.f850lp < 30 and
#                FIR.spire250_obs > 1e-4
#
#                '''
#    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{3.4}} \right )$'
#    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
#    plotMergerFractionsMultiplot(query, xlab, ylab,'ColorMergerPaper2'+type,
#                                 out_folder, obs, xmin = 0.8, size = 20,
#                                 mergetimelimit = 0.5)
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs,
#                galphotdust.f775w, galphotdust.f850lp,
#                galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop, galphotdust where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphotdust.gal_id and
#                FIR.halo_id = galphotdust.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphotdust.f775w < 30 and
#                galphotdust.f850lp < 30 and
#                FIR.spire250_obs > 5e-3
#
#                '''
#    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{3.4}} \right )$'
#    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
#    plotMergerFractionsMultiplot(query, xlab, ylab,'ColorMergerPaper3'+type,
#                                 out_folder, obs, xmin = 1.5, size = 30,
#                                 mergetimelimit = 0.5, alpha = 0.5)
###############################################################################
###############################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs,
#                galphotdust.f775w, galphotdust.f850lp,
#                galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop, galphotdust where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphotdust.gal_id and
#                FIR.halo_id = galphotdust.halo_id and
#                FIR.spire250_obs < 1e6 and
#                galphotdust.f775w < 50 and
#                galphotdust.f850lp < 50 and
#                FIR.spire250_obs > 1e-15 and
#                FIR.irac_ch2_obs > 1e-15
#                '''
#    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{4.5}} \right )$'
#    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
#    plotMergerFractionsMultiplot(query, xlab, ylab,'ColorMergerPaper4'+type,
#                                 out_folder, obs, ch = 2,
#                                 title = 'All Simulated Galaxies')
##############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w_obs < 50 and
                galphotdust.f850lp_obs < 50 and
                FIR.spire250_obs > 1e-4 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id
                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{4.5}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,'ColorMergerPaper5'+type,
                                 out_folder, obs, xmin = 1.5, size = 20, xmax = 3.8,
                                 mergetimelimit = 0.25, alpha = 0.4, ch = 2,
                                 title = '$S_{250} > 10^{-4} \ \mathrm{Jy}$')
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w_obs < 50 and
                galphotdust.f850lp_obs < 50 and
                FIR.spire250_obs > 5e-3 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id
                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{4.5}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,'ColorMergerPaper6'+type,
                                 out_folder, obs, xmin = 1.5, size = 30, xmax = 3.8,
                                 mergetimelimit = 0.25, alpha = 0.5, ch = 2,
                                 title = '$S_{250} > 5 \ \mathrm{mJy}$')
###############################################################################
    print 'All done'
