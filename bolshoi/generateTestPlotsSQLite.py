'''
This script can be used to generate some basic plots
from Rachel's SAM. In these plots comparisons to
observational constrains are also performed.

:author : Sami-Matias Niemi
:contact : niemi@stsci.edu
'''
import matplotlib

matplotlib.rc('text', usetex=True)
matplotlib.rc('xtick', labelsize=12)
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rc('lines', markeredgewidth=2.0)
matplotlib.rcParams['lines.linewidth'] = 1.8
matplotlib.rcParams['legend.fontsize'] = 10
matplotlib.rcParams['legend.handlelength'] = 5
matplotlib.rcParams['font.size'] = 16
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
matplotlib.rcParams['xtick.labelsize'] = 'large'
matplotlib.rcParams['ytick.labelsize'] = 'large'
matplotlib.rcParams['legend.fancybox'] = True
matplotlib.rcParams['legend.shadow'] = True
matplotlib.use('Agg')
from matplotlib.ticker import MultipleLocator, NullFormatter
from matplotlib import cm
import numpy as N
import pylab as P
import scipy.stats as ss
#Imports from Sami's repo
import db.sqlite as sq
import astronomy.stellarMFs as stellarMFs
import astronomy.metals as metallicity
import astronomy.gasmasses as gas
import astronomy.blackholes as bh
import astronomy.baryons as baryons

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
        xbin_mid[i] = xbin[i] + 0.5 * (xbin[i + 1] - xbin[i])
        mask = (xdata > xbin[i]) & (xdata <= xbin[i + 1])
        if len(ydata[mask]) >= 10:
            y50[i] = ss.scoreatpercentile(ydata[mask], 50)
            y16[i] = ss.scoreatpercentile(ydata[mask], 16)
            y84[i] = ss.scoreatpercentile(ydata[mask], 84)

    return xbin_mid, y50, y16, y84


def fstar(path, db, output='fstar.png'):
    '''
    Stellar mass to halo mass ratio as a function of halo mass.
    This plot differs slightly from the one in the Somerville 2008:
    the plot in the paper is the fraction of baryons in stars. 
    '''
    #get data
    query = '''select mstar, mhalo, gal_id from galprop'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    mstar = data[:, 0]
    mhalo = data[:, 1]
    gal_id = data[:, 2]

    mfit = 10. + N.arange(50) * 0.1
    mbin = 10.7 + N.arange(25) * 0.2

    f8 = 8. - mfit
    #f9 = 9. - mfit

    fs_halo = 10.0 ** (mstar - mhalo)

    #central and satellite galaxies
    central = gal_id == 1
    sat = gal_id != 1

    mbin_mid, fs_50, fs_10, fs_90 = perc_bin(mbin, mhalo, fs_halo)
    mbin_mid, fs_cen_50, fs_cen_10, fs_cen_90 = perc_bin(mbin, mhalo[central], fs_halo[central])
    mbin_mid, fs_sat_50, fs_sat_10, fs_sat_90 = perc_bin(mbin, mhalo[sat], fs_halo[sat])

    #begin figure
    fig = P.figure(figsize=(10, 10))
    ax = fig.add_subplot(111)

    ax.scatter(mhalo[central], N.log10(fs_halo[central]),
               edgecolor='r', s=2, facecolor='r', label='Central galaxies')

    ax.plot(mbin_mid, N.log10(fs_50), 'ko', ms=10, label='Median, all galaxies')
    ax.plot(mbin_mid, N.log10(fs_10), 'k--')
    ax.plot(mbin_mid, N.log10(fs_90), 'k--')

    ax.plot(mbin_mid, N.log10(fs_sat_50), 'cD', ms=8, label='Median, satellite galaxies')
    ax.plot(mbin_mid, N.log10(fs_cen_50), 'pm', ms=8, label='Median, central galaxies')

    #constrains from moster et al.
    fstar_med_ben = stellarMFs.fstarBen(mfit, 11.884, 0.0282, 1.057, 0.5560)
    fstar_med_ben_scat = stellarMFs.fstarBen(mfit, 11.866, 0.02891, 1.110, 0.648)
    ax.plot(mfit, N.log10(fstar_med_ben), 'g-', label='Moster et al.')
    ax.plot(mfit, N.log10(fstar_med_ben_scat), c='burlywood', label='Moster et al. (sc)')

    #get fstar_behroozi_log
    mh, sh = stellarMFs.fstarBehroozi()
    ax.plot(mh, sh, 'hg', label='Behroozi et al.')

    ax.plot(mfit, f8, 'k--', c='0.25')

    #axis scales
    ax.set_xlim(9.8, 15.0)
    ax.set_ylim(-4.0, -0.75)

    #small ticks
    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m / 5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m / 5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)

    ax.set_ylabel(r'$\log_{10} \left ( \frac{M_{star}}{f_{b}M_{halo}} \right )$')
    ax.set_xlabel(r'$\log_{10} \left ( \frac{M_{(sub)halo}}{M_{\odot}} \right )$')

    P.legend(numpoints=1, scatterpoints=1)
    P.savefig(output)
    P.close()


def massfunctions(path, db,
                  mmax=12.5,
                  mmin=5.0,
                  nbins=30,
                  output='SMN',
                  nvolumes=15):
    '''
    Plots stellar mass functions, cold gas mass functions, & BH MF
    '''
    #get data
    query = '''select gal_id, halo_id, mbulge, mstar, mcold, mbh from galprop'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    gal_id = data[:, 0]
    halo_id = data[:, 1]
    mbulge = data[:, 2]
    mstar = data[:, 3]
    mcold = data[:, 4]
    mbh = data[:, 5]

    ngal = len(gal_id)
    print '%i galaxies found' % ngal

    #overrides weight for nvolumes Bolshoi sub-volumes
    weight = N.zeros(ngal) + 1. / (nvolumes * (50. / 0.7) ** 3)

    #mass bins
    dm = (mmax - mmin) / nbins
    mbin = mmin + (N.arange(nbins) + 0.5) * dm

    #mfit = mmin + N.arange(150) * 0.05

    mf_cold = N.zeros(nbins)
    mf_star = N.zeros(nbins)
    mf_star_central = N.zeros(nbins)
    mf_bar = N.zeros(nbins)
    mf_bh = N.zeros(nbins)

    mf_early = N.zeros(nbins)
    mf_late = N.zeros(nbins)
    mf_bulge = N.zeros(nbins)

    #TODO from IDL, should be done without looping
    btt = 10.0 ** (mbulge - mstar)
    for i in range(ngal):
        ihalo = halo_id[i]
        #cold gas
        ibin = int(N.floor((mcold[i] - mmin) / dm))
        if ibin >= 0 and ibin < nbins:
            mf_cold[ibin] += weight[ihalo]
            #stellar mass
        ibin = int(N.floor((mstar[i] - mmin) / dm))
        if ibin >= 0 and ibin < nbins:
            mf_star[ibin] += weight[ihalo]
            #stellar mass, by type
            if btt[i] >= 0.4:
                mf_early[ibin] += weight[ihalo]
            else:
                mf_late[ibin] += weight[ihalo]
                #stellar mass, centrals
            if gal_id[i] == 1:
                if ibin >= 0 and ibin < nbins:
                    mf_star_central[ibin] += weight[ihalo]
                    #bulge mass
        ibin = int(N.floor((mbulge[i] - mmin) / dm))
        if ibin >= 0 and ibin < nbins:
            mf_bulge[ibin] += weight[ihalo]
            #baryonic mass
        mbar = N.log10(10.0 ** mcold[i] + 10.0 ** mstar[i])
        ibin = int(N.floor((mbar - mmin) / dm))
        if ibin >= 0 and ibin < nbins:
            mf_bar[ibin] += weight[ihalo]
            #black hole
        ibin = int(N.floor((mbh[i] - mmin) / dm))
        if ibin >= 0 and ibin < nbins:
            mf_bh[ibin] += weight[ihalo]

    mf_cold = N.log10(mf_cold / dm)
    mf_star = N.log10(mf_star / dm)
    #mf_early = N.log10(mf_early / dm)
    #mf_late = N.log10(mf_late / dm)
    #mf_bulge = N.log10(mf_bulge / dm)
    #mf_star_central = N.log10(mf_star_central / dm)
    mf_bar = N.log10(mf_bar / dm)
    mf_bh = N.log10(mf_bh / dm)

    #stellar mass function plot
    #obs constrains
    mg, phig, phi_lowg, phi_highg = stellarMFs.bellG()
    mk, phik, phi_lowk, phi_highk = stellarMFs.bellK()
    #ml, phil, phi_lowl, phi_hiugl = mstar_lin(obs + 'sdss_mf/SDSS_SMF.dat')
    m, n, nlow, nhigh = stellarMFs.panter()

    fig = P.figure()
    ax = fig.add_subplot(111)
    ax.plot(mbin, mf_star, label='Stellar Mass Function')
    ax.errorbar(mg, phig, yerr=[phig - phi_highg, phi_lowg - phig], label='$G$-band from Bell et al.')
    ax.errorbar(mk, phik, yerr=[phik - phi_highk, phi_lowk - phik], label='$K$-band from Bell et al.')
    #ax.errorbar(ml, phil, yerr = [phi_lowl, phi_highl], label = 'Lin et al. K')
    ax.errorbar(m, n, yerr=[nlow - n, n - nhigh], label='$K$-band from Panter et al.')
    ax.set_xlim(8.0, 12.5)
    ax.set_ylim(-6.1, -1.0)
    ax.set_xlabel(r'$\log_{10} \left ( M_{\star} \ [M_{\odot}] \right )$')
    ax.set_ylabel(
        r'$\frac{\log_{10} \mathrm{d}N}{\mathrm{d}\log_{10} M_{\star}} \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    #small ticks
    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m / 5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m / 5)
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
    theta = gas.HIMassFunctionZwaan(mbin)
    m_hi, phi_hi, phi_low_hi, phi_high_hi = gas.HIMassFunctionBell()
    m_h2, phi_h2, phi_low_h2, phi_high_h2 = gas.H2MassFunctionBell()

    fig = P.figure()
    ax = fig.add_subplot(111)
    ax.plot(mbin, mf_cold, label='Cold Gas Mass Function')
    ax.plot(mbin, theta, 'g-', lw=1.8, label='Zwaan et al.')
    ax.errorbar(m_hi, phi_hi, yerr=[phi_hi - phi_high_hi, phi_low_hi - phi_hi],
                c='cyan', ls='--', lw=1.5, label='Bell et al. $H_{I}$')
    ax.errorbar(m_h2, phi_h2, yerr=[phi_h2 - phi_high_h2, phi_low_h2 - phi_h2],
                c='magenta', ls=':', lw=1.5, label='Bell et al. $H_{2}$')
    ax.plot(m_hi, N.log10(10.0 ** phi_hi + 10 ** phi_h2), 'r-', label='$H_{I} + H_{2}$')
    ax.set_xlim(8.0, 11.5)
    ax.set_ylim(-5.5, -0.8)
    ax.set_xlabel(r'$\log_{10} \left ( M_{\mathrm{cold}} \ [M_{\odot}] \right )$')
    ax.set_ylabel(r'$\frac{\log_{10} \mathrm{d}N}{\mathrm{d}\log_{10} M} \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    #small ticks
    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m / 5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m / 5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    P.legend()
    P.savefig('mfcold_' + output + '.pdf')
    P.close()

    #total baryons
    #obs contstrains
    m_bar, phi_bar, phi_low_bar, phi_high_bar = baryons.BellBaryonicMassFunction()

    fig = P.figure()
    ax = fig.add_subplot(111)
    ax.plot(mbin, mf_bar, label='Total Baryon Mass')
    ax.errorbar(m_bar, phi_bar, yerr=[phi_bar - phi_high_bar, phi_low_bar - phi_bar],
                c='g', ls='-', label='Bell et al.')
    ax.set_xlim(8.0, 12.5)
    ax.set_ylim(-4.9, -0.25)
    ax.set_xlabel(r'$\log_{10} \left ( M_{\mathrm{baryons}} \ [M_{\odot}] \right )$')
    ax.set_ylabel(
        r'$\frac{\log_{10} \mathrm{d}N}{\mathrm{d}\log_{10} M_{\mathrm{baryons}}} \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    #small ticks
    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m / 5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m / 5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    P.legend()
    P.savefig('mfbar_' + output + '.pdf')
    P.close()

    #BH mass function
    #obs constrains
    m_bh, phi_low_bh, phi_med_bh, phi_high_bh = bh.MarconiMassFunction()

    fig = P.figure()
    ax = fig.add_subplot(111)
    ax.plot(mbin, mf_bh, 'k-', label='Black Hole Mass Function')
    ax.plot(m_bh, phi_low_bh, 'g--')
    ax.plot(m_bh, phi_med_bh, 'g-', label='Marconi et al.')
    ax.plot(m_bh, phi_high_bh, 'g--')
    ax.set_xlim(6.0, 10.2)
    ax.set_ylim(-6.9, -1.5)
    ax.set_xlabel(r'$\log_{10} \left ( M_{BH} \ [M_{\odot}] \right )$')
    ax.set_ylabel(r'$\frac{\log_{10} \mathrm{d}N}{\mathrm{d}\log_{10} M} \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    #small ticks
    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m / 5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m / 5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    P.legend()
    P.savefig('mfBH_' + output + '.pdf')
    P.close()


def gasfracHess(mstar, fgas, weight, label, output,
                mmin=8.5, mmax=11.7, nmbins=16,
                fgasmin=0.0, fgasmax=1.0, nfbins=10,
                pmax=1.0, pmin=0.01):
    '''
    Plot _conditional_ distribution of gas fraction vs. stellar mass.
    Ported from an IDL code, should be cleaned.
    '''
    #n.b. mbin and fgasbin are the bin CENTERS
    dm = (mmax - mmin) / nmbins
    mbin = mmin + (N.arange(nmbins)) * dm + dm / 2.0
    dfgas = (fgasmax - fgasmin) / nfbins
    #fgasbin = fgasmin + (N.arange(nfbins)) * dfgas + dfgas / 2.0

    fgashist = N.zeros((nfbins, nmbins))

    #without weight factor
    yhist_num = N.zeros((nfbins, nmbins))
    #number of halos in each bin
    nh = N.zeros(nmbins)

    #compute gas fraction distributions in stellar mass bins
    #with weight factor
    #this should be rewritten...
    for i in range(len(mstar)):
        imbin = int(N.floor((mstar[i] - mmin) / dm))
        if imbin >= 0 and imbin < nmbins:
            nh[imbin] = nh[imbin] + weight[i]
            ifgas = int(N.floor((fgas[i] - fgasmin) / dfgas))
            if ifgas >= 0 and ifgas < nfbins:
                fgashist[ifgas, imbin] = fgashist[ifgas, imbin] + weight[i]
                yhist_num[ifgas, imbin] = yhist_num[ifgas, imbin] + 1

    #conditional distributions in Mh bins
    for i in range(nmbins):
        if nh[i] > 0.0:
            fgashist[:, i] /= nh[i]

    s = N.log10(pmax) - N.log10(fgashist)
    smax = N.log10(pmax) - N.log10(pmin)
    smin = N.log10(pmax)

    s[fgashist <= 0.0] = 2.0 * smax
    s[yhist_num <= 1] = 2.0 * smax

    #obs contstrains
    kmstar, kfgas = gas.gasFractionKannappan()

    #medians
    mbin_mid, y50, y16, y84 = perc_bin(mbin, mstar, fgas)

    #image
    fig = P.figure()
    ax = fig.add_subplot(111)
    ims = ax.imshow(s, vmin=smin, vmax=smax,
                    origin='lower', cmap=cm.gray,
                    interpolation=None,
                    extent=[mmin, mmax, pmin, pmax],
                    aspect='auto')
    ax.plot(mbin_mid, y50, 'r-', label='Median')
    ax.plot(mbin_mid, y16, 'r--')
    ax.plot(mbin_mid, y84, 'r--')
    ax.plot(kmstar, kfgas, 'go', label='Kannappan et al.')
    ax.set_xlim(mmin, mmax)
    ax.set_ylim(pmin, pmax)
    ax.set_ylabel('Gas fraction')
    ax.set_xlabel(r'$\log_{10} \left ( M_{\star} \ [M_{\odot}] \right ) $')
    # cbar = fig.colorbar(ims, orientation='horizontal')
    # cbar = fig.colorbar(ims, ticks=[min, max/factor/2., max/factor], orientation='horizontal')
    # cbar.ax.set_xticklabels(['%3.2f' % min, '%3.2f' % (max/2.), '%3.2f' % (max)])
    # cbar.ax.set_title('Pixel Values (counts s$^{-1}$)')
    #small ticks
    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m / 5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m / 5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    try:
        P.legend(numpoints=1, shadow=True, fancybox=True)
    except:
        P.legend()
    P.savefig(output)


def ssfr(path, db, mask, output, typ='.pdf'):
    '''
    Specific star formation rate plots.
    '''
    #get data
    query = '''select halo_id, mstar, sfr_ave from galprop'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    halo_id = data[:, 0].astype(N.int)
    mstar = data[:, 1]
    sfr_ave = data[:, 2]
    #get the weights from another table
    query = '''select weight from halos'''
    d = sq.get_data_sqliteSMNfunctions(path, db, query)
    weight = d[:, 0]

    #set weighting
    wgal = weight[halo_id]

    log_ssfr = N.log10(sfr_ave / 10.0 ** mstar)
    log_ssfr[log_ssfr <= -14.0] = -13.8

    ssfrHess(mstar[mask], log_ssfr[mask], wgal[mask], output + typ)


def ssfrHess(mstar, ssfr, weight, output,
             mmin=9.027, dm=0.309, nmbins=11,
             ssfrmin=-13.0, ssfrmax=-8.5, nssfrbins=24,
             ssfr_cut=-11.1, pmax=0.5, pmin=1e-5):
    '''
    log ssfr in yr
    '''
    mmax = mmin + dm * nmbins
    fpass = N.zeros(nmbins)

    #n.b. mbin and fgasbin are the bin CENTERS
    #mbin = mmin + (N.zeros(nmbins)) * dm + dm / 2.0
    dssfr = (ssfrmax - ssfrmin) / (nssfrbins)
    #ssfrbin = ssfrmin + (N.arange(nssfrbins)) * dssfr + dssfr / 2.0
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
        imbin = int(N.floor((mstar[i] - mmin) / dm))
        if imbin >= 0 and imbin < nmbins:
            nh[imbin] += weight[i]
            if ssfr[i] <= ssfr_cut: fpass[imbin] += weight[i]
            issfr = int(N.floor((ssfr[i] - ssfrmin) / dssfr))
            if issfr >= 0 and issfr < nssfrbins:
                ssfrhist[issfr, imbin] += weight[i]
                yhist_num[issfr, imbin] += 1.

    nhtot = N.sum(nh)
    print nhtot

    #Make hess plots
    #conditional distributions in Mh bins
    for i in range(nmbins):
        if nh[i] > 0.0:
            ssfrhist[:, i] = ssfrhist[:, i] / nh[i]
            fpass[i] = fpass[i] / nh[i]

    s = N.log10(pmax) - N.log10(ssfrhist)
    smax = N.log10(pmax) - N.log10(pmin)
    smin = N.log10(pmax)

    s[ssfrhist <= 0.0] = 2.0 * smax
    s[yhist_num <= 1.0] = 2.0 * smax

    print 'SSFRhist: ', N.min(ssfrhist), N.min(ssfrhist[ssfrhist >= 0])
    print 'smin, smax: ', smin, smax
    print N.min(s), N.max(s)

    c = s.copy()
    c[ssfrhist > 0.0] = N.log10(ssfrhist[ssfrhist > 0.0])
    #print N.max(c), N.min(c[ssfrhist > 0.0])
    c[ssfrhist <= 0.0] = -99.9
    c[yhist_num <= 2.0] = -99.9

    #main sequence and quenched box
    mbin = 8.0 + N.arange(32) * 0.1
    #Salim et al.
    ssfr_fit = -0.36 * mbin - 6.4

    #contour levels
    clev = -5.0 + N.arange(30) * 0.30

    #image
    fig = P.figure()
    fig.subplots_adjust(left=0.16, bottom=0.11,
                        right=0.99, top=0.93,
                        wspace=0.0, hspace=0.0)
    ax = fig.add_subplot(111)

    #set title
    if '_sph' in output:
        ax.set_title('Spherical Galaxies')
    elif '_sat' in output:
        ax.set_title('Satellite Galaxies')
    elif '_cent' in output:
        ax.set_title('Central Galaxies')
    elif '_disk' in output:
        ax.set_title('Disk Galaxies')
    else:
        ax.set_title('All Galaxies')

    ims = ax.imshow(s, vmin=smin, vmax=smax,
                    origin='lower', cmap=cm.gray,
                    interpolation=None,
                    extent=[mmin, mmax, ssfrmin, ssfrmax],
                    aspect='auto')
    cs = ax.contour(c, levels=clev, origin='lower',
                    extent=[mmin, mmax, ssfrmin, ssfrmax],
                    colors='m', linewidths=1.0, linestyles='-',
                    rightside_up=True)
    ax.plot(mbin, ssfr_fit, 'b-', label='Blue Sequence')
    ax.plot([9.9, 11.5], [-11.7, -11.95], 'r-', label='Red Sequence')
    ax.plot([9.4, 11.5], [-10.7, -11.25], 'g--', label='Green Valley')
    P.clabel(cs, fontsize=5)
    ax.set_xlim(mmin, mmax)
    ax.set_ylim(ssfrmin, ssfrmax)
    ax.set_ylabel(r'$\log_{10} \left( \frac{\dot{M}_{\star}}{M_{\star}} \ [\mathrm{yr}^{-1}] \right)$')
    ax.set_xlabel(r'$\log_{10} \left ( M_{\star} \ [M_{\odot}] \right ) $')

    #small ticks
    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m / 5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m / 5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    try:
        P.legend(numpoints=1, shadow=True, fancybox=True)
    except:
        P.legend()
    P.savefig(output)


def ssfrWrapper(path, db):
    #get data
    query = '''select gal_id, mbulge, mstar from galprop'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    gal_id = data[:, 0]
    mbulge = data[:, 1]
    mstar = data[:, 2]

    #make masks for all, central, and satellite galaxies
    all = gal_id >= 0
    c = gal_id == 1
    s = gal_id != 1

    #early vs. late type galaxies
    btt = 10.0 ** (mbulge - mstar)
    early = btt >= 0.4
    late = btt < 0.4

    label = 'ssfrBolshoi'

    ssfr(path, db, all, label)
    ssfr(path, db, c, label + '_cent')
    ssfr(path, db, s, label + '_sat')
    ssfr(path, db, early, label + '_sph')
    ssfr(path, db, late, label + '_disk')


def gasFraction(path, db,
                label='Bolshoi',
                output='fgascentral',
                tpy='.pdf'):
    #get data
    query = '''select gal_id, halo_id, mbulge, mstar, mcold, mbh from galprop'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    gal_id = data[:, 0]
    halo_id = data[:, 1].astype(N.int)
    mbulge = data[:, 2]
    mstar = data[:, 3]
    mcold = data[:, 4]
    #get the weights from another table
    query = '''select weight from halos'''
    d = sq.get_data_sqliteSMNfunctions(path, db, query)
    weight = d[:, 0]

    fgas = 10.0 ** mcold / (10.0 ** mcold + 10.0 ** mstar)
    wgal = weight[halo_id]
    btt = 10.0 ** (mbulge - mstar)

    #masking
    cdisk = (gal_id == 1) & (btt < 0.4)

    #output file
    output = output + label + tpy
    #call the gas
    gasfracHess(mstar[cdisk], fgas[cdisk], wgal[cdisk], label, output)


def fix(x):
    '''
    IDL function.
    '''
    return int(N.floor(x))


def massMetHess(mstar, met, weight, output,
                mmin=8.8, mmax=12.0, nmbins=18,
                Zmin=-1.5, Zmax=1.0, nzbins=20,
                pmax=1.0, pmin=1e-3):
    #n.b. mbin and zbin are the bin CENTERS
    dm = (mmax - mmin) / nmbins
    mbin = mmin + (N.arange(nmbins)) * dm + dm / 2.0
    dmet = (Zmax - Zmin) / nzbins
    #metbin = Zmin + (N.arange(nzbins)) * dmet + dmet / 2.0

    methist = N.zeros((nzbins, nmbins))
    num = N.zeros((nzbins, nmbins))
    nh = N.zeros(nmbins)

    #compute gas distributions in stellar mass bins
    #with weight factor
    for i in range(len(mstar)):
        imbin = fix((mstar[i] - mmin) / dm)
        if imbin >= 0 and imbin < nmbins:
            nh[imbin] = nh[imbin] + weight[i]
            imet = fix((met[i] - Zmin) / dmet)
            if imet >= 0 and imet < nzbins:
                methist[imet, imbin] += weight[i]
                num[imet, imbin] += 1

    #conditional distributions in Mh bins
    for i in range(nmbins):
        if nh[i] > 0.0:
            methist[:, i] /= nh[i]

    s = N.log10(pmax) - N.log10(methist)
    smax = N.log10(pmax) - N.log10(pmin)
    smin = N.log10(pmax)

    s[methist <= 0.0] = 2.0 * smax
    s[num <= 1.0] = 2.0 * smax

    #medians
    mask = 10.0 ** met > 0.0
    mbin_mid, y50, y16, y84 = perc_bin(mbin, mstar[mask], 10.0 ** met[mask])

    #gallazzi
    mstar, z_50, z_16, z_84 = metallicity.gallazzi(h=1.0)

    #image
    fig = P.figure()
    fig.subplots_adjust(left=0.14, bottom=0.11,
                        right=0.97, top=0.97,
                        wspace=0.0, hspace=0.0)
    ax = fig.add_subplot(111)
    ims = ax.imshow(s, vmin=smin, vmax=smax,
                    origin='lower', cmap=cm.gray,
                    interpolation=None,
                    extent=[mmin, mmax, Zmin, Zmax],
                    aspect='auto')
    ax.plot(mstar, z_50, 'g-', lw=1.4, label='Median from Gallazzi et al.')
    ax.plot(mstar, z_16, 'g--', lw=1.3)
    ax.plot(mstar, z_84, 'g--', lw=1.3)
    ax.plot(mbin_mid, N.log10(y50), 'c-', lw=1.4, label='Median from Data')
    ax.plot(mbin_mid, N.log10(y16), 'c--', lw=1.3)
    ax.plot(mbin_mid, N.log10(y84), 'c--', lw=1.3)
    ax.scatter([10.7], [0.0])
    ax.set_xlim(mmin, mmax)
    ax.set_ylim(Zmin, Zmax)
    ax.set_ylabel(r'$\log_{10} \left( \frac{Z}{Z_{\odot}} \right)$')
    ax.set_xlabel(r'$\log_{10} \left ( M_{\star} \ [M_{\odot}] \right ) $')

    #small ticks
    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m / 5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m / 5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    try:
        P.legend(numpoints=1, shadow=True, fancybox=True)
    except:
        P.legend()
    P.savefig(output)


def massMet(path, db, typ='.pdf'):
    #get data
    query = '''select halo_id, mstar, zstar from galprop where zstar > -50 and zstar < 50'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    halo_id = data[:, 0].astype(N.int)
    mstar = data[:, 1]
    zstar = N.log10(data[:, 2])

    #get the weights from another table
    query = '''select weight from halos'''
    d = sq.get_data_sqliteSMNfunctions(path, db, query)
    weight = d[:, 0]
    wgal = weight[halo_id]

    output = 'massMetStarBolshoi' + typ
    #mbar = (10.0 ** mcold + 10.0 ** mstar)
    #fg = 10.0 ** p.mcold / mbar

    #massmet_hess
    massMetHess(mstar, zstar, wgal, output)


def mbhHess(mbulge, mbh, weight, ymin, ymax, nybins,
            mbin_fit, mbh_fit, output,
            mmin=8.0, mmax=12.0, nmbins=40,
            pmax=1.0, pmin=1e-3):
    #n.b. mbin and fgasbin are the bin CENTERS
    dm = (mmax - mmin) / nmbins
    mbin = mmin + N.arange(nmbins) * dm + dm / 2.0

    dy = (ymax - ymin) / nybins
    #ybin = ymin + N.arange(nybins) * dy + dy / 2.0

    yhist = N.zeros((nybins, nmbins))

    #distributions in bins with weight factor
    for i in range(len(mbulge)):
        imbin = fix((mbulge[i] - mmin) / dm)
        if imbin >= 0 and imbin < nmbins:
            iy = fix((mbh[i] - ymin) / dy)
            if iy >= 0 and iy < nybins:
                yhist[iy, imbin] += weight[i]
                #conditional distributions in Mh bins
    for i in range(nmbins):
        pm = N.sum(yhist[:, i])
        if pm > 0:
            yhist[:, i] /= pm

    print N.min(yhist), N.max(yhist)

    s = N.log10(pmax) - N.log10(yhist)
    smax = N.log10(pmax) - N.log10(pmin)
    smin = N.log10(pmax)
    s[yhist <= 0.0] = 2.0 * smax

    #medians
    mbin, y50, y16, y84 = perc_bin(mbin, mbulge, mbh)

    #haering_rix
    m_bulge, m_bh, ellip, spiral, S0 = bh.MassesHaeringRix()

    #image
    fig = P.figure()
    fig.subplots_adjust(left=0.1, bottom=0.11,
                        right=0.97, top=0.97,
                        wspace=0.0, hspace=0.0)
    ax = fig.add_subplot(111)
    ims = ax.imshow(s, vmin=smin, vmax=smax,
                    origin='lower', cmap=cm.gray,
                    interpolation=None,
                    extent=[mmin, mmax, ymin, ymax],
                    aspect='auto')
    ax.plot(mbin_fit, mbh_fit, 'g-', lw=1.4, label='Fit')
    ax.plot(mbin_fit, mbh_fit + .3, 'g--', lw=1.3)
    ax.plot(mbin_fit, mbh_fit - .3, 'g--', lw=1.3)
    ax.plot(mbin[y50 != -99], y50[y50 != -99], 'c-', lw=1.4, label='Median Data')
    ax.plot(mbin[y16 != -99], y16[y16 != -99], 'c--', lw=1.3)
    ax.plot(mbin[y84 != -99], y84[y84 != -99], 'c--', lw=1.3)
    ax.plot(m_bulge[ellip], m_bh[ellip], 'rs', lw=1.3, label='Ellipticals')
    ax.plot(m_bulge[spiral], m_bh[spiral], 'bp', lw=1.3, label='Spirals')
    ax.plot(m_bulge[S0], m_bh[S0], 'mD', lw=1.3, label='S0')
    ax.set_xlim(mmin, mmax)
    ax.set_ylim(ymin, ymax)
    ax.set_ylabel(r'$\log_{10} \left ( M_{\mathrm{BH}} \ [M_{\odot}] \right )$')
    ax.set_xlabel(r'$\log_{10} \left ( M_{\mathrm{bulge}} \ [M_{\odot}] \right ) $')

    #small ticks
    m = ax.get_yticks()[1] - ax.get_yticks()[0]
    yminorLocator = MultipleLocator(m / 5)
    yminorFormattor = NullFormatter()
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    m = ax.get_xticks()[1] - ax.get_xticks()[0]
    xminorLocator = MultipleLocator(m / 5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    try:
        P.legend(numpoints=1, loc='best',
                 shadow=True, fancybox=True)
    except:
        P.legend()
    P.savefig(output)


def mhb(path, db, type='.pdf'):
    #get data
    query = '''select halo_id, mstar, mbulge, mbh from galprop'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    halo_id = data[:, 0].astype(N.int)
    mstar = data[:, 1]
    mbulge = data[:, 2]
    mbh = data[:, 3]

    #get the weights from another table
    query = '''select weight from halos'''
    d = sq.get_data_sqliteSMNfunctions(path, db, query)
    weight = d[:, 0]
    wgal = weight[halo_id]

    #fitting functions of ??
    mbin_fit = 8.0 + N.arange(40) * 0.1
    mbh_fit = 8.2 + 1.12 * (mbin_fit - 11.0)

    #central = p.gal_id == 1
    btt = 10.0 ** (mbulge - mstar)

    #These could be changed to 0.4 and 0.6...
    early = btt >= 0.5
    late = btt <= 0.5
    print 'Number of galaxies %i, early types %i and late %i' % (len(mstar), len(mstar[early]), len(mstar[late]))

    #mbin = 8.0 + ((11.8 - 8.0) / 19.0) * N.arange(19)
    #mbh_hr = 8.2 + 1.12 * (p.mbulge - 11.0)
    output = 'mbhBolshoi' + type

    mbhHess(mbulge, mbh, wgal, 4.85, 10.0, 40,
            mbin_fit, mbh_fit, output)


def main(path, db):
    '''
    Driver function, call this with a path to the data,
    and label you wish to use for the files.
    '''
    #call plotting functions
    fstar(path, db)
    massfunctions(path, db)
    gasFraction(path, db)
    ssfrWrapper(path, db)
    massMet(path, db)
    mhb(path, db)

if __name__ == '__main__':
    #input data
    path = '/Users/niemi/Desktop/Research/run/newtree1/'
    db = 'sams.db'

    #call the driver
    main(path, db)