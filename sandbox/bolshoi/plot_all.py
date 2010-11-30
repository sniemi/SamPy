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
#matplotlib.rcParams['xtick.labelsize'] = 'large'
matplotlib.rcParams['ytick.major.size'] = 5
#matplotlib.rcParams['ytick.labelsize'] = 'large'
#matplotlib.rcParams['legend.fancybox'] = True
matplotlib.use('PDF')
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, NullFormatter, LogLocator
from matplotlib import cm
from matplotlib.patches import Circle

import numpy as N
import pylab as P
import sextutils as su
import scipy.stats as ss
import glob, shutil, os

def perc_bin(xbin, xdata, ydata):
    '''
    Compute median and 16 and 8 percentiles of y-data in bins in x
    '''
    #xbin.sort
    nbin = len(xbin) - 1
    xbin_mid = N.zeros(nbin)
    y50 = N.zeros(nbin) - 99.
    y16 = N.zeros(nbin) - 99.
    y84 = N.zeros(nbin) - 99.

    for i in range(nbin):
        xbin_mid[i] = xbin[i] + 0.5*(xbin[i+1] - xbin[i])
        mask = (xdata > xbin[i]) & (xdata <= xbin[i+1])
        if len(ydata[mask]) >= 10:
            y50[i] = ss.scoreatpercentile(ydata[mask], 50)
            y16[i] = ss.scoreatpercentile(ydata[mask], 16)
            y84[i] = ss.scoreatpercentile(ydata[mask], 84)

    return xbin_mid, y50, y16, y84

def read_data(path):
    '''
    Reads Rachel's SAMs output data
    '''
    print 'Reading from %s' % path
    print 'Coverting Johnson U, B, V, and K bands to vega system'

    h_100 = 1.0

    galfile = path + 'galphot.dat'
    galdustfile = path + 'galphotdust.dat'
    profile = path + 'galprop.dat'
    halofile = path + 'halos.dat'

    g = su.se_catalog(galfile)
    gdust = su.se_catalog(galdustfile)
    p = su.se_catalog(profile)
    h = su.se_catalog(halofile)
    
    print 'Found %i haloes' % len(h)
    print 'Found %i galaxies' % len(g)

    AB_vega_U = 0.729977
    AB_vega_B = -0.0934
    AB_vega_V = 0.0112
    AB_vega_K = 1.854

    g.uj = g.uj - AB_vega_U
    g.bj = g.bj - AB_vega_B
    g.vj = g.vj - AB_vega_V
    g.k = g.k - AB_vega_K

    #bulge
    g.uj_bulge = g.uj_bulge - AB_vega_U
    g.bj_bulge = g.bj_bulge - AB_vega_B
    g.vj_bulge = g.vj_bulge - AB_vega_V
    g.k_bulge = g.k_bulge - AB_vega_K

    #dusty
    gdust.uj = gdust.uj - AB_vega_U
    gdust.bj = gdust.bj - AB_vega_B
    gdust.vj = gdust.vj - AB_vega_V
    gdust.j = gdust.k - AB_vega_K
    
    return g, gdust, p, h

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

def mfobs(mbin):
    '''
    Observed HI mass function.
    Zwaan et al.
    '''
    mstar = 9.8 - 2.0 * N.log10(70.0 / 75.0)
    alpha = -1.37
    thetastar = 0.006 * (70.0 / 75.0)**3
    x = 10.0**(mbin - mstar)
    theta = N.log10(2.3 * thetastar * x**(alpha + 1) * N.exp(-x))
    return theta

def mhi_bell(file, h = 0.7):
    data = N.loadtxt(file)
    m = data[:,0] - 2.*N.log10(h)
    phi = N.log10(data[:,1]*h**3)
    phi_low = N.log10(data[:,2]*h**3)
    phi_high = N.log10(data[:,3]*h**3)
    return m, phi, phi_low, phi_high

def obs_BHmf(file, const = 0.362216, comments = ';'):
    data = N.loadtxt(file, comments = comments)
    phi_low = data[:,1] + const
    phi_med = data[:,2] + const
    phi_high = data[:,3] + const
    return data[:,0], phi_low, phi_med, phi_high

def gallazzi(file, h = 0.7, comments = ';'):
    '''
    Scale stellar masses with h.
    n.b. masses in file are for H0=70.
    '''
    data = N.loadtxt(file, comments = comments)
    twologh = 2.0*N.log10(h)
    return data[:,0]+twologh, data[:,1], data[:,2], data[:,3]

def fstar_plot(behroozi, g, prop, h, output):
    '''
    Stellar mass to halo mass ratio as a function of halo mass.
    This plot differs slightly from the one in the Somerville 2008:
    the plot in the paper is the fraction of baryons in stars. 
    '''
    mfit = 10. + N.arange(50)*0.1
    mbin = 10.7 + N.arange(25)*0.2

    f8 = 8. - mfit
    f9 = 9. - mfit

    fs_halo = 10.0**(prop.mstar - prop.mhalo)

    #central and satellite galaxies
    central = prop.gal_id == 1
    sat = prop.gal_id != 1

    mbin_mid, fs_50, fs_10, fs_90 = perc_bin(mbin, prop.mhalo, fs_halo)
    mbin_mid, fs_cen_50, fs_cen_10, fs_cen_90 = perc_bin(mbin, prop.mhalo[central], fs_halo[central])
    mbin_mid, fs_sat_50, fs_sat_10, fs_sat_90 = perc_bin(mbin, prop.mhalo[sat], fs_halo[sat])

    #begin figure
    fig = P.figure()
    ax = fig.add_subplot(111)
    #ax.plot(prop.mhalo, prop.mstar)
    ax.scatter(prop.mhalo[central], N.log10(fs_halo[central]),
               edgecolor = 'r', s = 2, facecolor = 'r', label = 'Central galaxies')
    
    ax.plot(mbin_mid, N.log10(fs_50), 'ko', ms = 10, label = 'Median, all galaxies')
    ax.plot(mbin_mid, N.log10(fs_10), 'k--')
    ax.plot(mbin_mid, N.log10(fs_90), 'k--')

    ax.plot(mbin_mid, N.log10(fs_sat_50), 'cD', ms = 8, label = 'Median, satellite galaxies')
    ax.plot(mbin_mid, N.log10(fs_cen_50), 'pm', ms = 8, label = 'Median, central galaxies')

    #constrains from moster et al.
    fstar_med_ben = fstar_ben(mfit, 11.884, 0.0282, 1.057, 0.5560)
    fstar_med_ben_scat = fstar_ben(mfit, 11.866, 0.02891, 1.110, 0.648)
    ax.plot(mfit, N.log10(fstar_med_ben), 'g-', label = 'Moster et al.')
    ax.plot(mfit, N.log10(fstar_med_ben_scat), c = 'burlywood', label = 'Moster et al. (sc)' )

    #get fstar_behroozi_log
    mh, sh = fstar_behroozi_data(behroozi)
    ax.plot(mh, sh, 'hg', label = 'Behroozi et al.')
    
    ax.plot(mfit, f8, 'k--', c = '0.25')

    #axis scales
    ax.set_xlim(10.0, 15.0)
    ax.set_ylim(-4.0, -0.75)

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
    
    ax.set_ylabel(r'$\log \left ( \frac{M_{star}}{f_{b}M_{halo}} \right )$')
    ax.set_xlabel(r'$\log \left ( \frac{M_{(sub)halo}}{M_{\odot}} \right )$')

    P.legend()
    P.savefig(output)
    P.close()

def massfunc_plot(halos, props, obs, mmax = 12.5, mmin = 5.0, nbins = 30, output = 'SMN'):
    '''
    Plots stellar mass functions, cold gas mass functions, & BH MF
    '''
    #files
    path_BH = '/Users/niemi/Desktop/Research/IDL/obs/phopkins/'
    BH_file = path_BH + 'rachel_bhmf_data.dat'

    #overrides weight for a single Bolshoi sub-volume
    #halos.weight = halos.weight * 0. + 1./(50.0/0.7)**3
    #for ten sub-volumes
    halos.weight = halos.weight * 0. + 1./(8.*(50./0.7)**3)
    
    ngal = len(props.gal_id)
    print '%i galaxies found' % ngal

    dm = (mmax-mmin)/nbins
    print dm
    mbin = mmin + (N.arange(nbins)+0.5)*dm
    
    mfit = mmin + N.arange(150)*0.05

    mf_cold = N.zeros(nbins)
    mf_star = N.zeros(nbins)
    mf_star_central = N.zeros(nbins)
    mf_bar = N.zeros(nbins)
    mf_bh = N.zeros(nbins)

    mf_early = N.zeros(nbins)
    mf_late = N.zeros(nbins)
    mf_bulge = N.zeros(nbins)

    #from IDL, should be done without looping
    btt = 10.0**(props.mbulge - props.mstar)
    for i in range(ngal):
        ihalo = props.halo_id[i]
       #cold gas
        ibin = int(N.floor((props.mcold[i] - mmin)/dm))
        if ibin >= 0 and ibin < nbins:
            mf_cold[ibin] += halos.weight[ihalo]
        #stellar mass
        ibin = int(N.floor((props.mstar[i] - mmin)/dm))
        if ibin >= 0 and ibin < nbins:
            mf_star[ibin] += halos.weight[ihalo]
            #stellar mass, by type
            if btt[i] >= 0.4:
                mf_early[ibin] += halos.weight[ihalo]
            else:
                mf_late[ibin] += halos.weight[ihalo]
            #stellar mass, centrals
            if props.gal_id[i] == 1:
                if ibin >= 0 and ibin < nbins:
                    mf_star_central[ibin] += halos.weight[ihalo]
        #bulge mass
        ibin = int(N.floor((props.mbulge[i] - mmin)/dm))
        if ibin >= 0 and ibin < nbins:
            mf_bulge[ibin] += halos.weight[ihalo]
        #baryonic mass
        mbar = N.log10(10.0**props.mcold[i] + 10.0**props.mstar[i])
        ibin = int(N.floor((mbar - mmin)/dm))
        if ibin >= 0 and ibin < nbins:
            mf_bar[ibin] += halos.weight[ihalo]
        #black hole
        ibin = int(N.floor((props.mbh[i] - mmin)/dm))
        if ibin >= 0 and ibin < nbins:
            mf_bh[ibin] += halos.weight[ihalo]

    mf_cold =  N.log10(mf_cold/dm)
    mf_star =  N.log10(mf_star/dm)
    mf_early = N.log10(mf_early/dm)
    mf_late = N.log10(mf_late/dm)
    mf_bulge = N.log10(mf_bulge/dm)
    mf_star_central = N.log10(mf_star_central/dm)
    mf_bar =  N.log10(mf_bar/dm)
    mf_bh = N.log10(mf_bh/dm)

    #stellar mass function plot
    #obs constrains
    mg, phig, phi_lowg, phi_highg = mstar_Bell_H(obs + 'bell/sdss2mass_lf/gmf.out')
    mk, phik, phi_lowk, phi_highk = mstar_Bell_H(obs + 'bell/sdss2mass_lf/kmf.out')
    #ml, phil, phi_lowl, phi_hiugl = mstar_lin(obs + 'sdss_mf/SDSS_SMF.dat')
    m, n, nlow, nhigh = panter(obs + 'panter/panter.dat')

    fig = P.figure()
    ax = fig.add_subplot(111)
    ax.plot(mbin, mf_star, label = 'Stellar Mass Function')
    ax.errorbar(mg, phig, yerr = [phig - phi_highg, phi_lowg - phig], label = 'Bell et al. G')
    ax.errorbar(mk, phik, yerr = [phik - phi_highk, phi_lowk - phik], label = 'Bell et al. K')
    #ax.errorbar(ml, phil, yerr = [phi_lowl, phi_highl], label = 'Lin et al. K')
    ax.errorbar(m, n, yerr = [nlow - n, n - nhigh], label = 'Panter et al. K')
    ax.set_xlim(8.0, 12.5)
    ax.set_ylim(-6.0, -1.0)
    ax.set_xlabel(r'$\log M_{star} \quad [M_{\odot}]$')
    ax.set_ylabel(r'$\frac{\log \textrm{d}N}{\textrm{d}\log M_{star}} \quad [\textrm{Mpc}^{-3} \textrm{dex}^{-1}]$')
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
    P.legend()
    P.savefig('mfstar_' + output + '.pdf')
    P.close()

    #cold gas mass function
    #obs constrains
    #mhi_bell_h70
    #mgas_bell_h70
    theta = mfobs(mbin)
    m_hi, phi_hi, phi_low_hi, phi_high_hi = mhi_bell(obs + 'bell/sdss2mass_lf/himf.out')
    m_h2, phi_h2, phi_low_h2, phi_high_h2 = mhi_bell(obs + 'bell/sdss2mass_lf/h2mf.out')

    fig = P.figure()
    ax = fig.add_subplot(111)
    ax.plot(mbin, mf_cold, label = 'Cold Gas Mass Function')
    ax.plot(mbin, theta, 'g-', lw = 1.8, label = 'Zwaan et al.')
    ax.errorbar(m_hi, phi_hi, yerr = [phi_hi - phi_high_hi, phi_low_hi - phi_hi], 
                c = 'cyan', ls ='--', lw = 1.5, label = 'Bell et al. $H_{I}$')
    ax.errorbar(m_h2, phi_h2, yerr = [phi_h2 - phi_high_h2, phi_low_h2 - phi_h2],
                c= 'magenta', ls = ':', lw = 1.5, label = 'Bell et al. $H_{2}$')
    ax.plot(m_hi, N.log10(10.0**phi_hi + 10**phi_h2), 'r-', label = '$H_{I} + H_{2}$' )
    ax.set_xlim(8.0, 11.5)
    ax.set_ylim(-5.5, -0.8)
    ax.set_xlabel(r'$\log M_{cold} \quad [M_{\odot}]$')
    ax.set_ylabel(r'$\frac{\log \textrm{d}N}{\textrm{d}\log M} \quad [\textrm{Mpc}^{-3} \textrm{dex}^{-1}]$')
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
    P.legend()
    P.savefig('mfcold_' + output + '.pdf')
    P.close()

    #total baryons
    #obs contstrains
    m_bar, phi_bar, phi_low_bar, phi_high_bar = mstar_Bell_H(obs + 'bell/sdss2mass_lf/barymf1.out')

    fig = P.figure()
    ax = fig.add_subplot(111)
    ax.plot(mbin, mf_bar, label = 'Total Baryon Mass')
    ax.errorbar(m_bar, phi_bar, yerr = [phi_bar - phi_high_bar, phi_low_bar - phi_bar],
                c = 'g', ls = '-', label = 'Bell et al.')
    ax.set_xlim(8.0, 12.5)
    ax.set_ylim(-5.0, -0.25)
    ax.set_xlabel(r'$\log M_{baryons} \quad [M_{\odot}]$')
    ax.set_ylabel(r'$\frac{\log \textrm{d}N}{\textrm{d}\log M_{baryons}} \quad [\textrm{Mpc}^{-3} \textrm{dex}^{-1}]$')
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
    P.legend()
    P.savefig('mfbar_' + output + '.pdf')
    P.close()

    #BH mass function
    #obs constrains
    m_bh, phi_low_bh, phi_med_bh, phi_high_bh = obs_BHmf(BH_file)

    fig = P.figure()
    ax = fig.add_subplot(111)
    ax.plot(mbin, mf_bh, 'k-', label = 'Black Hole Mass Function')
    ax.plot(m_bh, phi_low_bh, 'g--')
    ax.plot(m_bh, phi_med_bh, 'g-', label = 'Obs. constrains')
    ax.plot(m_bh, phi_high_bh, 'g--')
    ax.set_xlim(6.0, 10.2)
    ax.set_ylim(-7.0, -1.5)
    ax.set_xlabel(r'$\log M_{BH} \quad [M_{\odot}]$')
    ax.set_ylabel(r'$\frac{\log \textrm{d}N}{\textrm{d}\log M} \quad [\textrm{Mpc}^{-3} \textrm{dex}^{-1}]$')
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
    P.legend()
    P.savefig('mfBH_' + output + '.pdf')
    P.close()

def fgas_kannappan():
    mstar = N.array([8.75, 9.25, 9.75, 10.25, 10.75, 11.25, 11.75])
    log_gs = N.array([0.2, 0.0, -0.1, -0.4, -0.7, -0.8, -0.85])
    #convert from diet salpeter to chabrier
    mstar -= 0.1
    fgas = 10.0**log_gs/(1.0 + 10.0**log_gs)
    return mstar, fgas

def gasfrac_hess(mstar, fgas, weight, label, output,
                 mmin = 8.5, mmax = 11.7, nmbins = 16,
                 fgasmin = 0.0, fgasmax = 1.0, nfbins = 10,
                 pmax = 1.0, pmin = 0.01):
    '''
    Plot _conditional_ distribution of gas fraction vs. stellar mass.
    Ported from an IDL code, should be cleaned.
    Most likely N.zeros are not needed
    '''
    #n.b. mbin and fgasbin are the bin CENTERS
    dm = (mmax - mmin) /nmbins
    mbin = mmin + (N.arange(nmbins))*dm + dm/2.0
    dfgas = (fgasmax - fgasmin) / nfbins
    fgasbin = fgasmin + (N.arange(nfbins))*dfgas + dfgas/2.0

    fgashist = N.zeros((nfbins, nmbins))
    #fraction of galaxies with no gas
    nogas = N.zeros(nmbins)
    #without weight factor
    yhist_num = N.zeros((nfbins, nmbins))
    #number of halos in each bin
    nh = N.zeros(nmbins)
    
    #compute gas fraction distributions in stellar mass bins
    #with weight factor
    #this should be rewritten...
    for i in range(len(mstar)):
        imbin = int(N.floor((mstar[i] - mmin)/dm))
        if imbin >= 0 and imbin < nmbins:
            nh[imbin] = nh[imbin]+ weight[i]
            ifgas = int(N.floor((fgas[i]-fgasmin)/dfgas))
            if ifgas >= 0 and ifgas < nfbins:
                fgashist[ifgas, imbin] = fgashist[ifgas, imbin] + weight[i]
                yhist_num[ifgas, imbin] = yhist_num[ifgas, imbin] + 1

    #conditional distributions in Mh bins
    for i in range(nmbins):
        if nh[i] > 0.0:
            fgashist[:,i] /= nh[i]

    s = N.log10(pmax) - N.log10(fgashist)
    smax = N.log10(pmax) - N.log10(pmin)
    smin = N.log10(pmax)
    
    s[fgashist <= 0.0] = 2.0 * smax
    s[yhist_num <= 1] = 2.0 * smax

    #obs contstrains
    kmstar, kfgas = fgas_kannappan()

    #medians
    mbin_mid, y50, y16, y84 = perc_bin(mbin, mstar, fgas)

    #image
    fig = P.figure()
    ax = fig.add_subplot(111)
    ims = ax.imshow(s, vmin = smin, vmax = smax,
                    origin = 'lower', cmap = cm.gray,
                    interpolation = None,
                    extent = [mmin, mmax, pmin, pmax],
                    aspect = 'auto')
    ax.plot(mbin_mid, y50, 'r-', label = 'Median')
    ax.plot(mbin_mid, y16, 'r--')
    ax.plot(mbin_mid, y84, 'r--')
    ax.plot(kmstar, kfgas, 'go', label = 'Kannappan et al.')
    ax.set_xlim(mmin, mmax)
    ax.set_ylim(pmin, pmax)
    ax.set_ylabel('Gas fraction')
    ax.set_xlabel('$\log M_{star} \quad [M_{\odot}] $')
    cbar = fig.colorbar(ims, orientation='horizontal')
#    cbar = fig.colorbar(ims, ticks=[min, max/factor/2., max/factor], orientation='horizontal')
#    cbar.ax.set_xticklabels(['%3.2f' % min, '%3.2f' % (max/2.), '%3.2f' % (max)])
#    cbar.ax.set_title('Pixel Values (counts s$^{-1}$)')
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
    try:
        P.legend(numpoints = 1, shadow = True, fancybox = True)
    except:
        P.legend()
    P.savefig(output)

def ssfr_plot(halos, prop, mask, output, typ = '.pdf'):
    '''
    Specific starformation rate plots.
    '''

    wgal = halos.weight[prop.halo_id]

    log_ssfr = N.log10(prop.sfr_ave / 10.0**prop.mstar)
    log_ssfr[log_ssfr <= -14.0] = -13.8

    ssfrhess_sam(prop.mstar[mask], log_ssfr[mask], wgal[mask], output+typ)

def ssfrhess_sam(mstar, ssfr, weight, output,
                 mmin = 9.027, dm = 0.309, nmbins = 11,
                 ssfrmin = -13.0, ssfrmax = -8.5, nssfrbins = 24,
                 ssfr_cut = -11.1, pmax = 0.5, pmin = 1e-5):
    '''
    log ssfr in yr
    '''
    mmax = mmin + dm*nmbins
    fpass = N.zeros(nmbins)
    
    #n.b. mbin and fgasbin are the bin CENTERS
    mbin = mmin + (N.zeros(nmbins))*dm + dm/2.0
    dssfr = (ssfrmax-ssfrmin)/(nssfrbins)
    ssfrbin = ssfrmin + (N.arange(nssfrbins))*dssfr + dssfr/2.0
    #again, this should be rewritten
    #could make a function that several functions could call
    ssfrhist = N.zeros((nssfrbins, nmbins))
    yhist_num = N.zeros((nssfrbins, nmbins))

    #number of halos in each bin
    nh = N.zeros(nmbins)

    ssfr[ssfr < ssfrmin] = ssfrmin + 0.1

    #compute distributions in stellar mass bins
    #with weight factor
    for i in range(len(mstar)):
        imbin = int(N.floor((mstar[i]-mmin)/dm))
        if imbin >= 0 and imbin < nmbins:
            nh[imbin] += weight[i]
            if ssfr[i] <= ssfr_cut: fpass[imbin] += weight[i]
            issfr = int(N.floor((ssfr[i]-ssfrmin)/dssfr))
            if issfr >= 0 and issfr < nssfrbins:
                ssfrhist[issfr, imbin] += weight[i]
                yhist_num[issfr, imbin] += 1.
    
    nhtot = N.sum(nh)
    print nhtot

    #Make hess plots
    #conditional distributions in Mh bins
    for i in range(nmbins):
        if nh[i] > 0.0:
            ssfrhist[:,i] = ssfrhist[:,i]/nh[i]
            fpass[i] = fpass[i]/nh[i]

    s = N.log10(pmax) - N.log10(ssfrhist)
    smax = N.log10(pmax) - N.log10(pmin)
    smin = N.log10(pmax)

    s[ssfrhist <= 0.0] = 2.0*smax
    s[yhist_num <= 1.0] = 2.0*smax

    print 'SSFRhist: ', N.min(ssfrhist), N.min(ssfrhist[ssfrhist >= 0])
    print 'smin, smax: ', smin, smax
    print N.min(s), N.max(s)

    c = s.copy()
    c[ssfrhist > 0.0] = N.log10(ssfrhist[ssfrhist > 0.0])
    #print N.max(c), N.min(c[ssfrhist > 0.0])
    c[ssfrhist <= 0.0] = -99.9
    c[yhist_num <= 2.0] = -99.9

    #main sequence and quenched box
    mbin = 8.0 + N.arange(32)*0.1
    #Salim et al.
    ssfr_fit = -0.36*mbin - 6.4

    #contour levels
    clev = -5.0 + N.arange(30)*0.30

    #image
    fig = P.figure()
    ax = fig.add_subplot(111)
    ims = ax.imshow(s, vmin = smin, vmax = smax,
                    origin = 'lower', cmap = cm.gray,
                    interpolation = None,
                    extent = [mmin, mmax, ssfrmin, ssfrmax],
                    aspect = 'auto')
    cs = ax.contour(c, levels = clev, origin = 'lower',
                    extent = [mmin, mmax, ssfrmin, ssfrmax],
                    colors = 'm', linewidths = 1.0, linestyles = '-',
                    rightside_up = True)
    ax.plot(mbin, ssfr_fit, 'b-', label = 'Blue Sequence')
    ax.plot([9.9, 11.5], [-11.7, -11.95], 'r-', label = 'Red Sequence')
    ax.plot([9.4, 11.5], [-10.7, -11.25], 'g--', label = 'Green Valley')
    P.clabel(cs, fontsize=5)
    ax.set_xlim(mmin, mmax)
    ax.set_ylim(ssfrmin, ssfrmax)
    ax.set_ylabel(r'$\log \left( \frac{SFR}{M_{star}} \right)$')
    ax.set_xlabel('$\log M_{star} \quad [M_{\odot}] $')
    cbar = fig.colorbar(ims, orientation='horizontal')
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
    try:
        P.legend(numpoints = 1, shadow = True, fancybox = True)
    except:
        P.legend()
    P.savefig(output)

def ssfr_wrapper(halos, prop, label):
    
    #masks
    all = prop.gal_id >= 0
    c = prop.gal_id == 1
    s = prop.gal_id != 1
    #early vs. late type galaxies
    btt = 10.0**(prop.mbulge - prop.mstar)
    early = btt >= 0.4
    late = btt < 0.4

    label = 'ssfr_' + label

    ssfr_plot(halos, prop, all, label)
    ssfr_plot(halos, prop, c, label+'_cent')
    ssfr_plot(halos, prop, s, label+'_sat')
    ssfr_plot(halos, prop, early, label+'_sph')
    ssfr_plot(halos, prop, late, label+'_disk')

def gasfrac_sam_cent(halos, prop, 
                     label = 'Bolshoi', output = 'fgascentral' , tpy = '.pdf'):
    output = output + label + tpy

    fgas = 10.0**prop.mcold / (10.0**prop.mcold + 10.0**prop.mstar)
    wgal = halos.weight[prop.halo_id]
    btt = 10.0**(prop.mbulge - prop.mstar)
    #masking
    cdisk = (prop.gal_id == 1) & (btt < 0.4)

    gasfrac_hess(prop.mstar[cdisk], fgas[cdisk], wgal[cdisk], label, output)

def findgen(x):
    '''
    IDL function.
    '''
    return N.arange(x)

def fix(x):
    '''
    IDL function.
    '''
    return int(N.floor(x))

def alog10(x):
    '''
    IDL function.
    '''
    return N.log10(x)

def massmet_hess(mstar, met, weight, obs_data, output,
                 mmin = 8.8, mmax = 12.4, nmbins = 18,
                 Zmin = -1.5, Zmax = 1.0, nzbins = 20,
                 pmax = 1.0, pmin = 1e-3):

    #n.b. mbin and zbin are the bin CENTERS
    dm = (mmax - mmin) / nmbins
    mbin = mmin + (findgen(nmbins))*dm + dm/2.0
    dmet = (Zmax - Zmin) / nzbins
    metbin = Zmin + (findgen(nzbins))*dmet + dmet/2.0

    methist = N.zeros((nzbins, nmbins))
    num = N.zeros((nzbins, nmbins))
    nh = N.zeros(nmbins)

    #compute gas distributions in stellar mass bins
    #with weight factor
    for i in range(len(mstar)):
        imbin = fix((mstar[i]-mmin)/dm)
        if imbin >= 0 and imbin < nmbins:
            nh[imbin] = nh[imbin]+ weight[i]
            imet = fix((met[i] - Zmin) / dmet)
            if imet >= 0 and imet < nzbins:
                methist[imet, imbin] += weight[i]
                num[imet, imbin] += 1

    #conditional distributions in Mh bins
    for i in range(nmbins):
        if nh[i] > 0.0:
            methist[:,i] /= nh[i]

    s = N.log10(pmax) - N.log10(methist)
    smax = N.log10(pmax) - N.log10(pmin)
    smin = N.log10(pmax)

    s[methist <= 0.0] = 2.0*smax
    s[num <= 1.0] = 2.0*smax

    #medians
    mask = 10.0**met > 0.0
    mbin_mid, y50, y16, y84 = perc_bin(mbin, mstar[mask], 10.0**met[mask])

    #gallazzi
    mstar, z_50, z_16, z_84 = gallazzi(obs_data + 'metals/gallazzi.dat', h = 1.0)

    #image
    fig = P.figure()
    ax = fig.add_subplot(111)
    ims = ax.imshow(s, vmin = smin, vmax = smax,
                    origin = 'lower', cmap = cm.gray,
                    interpolation = None,
                    extent = [mmin, mmax, Zmin, Zmax],
                    aspect = 'auto')
    ax.plot(mstar, z_50, 'g-', lw = 1.4, label = 'Median Gallazzi et al.')
    ax.plot(mstar, z_16, 'g--', lw = 1.3)
    ax.plot(mstar, z_84, 'g--', lw = 1.3)
    ax.plot(mbin_mid, N.log10(y50), 'c-', lw = 1.4, label = 'Median Data')
    ax.plot(mbin_mid, N.log10(y16), 'c--', lw = 1.3)
    ax.plot(mbin_mid, N.log10(y84), 'c--', lw = 1.3)
    ax.scatter([10.7], [0.0])
    ax.set_xlim(mmin, mmax)
    ax.set_ylim(Zmin, Zmax)
    ax.set_ylabel(r'$\log \left( \frac{Z}{Z_{\odot}} \right)$')
    ax.set_xlabel('$\log M_{star} \quad [M_{\odot}] $')
    cbar = fig.colorbar(ims, orientation='horizontal')
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
    try:
        P.legend(numpoints = 1, shadow = True, fancybox = True)
    except:
        P.legend()
    P.savefig(output)    

def massmet_star(halos, g, p, obs_data, label, typ = '.pdf'):
    
    output = 'massmet_star_' + label + typ
    mbar = (10.0**p.mcold + 10.0**p.mstar)
    fg = 10.0**p.mcold / mbar

    wgal = halos.weight[p.halo_id]
    #massmet_hess
    massmet_hess(p.mstar, N.log10(p.zstar), wgal, obs_data, output)

def haering_rix(file, comments = ';'):
    data = N.loadtxt(file, comments = ';')
    
    m_bulge = N.log10(data[:,10])
    m_bh = N.log10(data[:,2] * data[:,5])
    ellip = data[:,1] == 0
    s0 = data[:,1] == 1
    spiral = data[:,1] == 2

    return m_bulge, m_bh, ellip, spiral, s0

def mbh_hess(mbulge, mbh, weight, ymin, ymax, nybins, 
             mbin_fit, mbh_fit, output, obs,
             mmin = 8.0, mmax = 12.0, nmbins = 40,
             pmax = 1.0, pmin = 1e-3):
    
    #n.b. mbin and fgasbin are the bin CENTERS
    dm = (mmax - mmin) / nmbins
    mbin = mmin + N.arange(nmbins)*dm + dm/2.0

    dy = (ymax - ymin) / nybins
    ybin = ymin + N.arange(nybins)*dy + dy/2.0

    yhist = N.zeros((nybins,nmbins))

    #distributions in bins with weight factor
    for i in range(len(mbulge)):
        imbin = fix((mbulge[i]-mmin)/dm)
        if imbin >= 0 and imbin < nmbins:
            iy = fix((mbh[i]-ymin)/dy)
            if iy >= 0 and iy < nybins:
                yhist[iy, imbin] += weight[i]
    #conditional distributions in Mh bins
    for i in range(nmbins):
        pm = N.sum(yhist[:,i])
        if pm > 0:
            yhist[:,i] /= pm

    print N.min(yhist), N.max(yhist)

    s = N.log10(pmax) - N.log10(yhist)
    smax = N.log10(pmax) - N.log10(pmin)
    smin = N.log10(pmax)
    s[yhist <= 0.0] = 2.0*smax

    #medians
    mbin, y50, y16, y84 = perc_bin(mbin, mbulge, mbh)
    #y50 = N.zeros(nmbins)
    #y16 = N.zeros(nmbins)
    #y84 = N.zeros(nmbins)
    #ycum = N.zeros(nybins)
    #for i in range(nmbins):
    #    for j in range(nybins):
    #        ycum[j] = N.sum(yhist[0:j+1, i])
    #        ycum /= N.sum(yhist[:,i])
    #        y16[i] = N.interp(0.16, ybin, ycum)
    #        y50[i] = N.interp(0.50, ybin, ycum)
    #        y84[i] = N.interp(0.84, ybin, ycum)

    #haering_rix
    m_bulge, m_bh, ellip, spiral, S0 = haering_rix(obs + 'haering_rix/table1.dat')

    #image
    fig = P.figure()
    ax = fig.add_subplot(111)
    ims = ax.imshow(s, vmin = smin, vmax = smax,
                    origin = 'lower', cmap = cm.gray,
                    interpolation = None,
                    extent = [mmin, mmax, ymin, ymax],
                    aspect = 'auto')
    ax.plot(mbin_fit, mbh_fit, 'g-', lw = 1.4, label = 'Fit?')
    ax.plot(mbin_fit, mbh_fit + .3, 'g--', lw = 1.3)
    ax.plot(mbin_fit, mbh_fit - .3, 'g--', lw = 1.3)
    ax.plot(mbin[y50 != -99], y50[y50 != -99], 'c-', lw = 1.4, label = 'Median Data')
    ax.plot(mbin[y16 != -99], y16[y16 != -99], 'c--', lw = 1.3)
    ax.plot(mbin[y84 != -99], y84[y84 != -99], 'c--', lw = 1.3)
    ax.plot(m_bulge[ellip], m_bh[ellip], 'rs', lw = 1.3, label = 'Ellipticals')
    ax.plot(m_bulge[spiral], m_bh[spiral], 'bp', lw = 1.3, label = 'Spirals')
    ax.plot(m_bulge[S0], m_bh[S0], 'mD', lw = 1.3, label = 'S0')
    ax.set_xlim(mmin, mmax)
    ax.set_ylim(ymin, ymax)
    ax.set_ylabel(r'$\log M_{BH} \quad [M_{\odot}]$')
    ax.set_xlabel('$\log M_{bulge} \quad [M_{\odot}] $')
    #cbar = fig.colorbar(ims, orientation='horizontal')
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
    try:
        P.legend(numpoints = 1, loc = 'best', 
                 shadow = True, fancybox = True)
    except:
        P.legend()
    P.savefig(output)    

def mhb(h, p, obs, label):
    output = 'mbh_' + label + '.pdf'

    mbin_fit = 8.0 + N.arange(40)*0.1
    mbh_fit = 8.2 + 1.12*(mbin_fit - 11.0)

    central = p.gal_id == 1
    btt = 10.0**(p.mbulge - p.mstar)

    #TODO, maybe change this?
    early = btt >= 0.5
    late = btt <= 0.5
    print 'Number of galaxies %i, early types %i and late %i' % (len(p), len(p.mstar[early]), len(p.mstar[late]))
    
    mbin = 8.0 + ((11.8 - 8.0) / 19.0) * N.arange(19)
    mbh_hr = 8.2 + 1.12*(p.mbulge - 11.0)

    wgal = h.weight[p.halo_id]
    
    mbh_hess(p.mbulge, p.mbh, wgal, 5.0, 10.0, 40,
             mbin_fit, mbh_fit, output, obs)


def main(path, label):
    '''
    Driver function, call this with a path to the data,
    and label you wish to use for the files.
    '''
    #paths
    obs_data = '/Users/niemi/Desktop/Research/IDL/obs/'
    behroozi = obs_data + 'behroozi/mhmstar.dat'
    #read data from path
    g, gdust, prop, h = read_data(path)

    #plots
    fstar_plot(behroozi, g, prop, h, output = 'fstar.pdf')
    massfunc_plot(h, prop, obs_data)
    gasfrac_sam_cent(h, prop)
    ssfr_wrapper(h, prop, label)
    massmet_star(h, g, prop, obs_data, label)
    mhb(h, prop, obs_data, label)

if __name__ == '__main__':    
    label = 'Bolshoi'

    overWrite = False

    paths = glob.glob('/Users/niemi/Desktop/Research/run/*')
    for path in paths:
        last = path.split('/')[-1]
        if overWrite:
            print 'Plotting data from %s' % path
            try:
                os.mkdir(last)
            except:
                pass
            main(path+'/', label)
            for x in glob.glob('*.pdf'):
                shutil.move(x, './' + last + '/')
        else:
            if not os.path.isdir(last):
                print 'Plotting data from %s' % path 
                os.mkdir(last)
                main(path+'/', label)
                for x in glob.glob('*.pdf'):
                    new_name = x[:-4] + '_' + last + '.pdf'
                    os.rename(x, new_name)
                    shutil.move(new_name, './' + last + '/')
