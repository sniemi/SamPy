import matplotlib
matplotlib.use('PS')
#matplotlib.use('Agg')
matplotlib.rc('text', usetex=True)
matplotlib.rcParams['font.size'] = 16
matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('axes', linewidth=1.5)
#matplotlib.rcParams['legend.fontsize'] = 10
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
matplotlib.rcParams['legend.fancybox'] = True
matplotlib.rcParams['legend.shadow'] = True
import os
import pylab as P
import numpy as N
#Sami's repository
import db.sqlite as sq
import astronomy.datamanipulation as dm
import fitting.fits as fit

def plot_sfrs(path, db, redshifts, out_folder,
              xmin=0.0, xmax=2.3, fluxlimit=5,
              obs=True):
    '''
    Plots SFR
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for reds in redshifts:
        query = '''select galprop.mstardot, FIR.pacs160_obs*1000
                from FIR, galprop where
                %s and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = sq.get_data_sqlitePowerTen(path, db, query)

        #set 1
        xd = N.log10(data[:, 1])
        yd = N.log10(data[:, 0])

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(11 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)

        msk = y50d > -10
        ax.errorbar(xbin_midd[msk], y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

        print '\nStraight line fit for z = %.1f' % zz
        tmp = fit.linearregression(xbin_midd[msk], y50d[msk],
                                   report=True)
        #tmp = fit.linearregression(xd, yd, 
        #                           report = True)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')
    #label = '$S_{160} =$ %.1f mJy' % fluxlimit)

    if obs:
        data = N.loadtxt('/Users/sammy/Dropbox/Research/Herschel/LaceySFRs.txt')
        data[:, 2] = N.log10(10 ** data[:, 2] / (1. / (1. / 0.7)))
        msk1 = data[:, 0] < 15
        msk2 = (data[:, 0] > 15) & (data[:, 0] < 35)
        msk3 = (data[:, 0] > 35) & (data[:, 0] < 55)
        msk4 = (data[:, 0] > 55) & (data[:, 0] < 70)
        msk5 = (data[:, 0] > 70) & (data[:, 0] < 80)
        ax.plot(data[msk1][:, 1], data[msk1][:, 2],
                'b--', label='$\mathrm{L10:}\ z = 0.25$')
        ax.plot(data[msk2][:, 1], data[msk2][:, 2],
                'r--', label='$\mathrm{L10:}\ z = 1.0$')
        ax.plot(data[msk3][:, 1], data[msk3][:, 2],
                'c--', label='$\mathrm{L10:}\ z = 2.0$')
        ax.plot(data[msk4][:, 1], data[msk4][:, 2],
                'm--', label='$\mathrm{L10:}\ z = 3.0$')
        ax.plot(data[msk5][:, 1], data[msk5][:, 2],
                'y--', label='$\mathrm{L10:}\ z = 4.0$')

    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(\dot{M}_{\star} \ [M_{\odot}\mathrm{yr}^{-1}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-1.2, 3)

    P.legend(loc='lower right')
    if obs:
        P.savefig(out_folder + 'sfrOBS.ps')
    else:
        P.savefig(out_folder + 'sfr.ps')


def plot_ssfr(path, db, redshifts, out_folder,
              xmin=0.0, xmax=2.3, fluxlimit=5):
    '''
    Plots SSFR. 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for reds in redshifts:
        query = '''select galprop.mstardot, galprop.mstar, FIR.pacs160_obs
                from FIR, galprop where
                %s and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = sq.get_data_sqlitePowerTen(path, db, query)

        #set 1
        xd = N.log10(data[:, 2] * 1e3)
        yd = N.log10(data[:, 0] / 10 ** data[:, 1])

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(9 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)

        msk = y50d > -20
        ax.errorbar(xbin_midd[msk], y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')
    #label = '$S_{160} =$ %.1f mJy' % fluxlimit)


    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel(r'$\log_{10} \left (\frac{\dot{M}_{\star}}{M_{\star}} \ [\mathrm{yr}^{-1}] \right )$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-11.1, -7.8)

    P.legend()#loc = 'lower right')
    P.savefig(out_folder + 'ssfr.ps')


def plot_stellarmass(path, db, redshifts, out_folder,
                     xmin=0.0, xmax=2.3, fluxlimit=5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mstar, FIR.pacs160_obs*1000
                from FIR, galprop where
                %s and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

        #set 1
        xd = N.log10(data[:, 1])
        yd = data[:, 0]

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(13 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')

    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(M_{\star} \ [M_{\odot}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(8.9, 11.8)

    P.legend(loc='lower right')
    P.savefig(out_folder + 'mstellar.ps')


def plot_Lbol(path, db, redshifts, out_folder,
              xmin=0.0, xmax=2.3, fluxlimit=5):
    '''
    Plots pacs 160 flux versus bolometric luminosity
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select FIR.L_bol, FIR.pacs160_obs
                from FIR where %s and FIR.L_bol > 0 and FIR.L_bol < 1e8''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = sq.get_data_sqlite(path, db, query)

        #set 1
        xd = N.log10(data[:, 1] * 1e3)
        yd = data[:, 0]

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(13 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')

    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(L_{\mathrm{bol}} \ [L_{\odot}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(9.6, 13.0)

    P.legend(loc='lower right')
    P.savefig(out_folder + 'Lbol.ps')

def plot_Ldust(path, db, redshifts, out_folder,
              xmin=0.0, xmax=2.3, fluxlimit=5):
    '''
    Plots pacs 160 flux versus dust luminosity
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select FIR.L_dust, FIR.pacs160_obs
                from FIR where %s and FIR.L_dust > 0 and FIR.L_dust < 1e8''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = sq.get_data_sqlite(path, db, query)

        #set 1
        xd = N.log10(data[:, 1] * 1e3)
        yd = data[:, 0]

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(13 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')

    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(L_{\mathrm{dust}} \ [L_{\odot}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(8.9, 13.0)

    P.legend(loc='lower right')
    P.savefig(out_folder + 'Ldust.ps')


def plot_coldgas(path, db, reshifts, out_folder,
                 xmin=0.0, xmax=2.3, fluxlimit=5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mcold, FIR.pacs160_obs*1000
                from FIR, galprop where
                %s and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

        #set 1
        xd = N.log10(data[:, 1])
        yd = data[:, 0]

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(13 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')

    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(M_{\mathrm{coldgas}} \ [M_{\odot}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(8.8, 11.5)

    P.legend(loc='lower right')
    P.savefig(out_folder + 'mcold.ps')


def plot_massratios(path, db, reshifts, out_folder,
                    xmin=0.0, xmax=2.0, fluxlimit=5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mcold - galprop.mstar, FIR.pacs160_obs*1000
                from FIR, galprop where
                %s and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

        #set 1
        xd = N.log10(data[:, 1])
        yd = data[:, 0]

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')

    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel(r'$\log_{10} \left ( \frac{M_{\mathrm{coldgas}}}{M_{\star}} \right )$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-1.2, 1.0)

    P.legend(loc='lower right')
    P.savefig(out_folder + 'mratio.ps')


def plot_burstmass(path, db, reshifts, out_folder,
                   xmin=0.0, xmax=2.0, fluxlimit=5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mstar_burst, FIR.pacs160_obs*1000
                from FIR, galprop where
                %s and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                galprop.mstar_burst > 0.0
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

        #set 1
        xd = N.log10(data[:, 1])
        yd = data[:, 0]

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(10 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')

    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel(r'$\log_{10} ( M_{\mathrm{starburst}})$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(7.3, 10.3)

    P.legend(loc='lower right')
    P.savefig(out_folder + 'mburst.ps')


def plot_metallicity(path, db, reshifts, out_folder,
                     xmin=0.0, xmax=2.0, fluxlimit=5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.zstar, FIR.pacs160_obs*1000
                from FIR, galprop where
                %s and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

        #set 1
        xd = N.log10(data[:, 1])
        yd = data[:, 0]

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')

    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$Z_{\star}$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-0.1, 1.5)

    P.legend(loc='lower right')
    P.savefig(out_folder + 'metallicity.ps')


def plot_starburst(path, db, reshifts, out_folder,
                   xmin=0.0, xmax=2.0, fluxlimit=5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mstar_burst - galprop.mstar, FIR.pacs160_obs*1000
                from FIR, galprop where
                %s and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

        #set 1
        xd = N.log10(data[:, 1])
        yd = data[:, 0]

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')

    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel(r'$\log_{10} \left ( \frac{M_{starbust}}{M_{\star}} \right )$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-3.0, -0.5)

    P.legend(loc='lower right')
    P.savefig(out_folder + 'mburstratio.ps')


def plot_BHmass(path, db, reshifts, out_folder,
                xmin=0.0, xmax=2.0, fluxlimit=5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mBH, FIR.pacs160_obs*1000
                from FIR, galprop where
                %s and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

        #set 1
        xd = N.log10(data[:, 1])
        yd = data[:, 0]

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')

    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(M_{BH} \ [M_{\odot}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(4.0, 8.0)

    P.legend(loc='lower right')
    P.savefig(out_folder + 'BHmass.ps')


def plot_DMmass(path, db, redshifts, out_folder,
                xmin=0.0, xmax=2.5, fluxlimit=5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mhalo, FIR.spire250_obs*1000
                from FIR, galprop where
                %s and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

        #set 1
        xd = N.log10(data[:, 1])
        yd = data[:, 0]

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(9 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins,
                                                         limit=9)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')

    ax.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(M_{\mathrm{dm}} \ [M_{\odot}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(10.98, 13.3)

    P.legend(loc='lower right')
    P.savefig(out_folder + 'DMmass.ps')


def plot_Age(path, db, redshifts, out_folder,
             xmin=0.0, xmax=2.1, fluxlimit=5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.meanage, FIR.pacs160_obs*1000
                from FIR, galprop where
                %s and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))

        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))

        #set 1
        xd = N.log10(data[:, 1])
        yd = data[:, 0]

        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12 * (xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins=nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr=[y50d[msk] - y16d[msk], y84d[msk] - y50d[msk]],
                    label='$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls=':', color='green')

    ax.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    ax.set_ylabel('Mean Age [Gyr]')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0.1, 6.0)

    P.legend(loc='lower right')
    P.savefig(out_folder + 'Age.ps')


def plot_mergerfraction(path, db, reshifts, out_folder, outname,
                        xmin=-0.01, xmax=2.3, fluxlimit=5,
                        png=True, mergetimelimit=0.25,
                        xbin=[10, 8, 9, 7, 7, 5],
                        neverMerged=False, obs=True):
    '''
    Plots 
    '''
    #figure
    if png:
        fig = P.figure(figsize=(10, 10))
        type = '.png'
    else:
        fig = P.figure()
        type = '.ps'
    fig.subplots_adjust(left=0.09, bottom=0.08,
                        right=0.93, top=0.95,
                        wspace=0.0, hspace=0.0)
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    #loop over all the redshifts
    for i, reds in enumerate(redshifts):
        if obs:
            query = '''select FIR.pacs160_obs, galprop.tmerge, galprop.tmajmerge
                    from FIR, galprop where
                    %s and
                    FIR.pacs160_obs > 5e-4 and
                    FIR.pacs160_obs < 1e6 and
                    FIR.gal_id = galprop.gal_id and
                    FIR.halo_id = galprop.halo_id
                    ''' % reds
        else:
            query = '''select FIR.pacs160, galprop.tmerge, galprop.tmajmerge
                    from FIR, galprop where
                    %s and
                    FIR.pacs160 > 8.8 and
                    FIR.pacs160 < 13.0 and
                    FIR.gal_id = galprop.gal_id and
                    FIR.halo_id = galprop.halo_id
                    ''' % reds
            #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        #get data
        data = sq.get_data_sqliteSMNfunctions(path, db, query)
        if obs:
            x = N.log10(data[:, 0] * 1e3)
        else:
            x = data[:, 0]
        tmerge = data[:, 1]
        tmajor = data[:, 2]
        print N.min(x), N.max(x)
        #masks
        nomergeMask = tmerge < 0.0
        majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
        majorsMask2 = (tmajor > mergetimelimit)
        mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) &\
                      (majorsMask == False) & (majorsMask2 == False)
        mergersMask2 = (nomergeMask == False) & (majorsMask == False) &\
                       (mergersMask == False) & (majorsMask2 == False)

        print xbin[i]
        mids, numbs = dm.binAndReturnMergerFractions2(x,
                                                      nomergeMask,
                                                      mergersMask,
                                                      majorsMask,
                                                      mergersMask2,
                                                      majorsMask2,
                                                      N.min(x),
                                                      N.max(x),
                                                      xbin[i],
                                                      False)
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

            #plots
        ax1.plot(mids, majorMergerFraction, label='$z = %.1f$' % zz)
        ax2.plot(mids, majorMergerFraction2, label='$z = %.1f$' % zz)
        ax3.plot(mids, mergerFraction, label='$z = %.1f$' % zz)
        if neverMerged:
            ax4.plot(mids, noMergerFraction, label='$z = %.1f$' % zz)
        else:
            ax4.plot(mids, mergerFraction2, label='$z = %.1f$' % zz)

    #set obs limit
    if obs:
        ax1.axvline(N.log10(fluxlimit), ls=':', color='green')
        ax2.axvline(N.log10(fluxlimit), ls=':', color='green')
        ax3.axvline(N.log10(fluxlimit), ls=':', color='green')
        ax4.axvline(N.log10(fluxlimit), ls=':', color='green')
        #labels
    if obs:
        ax3.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
        ax4.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    else:
        ax3.set_xlabel('$\log_{10}(L_{160} \ [L_{\odot}])$')
        ax4.set_xlabel('$\log_{10}(L_{160} \ [L_{\odot}])$')
    ax1.set_ylabel('$\mathrm{Merger\ Fraction}$')
    ax3.set_ylabel('$\mathrm{Merger\ Fraction}$')
    ax2.set_yticklabels([])
    ax4.set_yticklabels([])
    ax1.set_xticklabels([])
    ax2.set_xticklabels([])
    #texts
    P.text(0.5, 0.94, '$\mathrm{Major\ mergers:}\ T_{\mathrm{merge}} \leq %i \ \mathrm{Myr}$' % (mergetimelimit * 1000.)
           ,
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax1.transAxes)
    P.text(0.5, 0.94, '$\mathrm{Major\ mergers:}\ T_{\mathrm{merge}} > %i \ \mathrm{Myr}$' % (mergetimelimit * 1000.),
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax2.transAxes)
    P.text(0.5, 0.94, '$\mathrm{Minor\ mergers:}\ T_{\mathrm{merge}} \leq %i \ \mathrm{Myr}$' % (mergetimelimit * 1000.)
           ,
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax3.transAxes)
    if neverMerged:
        P.text(0.5, 0.94, '$\mathrm{Never\ Merged}$',
               horizontalalignment='center',
               verticalalignment='center',
               transform=ax4.transAxes)
    else:
        P.text(0.5, 0.94,
               '$\mathrm{Minor\ mergers:}\ T_{\mathrm{merge}} > %i \ \mathrm{Myr}$' % (mergetimelimit * 1000.),
               horizontalalignment='center',
               verticalalignment='center',
               transform=ax4.transAxes)
        #set limits
    ax1.set_xlim(xmin, xmax)
    ax1.set_ylim(-0.01, 0.95)
    ax2.set_xlim(xmin, xmax)
    ax2.set_ylim(-0.01, 0.95)
    ax3.set_xlim(xmin, xmax)
    ax3.set_ylim(-0.01, 0.95)
    ax4.set_xlim(xmin, xmax)
    ax4.set_ylim(-0.01, 0.95)
    #make legend and save the figure
    ax3.legend(loc='center left')
    P.savefig(out_folder + outname + type)


def plot_mergerfraction2(path, db, redshifts, out_folder, outname,
                         xmin=-0.01, xmax=2.3, fluxlimit=5,
                         png=True, mergetimelimit=0.25,
                         xbin=[10, 8, 9, 7, 7, 5],
                         neverMerged=False, obs=True):
    '''
    Plots
    '''
    #figure
    if png:
        fig = P.figure(figsize=(10, 10))
        type = '.png'
    else:
        fig = P.figure()
        type = '.ps'
    fig.subplots_adjust(left=0.09, bottom=0.08,
                        right=0.93, top=0.95,
                        wspace=0.0, hspace=0.0)
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)
    #loop over all the redshifts
    for i, reds in enumerate(redshifts):
        if obs:
            query = '''select FIR.pacs160_obs, galprop.tmerge, galprop.tmajmerge
                    from FIR, galprop where
                    %s and
                    FIR.pacs160_obs > 5e-4 and
                    FIR.pacs160_obs < 1e6 and
                    FIR.gal_id = galprop.gal_id and
                    FIR.halo_id = galprop.halo_id
                    ''' % reds
        else:
            query = '''select FIR.pacs160, galprop.tmerge, galprop.tmajmerge
                    from FIR, galprop where
                    %s and
                    FIR.pacs160 > 8.8 and
                    FIR.pacs160 < 13.0 and
                    FIR.gal_id = galprop.gal_id and
                    FIR.halo_id = galprop.halo_id
                    ''' % reds
            #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        #get data
        data = sq.get_data_sqliteSMNfunctions(path, db, query)
        if obs:
            x = N.log10(data[:, 0] * 1e3)
        else:
            x = data[:, 0]
        tmerge = data[:, 1]
        tmajor = data[:, 2]
        print N.min(x), N.max(x)
        #masks
        nomergeMask = tmerge < 0.0
        majorsMask = (tmajor >= 0.0) & (tmajor <= mergetimelimit)
        majorsMask2 = (tmerge >= 0.0) & (tmerge <= mergetimelimit * 2.)
        mergersMask = (tmerge >= 0.0) & (tmerge <= mergetimelimit) &\
                      (majorsMask == False)
        mergersMask2 = (nomergeMask == False) & (majorsMask == False) &\
                       (mergersMask == False) & (majorsMask2 == False)
        #mergersMask2 = (tmerge > mergetimelimit) & (tmerge <= 2*mergetimelimit) & \
        #              (majorsMask == False) & (majorsMask2 == False)


        print xbin[i]
        mids, numbs = dm.binAndReturnMergerFractions2(x,
                                                      nomergeMask,
                                                      mergersMask,
                                                      majorsMask,
                                                      mergersMask2,
                                                      majorsMask2,
                                                      N.min(x),
                                                      N.max(x),
                                                      xbin[i],
                                                      False)
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

        #plots
        ax1.plot(mids, majorMergerFraction, label='$z = %.1f$' % zz)
        ax2.plot(mids, majorMergerFraction2, label='$z = %.1f$' % zz)
        ax3.plot(mids, mergerFraction, label='$z = %.1f$' % zz)
        if neverMerged:
            ax4.plot(mids, noMergerFraction, label='$z = %.1f$' % zz)
        else:
            ax4.plot(mids, mergerFraction2, label='$z = %.1f$' % zz)

    #set obs limit
    if obs:
        ax1.axvline(N.log10(fluxlimit), ls=':', color='green')
        ax2.axvline(N.log10(fluxlimit), ls=':', color='green')
        ax3.axvline(N.log10(fluxlimit), ls=':', color='green')
        ax4.axvline(N.log10(fluxlimit), ls=':', color='green')
        #labels
    if obs:
        ax3.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
        ax4.set_xlabel('$\log_{10}(S_{160} \ [\mathrm{mJy}])$')
    else:
        ax3.set_xlabel('$\log_{10}(L_{160} \ [L_{\odot}])$')
        ax4.set_xlabel('$\log_{10}(L_{160} \ [L_{\odot}])$')
    ax1.set_ylabel('$\mathrm{Merger\ Fraction}$')
    ax3.set_ylabel('$\mathrm{Merger\ Fraction}$')
    ax2.set_yticklabels([])
    ax4.set_yticklabels([])
    ax1.set_xticklabels([])
    ax2.set_xticklabels([])
    #texts
    P.text(0.5, 0.94, '$\mathrm{Major\ mergers:}\ T_{\mathrm{merge}} \leq %i \ \mathrm{Myr}$' % (mergetimelimit * 1000.)
           ,
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax1.transAxes)
    P.text(0.5, 0.94, '$\mathrm{All\ mergers:}\ T_{\mathrm{merge}} \leq %i \ \mathrm{Myr}$' % (mergetimelimit * 2e3),
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax2.transAxes)
    P.text(0.5, 0.94, '$\mathrm{Minor\ mergers:}\ T_{\mathrm{merge}} \leq %i \ \mathrm{Myr}$' % (mergetimelimit * 1000.)
           ,
           horizontalalignment='center',
           verticalalignment='center',
           transform=ax3.transAxes)
    if neverMerged:
        P.text(0.5, 0.94, '$\mathrm{Never\ Merged}$',
               horizontalalignment='center',
               verticalalignment='center',
               transform=ax4.transAxes)
    else:
        P.text(0.5, 0.94,
               '$\mathrm{Minor\ mergers:}\ T_{\mathrm{merge}} \leq %i \ \mathrm{Myr}$' % (mergetimelimit * 2e3),
               horizontalalignment='center',
               verticalalignment='center',
               transform=ax4.transAxes)
        #set limits
    ax1.set_xlim(xmin, xmax)
    ax1.set_ylim(-0.01, 0.95)
    ax2.set_xlim(xmin, xmax)
    ax2.set_ylim(-0.01, 0.95)
    ax3.set_xlim(xmin, xmax)
    ax3.set_ylim(-0.01, 0.95)
    ax4.set_xlim(xmin, xmax)
    ax4.set_ylim(-0.01, 0.95)
    #make legend and save the figure
    ax4.legend()#loc = 'center right')
    P.savefig(out_folder + outname + type)

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    #path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    path = hm + '/Research/Herschel/runs/big_volume/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/predictions/big/250/'
    db = 'sams.db'

    redshifts = ['FIR.z > 0.1 and FIR.z < 0.3',
                 'FIR.z > 0.4 and FIR.z < 0.6',
                 'FIR.z > 0.9 and FIR.z < 1.1',
                 'FIR.z > 1.9 and FIR.z < 2.1',
                 'FIR.z > 2.9 and FIR.z < 3.1',
                 'FIR.z > 3.8 and FIR.z < 4.2']

    print 'Begin plotting'
    print 'Input DB: ', path + db
    print 'Output folder: ', out_folder

    #These plots are in the paper
#    plot_sfrs(path, db, redshifts, out_folder, obs=False)
#    plot_mergerfraction2(path, db, redshifts, out_folder, 'MergeFractions',
#                         xbin = [10,8,7,7,5,5], png = False, neverMerged = True)
#    plot_stellarmass(path, db, redshifts, out_folder)
#    plot_coldgas(path, db, redshifts, out_folder)
#    plot_ssfr(path, db, redshifts, out_folder)
#    plot_Lbol(path, db, redshifts, out_folder)
#    plot_Ldust(path, db, redshifts, out_folder)

    plot_DMmass(path, db, redshifts, out_folder)


    #TEST plots
#    plot_mergerfraction(path, db, redshifts, out_folder, 'MergeFractions',
#                        xbin = [10,8,9,7,5,5], png = False)
#    plot_sfrs(path, db, redshifts, out_folder, obs = True)
#    plot_massratios(path, db, redshifts, out_folder)
#    plot_metallicity(path, db, redshifts, out_folder)
#    plot_starburst(path, db, redshifts, out_folder)
#    plot_BHmass(path, db, redshifts, out_folder)
#    plot_Age(path, db, redshifts, out_folder)
#    plot_burstmass(path, db, redshifts, out_folder)
#    plot_mergerfraction(path, db, redshifts, out_folder, 'Merge')
#    plot_mergerfraction(path, db, redshifts, out_folder, 'Merge3',
#                        xbin = [8,8,8,8,8,8], xmin = 9, xmax = 11.85,
#                        obs = False)