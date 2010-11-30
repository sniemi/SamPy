import matplotlib
matplotlib.rc('text', usetex = True)
matplotlib.rc('xtick', labelsize=12) 
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rc('lines', markeredgewidth=2.0)
matplotlib.rcParams['lines.linewidth'] = 1.8
matplotlib.rcParams['legend.fontsize'] = 10
matplotlib.rcParams['legend.handlelength'] = 5
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
matplotlib.use('PDF')
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, NullFormatter, LogLocator

import numpy as N
import pylab as P
import glob, shutil, os
import re
import db.sqlite

def fstar_ben(mh, m1, f0, beta, gamma):
  mstar = 2.0*f0*10.0**mh / ((10.0**mh/10.0**m1)**(-beta)+(10.0**mh/10.0**m1)**gamma)
  fstar = mstar / 10.0**mh
  return fstar

def fstar_behroozi_data(file):
    data = N.loadtxt(file)
    return data[:,0], data[:,1]

def mstar_Bell_H(file, h = 0.7):
    '''
    Stellar mass function at z=0 from bell et al.
    Convert to H_0 = 70 and Chabrier IMF.
    '''
    data = N.loadtxt(file)
    
    m = data[:,0] - 2.0 * N.log10(h) - 0.15
    phi = data[:,1]*h**3
    phi_low = data[:,2]*h**3
    phi_high = data[:,3]*h**3

    return m, N.log10(phi), N.log10(phi_low), N.log10(phi_high)

def mstar_bell(file, h = 0.7):
    '''
    Stellar mass function from bell et al. (H0=100).
    Convert to Chabrier IMF.
    '''
    data = N.loadtxt(file)

    m = data[:,0] - 0.1
    phi = N.log10(data[:,1])
    phi_low = N.log10(data[:,2])
    phi_high = N.log10(data[:,3])
    return m, phi, phi_low, phi_high

def mstar_lin(file, h = 0.7):

    data = N.loadtxt(file)

    mbin = data[:,2] - 2.0*N.log10(h)
    phi_low = N.log10((data[:,3] - data[:,4])*h**3)
    phi_high = N.log10((data[:,3] + data[:,4])*h**3)
    phi = N.log10(data[:,3]*h**3)

    return mbing, phi, phi_low, phi_high

def panter(file):
    data = N.loadtxt(file, comments = ';')
    
    nlow = N.log10(data[:,1] - data[:,2])
    nhigh = N.log10(data[:,1] + data[:,2])
    n = N.log10(data[:,1])

    return data[:,0], n, nlow, nhigh

def mhi_bell(file, h = 0.7):
    data = N.loadtxt(file)
    m = data[:,0] - 2.*N.log10(h)
    phi = N.log10(data[:,1]*h**3)
    phi_low = N.log10(data[:,2]*h**3)
    phi_high = N.log10(data[:,3]*h**3)
    return m, phi, phi_low, phi_high

def gallazzi(file, h = 0.7, comments = ';'):
    '''
    Scale stellar masses with h.
    n.b. masses in file are for H0=70.
    '''
    data = N.loadtxt(file, comments = comments)
    twologh = 2.0*N.log10(h)
    return data[:,0]+twologh, data[:,1], data[:,2], data[:,3]

def stellarmassfunc_plot(path, database, redshifts, mmax = 12.5, mmin = 5.0, 
                         nbins = 40, nvolumes = 8, h = 0.7,
                         obs = '/Users/niemi/Desktop/Research/IDL/obs/',
                         output_folder = '/Users/niemi/Desktop/Research/stellar_mass_functions/'):
    '''
    Plots stellar mass functions as a function of redshift
    '''

    weight = 1./(nvolumes*(50.0/0.7)**3)
    multiply = 10**9

    #make the figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    #obs constrains
    mg, phig, phi_lowg, phi_highg = mstar_Bell_H(obs + 'bell/sdss2mass_lf/gmf.out')
    mk, phik, phi_lowk, phi_highk = mstar_Bell_H(obs + 'bell/sdss2mass_lf/kmf.out')
#    m, n, nlow, nhigh = panter(obs + 'panter/panter.dat')
    ax.errorbar(mg, phig, yerr = [phig - phi_highg, phi_lowg - phig], label = 'Bell et al. G (z=0)')
#    ax.errorbar(mk, phik, yerr = [phik - phi_highk, phi_lowk - phik], label = 'Bell et al. K (z=0)')
#    ax.errorbar(m, n, yerr = [nlow - n, n - nhigh], label = 'Panter et al. K')

    #plot the different redshifts
    for redshift in redshifts:
        query = '''select mstar_disk, mbulge, gal_id from galpropz where ''' + redshift
        query += ' and mstar_disk + mbulge > 0'
        
        data = db.sqlite.get_data_sqlite(path, database, query)

#        disk = N.log10(data[:,0] * multiply)
#        bulge = N.log10(data[:,1] * multiply)
        mstar = N.log10(data[:,0] * multiply + data[:,1] * multiply)
        galid = data[:,2]
        
        ngal = len(mstar)
        print ngal, redshift

        dm = (mmax-mmin)/nbins
        mbin = mmin + (N.arange(nbins)+0.5)*dm

        mf_star = N.zeros(nbins)
        mf_star_central = N.zeros(nbins)

        mf_early = N.zeros(nbins)
        mf_late = N.zeros(nbins)
        mf_bulge = N.zeros(nbins)

        #from IDL, should be done without looping
#        btt = 10.0**(props.mbulge - props.mstar)
        btt = data[:,1] / mstar
        for i in range(ngal):
            ibin = int(N.floor((mstar[i] - mmin)/dm))
            if ibin >= 0 and ibin < nbins:
                mf_star[ibin] += weight
                #stellar mass, by type
                if btt[i] >= 0.4:
                    mf_early[ibin] += weight
                else:
                    mf_late[ibin] += weight
                #stellar mass, centrals
                if galid[i] == 1:
                    if ibin >= 0 and ibin < nbins:
                        mf_star_central[ibin] += weight

        mf_star =  N.log10(mf_star/dm)
        mf_early = N.log10(mf_early/dm)
        mf_late = N.log10(mf_late/dm)
        mf_star_central = N.log10(mf_star_central/dm)

        tmp = redshift.split()
        rd = int(float(tmp[2]) + 0.1)

        ax.plot(mbin, mf_star, label = 'z = %i' % rd)

    ax.set_xlim(8.0, 12.1)
    ax.set_ylim(-4.5, -1.0)
    ax.set_xlabel(r'$\log M_{\star} \quad [M_{\odot}]$')
    ax.set_ylabel(r'$\log \left ( \frac{dN}{d\log M_{\star}} \right ) \quad [$Mpc$^{-3}$ dex$^{-1}]$')
    #small ticks
    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m/5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor) 
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m/5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor) 

    P.legend(shadow = True, fancybox = True)
    P.savefig(output_folder+'stellarmf.pdf')
    P.close()

def findgen(x):
    '''
    IDL function findgen, same as numpy.arange.
    '''
    return N.arange(x)

def fix(x):
    '''
    IDL function fix, same as numpy.floor.
    '''
    return int(N.floor(x))

def alog10(x):
    '''
    IDL function alog10, same as numpy.log10.
    '''
    return N.log10(x)

def haering_rix(file, comments = ';'):
    data = N.loadtxt(file, comments = ';')
    
    m_bulge = N.log10(data[:,10])
    m_bh = N.log10(data[:,2] * data[:,5])
    ellip = data[:,1] == 0
    s0 = data[:,1] == 1
    spiral = data[:,1] == 2

    return m_bulge, m_bh, ellip, spiral, s0

def main(path, database):
    '''
    Driver function, call this with a path to the data,
    and label you wish to use for the files.
    '''
    redshifts = ['galpropz.zgal > 0.9 and galpropz.zgal <= 1.1',
                 'galpropz.zgal > 1.9 and galpropz.zgal <= 2.1',
                 'galpropz.zgal > 2.9 and galpropz.zgal <= 3.1',
                 'galpropz.zgal > 3.9 and galpropz.zgal <= 4.1',
                 'galpropz.zgal > 4.9 and galpropz.zgal <= 5.1',
                 'galpropz.zgal > 5.9 and galpropz.zgal <= 6.1',
                 'galpropz.zgal > 6.9 and galpropz.zgal <= 7.1']

    stellarmassfunc_plot(path, database, redshifts)

if __name__ == '__main__':    
    path = '/Users/niemi/Desktop/Research/run/trial1/'
    database = 'sams.db'
    main(path, database)
