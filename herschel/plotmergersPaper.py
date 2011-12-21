"""
Generates some prediction plots for the Herschel I paper.

:author: Sami-Matias Niemi
:contact: sammy@sammyniemi.com

:version: 0.5
"""
import matplotlib
#matplotlib.use('Cairo')
matplotlib.use('Agg')
matplotlib.rc('text', usetex=True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('axes', linewidth=1.1)
matplotlib.rcParams['legend.fontsize'] = 11
matplotlib.rcParams['legend.handlelength'] = 3
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import pylab as P
import os
import numpy as N
from matplotlib import cm
import SamPy.db.sqlite as sq
import SamPy.sandbox.MyTools as M
import SamPy.smnIO.sextutils as sex
import SamPy.astronomy.conversions as cv


def ujy_to_abmag(flux):
    ab = N.zeros(len(flux)) + 99
    msk = flux > 0.
    ab[msk] = 23.9 - 2.5 * N.log10(flux[msk])
    return ab


def plotMergerFractionsMultiplot(query, xlabel, ylabel,
                                 output, out_folder, obs,
                                 mergetimelimit=0.25,
                                 ymin=-0.2, ymax=1.5,
                                 xmin=-1.9, xmax=4.15,
                                 xbins=80, ybins=80,
                                 title='Simulated Galaxies',
                                 size=4.5, alpha=0.2, ch=1):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x = data[:, 0]
    f775w = data[:, 1]
    f850lp = data[:, 2]
    uvcolor = f775w - f850lp
    tmerge = data[:, 3]
    tmajor = data[:, 4]

    #masks for simulated galaxies
    nomergeMask = tmerge < 0.0
    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
    majorsMask2 = (tmajor > mergetimelimit)
    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) &\
                  (majorsMask == False) & (majorsMask2 == False)
    mergersMask2 = (nomergeMask == False) & (majorsMask == False) &\
                   (mergersMask == False) & (majorsMask2 == False)

    #KDE
    mu = M.AnaKDE([N.log10(x[nomergeMask]), uvcolor[nomergeMask]])
    x_vec, y_vec, zm, lvls, d0, d1 = mu.contour(N.linspace(xmin, xmax, xbins),
                                                N.linspace(ymin, ymax, ybins),
                                                return_data=True)
    #make the figure
    #fig = P.figure()
    fig = P.figure(figsize=(10, 10))
    fig.subplots_adjust(left=0.09, bottom=0.08,
                        right=0.93, top=0.95,
                        wspace=0.0, hspace=0.0)
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    #make contours
    lv = N.linspace(0.015, 0.95 * N.max(zm), 5)
    cont = ax1.contour(x_vec, y_vec, zm, linewidths=0.9,
                       levels=lv, colors='black')
    cont = ax2.contour(x_vec, y_vec, zm, linewidths=0.9,
                       levels=lv, colors='black')
    cont = ax3.contour(x_vec, y_vec, zm, linewidths=0.9,
                       levels=lv, colors='black')
    cont = ax4.contour(x_vec, y_vec, zm, linewidths=0.9,
                       levels=lv, colors='black')

    #plot scatters
    s2 = ax2.scatter(N.log10(x[majorsMask]), uvcolor[majorsMask],
                     s=size, c=1000. * tmajor[majorsMask], marker='o',
                     cmap=cm.get_cmap('jet'), edgecolor='none',
                     label='Major Merger: $T \leq %.0f$ Myr' % (mergetimelimit * 1000.),
                     alpha=alpha)
    s2 = ax2.scatter(N.log10(x[majorsMask]), uvcolor[majorsMask],
                     s=size, c=1000. * tmajor[majorsMask], marker='o',
                     cmap=cm.get_cmap('jet'), edgecolor='none',
                     visible=False)
    s4 = ax4.scatter(N.log10(x[mergersMask]), uvcolor[mergersMask],
                     s=size * 1.8, c=1000. * tmerge[mergersMask], marker='^',
                     cmap=cm.get_cmap('jet'), edgecolor='none',
                     label='Minor Merger: $T \leq %.0f$ Myr' % (mergetimelimit * 1000.),
                     alpha=alpha)
    s4 = ax4.scatter(N.log10(x[mergersMask]), uvcolor[mergersMask],
                     s=size * 1.8, c=1000. * tmerge[mergersMask], marker='^',
                     cmap=cm.get_cmap('jet'), edgecolor='none',
                     visible=False)
    #Observed
    c = sex.sextractor('/Users/sammy/workspace/herschelpaper/Kuang/section5_v5/f250_detect_z2-4_VC.txt')
    c24 = sex.sextractor(
        '/Users/sammy/workspace/herschelpaper/Kuang/section5_v5/goodsh_goodsn_acsmatch_unified_z2-4.cat')
    VC = []
    for i in range(len(c24)):
        VC += [N.compress(c.id_zband == c24.id_zband[i], c.vcflag)[0]]
    VC = N.array(VC)

    # enforce upper limits in ch2 flux
    fch2 = c24.ch2_flux_ujy.copy()
    for i in range(len(fch2)):
        if c24.ch2_flux_ujy[i] < c24.ch2_fluxerr_ujy[i]:
            fch2[i] = c24.ch2_fluxerr_ujy[i]
        if fch2[i] < 0.: fch2[
                         i] = 0.5  # set a upper limit in ch2 of 0.5 uJy (it's the largest flux error in the sample; reasonable?)
        # enforce upper limits in i-band flux
    f_i = c24.i_flux_ujy.copy()
    for i in range(len(c24)):
        if c24.i_flux_ujy[i] < c24.i_fluxerr_ujy[i]:
            f_i[i] = c24.i_fluxerr_ujy[i]

    f_z = c24.z_flux_ujy.copy()
    imag = ujy_to_abmag(f_i)
    zmag = ujy_to_abmag(f_z)
    imz = imag - zmag

    l1 = ax1.scatter(N.compress(VC == 'a', N.log10(c24.f250_mjy * 1000. / fch2)), N.compress(VC == 'a', imz),
                     marker='x', s=35, color='black', label='Regulars')
    l2 = ax1.scatter(N.compress(VC == 'b', N.log10(c24.f250_mjy * 1000. / fch2)), N.compress(VC == 'b', imz),
                     marker='o', s=35, color='red', label='Mergers')
    l3 = ax1.scatter(N.compress(VC == 'c', N.log10(c24.f250_mjy * 1000. / fch2)), N.compress(VC == 'c', imz),
                     marker='^', s=35, color='gray', label='Ambiguous')
    l4 = ax1.scatter(N.compress(VC == 'd', N.log10(c24.f250_mjy * 1000. / fch2)), N.compress(VC == 'd', imz),
                     marker='s', s=35, color='blue', label='Compact core')
    zlim = 25.7
    if sum(zmag > zlim) > 0:
        l5 = ax1.scatter(N.compress(zmag > zlim, N.log10(c24.f250_mjy * 1000. / fch2)),
                         N.compress(zmag > zlim, imz), marker='o', facecolor='None', edgecolor='black', s=64,
                         label=r'$z_{850}>%.1f$' % zlim)

    l1 = ax3.scatter(N.compress(VC == 'a', N.log10(c24.f250_mjy * 1000. / fch2)), N.compress(VC == 'a', imz),
                     marker='x', s=35, color='black', label='Regulars')
    l2 = ax3.scatter(N.compress(VC == 'b', N.log10(c24.f250_mjy * 1000. / fch2)), N.compress(VC == 'b', imz),
                     marker='o', s=35, color='red', label='Mergers')
    l3 = ax3.scatter(N.compress(VC == 'c', N.log10(c24.f250_mjy * 1000. / fch2)), N.compress(VC == 'c', imz),
                     marker='^', s=35, color='gray', label='Ambiguous')
    l4 = ax3.scatter(N.compress(VC == 'd', N.log10(c24.f250_mjy * 1000. / fch2)), N.compress(VC == 'd', imz),
                     marker='s', s=35, color='blue', label='Compact core')
    zlim = 25.7
    if sum(zmag > zlim) > 0:
        l5 = ax3.scatter(N.compress(zmag > zlim, N.log10(c24.f250_mjy * 1000. / fch2)),
                         N.compress(zmag > zlim, imz), marker='o', facecolor='None', edgecolor='black', s=64,
                         label=r'$z_{850}>%.1f$' % zlim)

    #color bars
    c1 = fig.colorbar(s2, ax=ax2, shrink=0.7, fraction=0.05)
    c2 = fig.colorbar(s4, ax=ax4, shrink=0.7, fraction=0.05)
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
           transform=ax2.transAxes)
    P.text(0.5, 1.04, 'Observed Galaxies',
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax1.transAxes)
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
    #ax1.grid()
    #ax2.grid()
    #ax3.grid()
    #ax4.grid()
    #legend and save
    ax1.legend(loc='upper right', scatterpoints=1,
               shadow=True, fancybox=True, markerscale=1.5)
    ax2.legend(loc='upper left', scatterpoints=1,
               shadow=True, fancybox=True, markerscale=1.5)
    ax3.legend(loc='upper right', scatterpoints=1,
               shadow=True, fancybox=True, markerscale=1.5)
    ax4.legend(loc='upper left', scatterpoints=1,
               shadow=True, fancybox=True, markerscale=1.5)
    P.savefig(out_folder + output)


def plotMergerFractionsMultiplot2(query, xlabel, ylabel,
                                  output, out_folder,
                                  mergetimelimit=0.25,
                                  ymin=-0.1, ymax=1.1,
                                  xmin=-1.9, xmax=4.15,
                                  xbins=80, ybins=80,
                                  title='Simulated Galaxies',
                                  size=4.5, alpha=0.2):
    #get data, all galaxies
    """
    Plots merger fraction
    """
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x = data[:, 0]
    f775w = data[:, 1]
    f850lp = data[:, 2]
    uvcolor = f775w - f850lp
    tmerge = data[:, 3]
    tmajor = data[:, 4]

    #masks for simulated galaxies
    nomergeMask = tmerge < 0.0
    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
    majorsMask2 = (tmajor > mergetimelimit)
    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) &\
                  (majorsMask == False) & (majorsMask2 == False)
    mergersMask2 = (nomergeMask == False) & (majorsMask == False) &\
                   (mergersMask == False) & (majorsMask2 == False)

    #KDE
    mu = M.AnaKDE([N.log10(x[nomergeMask]), uvcolor[nomergeMask]])
    x_vec, y_vec, zm, lvls, d0, d1 = mu.contour(N.linspace(xmin, xmax, xbins),
                                                N.linspace(ymin, ymax, ybins),
                                                return_data=True)
    #make the figure
    #fig = P.figure()
    fig = P.figure(figsize=(10, 10))
    fig.subplots_adjust(left=0.09, bottom=0.08,
                        right=0.93, top=0.95,
                        wspace=0.0, hspace=0.0)
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)
    #make contours
    lv = N.linspace(0.015, 0.95 * N.max(zm), 5)
    cont = ax1.contour(x_vec, y_vec, zm, linewidths=0.9,
                       levels=lv, colors='black')
    cont = ax2.contour(x_vec, y_vec, zm, linewidths=0.9,
                       levels=lv, colors='black')

    #plot scatters
    s2 = ax1.scatter(N.log10(x[majorsMask]), uvcolor[majorsMask],
                     s=size, c=1000. * tmajor[majorsMask], marker='o',
                     cmap=cm.get_cmap('jet'), edgecolor='none',
                     label='Major Merger: $T \leq %.0f$ Myr' % (mergetimelimit * 1000.),
                     alpha=alpha)
    s2 = ax1.scatter(N.log10(x[majorsMask]), uvcolor[majorsMask],
                     s=size, c=1000. * tmajor[majorsMask], marker='o',
                     cmap=cm.get_cmap('jet'), edgecolor='none',
                     visible=False)
    s4 = ax2.scatter(N.log10(x[mergersMask]), uvcolor[mergersMask],
                     s=size * 1.8, c=1000. * tmerge[mergersMask], marker='^',
                     cmap=cm.get_cmap('jet'), edgecolor='none',
                     label='Minor Merger: $T \leq %.0f$ Myr' % (mergetimelimit * 1000.),
                     alpha=alpha)
    s4 = ax2.scatter(N.log10(x[mergersMask]), uvcolor[mergersMask],
                     s=size * 1.8, c=1000. * tmerge[mergersMask], marker='^',
                     cmap=cm.get_cmap('jet'), edgecolor='none',
                     visible=False)

    #color bars
    c1 = fig.colorbar(s2, ax=ax1, shrink=0.7, fraction=0.05)
    c2 = fig.colorbar(s4, ax=ax2, shrink=0.7, fraction=0.05)
    c1.set_label('Time since latest merger [Myr]')
    c2.set_label('Time since latest merger [Myr]')
    #plot dividing line
    x = N.array([2.0, 2.5, 3.0, 4.0])
    y = x - 2.4
    ax1.plot(x, y, 'g--', lw=1.8)
    ax2.plot(x, y, 'g--', lw=1.8)

    #add annotate
    P.text(0.5, 1.04, title,
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax1.transAxes)
    #labels
    ax1.set_ylabel(ylabel)
    ax2.set_ylabel(ylabel)
    ax2.set_xlabel(xlabel)
    ax1.set_xticklabels([])
    #limits
    ax1.set_ylim(ymin, ymax)
    ax1.set_xlim(xmin, xmax)
    ax2.set_ylim(ymin, ymax)
    ax2.set_xlim(xmin, xmax)
    #legend and save
    ax1.legend(loc='upper left', scatterpoints=1,
               shadow=True, fancybox=True, markerscale=1.5)
    ax2.legend(loc='upper left', scatterpoints=1,
               shadow=True, fancybox=True, markerscale=1.5)
    P.savefig(out_folder + output)

    
if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Research/Herschel/runs/big_volume/'
    out_folder = hm + '/Research/Herschel/plots/mergers/'
    db = 'sams.db'
    obs = hm + '/Research/Herschel/obs_data/goodsh_goodsn_allbands_z2-4.cat'

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
    #    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs,
    #                galphotdust.f775w, galphotdust.f850lp,
    #                galprop.tmerge, galprop.tmajmerge
    #                from FIR, galprop, galphotdust where
    #                FIR.z >= 2.0 and
    #                FIR.z < 4.0 and
    #                FIR.spire250_obs < 1e6 and
    #                galphotdust.f775w_obs < 50 and
    #                galphotdust.f850lp_obs < 50 and
    #                FIR.spire250_obs > 1e-4 and
    #                FIR.gal_id = galprop.gal_id and
    #                FIR.halo_id = galprop.halo_id and
    #                FIR.gal_id = galphotdust.gal_id and
    #                FIR.halo_id = galphotdust.halo_id
    #                '''
    #    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{4.5}} \right )$'
    #    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    #    plotMergerFractionsMultiplot(query, xlab, ylab,'ColorMergerPaper5'+type,
    #                                 out_folder, obs, xmin = 1.5, size = 20, xmax = 3.8,
    #                                 mergetimelimit = 0.25, alpha = 0.4, ch = 2,
    #                                 title = '$S_{250} > 10^{-4} \ \mathrm{Jy}$')
    ###############################################################################
    #    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs,
    #                galphotdust.f775w, galphotdust.f850lp,
    #                galprop.tmerge, galprop.tmajmerge
    #                from FIR, galprop, galphotdust where
    #                FIR.z >= 2.0 and
    #                FIR.spire250_obs > 5e-3 and
    #                FIR.z < 4.0 and
    #                FIR.spire250_obs < 1e6 and
    #                galphotdust.f775w_obs < 50 and
    #                galphotdust.f850lp_obs < 50 and
    #                FIR.gal_id = galprop.gal_id and
    #                FIR.halo_id = galprop.halo_id and
    #                FIR.gal_id = galphotdust.gal_id and
    #                FIR.halo_id = galphotdust.halo_id
    #                '''
    #    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{4.5}} \right )$'
    #    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    #    plotMergerFractionsMultiplot(query, xlab, ylab, 'ColorMergerPaper6' + type,
    #                                 out_folder, obs, xmin=1.5, size=30, xmax=3.8,
    #                                 mergetimelimit=0.25, alpha=0.5, ch=2,
    #                                 title='Simulated Galaxies: $S_{250} > 5 \ \mathrm{mJy}$')
    #    ###############################################################################
    #    #This is what the paper has now
    #    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs,
    #                galphotdust.f775w, galphotdust.f850lp,
    #                galprop.tmerge, galprop.tmajmerge
    #                from FIR, galprop, galphotdust where
    #                FIR.z >= 2.0 and
    #                FIR.spire250_obs > 5e-3 and
    #                FIR.z < 4.0 and
    #                FIR.spire250_obs < 1e6 and
    #                galphotdust.f775w_obs < 50 and
    #                galphotdust.f850lp_obs < 50 and
    #                FIR.gal_id = galprop.gal_id and
    #                FIR.halo_id = galprop.halo_id and
    #                FIR.gal_id = galphotdust.gal_id and
    #                FIR.halo_id = galphotdust.halo_id
    #                '''
    #    xlab = r'$\log_{10}\left ( \frac{S_{250}}{S_{4.5}} \right )$'
    #    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    #    plotMergerFractionsMultiplot2(query, xlab, ylab, 'ColorMergerPaper7'+type,
    #                                  out_folder, xmin=1.9, size=40, xmax=4.0,
    #                                  mergetimelimit=0.25, alpha=0.5,
    #                                  title='Simulated Galaxies: $S_{250} > 5 \ \mathrm{mJy}$')

    query = '''select FIR.pacs160_obs / FIR.irac_ch2_obs,
                galphotdust.f775w, galphotdust.f850lp,
                galprop.tmerge, galprop.tmajmerge
                from FIR, galprop, galphotdust where
                FIR.z >= 2.0 and
                FIR.pacs160_obs > 5e-3 and
                FIR.z < 4.0 and
                FIR.pacs160_obs < 1e6 and
                galphotdust.f775w_obs < 50 and
                galphotdust.f850lp_obs < 50 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.gal_id = galphotdust.gal_id and
                FIR.halo_id = galphotdust.halo_id
                '''
    xlab = r'$\log_{10}\left ( \frac{S_{160}}{S_{4.5}} \right )$'
    ylab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
    plotMergerFractionsMultiplot2(query, xlab, ylab, 'ColorMergerPaperBW' + type,
                                  out_folder, xmin=1.9, size=40, xmax=4.0,
                                  mergetimelimit=0.25, alpha=0.5,
                                  title='Simulated Galaxies: $S_{160} > 5 \ \mathrm{mJy}$')

    print 'All done'
