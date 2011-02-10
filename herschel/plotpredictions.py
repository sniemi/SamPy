import matplotlib
#matplotlib.use('PS')
matplotlib.use('Agg')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 16
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.2)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 1
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
matplotlib.rcParams['legend.fancybox'] = True
matplotlib.rcParams['legend.shadow'] = True
import pylab as P
import os
import numpy as N
from matplotlib import cm
#Sami's repository
import db.sqlite as sq
import astronomy.datamanipulation as dm

def plot_sfrs(path, db, reshifts, out_folder,
              xmin = 0.0, xmax = 2.0, fluxlimit = 5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for reds in redshifts:
        query = '''select galprop.mstardot, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                %s
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        
        #get data
        data = sq.get_data_sqlitePowerTen(path, db, query)
    
        #set 1
        xd = N.log10(data[:,1])
        yd = N.log10(data[:,0])
        
        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12*(xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins = nxbins)

        msk = y50d > -10
        ax.errorbar(xbin_midd[msk], y50d[msk], yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
               #label = '$S_{250} =$ %.1f mJy' % fluxlimit)
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(\dot{M}_{\star} \ [M_{\odot}\mathrm{yr}^{-1}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-1.2, 3)

    P.legend()
    P.savefig(out_folder + 'sfr.ps')
    
def plot_stellarmass(path, db, reshifts, out_folder,
                     xmin = 0.0, xmax = 2.0, fluxlimit = 5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mstar, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                %s
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        
        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))
    
        #set 1
        xd = N.log10(data[:,1])
        yd = data[:,0]
        
        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12*(xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins = nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(M_{\star} \ [M_{\odot}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(8.9, 11.5)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'mstellar.ps')

def plot_coldgas(path, db, reshifts, out_folder,
                xmin = 0.0, xmax = 2.0, fluxlimit = 5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mcold, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                %s
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        
        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))
    
        #set 1
        xd = N.log10(data[:,1])
        yd = data[:,0]
        
        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(11*(xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins = nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(M_{\mathrm{coldgas}} \ [M_{\odot}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(8.8, 11.2)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'mcold.ps')

def plot_massratios(path, db, reshifts, out_folder,
                    xmin = 0.0, xmax = 2.0, fluxlimit = 5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mcold - galprop.mstar, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                %s
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        
        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))
    
        #set 1
        xd = N.log10(data[:,1])
        yd = data[:,0]
        
        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12*(xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins = nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax.set_ylabel(r'$\log_{10} \left ( \frac{M_{\mathrm{coldgas}}}{M_{\star}} \right )$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-1.2, 1.0)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'mratio.ps')

def plot_burstmass(path, db, reshifts, out_folder,
                   xmin = 0.0, xmax = 2.0, fluxlimit = 5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mstar_burst, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                galprop.mstar_burst > 0.0 and
                %s
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        
        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))
    
        #set 1
        xd = N.log10(data[:,1])
        yd = data[:,0]
        
        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(10*(xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins = nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax.set_ylabel(r'$\log_{10} ( M_{\mathrm{starburst}})$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(7.3, 10.3)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'mburst.ps')

def plot_metallicity(path, db, reshifts, out_folder,
                     xmin = 0.0, xmax = 2.0, fluxlimit = 5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.zstar, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                %s
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        
        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))
    
        #set 1
        xd = N.log10(data[:,1])
        yd = data[:,0]
        
        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12*(xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins = nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$Z_{\star}$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-0.1, 1.5)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'metallicity.ps')

def plot_starburst(path, db, reshifts, out_folder,
                   xmin = 0.0, xmax = 2.0, fluxlimit = 5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mstar_burst - galprop.mstar, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                %s
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        
        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))
    
        #set 1
        xd = N.log10(data[:,1])
        yd = data[:,0]
        
        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12*(xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins = nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax.set_ylabel(r'$\log_{10} \left ( \frac{M_{starbust}}{M_{\star}} \right )$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-3.0, -0.5)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'mburstratio.ps')

def plot_BHmass(path, db, reshifts, out_folder,
                xmin = 0.0, xmax = 2.0, fluxlimit = 5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mBH, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                %s
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        
        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))
    
        #set 1
        xd = N.log10(data[:,1])
        yd = data[:,0]
        
        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12*(xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins = nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(M_{BH} \ [M_{\odot}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(4.0, 8.0)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'BHmass.ps') 

def plot_DMmass(path, db, reshifts, out_folder,
                xmin = 0.0, xmax = 2.0, fluxlimit = 5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.mhalo, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                %s
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        
        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))
    
        #set 1
        xd = N.log10(data[:,1])
        yd = data[:,0]
        
        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12*(xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins = nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax.set_ylabel('$\log_{10}(M_{\mathrm{dm}} \ [M_{\odot}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(11.0, 13.0)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'DMmass.ps') 

def plot_Age(path, db, reshifts, out_folder,
             xmin = 0.0, xmax = 2.1, fluxlimit = 5):
    '''
    Plots 
    '''
    #figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    for i, reds in enumerate(redshifts):
        query = '''select galprop.meanage, FIR.spire250_obs*1000
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                %s
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        
        #get data
        data = N.array(sq.get_data_sqlitePowerTen(path, db, query))
    
        #set 1
        xd = N.log10(data[:,1])
        yd = data[:,0]
        
        #percentiles
        xmaxb = N.max(xd)
        nxbins = int(12*(xmaxb - xmin))
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd,
                                                         yd,
                                                         xmin,
                                                         xmaxb,
                                                         nxbins = nxbins)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax.set_ylabel('Mean Age [Gyr]')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0.1, 6.0)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'Age.ps') 

def plot_mergerfraction(path, db, reshifts, out_folder,
                        xmin = -0.5, xmax = 2.35, fluxlimit = 5,
                        png = True, mergetimelimit = 0.5,
                        xbin = 9):
    '''
    Plots 
    '''
    #figure
    if png:
        fig = P.figure(figsize= (10,10))
        type = '.png'
    else:
        fig = P.figure()
        type = '.ps'
    fig.subplots_adjust(left = 0.09, bottom = 0.08,
                        right = 0.93, top = 0.95,
                        wspace = 0.0, hspace = 0.0)
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    for i, reds in enumerate(redshifts):
        query = '''select FIR.spire250_obs*1000, galprop.tmerge, galprop.tmajmerge
                from FIR, galprop where
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs < 1e6 and
                FIR.spire250_obs > 5e-5 and
                %s
                ''' % reds
        #tmp
        tmp = reds.split()
        zz = N.mean(N.array([float(tmp[2]), float(tmp[6])]))
        
        data = sq.get_data_sqliteSMNfunctions(path, db, query)
        x = N.log10(data[:,0])
        tmerge = data[:,1]
        tmajor = data[:,2]
        print N.min(x), N.max(x)
        #masks
        nomergeMask = tmerge < 0.0
        majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
        majorsMask2 = (tmajor > mergetimelimit)
        mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) & \
                      (majorsMask == False) & (majorsMask2 == False)
        mergersMask2 = (nomergeMask == False) & (majorsMask == False) & \
                       (mergersMask == False) & (majorsMask2 == False)
        
        #xbin =  int(N.max(x)*4.)
        if i > 0: xbin -= i - 2
        if i > 2: xbin = 6
        mids, numbs = dm.binAndReturnMergerFractions2(x,
                                                      nomergeMask,
                                                      mergersMask,
                                                      majorsMask,
                                                      mergersMask2,
                                                      majorsMask2,
                                                      N.min(x),
                                                      N.max(x),
                                                      xbin,
                                                      False)
        #the fraction of mergers
        noMergerFraction = [float(x[1]) / x[0] for x in numbs]
        mergerFraction = [float(x[2]) / x[0] for x in numbs]
        majorMergerFraction = [float(x[3]) / x[0] for x in numbs]
        mergerFraction2 = [float(x[4]) / x[0] for x in numbs]
        majorMergerFraction2 = [float(x[5]) / x[0] for x in numbs]
        
        #sanity check
        for a, b, c, d, e in zip(noMergerFraction,mergerFraction,majorMergerFraction,
                                 mergerFraction2,majorMergerFraction2):
            print a+b+c+d+e 
        
        #plots
        ax1.plot(mids, majorMergerFraction, label = '$z = %.1f$' % zz)
        ax2.plot(mids, majorMergerFraction2, label = '$z = %.1f$' % zz)
        ax3.plot(mids, mergerFraction, label = '$z = %.1f$' % zz)
        ax4.plot(mids, mergerFraction2, label = '$z = %.1f$' % zz)
        #ax4.plot(mids, noMergerFraction, label = '$z = %.1f$' % zz)

    #set obs limit
    ax1.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
    ax2.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
    ax3.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
    ax4.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    #labels
    ax3.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax4.set_xlabel('$\log_{10}(S_{250} \ [\mathrm{mJy}])$')
    ax1.set_ylabel('Merger Fraction')
    ax3.set_ylabel('Merger Fraction')
    ax2.set_yticklabels([])
    ax4.set_yticklabels([])
    ax1.set_xticklabels([])
    ax2.set_xticklabels([])
    
    #texts
    P.text(0.5, 0.94,'Major mergers: $T_{\mathrm{merge}} \leq %i$' % (mergetimelimit * 1000.),
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax1.transAxes)
    P.text(0.5, 0.94,'Major mergers: $T_{\mathrm{merge}} > %i$' % (mergetimelimit * 1000.),
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax2.transAxes)
    P.text(0.5, 0.94,'Minor mergers: $T_{\mathrm{merge}} \leq %i$' % (mergetimelimit * 1000.),
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax3.transAxes)
    P.text(0.5, 0.94,'Minor mergers: $T_{\mathrm{merge}} > %i$' % (mergetimelimit * 1000.),
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax4.transAxes)
#    P.text(0.5, 0.94,'Never Merged',
#           horizontalalignment='center',
#           verticalalignment='center',
#           transform = ax4.transAxes)

    ax1.set_xlim(xmin, xmax)
    ax1.set_ylim(-0.01, 0.95)
    ax2.set_xlim(xmin, xmax)
    ax2.set_ylim(-0.01, 0.95)
    ax3.set_xlim(xmin, xmax)
    ax3.set_ylim(-0.01, 0.95)
    ax4.set_xlim(xmin, xmax)
    ax4.set_ylim(-0.01, 0.95)

    ax3.legend(loc = 'center right')
    P.savefig(out_folder + 'Merge' + type) 

   
if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/predictions/'
    db = 'sams.db'

    redshifts = ['FIR.z > 0.1 and FIR.z < 0.3',
                 'FIR.z > 0.4 and FIR.z < 0.6',
                 'FIR.z > 0.9 and FIR.z < 1.1',
                 'FIR.z > 1.9 and FIR.z < 2.1',
                 'FIR.z > 2.9 and FIR.z < 3.1',
                 'FIR.z > 3.9 and FIR.z < 4.1']
#
#    plot_sfrs(path, db, redshifts, out_folder)
#    plot_stellarmass(path, db, redshifts, out_folder)
#    plot_massratios(path, db, redshifts, out_folder)
#    plot_metallicity(path, db, redshifts, out_folder)
#    plot_starburst(path, db, redshifts, out_folder)
#    plot_BHmass(path, db, redshifts, out_folder)
#    plot_DMmass(path, db, redshifts, out_folder)
#    plot_Age(path, db, redshifts, out_folder)
#    plot_coldgas(path, db, redshifts, out_folder)
#    plot_burstmass(path, db, redshifts, out_folder)
    plot_mergerfraction(path, db, redshifts, out_folder)