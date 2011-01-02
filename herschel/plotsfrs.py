import matplotlib
matplotlib.use('PS')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.2)
matplotlib.rcParams['legend.fontsize'] = 14
matplotlib.rcParams['legend.handlelength'] = 2
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
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd, yd, xmin, xmax,
                                                         nxbins = 18)
        msk = y50d > -10
        ax.errorbar(xbin_midd[msk], y50d[msk], yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
               #label = '$S_{250} =$ %.1f mJy' % fluxlimit)
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [$mJy$])$')
    ax.set_ylabel('$\log_{10}(\dot{M}_{\star} \ [M_{\odot}yr^{-1}])$')

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
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd, yd, xmin, xmax,
                                                         nxbins = 15)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [$mJy$])$')
    ax.set_ylabel('$\log_{10}(M_{\star} \ [M_{\odot}])$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(8.9, 11.5)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'mstellar.ps')

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
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd, yd, xmin, xmax,
                                                         nxbins = 15)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [$mJy$])$')
    ax.set_ylabel(r'$\log_{10} \left ( \frac{M_{coldgas}}{M_{\star}} \right )$')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(-1.2, 1.0)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'mratio.ps')

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
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd, yd, xmin, xmax,
                                                         nxbins = 15)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [$mJy$])$')
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
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd, yd, xmin, xmax,
                                                         nxbins = 15)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [$mJy$])$')
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
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd, yd, xmin, xmax,
                                                         nxbins = 15)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [$mJy$])$')
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
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd, yd, xmin, xmax,
                                                         nxbins = 15)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [$mJy$])$')
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
        xbin_midd, y50d, y16d, y84d = dm.percentile_bins(xd, yd,
                                                         xmin, xmax,
                                                         nxbins = 15)
        msk = y50d > -10
        add = eval('0.0%s' % str(i))
        ax.errorbar(xbin_midd[msk] + add, y50d[msk],
                    yerr = [y50d[msk]-y16d[msk], y84d[msk]-y50d[msk]],
                    label = '$z = %.1f$' % zz)

    ax.axvline(N.log10(fluxlimit), ls = ':', color = 'green')
  
    ax.set_xlabel('$\log_{10}(S_{250} \ [$mJy$])$')
    ax.set_ylabel('Mean Age [Gyr]')

    ax.set_xlim(xmin, xmax)
    ax.set_ylim(0.1, 6.0)

    P.legend(loc = 'lower right')
    P.savefig(out_folder + 'Age.ps') 

   
if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/sfrs/'
    db = 'sams.db'

    redshifts = ['FIR.z > 0.1 and FIR.z < 0.3',
                 'FIR.z > 0.4 and FIR.z < 0.6',
                 'FIR.z > 0.9 and FIR.z < 1.1',
                 'FIR.z > 1.9 and FIR.z < 2.1',
                 'FIR.z > 2.9 and FIR.z < 3.1',
                 'FIR.z > 3.9 and FIR.z < 4.1']

    plot_sfrs(path, db, redshifts, out_folder)
    plot_stellarmass(path, db, redshifts, out_folder)

    plot_massratios(path, db, redshifts, out_folder)
    plot_metallicity(path, db, redshifts, out_folder)
    plot_starburst(path, db, redshifts, out_folder)
    plot_BHmass(path, db, redshifts, out_folder)
    plot_DMmass(path, db, redshifts, out_folder)
    plot_Age(path, db, redshifts, out_folder)
    
