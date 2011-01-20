import matplotlib
#matplotlib.use('PS')
matplotlib.use('Agg')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.1)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 2
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

def plotMergerFractions(query,
                        xlabel, ylabel,
                        output, out_folder,
                        mergetimelimit = 0.25,
                        mstarmin = 8.0,
                        mstarmax = 11.5,
                        mbins = 15,
                        ymin = -0.01,
                        ymax = 1.01,
                        logscale = False):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    mstar = data[:,0]
    tmerge = data[:,1]
    tmajor = data[:,2]
    #masks
    nomergeMask = tmerge < -99
    mergersMask = (tmerge >= 0.0) & (tmerge < mergetimelimit)
    majorsMask = (tmajor >= 0.0) & (tmajor < mergetimelimit)
    mergersMask2 = (tmerge >= 0.0) & (tmerge < mergetimelimit*2.)
    majorsMask2 = (tmajor >= 0.0) & (tmajor < mergetimelimit*2.)
    #bin the data
    mids, numbs = dm.binAndReturnMergerFractions(mstar,
                                                 nomergeMask,
                                                 mergersMask,
                                                 majorsMask,
                                                 mstarmin,
                                                 mstarmax,
                                                 mbins,
                                                 logscale)
    mids2, numbs2 = dm.binAndReturnMergerFractions(mstar,
                                                    nomergeMask,
                                                    mergersMask2,
                                                    majorsMask2,
                                                    mstarmin,
                                                    mstarmax,
                                                    mbins,
                                                    logscale)
    #the fraction of mergers
    noMergerFraction = [float(x[1]) / x[0] for x in numbs]
    mergerFraction = [float(x[2]-x[3]) / x[0] for x in numbs]
    majorMergerFraction = [float(x[3]) / x[0] for x in numbs]
    mergerFraction2 = [float(x[2]-x[3]) / x[0] for x in numbs2]
    majorMergerFraction2 = [float(x[3]) / x[0] for x in numbs2]

    #make the figure
#    fig = P.figure()
    fig = P.figure(figsize= (10,10))
    fig.subplots_adjust(left = 0.08, bottom = 0.07,
                        right = 0.97, top = 0.93)
    ax1 = fig.add_subplot(111)
    #draw lines
    ax1.plot(mids, noMergerFraction, 'k-', lw = 2.6,
             label = 'Never Merged')
    ax1.plot(mids, mergerFraction, ls = '--', lw = 2.6,
             label = 'Minor Merger: $T < 250$ Myr')
    ax1.plot(mids2, mergerFraction2, ls = '-.', lw = 2.6,
             label = 'Minor Merger: $T < 500$ Myr')
    ax1.plot(mids, majorMergerFraction, ls = '--', lw = 2.6,
             label = 'Major Merger: $T < 250$ Myr')
    ax1.plot(mids2, majorMergerFraction2, ls = '-.', lw = 2.6,
             label = 'Major Merger: $T < 500$ Myr')
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

def plotMergerFractions2(query,
                         xlabel, ylabel,
                         output, out_folder,
                         mergetimelimit = 0.25,
                         mstarmin = 8.0,
                         mstarmax = 11.5,
                         mbins = 15,
                         ymin = 0.0,
                         ymax = 1.0,
                         logscale = False):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    if logscale:
        mstar = N.log10(data[:,0])
        logscale = False
    else:
        mstar = data[:,0]
    print N.min(mstar), N.max(mstar)
    tmerge = data[:,1]
    tmajor = data[:,2]
    #masks
    nomergeMask = tmerge < -99
    mergersMask = (tmerge >= 0.0) & (tmerge <= mergetimelimit)
    majorsMask = (tmajor >= 0.0) & (tmajor <= mergetimelimit)
    mergersMask2 = (tmerge >= 0.0) & (tmerge > mergetimelimit)
    majorsMask2 = (tmajor >= 0.0) & (tmajor > mergetimelimit)
    #bin the data
    mids, numbs = dm.binAndReturnMergerFractions(mstar,
                                                 nomergeMask,
                                                 mergersMask,
                                                 majorsMask,
                                                 mstarmin,
                                                 mstarmax,
                                                 mbins,
                                                 logscale)
    mids2, numbs2 = dm.binAndReturnMergerFractions(mstar,
                                                   nomergeMask,
                                                   mergersMask2,
                                                   majorsMask2,
                                                   mstarmin,
                                                   mstarmax,
                                                   mbins,
                                                   logscale)
    #the fraction of mergers
    noMergerFraction = N.array([float(x[1]) / x[0] for x in numbs])
    mergerFraction = N.array([float(x[2]-x[3]) / x[0] for x in numbs])
    majorMergerFraction = N.array([float(x[3]) / x[0] for x in numbs])
    mergerFraction2 = N.array([float(x[2]-x[3]) / x[0] for x in numbs2])
    majorMergerFraction2 = N.array([float(x[3]) / x[0] for x in numbs2])

    #make the figure
#    fig = P.figure()
    fig = P.figure(figsize= (10,10))
    fig.subplots_adjust(left = 0.08, bottom = 0.07,
                        right = 0.97, top = 0.93)
    ax1 = fig.add_subplot(111)
    #calculate widths
    wd = (mids[1] - mids[0])* 1.0
    #draw bars
    ax1.bar(mids, noMergerFraction,
            label = 'Never Merged', align = 'center',
            color = 'grey', width = wd, hatch = '.')
    ax1.bar(mids, mergerFraction,
            bottom = noMergerFraction, align = 'center',
            label = 'Minor Merger: $T \leq %.0f$ Myr' % (mergetimelimit*1000.),
            color = 'red', width = wd, hatch = '/')
    ax1.bar(mids, mergerFraction2, align = 'center',
            bottom = noMergerFraction+mergerFraction,
            label = 'Minor Merger: $T > %.0f$ Myr' % (mergetimelimit*1000.),
            color = 'blue', width = wd, hatch = '|')
    ax1.bar(mids, majorMergerFraction, align = 'center',
            bottom = noMergerFraction+mergerFraction+mergerFraction2,
            label = 'Major Merger: $T \leq %.0f$ Myr' % (mergetimelimit*1000.),
            color = 'magenta', width = wd, hatch = 'x')
    ax1.bar(mids, majorMergerFraction2, align = 'center',
            bottom = noMergerFraction+mergerFraction+mergerFraction2+majorMergerFraction,
            label = 'Major Merger: $T > %.0f$ Myr' % (mergetimelimit*1000.),
            color = 'green', width = wd, hatch = '-')
    #labels
    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    #limits
    ax1.set_ylim(ymin, ymax)
    ax1.set_xlim(mids[0] - wd/2., mids[-1] +  wd/2.)
    #add annotate
    P.text(0.5, 1.05,'All galaxies in $2 \leq z < 4$',
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    #legend and save
    P.legend(loc = 'upper center')
    P.savefig(out_folder + output)

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/mergers/'
    db = 'sams.db'

    ylab = r'$\mathrm{Fraction \ of \ Sample}$'
    type = '.png'

    #plots start
################################################################################
#    query = '''select galprop.mstar, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$\log_{10}(M_{\star} \ [M_{\odot}])$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerSM'+type, out_folder,
#                        ymax = 0.5)
################################################################################
#    query = '''select galprop.mhalo, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$\log_{10}(M_{\mathrm{DM}} \ [M_{\odot}])$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerDM'+type, out_folder,
#                        mstarmin = 9.4, mstarmax = 12.9, mbins = 14,
#                        ymax = 0.6)
###############################################################################
#    query = '''select galprop.mcold, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$\log_{10}(M_{\mathrm{coldgas}} \ [M_{\odot}])$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerMcold'+type, out_folder,
#                        mstarmin = 7.0, mstarmax = 11.5, mbins = 15,
#                        ymax = 0.8)
################################################################################
#    query = '''select FIR.spire250_obs*1000, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$S_{250} \ [\mathrm{mJy}]$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerSPIRE250'+type, out_folder,
#                        mstarmin = 1, mstarmax = 40, mbins = 10, logscale = True,
#                        ymax = 0.7)
##############################################################################
#    query = '''select FIR.pacs100_obs*1000, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id
#                '''
#    xlab = r'$S_{100} \ [\mathrm{mJy}]$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerPACS100'+type, out_folder,
#                        mstarmin = 1, mstarmax = 30, mbins = 8, logscale = True)
##############################################################################
#    query = '''select galprop.mstardot, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$\log_{10}(\dot{M}_{\star} \ [M_{\odot} \ \mathrm{yr}^{-1}])$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerSFR'+type, out_folder,
#                        mstarmin = 1, mstarmax = 1000, mbins = 10, logscale = True,
#                        ymax = 1.01)
##############################################################################
    #2nd generation of plots start
##############################################################################
#    query = '''select galprop.mstar, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$\log_{10}(M_{\star} \ [M_{\odot}])$'
#    plotMergerFractions2(query, xlab, ylab,'FractionMergerSM2'+type, out_folder)
################################################################################
#    query = '''select galprop.mhalo, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$\log_{10}(M_{\mathrm{DM}} \ [M_{\odot}])$'
#    plotMergerFractions2(query, xlab, ylab,'FractionMergerDM2'+type, out_folder,
#                         mstarmin = 9.6, mstarmax = 13.5, mbins = 14)
###############################################################################
#    query = '''select galprop.mcold, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.spire250_obs < 1e6
#                '''
#    xlab = r'$\log_{10}(M_{\mathrm{coldgas}} \ [M_{\odot}])$'
#    plotMergerFractions2(query, xlab, ylab,'FractionMergerMcold2'+type, out_folder,
#                         mstarmin = 7.0, mstarmax = 11.6, mbins = 15)
###############################################################################
    query = '''select FIR.spire250_obs*1000, galprop.tmerge, galprop.tmajmerge
                from FIR, galprop where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs < 1e6 and
                FIR.spire250_obs > 1e-8
                '''
    xlab = r'$\log_{10}(S_{250} \ [\mathrm{mJy}])$'
    plotMergerFractions2(query, xlab, ylab,'FractionMergerSPIRE2502'+type, out_folder,
                         mstarmin = -2, mstarmax = 2.2, mbins = 13, logscale = True)
##############################################################################
#    query = '''select FIR.pacs100_obs*1000, galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id and
#                FIR.pacs100_obs > 1e-8
#                '''
#    xlab = r'$\log_{10}(S_{100} \ [\mathrm{mJy}])$'
#    plotMergerFractions(query, xlab, ylab,'FractionMergerPACS100'+type, out_folder,
#                        mstarmin = -1, mstarmax = 1, mbins = 5, logscale = True)
##############################################################################
    query = '''select galprop.mstardot, galprop.tmerge, galprop.tmajmerge
                from FIR, galprop where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs < 1e6 and 
                galprop.mstardot > 1e-5
                '''
    xlab = r'$\log_{10}(\dot{M}_{\star} \ [M_{\odot} \ \mathrm{yr}^{-1}])$'
    plotMergerFractions2(query, xlab, ylab,'FractionMergerSFR2'+type, out_folder,
                         mstarmin =  -2, mstarmax = 2.2, mbins = 16, logscale = True)