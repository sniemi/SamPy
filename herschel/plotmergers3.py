"""
Generates some prediction plots for the Herschel I paper.

:author: Sami-Matias Niemi
:contact: sammy@sammyniemi.com

:version: 0.5
"""
import matplotlib
matplotlib.use('PS')
#matplotlib.use('Agg')
matplotlib.rc('text', usetex=True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('axes', linewidth=1.1)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 3
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import os
import pylab as P
import numpy as N
import SamPy.db.sqlite as sq
import SamPy.astronomy.datamanipulation as dm


def plotMergerFractions(query,
                        xlabel, ylabel,
                        output, out_folder,
                        mergetimelimit=0.25,
                        mstarmin=8.0,
                        mstarmax=11.5,
                        mbins=15,
                        ymin=-0.001,
                        ymax=1.01,
                        logscale=False):
    """
    Plot merger fractions.
    """
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    #mstar = N.log10(data[:, 0])
    mstar = data[:, 0]
    tmerge = data[:, 1]
    tmajor = data[:, 2]
    print N.min(mstar), N.max(mstar)
    #masks
    nomergeMask = tmerge < 0.0
    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
    majorsMask2 = (tmajor > mergetimelimit) & (tmajor <= 0.5)
    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) &\
                  (majorsMask == False) & (majorsMask2 == False)
    mergersMask2 = (tmerge > mergetimelimit) & (tmerge <= 0.5) &\
                   (majorsMask2 == False)
    #bin the data
    mids, numbs = dm.binAndReturnMergerFractions2(mstar,
                                                  nomergeMask,
                                                  mergersMask,
                                                  majorsMask,
                                                  mergersMask2,
                                                  majorsMask2,
                                                  mstarmin,
                                                  mstarmax,
                                                  mbins,
                                                  logscale)
    #the fraction of mergers
    noMergerFraction = [float(x[1]) / x[0] for x in numbs]
    mergerFraction = [float(x[2]) / x[0] for x in numbs]
    majorMergerFraction = [float(x[3]) / x[0] for x in numbs]
    mergerFraction2 = [float(x[4]) / x[0] for x in numbs]
    majorMergerFraction2 = [float(x[5]) / x[0] for x in numbs]

    #sanity check
    for a, b, c, d, e in zip(noMergerFraction, mergerFraction, majorMergerFraction,
                             mergerFraction2, majorMergerFraction2):
        print a + b + c + d + e

    #make the figure
    if 'ps' in output:
        fig = P.figure()
    else:
        fig = P.figure(figsize=(10, 10))
    fig.subplots_adjust(left=0.08, bottom=0.07,
                        right=0.97, top=0.93)
    ax1 = fig.add_subplot(111)
    #draw lines ["-","--","-.",":"]
    ax1.plot(mids, noMergerFraction, 'k-', lw=2.6,
             label='Never Merged')
    #    ax1.plot(mids, mergerFraction, ls = '--', lw = 2.6,
    #             label = 'Minor Merger: $T \leq 250$ Myr')
    #    ax1.plot(mids, mergerFraction2, ls = '-.', lw = 2.6,
    #             label = 'Minor Merger: $250 < T \leq 500$ Myr')
    #    ax1.plot(mids, majorMergerFraction, ls = '--', lw = 2.6,
    #             label = 'Major Merger: $T \leq 250$ Myr')
    #    ax1.plot(mids, majorMergerFraction2, ls = '-.', lw = 2.6,
    #             label = 'Major Merger: $250 < T \leq 500$ Myr')
    ax1.plot(mids, majorMergerFraction, ls='-', lw=2.6, c='0.3',
             label='Young Major Merger')
    ax1.plot(mids, mergerFraction, ls='-.', lw=2.6, c='0.2',
             label='Young Minor Merger')
    ax1.plot(mids, majorMergerFraction2, ls='--', lw=2.6, c='0.4',
             label='Old Major Merger')
    ax1.plot(mids, mergerFraction2, ls=':', lw=2.6, c='0.5',
             label='Old Minor Merger')
    #labels
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    #limits
    ax1.set_ylim(ymin, ymax)
    #add annotate
    P.text(0.5, 0.93, 'All galaxies\n$2 \leq z < 4$',
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax1.transAxes)
    #legend and save
    P.legend(loc='upper left')
    P.savefig(out_folder + output)


def plotMergerFractions2(query,
                         xlabel, ylabel,
                         output, out_folder,
                         mergetimelimit=0.25,
                         mstarmin=8.0,
                         mstarmax=11.5,
                         mbins=15,
                         ymin=0.0,
                         ymax=1.0,
                         logscale=False):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    if logscale:
        mstar = N.log10(data[:, 0])
        logscale = False
    else:
        mstar = data[:, 0]
    print N.min(mstar), N.max(mstar)
    tmerge = data[:, 1]
    tmajor = data[:, 2]
    #masks
    nomergeMask = tmerge < 0.0
    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
    majorsMask2 = (tmajor > mergetimelimit)
    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) &\
                  (majorsMask == False) & (majorsMask2 == False)
    mergersMask2 = (nomergeMask == False) & (majorsMask == False) &\
                   (mergersMask == False) & (majorsMask2 == False)
    #bin the data
    mids, numbs = dm.binAndReturnMergerFractions2(mstar,
                                                  nomergeMask,
                                                  mergersMask,
                                                  majorsMask,
                                                  mergersMask2,
                                                  majorsMask2,
                                                  mstarmin,
                                                  mstarmax,
                                                  mbins,
                                                  logscale)
    #the fraction of mergers
    noMergerFraction = N.array([float(x[1]) / x[0] for x in numbs])
    mergerFraction = N.array([float(x[2]) / x[0] for x in numbs])
    majorMergerFraction = N.array([float(x[3]) / x[0] for x in numbs])
    mergerFraction2 = N.array([float(x[4]) / x[0] for x in numbs])
    majorMergerFraction2 = N.array([float(x[5]) / x[0] for x in numbs])

    #sanity check
    for a, b, c, d, e in zip(noMergerFraction, mergerFraction, majorMergerFraction,
                             mergerFraction2, majorMergerFraction2):
        print a + b + c + d + e

        #make the figure
    #    fig = P.figure()
    fig = P.figure(figsize=(10, 10))
    fig.subplots_adjust(left=0.08, bottom=0.1,
                        right=0.97, top=0.93)
    ax1 = fig.add_subplot(111)
    #calculate widths
    wd = (mids[1] - mids[0]) * 1.0
    #draw bars
    ax1.bar(mids, noMergerFraction,
            label='Never Merged', align='center',
            color='grey', width=wd, hatch='.')
    ax1.bar(mids, mergerFraction,
            bottom=noMergerFraction, align='center',
            label='Minor Merger: $T \leq %.0f$ Myr' % (mergetimelimit * 1000.),
            color='red', width=wd, hatch='/')
    ax1.bar(mids, mergerFraction2, align='center',
            bottom=noMergerFraction + mergerFraction,
            label='Minor Merger: $T > %.0f$ Myr' % (mergetimelimit * 1000.),
            color='blue', width=wd, hatch='|')
    ax1.bar(mids, majorMergerFraction, align='center',
            bottom=noMergerFraction + mergerFraction + mergerFraction2,
            label='Major Merger: $T \leq %.0f$ Myr' % (mergetimelimit * 1000.),
            color='magenta', width=wd, hatch='x')
    ax1.bar(mids, majorMergerFraction2, align='center',
            bottom=noMergerFraction + mergerFraction + mergerFraction2 + majorMergerFraction,
            label='Major Merger: $T > %.0f$ Myr' % (mergetimelimit * 1000.),
            color='green', width=wd, hatch='-')
    #labels
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_ylim(ymin, ymax)
    ax1.set_xlim(mids[0] - wd / 2., mids[-1] + wd / 2.)
    #add annotate
    P.text(0.5, 1.05, 'All galaxies in $2 \leq z < 4$',
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax1.transAxes)
    #legend and save
    P.legend(loc='upper center')
    P.savefig(out_folder + output)


def plotMergerFractions3(query,
                         xlabel, ylabel,
                         output, out_folder,
                         mergetimelimit=0.4,
                         mstarmin=8.0,
                         mstarmax=11.5,
                         mbins=15,
                         ymin=0.0,
                         ymax=1.0,
                         logscale=False):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    if logscale:
        mstar = N.log10(data[:, 0])
        logscale = False
    else:
        mstar = data[:, 0]
    print N.min(mstar), N.max(mstar)
    tmerge = data[:, 1]
    tmajor = data[:, 2]
    #masks
    nomergeMask = tmerge < 0.0
    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
    majorsMask2 = (tmajor > mergetimelimit)
    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) &\
                  (majorsMask == False) & (majorsMask2 == False)
    mergersMask2 = (nomergeMask == False) & (majorsMask == False) &\
                   (mergersMask == False) & (majorsMask2 == False)
    #bin the data
    mids, numbs = dm.binAndReturnMergerFractions2(mstar,
                                                  nomergeMask,
                                                  mergersMask,
                                                  majorsMask,
                                                  mergersMask2,
                                                  majorsMask2,
                                                  mstarmin,
                                                  mstarmax,
                                                  mbins,
                                                  logscale)
    #the fraction of mergers
    noMergerFraction = N.array([float(x[1]) / x[0] for x in numbs])
    mergerFraction = N.array([float(x[2]) / x[0] for x in numbs])
    majorMergerFraction = N.array([float(x[3]) / x[0] for x in numbs])
    mergerFraction2 = N.array([float(x[4]) / x[0] for x in numbs])
    majorMergerFraction2 = N.array([float(x[5]) / x[0] for x in numbs])

    #sanity check
    for a, b, c, d, e in zip(noMergerFraction, mergerFraction, majorMergerFraction,
                             mergerFraction2, majorMergerFraction2):
        print a + b + c + d + e

        #make the figure
    #    fig = P.figure()
    fig = P.figure(figsize=(10, 10))
    fig.subplots_adjust(left=0.08, bottom=0.1,
                        right=0.97, top=0.93)
    ax1 = fig.add_subplot(111)
    #calculate widths
    wd = (mids[1] - mids[0]) * 1.0
    #draw bars
    ax1.bar(mids, noMergerFraction,
            label='Never Merged', align='center',
            color='0.5', width=wd)#, hatch = '/')
    ax1.bar(mids, mergerFraction2, align='center',
            bottom=noMergerFraction,
            label='Minor Merger: $T > %.0f$ Myr' % (mergetimelimit * 1000.),
            color='0.7', width=wd)#, hatch = '|')
    ax1.bar(mids, majorMergerFraction2, align='center',
            bottom=noMergerFraction + mergerFraction2,
            label='Major Merger: $T > %.0f$ Myr' % (mergetimelimit * 1000.),
            color='0.9', width=wd)#, hatch = '-')
    ax1.bar(mids, majorMergerFraction, align='center',
            bottom=noMergerFraction + mergerFraction2 + majorMergerFraction2,
            label='Major Merger: $T \leq %.0f$ Myr' % (mergetimelimit * 1000.),
            color='green', width=wd)#, hatch = '.')
    ax1.bar(mids, mergerFraction,
            bottom=noMergerFraction + mergerFraction2 + majorMergerFraction2 + majorMergerFraction,
            align='center',
            label='Minor Merger: $T \leq %.0f$ Myr' % (mergetimelimit * 1000.),
            color='red', width=wd)#, hatch = 'x')

    #labels
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    ax1.set_ylim(ymin, ymax)
    ax1.set_xlim(mids[0] - wd / 2., mids[-1] + wd / 2.)
    #add annotate
    P.text(0.5, 1.05, 'All galaxies in $2 \leq z < 4$',
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax1.transAxes)
    #legend and save
    P.legend(loc='lower left')
    P.savefig(out_folder + output)

    
if __name__ == '__main__':
    #find the home directory, because
    #my user name is not always the same.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Research/Herschel/runs/big_volume/'
    out_folder = hm + '/Research/Herschel/plots/mergers/'
    db = 'sams.db'

    ylab = r'$\mathrm{Fraction \ of \ Sample}$'
    type = '.ps'

    print 'Begin plotting'
    print 'Input DB: ', path + db
    print 'Output folder: ', out_folder

    ################################################################################
    query = '''select FIR.pacs160_obs / FIR.irac_ch2_obs, galprop.tmerge, galprop.tmajmerge
                from FIR, galprop where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.pacs160_obs > 1e-5 and
                FIR.irac_ch2_obs > 1e-5 and
                FIR.pacs160_obs < 1e6 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                '''
    #xlab = r'$\log_{10} \left ( \frac{S_{160}}{S_{4.5}} \right )$'
    xlab = r'$\frac{S_{160}}{S_{4.5}}$'
    plotMergerFractions(query, xlab, ylab, 'FractionMergerPACS160IRAC2BW{0:>s}'.format(type),
                        out_folder, mstarmin=1.0, mstarmax=2000.0, mbins=10, ymax=1.0)
                        #out_folder, mstarmin=1.0, mstarmax=3.5, mbins=11, ymax=1.0)
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.spire250_obs > 1e-9 and
#                FIR.irac_ch4_obs > 1e-9 and
#                FIR.spire250_obs < 1e6 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id
#                '''
#    xlab = r'$\frac{S_{250}}{S_{8}}$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerSPIRE250IRAC4'+type,
#                        out_folder, mstarmin = 0.0, mstarmax = 2000, mbins = 14,
#                        logscale = False, ymax = 1.0)
#
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$\frac{S_{250}}{S_{3.4}}$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerSPIRE250IRAC1'+type,
#                        out_folder, mstarmin = 0.0, mstarmax = 2500, mbins = 12,
#                        logscale = False, ymax = 0.5)
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.spire250_obs > 1e-8 and
#                FIR.spire250_obs < 1e6 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id
#                '''
#    xlab = r'$\frac{S_{250}}{S_{4.5}}$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerSPIRE250IRAC2'+type,
#                        out_folder, mstarmin = 0.0, mstarmax = 1500, mbins = 12,
#                        logscale = False, ymax = 0.5)
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch3_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$\frac{S_{250}}{S_{5.8}}$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerSPIRE250IRAC3'+type,
#                        out_folder, mstarmin = 0.0, mstarmax = 1600, mbins = 12,
#                        logscale = False, ymax = 1.01)
################################################################################
#    query = '''select galphotdust.f775w - galphotdust.f850lp, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop, galphotdust where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.gal_id = galphotdust.gal_id and
#                FIR.halo_id = galphotdust.halo_id and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$\mathrm{F775W} - \mathrm{F850lp}$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerUVColour'+type,
#                        out_folder, mstarmin = -.2, mstarmax = 5, mbins = 10,
#                        logscale = False, ymax = 0.5)
###############################################################################
#    #2nd generation of plots
###############################################################################
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-20 and
#                FIR.irac_ch1_obs > 1e-20
#                '''
#    xlab = r'$\log_{10}\left(\frac{S_{250}}{S_{3.4}}\right)$'
#    plotMergerFractions2(query, xlab, ylab,'FractionMergerSPIRE250IRAC12'+type,
#                        out_folder, mstarmin = -2., mstarmax = 4.,
#                        mbins = 12, logscale = True)
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-20 and
#                FIR.irac_ch2_obs > 1e-20
#                '''
#    xlab = r'$\log_{10}\left(\frac{S_{250}}{S_{4.5}}\right)$'
#    plotMergerFractions2(query, xlab, ylab,'FractionMergerSPIRE250IRAC22'+type,
#                        out_folder, mstarmin = -2, mstarmax = 4.,
#                        mbins = 12, logscale = True)
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch3_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-20 and
#                FIR.irac_ch3_obs > 1e-20
#                '''
#    xlab = r'$\log_{10}\left(\frac{S_{250}}{S_{5.8}}\right)$'
#    plotMergerFractions2(query, xlab, ylab,'FractionMergerSPIRE250IRAC32'+type,
#                        out_folder, mstarmin = -2, mstarmax = 4.,
#                        mbins = 12, logscale = True)
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-20 and
#                FIR.irac_ch4_obs > 1e-20
#                '''
#    xlab = r'$\log_{10}\left(\frac{S_{250}}{S_{8}}\right)$'
#    plotMergerFractions2(query, xlab, ylab,'FractionMergerSPIRE250IRAC42'+type,
#                        out_folder, mstarmin = -2, mstarmax = 3.5,
#                        mbins = 12, logscale = True)
##############################################################################
#3rd generation of plots
##############################################################################
###############################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch1_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-20 and
#                FIR.irac_ch1_obs > 1e-20
#                '''
#    xlab = r'$\log_{10}\left(\frac{S_{250}}{S_{3.4}}\right)$'
#    plotMergerFractions3(query, xlab, ylab,'FractionMergerSPIRE250IRAC13'+type,
#                        out_folder, mstarmin = -2, mstarmax = 4.,
#                        mbins = 12, logscale = True)
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch2_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-20 and
#                FIR.irac_ch2_obs > 1e-20
#                '''
#    xlab = r'$\log_{10}\left(\frac{S_{250}}{S_{4.5}}\right)$'
#    plotMergerFractions3(query, xlab, ylab,'FractionMergerSPIRE250IRAC23'+type,
#                        out_folder, mstarmin = -2, mstarmax = 4.,
#                        mbins = 12, logscale = True)
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch3_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-20 and
#                FIR.irac_ch3_obs > 1e-20
#                '''
#    xlab = r'$\log_{10}\left(\frac{S_{250}}{S_{5.8}}\right)$'
#    plotMergerFractions3(query, xlab, ylab,'FractionMergerSPIRE250IRAC33'+type,
#                        out_folder, mstarmin = -2, mstarmax = 4.,
#                        mbins = 12, logscale = True)
################################################################################
#    query = '''select FIR.spire250_obs / FIR.irac_ch4_obs, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6 and
#                FIR.spire250_obs > 1e-20 and
#                FIR.irac_ch4_obs > 1e-20
#                '''
#    xlab = r'$\log_{10}\left(\frac{S_{250}}{S_{8}}\right)$'
#    plotMergerFractions3(query, xlab, ylab,'FractionMergerSPIRE250IRAC43'+type,
#                        out_folder, mstarmin = -2, mstarmax = 3.5,
#                        mbins = 12, logscale = True)