import matplotlib
#matplotlib.use('PS')
matplotlib.use('AGG')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.2)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 5
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import os
import pylab as P
import numpy as N
import scipy.stats as SS
#Sami's repository
import db.sqlite as sq
    
def plot_correlation(query, xlabel, ylabel, zmin, zmax, out_folder):
    #get data
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x = data[:,0]
    y = data[:,1]*10**3
    #make the figure
    P.figure()
    P.title('$%.1f \leq z < %.1f$' % (zmin, zmax)) 
    P.scatter(x, y, c = 'k', marker = 'o', s = 9)
    #P.yscale('log')
#    if 'meanage' in xlabel:
#        P.xlim(0.0, 8.0)
#    if 'mstar' in xlabel:
#        P.xlim(7, 12)
#    if 'mstardot' in xlabel:
#        P.xlim(0, 800)
    if 'sfr_ave' in xlabel:
        P.xlim(0, 500)
    if 'sfr_bur' in xlabel:
        P.xlim(-1, 750)
    if 'tmerge' in xlabel:
        P.xlim(-0.1, 3)
    if 'pacs70' in ylabel:
        P.ylim(0, 3)
    if 'pacs100' in ylabel:
        P.ylim(0, 12)
    if 'pacs160' in ylabel:
        P.ylim(0, 37)
    if 'spire250' in ylabel:
        P.ylim(0, 50)
    if 'spire350' in ylabel:
        P.ylim(0, 45)
    if 'spire500' in ylabel:
        P.ylim(0, 26)
    if 'tmajmerge' in xlabel:
        P.xlim(0, 2)
    if 'r_disk' in xlabel:
        P.xlim(0, 23)
    if 'sigma_bul' in xlabel:
        P.xlim(0, 1000)

    P.xlabel(xlabel.replace('_', '\_'))
    P.ylabel(ylabel.replace('_', '\_'))
    P.savefig(out_folder + '%s_%s.png' % (xlabel, ylabel[:-7]))
    P.close()
    
    print '\nSpearmann R-test (rho, P) for %s and %s:' % (xlabel, ylabel[:-7])
    print SS.spearmanr(x, y)

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
#    path = hm + '/Dropbox/Research/Herschel/runs/test3/'
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero/'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/spire_detected/'
    db = 'sams.db'

    zmin = 2.0
    zmax = 4.0

    #5sigma limits derived by Kuang
    depths = {'pacs100_obs': 1.7e-3,
              'pacs160_obs': 4.5e-3,
              'spire250_obs': 5.0e-3,
              'spire350_obs': 9.0e-3,
              'spire500_obs': 10.0e-3
              }
    FIRbands = ['pacs70_obs',
                'pacs100_obs',
                'pacs160_obs',
                'spire250_obs',
                'spire350_obs',
                'spire500_obs']

    galprop = ['mstar', 'mstardot', 'sfr_burst', 'sfr_ave', 'meanage', 'tmerge',
               'r_disk', 'sigma_bulge', 'mhalo', 'm_strip', 'mcold', 'maccdot',
               'maccdot_radio', 'Zstar', 'Zcold', 'tau0', 'tmajmerge']
    galprop = ['meanage']
    galphot = ['f775w', 'f606w', 'f125w', 'f160w']
    galphotdust = ['f775w', 'f606w', 'f125w', 'f160w']

    t1 = 'galprop'
    t2 = 'galphot'
    t3 = 'galphotdust'
    t4 = 'FIR'

    for ir in FIRbands:
        for p in galprop:
#            query = '''select %s.%s, %s.%s from %s, %s where
#                       %s.z >= %.4f and
#                        %s.z < %.4f and
#                        %s.gal_id = %s.gal_id and
#                        %s.halo_id = %s.halo_id and
#                        %s.%s > 1e-9 and
#                        FIR.spire250_obs > 5.0e-04''' % (t1, p,
#                                                         t4, ir,
#                                                         t1, t4,
#                                                         t4, zmin,
#                                                         t4, zmax,
#                                                         t1, t4,
#                                                         t1, t4,
#                                                         t4, ir)
            query = '''select %s.%s, %s.%s from %s, %s where
                       %s.z >= %.4f and
                        %s.z < %.4f and
                        %s.gal_id = %s.gal_id and
                        %s.halo_id = %s.halo_id and
                        %s.%s > 1e-9 and
                        galprop.mstar > 9.5''' % (t1, p,
                                                         t4, ir,
                                                         t1, t4,
                                                         t4, zmin,
                                                         t4, zmax,
                                                         t1, t4,
                                                         t1, t4,
                                                         t4, ir)

            
            #print query
            plot_correlation(query, p,
                             ir + ' [mJy]',
                             zmin, zmax,
                             out_folder)
