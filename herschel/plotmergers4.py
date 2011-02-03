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
import numpy as N
from matplotlib import cm
#Sami's repository
import db.sqlite as sq
import sandbox.MyTools as M

def plotMergerFractions(query,
                        xlabel, ylabel,
                        output, out_folder,
                        mergetimelimit = 0.25,
                        ymin = -0.2, ymax = 1.0,
                        xmin = -8, xmax = 4.1,
                        xbins = 70, ybins = 70,
                        title = 'All galaxies in $2 \leq z < 4$'):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x = data[:,0]
    f775w = data[:,1]
    f850lp = data[:,2]
    uvcolor = f775w - f850lp
    tmerge = data[:,3]
    tmajor = data[:,4]
    #masks
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
#    fig = P.figure()
    fig = P.figure(figsize= (10,10))
    fig.subplots_adjust(left = 0.09, bottom = 0.08,
                        right = 0.92, top = 0.94)
    ax1 = fig.add_subplot(111)
    #make contours
    cont = ax1.contour(x_vec, y_vec, zm, linewidths = 1.3,
                       colors = 'black',
                       levels = N.linspace(0.2, N.max(zm), 5))
    #plot scatters
    ax1.scatter(N.log10(x[nomergeMask]), uvcolor[nomergeMask],
                s=1, c='k', marker='s',
                label = 'Never merged')
    s2 = ax1.scatter(N.log10(x[mergersMask]), uvcolor[mergersMask],
                     s=18, c=1000.*tmerge[mergersMask], marker='^',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     label = 'Minor Merger: $T \leq %.0f$ Myr' % (mergetimelimit*1000.),
                     alpha = 0.2)
    s1 = ax1.scatter(N.log10(x[majorsMask]), uvcolor[majorsMask],
                     s=25, c=1000.*tmajor[majorsMask], marker='o',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     label = 'Major Merger: $T \leq %.0f$ Myr' % (mergetimelimit*1000.),
                     alpha = 0.2)
    s1 = ax1.scatter(N.log10(x[majorsMask]), uvcolor[majorsMask],
                     s=1, c=1000.*tmajor[majorsMask], marker='o',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     alpha = 1.0, visible = False)
    c1 = fig.colorbar(s1, shrink = 0.8, fraction = 0.03)
    c1.set_label('Time since merger [Myr]')
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
    P.legend(loc = 'upper left', scatterpoints = 1, shadow = True,
             fancybox = True, markerscale=2)
    P.savefig(out_folder + output)

def plotMergerFractionsMultiplot(query,
                                 xlabel, ylabel,
                                 output, out_folder,
                                 mergetimelimit = 0.25,
                                 ymin = -0.2, ymax = 0.8,
                                 xmin = -9, xmax = 4.1,
                                 xbins = 50, ybins = 50,
                                 title = ''):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x = data[:,0]
    f775w = data[:,1]
    f850lp = data[:,2]
    uvcolor = f775w - f850lp
    tmerge = data[:,3]
    tmajor = data[:,4]
    #masks
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
#    fig = P.figure()
    fig = P.figure(figsize= (10,10))
    fig.subplots_adjust(left = 0.09, bottom = 0.08,
                        right = 0.93, top = 0.95,
                        wspace = 0.0, hspace = 0.0)
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    #make contours
    lv = N.linspace(0.2, N.max(zm), 4)
    cont = ax1.contour(x_vec, y_vec, zm, linewidths  = 0.9,
                       levels = lv, colors = 'black')
    cont = ax2.contour(x_vec, y_vec, zm, linewidths  = 0.9,
                       levels = lv, colors = 'black')
    cont = ax3.contour(x_vec, y_vec, zm, linewidths  = 0.9,
                       levels = lv, colors = 'black')
    cont = ax4.contour(x_vec, y_vec, zm, linewidths  = 0.9,
                       levels = lv, colors = 'black')
    #plot scatters
    s1 = ax1.scatter(N.log10(x[majorsMask]), uvcolor[majorsMask],
                     s=4, c=1000.*tmajor[majorsMask], marker='o',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     label = 'Major Merger: $T \leq %.0f$ Myr' % (mergetimelimit*1000.),
                     alpha = 0.25)
    s2 = ax2.scatter(N.log10(x[mergersMask]), uvcolor[mergersMask],
                     s=6, c=1000.*tmerge[mergersMask], marker='^',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     label = 'Minor Merger: $T \leq %.0f$ Myr' % (mergetimelimit*1000.),
                     alpha = 0.25)
    s2 = ax2.scatter(N.log10(x[mergersMask]), uvcolor[mergersMask],
                     s=6, c=1000.*tmerge[mergersMask], marker='^',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     visible = False)
    #masks
    mergetimelimit *= 2.
    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
    majorsMask2 = (tmajor > mergetimelimit)
    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) & \
                  (majorsMask == False) & (majorsMask2 == False)
    s3 = ax3.scatter(N.log10(x[majorsMask]), uvcolor[majorsMask],
                     s=4, c=1000.*tmajor[majorsMask], marker='o',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     label = 'Major Merger: $T \leq %.0f$ Myr' % (mergetimelimit*1000.),
                     alpha = 0.25)
    s4 = ax4.scatter(N.log10(x[mergersMask]), uvcolor[mergersMask],
                     s=6, c=1000.*tmerge[mergersMask], marker='^',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     label = 'Minor Merger: $T \leq %.0f$ Myr' % (mergetimelimit*1000.),
                     alpha = 0.25)
    s4 = ax4.scatter(N.log10(x[mergersMask]), uvcolor[mergersMask],
                     s=6, c=1000.*tmerge[mergersMask], marker='^',
                     cmap = cm.get_cmap('jet'), edgecolor = 'none',
                     visible = False)

    c1 = fig.colorbar(s2, ax = ax2, shrink = 0.7, fraction = 0.05)
    c2 = fig.colorbar(s4, ax = ax4, shrink = 0.7, fraction = 0.05)
    c1.set_label('Time since merger [Myr]')
    c2.set_label('Time since merger [Myr]')
    #add annotate
    P.text(1.0, 1.04,title,
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
               shadow = True, fancybox = True, markerscale=3)
    ax2.legend(loc = 'upper left', scatterpoints = 1,
               shadow = True, fancybox = True, markerscale=3)
    ax3.legend(loc = 'upper left', scatterpoints = 1,
               shadow = True, fancybox = True, markerscale=3)
    ax4.legend(loc = 'upper left', scatterpoints = 1,
               shadow = True, fancybox = True, markerscale=3)
    P.savefig(out_folder + output)

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/mergers/'
    db = 'sams.db'

    type = '.png'

    print 'Begin plotting'
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch1_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{3.4}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC1Merger'+type,
                        out_folder)
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch2_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{4.5}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC2Merger'+type,
                        out_folder)
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch3_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch3_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{5.8}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC3Merger'+type,
                        out_folder)
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch4_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{8.0}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC4Merger'+type,
                        out_folder)
###############################################################################
    print 'IR bright galaxies only'
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 5e-3 and
                FIR.irac_ch1_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{3.4}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC1MergerIRBright'+type,
                        out_folder, xmin = 0.1,
                        title = 'Galaxies with $S_{250} > 5$mJy in $2 \leq z < 4$')
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 5e-3 and
                FIR.irac_ch2_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{4.5}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC2MergerIRBright'+type,
                        out_folder, xmin = 0.1,
                        title = 'Galaxies with $S_{250} > 5$mJy in $2 \leq z < 4$')
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch3_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 5e-3 and
                FIR.irac_ch3_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{5.8}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC3MergerIRBright'+type,
                        out_folder, xmin = 0.1,
                        title = 'Galaxies with $S_{250} > 5$mJy in $2 \leq z < 4$')
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 5e-3 and
                FIR.irac_ch4_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{8.0}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC4MergerIRBright'+type,
                        out_folder, xmin = 0.1,
                        title = 'Galaxies with $S_{250} > 5$mJy in $2 \leq z < 4$')
###############################################################################
##############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 5e-6 and
                FIR.irac_ch1_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{3.4}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC1MergerIRBrightish'+type,
                        out_folder, xmin = 0.1,
                        title = '$\mathrm{Galaxies \ with \ } S_{250} > 5 \ \mu \mathrm{Jy\ in \ } 2 \leq z < 4$')
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 5e-6 and
                FIR.irac_ch2_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{4.5}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC2MergerIRBrightish'+type,
                        out_folder, xmin = 0.1,
                        title = '$\mathrm{Galaxies \ with \ } S_{250} > 5 \ \mu \mathrm{Jy\ in \ } 2 \leq z < 4$')
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch3_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 5e-6 and
                FIR.irac_ch3_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{5.8}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC3MergerIRBrightish'+type,
                        out_folder, xmin = 0.1,
                        title = '$\mathrm{Galaxies \ with \ } S_{250} > 5 \ \mu \mathrm{Jy\ in \ } 2 \leq z < 4$')
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 5e-6 and
                FIR.irac_ch4_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{8.0}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractions(query, xlab, ylab,'ColorColorIRAC4MergerIRBrightish'+type,
                        out_folder, xmin = 0.1,
                        title = '$\mathrm{Galaxies \ with \ } S_{250} > 5 \ \mu \mathrm{Jy\ in \ } 2 \leq z < 4$')
##############################################################################
    # multiplots
    print 'Starting multiplots'
################################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch1_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{3.4}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,'ColorColorIRAC1Multi'+type,
                                 out_folder)
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch2_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{4.5}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,'ColorColorIRAC2Multi'+type,
                                 out_folder)
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch3_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch3_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{5.8}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,'ColorColorIRAC3Multi'+type,
                                 out_folder)
##############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch4_obs > 1e-15

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{8.0}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,'ColorColorIRAC4Multi'+type,
                                 out_folder)
##############################################################################
##############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch4_obs > 1e-15 and
                galprop.mhalo > 11.5

                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{8.0}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,
                                 'ColorColorIRAC4MultiLDM'+type,
                                 out_folder,
                                 title = '$\log_{10}(M_{\mathrm{DM}}) > 11.5$',
                                 xmin = 0.5, xmax = 4.)
################################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 5e-3 and
                FIR.irac_ch4_obs > 1e-15
                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{8.0}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,
                                 'ColorColorIRAC4MultiLSPIRE'+type,
                                 out_folder,
                                 title = '$S_{250} > 5\ \mathrm{mJy}$',
                                 xmin = 0.5, xmax = 4.0)
################################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.z < 2.5 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch4_obs > 1e-15
                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{8.0}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,
                                 'ColorColorIRAC4MultiLz2'+type,
                                 out_folder,
                                 title = '$2.0 \leq z < 2.5$')
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.5 and
                FIR.z < 3.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch4_obs > 1e-15
                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{8.0}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,
                                 'ColorColorIRAC4MultiLz25'+type,
                                 out_folder,
                                 title = '$2.5 \leq z < 3.0$')
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 3.0 and
                FIR.z < 3.5 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch4_obs > 1e-15
                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{8.0}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,
                                 'ColorColorIRAC4MultiLz3'+type,
                                 out_folder,
                                 title = '$3.0 \leq z < 3.5$')
###############################################################################
    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 3.5 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id and
                FIR.spire250_obs < 1e6 and
                galphotdust.f775w < 33 and
                galphotdust.f850lp < 33 and
                FIR.spire250_obs > 1e-15 and
                FIR.irac_ch4_obs > 1e-15
                '''
    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{8.0}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot(query, xlab, ylab,
                                 'ColorColorIRAC4MultiLz35'+type,
                                 out_folder,
                                 title = '$3.5 \leq z < 4.0$')
###############################################################################
    print 'All done'
