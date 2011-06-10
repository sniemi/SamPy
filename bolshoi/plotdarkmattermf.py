'''
Plots a dark matter halo mass function at different
redshifts. Input data are from the Bolshoi simulation.

:author: Sami-Matias Niemi
'''
import matplotlib

matplotlib.rc('text', usetex=True)
matplotlib.rcParams['font.size'] = 14
matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
matplotlib.use('PDF')
import pylab as P
import numpy as N
import glob as g
import os
#From Sami's repo
import astronomy.differentialfunctions as df
import smnIO.read as io
import db.sqlite
import log.Logger as lg

def plot_mass_function(redshift, h, no_phantoms, *data):
    #fudge factor
    fudge = 2.0
    #http://adsabs.harvard.edu/abs/2001MNRAS.321..372J
    #Jenkins et al. paper has sqrt(2./pi) while
    #Rachel's code has 1/(sqrt(2*pi))
    #ratio of these two is the fudge factor    

    #read data to dictionary
    dt = {}
    for x in data[0]:
        if 'Bolshoi' in x:
            dt[x] = io.readBolshoiDMfile(data[0][x], 0, no_phantoms)
        else:
            dt[x] = N.loadtxt(data[0][x])

    #calculate the mass functions from the Bolshoi data
    mbin0, mf0 = df.diffFunctionLogBinning(dt['Bolshoi'] / h,
                                           nbins=35,
                                           h=0.7,
                                           mmin=10 ** 9.0,
                                           mmax=10 ** 15.0,
                                           physical_units=True)

    del dt['Bolshoi']
    #use chain rule to get dN / dM
    #dN/dM = dN/dlog10(M) * dlog10(M)/dM
    #d/dM (log10(M)) = 1 / (M*ln(10)) 
    mf0 *= 1. / (mbin0 * N.log(10))
    #put mass back to power
    mbin0 = 10 ** mbin0
    #title
    if no_phantoms:
        ax1.set_title('Bolshoi Dark Matter Mass Functions (no phantoms)')
    else:
        ax1.set_title('Bolshoi Dark Matter Mass Functions')

    #mark redshift
    for a, b in zip(mbin0[::-1], mf0[::-1]):
        if b > 10 ** -6:
            break
    ax1.annotate('$z \sim %.1f$' % redshift,
            (0.98 * a, 3 * 10 ** -6), size='x-small')

    #Analytical MFs
    #0th column: log10 of mass (Msolar, NOT Msolar/h)
    #1st column: mass (Msolar/h)
    #2nd column: (dn/dM)*dM, per Mpc^3 (NOT h^3/Mpc^3)
    xST = 10 ** dt['Sheth-Tormen'][:, 0]
    yST = dt['Sheth-Tormen'][:, 2] * fudge
    sh = ax1.plot(xST, yST, 'b-', lw=1.3)
    #PS
    xPS = 10 ** dt['Press-Schecter'][:, 0]
    yPS = dt['Press-Schecter'][:, 2] * fudge
    ps = ax1.plot(xPS, yPS, 'g--', lw=1.1)

    #MF from Bolshoi
    bolshoi = ax1.plot(mbin0, mf0, 'ro:', ms=5)

    #delete data to save memory, dt is not needed any longer
    del dt

    #plot the residuals
    if round(float(redshift), 1) < 1.5:
        #interploate to right x scale
        yST = N.interp(mbin0, xST, yST)
        yPS = N.interp(mbin0, xPS, yPS)
        #make the plot
        ax2.annotate('$z \sim %.1f$' % redshift,
                (1.5 * 10 ** 9, 1.05), xycoords='data',
                     size=10)
        ax2.axhline(1.0, color='b')
        ax2.plot(mbin0, mf0 / yST, 'b-')
        ax2.plot(mbin0, mf0 / yPS, 'g-')

    ax1.set_xscale('log')
    ax2.set_xscale('log')
    ax1.set_yscale('log')

    ax1.set_ylim(10 ** -7, 10 ** -1)
    ax2.set_ylim(0.45, 1.55)
    ax1.set_xlim(10 ** 9, 10 ** 15)
    ax2.set_xlim(10 ** 9, 10 ** 15)

    ax1.set_xticklabels([])

    ax2.set_xlabel(r'$M_{\mathrm{vir}} \quad [M_{\odot}]$')
    ax1.set_ylabel(r'$\mathrm{d}N / \mathrm{d}M_{\mathrm{vir}} \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    ax2.set_ylabel(r'$\frac{\mathrm{Bolshoi}}{\mathrm{Model}}$')

    ax1.legend((bolshoi, sh, ps),
            ('Bolshoi', 'Sheth-Tormen', 'Press-Schecter'),
                                shadow=True, fancybox=True,
                                numpoints=1)


def plot_mass_functionAnalytical2(redshift, h, no_phantoms, *data):
    #fudge factor
    fudge = 1.
    #http://adsabs.harvard.edu/abs/2001MNRAS.321..372J
    #Jenkins et al. paper has sqrt(2./pi) while
    #Rachel's code has 1/(sqrt(2*pi))
    #ratio of these two is the fudge factor  

    #read data
    dt = {}
    for x in data[0]:
        if 'Bolshoi' in x:
            dt[x] = io.readBolshoiDMfile(data[0][x], 0, no_phantoms)
        else:
            #M dN/dM dNcorr/dM dN/dlog10(M) dN/dlog10(Mcorr)
            d = N.loadtxt(data[0][x])
            dt['Press-Schecter'] = N.array([d[:, 0], d[:, 3]])
            dt['Sheth-Tormen'] = N.array([d[:, 0], d[:, 4]])


    #calculate the mass functions from the Bolshoi data
    mbin0, mf0 = df.diffFunctionLogBinning(dt['Bolshoi'] / h,
                                           nbins=35,
                                           h=0.7,
                                           mmin=10 ** 9.0,
                                           mmax=10 ** 15.0,
                                           physical_units=True)
    del dt['Bolshoi']

    mbin0 = 10 ** mbin0
    #title
    if no_phantoms:
        ax1.set_title('Bolshoi Dark Matter Mass Functions (no phantoms)')
    else:
        ax1.set_title('Bolshoi Dark Matter Mass Functions')

    #mark redshift
    for a, b in zip(mbin0[::-1], mf0[::-1]):
        if b > 10 ** -6:
            break
    ax1.annotate('$z \sim %.1f$' % redshift,
            (0.98 * a, 3 * 10 ** -6), size='x-small')

    #Analytical MFs
    xST = dt['Sheth-Tormen'][0]
    yST = dt['Sheth-Tormen'][1] * fudge
    print xST[1000], yST[1000]
    sh = ax1.plot(xST, yST, 'b-', lw=1.3)
    #PS
    xPS = dt['Press-Schecter'][0]
    yPS = dt['Press-Schecter'][1] * fudge
    ps = ax1.plot(xPS, yPS, 'g--', lw=1.1)

    #MF from Bolshoi
    bolshoi = ax1.plot(mbin0, mf0, 'ro:', ms=5)

    #delete data to save memory, dt is not needed any longer
    del dt

    #plot the residuals
    if round(float(redshift), 1) < 1.5:
        #interploate to right x scale
        mfintST = N.interp(xST, mbin0, mf0)
        mfintPS = N.interp(xPS, mbin0, mf0)
        #yST = N.interp(mbin0, xST, yST)
        #yPS = N.interp(mbin0, xPS, yPS)
        #make the plot
        ax2.annotate('$z \sim %.0f$' % redshift,
                (1.5 * 10 ** 9, 1.05), xycoords='data',
                     size=10)
        ax2.axhline(1.0, color='b')
        ax2.plot(xST, mfintST / yST, 'b-')
        ax2.plot(xPS, mfintPS / yPS, 'g-')
        #ax2.plot(mbin0, mf0 / yST, 'b-')
        #ax2.plot(mbin0, mf0 / yPS, 'g-')

    ax1.set_xscale('log')
    ax2.set_xscale('log')
    ax1.set_yscale('log')

    ax1.set_ylim(3 * 10 ** -7, 10 ** 0)
    ax2.set_ylim(0.45, 1.55)
    ax1.set_xlim(10 ** 9, 10 ** 15)
    ax2.set_xlim(10 ** 9, 10 ** 15)

    ax1.set_xticklabels([])

    ax2.set_xlabel(r'$M_{\mathrm{vir}} \quad [M_{\odot}]$')
    ax1.set_ylabel(r'$\mathrm{d}N / \mathrm{d}\log_{10}(M_{\mathrm{vir}}) \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    ax2.set_ylabel(r'$\frac{\mathrm{Bolshoi}}{\mathrm{Model}}$')

    ax1.legend((bolshoi, sh, ps),
            ('Bolshoi', 'Sheth-Tormen', 'Press-Schecter'),
                                shadow=True, fancybox=True,
                                numpoints=1)


def plotDMMFfromGalpropz(redshift, h, *data):
    #fudge factor
    fudge = 2.0
    #http://adsabs.harvard.edu/abs/2001MNRAS.321..372J
    #Jenkins et al. paper has sqrt(2./pi) while
    #Rachel's code has 1/(sqrt(2*pi))
    #ratio of these two is the fudge factor

    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    path = hm + '/Dropbox/Research/Bolshoi/run/trial2/'
    database = 'sams.db'

    rlow = redshift - 0.1
    rhigh = redshift + 0.1

    query = '''select mhalo from galpropz where
               galpropz.zgal > %f and galpropz.zgal <= %f and
               galpropz.gal_id = 1
    ''' % (rlow, rhigh)

    print query

    #read data
    dt = {}
    for x in data[0]:
        dt[x] = N.loadtxt(data[0][x])

    dt['Bolshoi'] = db.sqlite.get_data_sqlite(path, database, query) * 1e9

    #calculate the mass functions from the Bolshoi data
    mbin0, mf0 = df.diffFunctionLogBinning(dt['Bolshoi'] / h,
                                           nbins=35,
                                           h=0.7,
                                           mmin=10 ** 9.0,
                                           mmax=10 ** 15.0,
                                           volume=50,
                                           nvols=26,
                                           physical_units=True)
    del dt['Bolshoi']
    #use chain rule to get dN / dM
    #dN/dM = dN/dlog10(M) * dlog10(M)/dM
    #d/dM (log10(M)) = 1 / (M*ln(10)) 
    mf0 *= 1. / (mbin0 * N.log(10))
    mbin0 = 10 ** mbin0
    #title
    ax1.set_title('Dark Matter Halo Mass Functions (galpropz.dat)')

    #mark redshift
    for a, b in zip(mbin0[::-1], mf0[::-1]):
        if b > 10 ** -6:
            break
    ax1.annotate('$z \sim %.0f$' % redshift,
            (0.98 * a, 3 * 10 ** -7), size='x-small')

    #Analytical MFs
    #0th column: log10 of mass (Msolar, NOT Msolar/h)
    #1st column: mass (Msolar/h)
    #2nd column: (dn/dM)*dM, per Mpc^3 (NOT h^3/Mpc^3)
    xST = 10 ** dt['Sheth-Tormen'][:, 0]
    yST = dt['Sheth-Tormen'][:, 2] * fudge
    sh = ax1.plot(xST, yST, 'b-', lw=1.3)
    #PS
    xPS = 10 ** dt['Press-Schecter'][:, 0]
    yPS = dt['Press-Schecter'][:, 2] * fudge
    ps = ax1.plot(xPS, yPS, 'g--', lw=1.1)

    #MF from Bolshoi
    bolshoi = ax1.plot(mbin0, mf0, 'ro:', ms=5)

    #delete data to save memory, dt is not needed any longer
    del dt

    #plot the residuals
    if round(float(redshift), 1) < 1.5:
        #interploate to right x scale
        ySTint = N.interp(mbin0, xST, yST)
        yPSint = N.interp(mbin0, xPS, yPS)
        #make the plot
        ax2.annotate('$z \sim %.0f$' % redshift,
                (1.5 * 10 ** 9, 1.05), xycoords='data',
                     size=10)
        ax2.axhline(1.0, color='b')
        ax2.plot(mbin0, mf0 / ySTint, 'b-')
        ax2.plot(mbin0, mf0 / yPSint, 'g-')

    ax1.set_xscale('log')
    ax2.set_xscale('log')
    ax1.set_yscale('log')

    ax1.set_ylim(5 * 10 ** -8, 10 ** -1)
    ax2.set_ylim(0.45, 1.55)
    ax1.set_xlim(10 ** 9, 10 ** 15)
    ax2.set_xlim(10 ** 9, 10 ** 15)

    ax1.set_xticklabels([])

    ax2.set_xlabel(r'$M_{\mathrm{vir}} \quad [M_{\odot}]$')
    ax1.set_ylabel(r'$\mathrm{d}N / \mathrm{d}M_{\mathrm{vir}} \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    ax2.set_ylabel(r'$\frac{\mathrm{galpropz.dat}}{\mathrm{Model}}$')

    ax1.legend((bolshoi, sh, ps),
            ('Bolshoi', 'Sheth-Tormen', 'Press-Schecter'),
                                shadow=True, fancybox=True,
                                numpoints=1)


def plotDMMFfromGalpropzAnalytical2(redshift, h, *data):
    #fudge factor
    fudge = 1.
    #http://adsabs.harvard.edu/abs/2001MNRAS.321..372J
    #Jenkins et al. paper has sqrt(2./pi) while
    #Rachel's code has 1/(sqrt(2*pi))
    #ratio of these two is the fudge factor    

    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    path = hm + '/Dropbox/Research/Bolshoi/run/trial2/'
    database = 'sams.db'

    rlow = redshift - 0.1
    rhigh = redshift + 0.1

    query = '''select mhalo from galpropz where
               galpropz.zgal > %f and galpropz.zgal <= %f and
               galpropz.gal_id = 1
    ''' % (rlow, rhigh)

    #Hubble constants
    h3 = h ** 3
    #read data
    dt = {}
    for x in data[0]:
        #M dN/dM dNcorr/dM dN/dlog10(M) dN/dlog10(Mcorr)
        d = N.loadtxt(data[0][x])
        dt['Press-Schecter'] = N.array([d[:, 0], d[:, 3]])
        dt['Sheth-Tormen'] = N.array([d[:, 0], d[:, 4]])

    dt['Bolshoi'] = db.sqlite.get_data_sqlite(path, database, query) * 1e9
    print len(dt['Bolshoi'])

    #calculate the mass functions from the Bolshoi data
    mbin0, mf0 = df.diffFunctionLogBinning(dt['Bolshoi'] / h,
                                           nbins=35,
                                           h=0.7,
                                           mmin=10 ** 9.0,
                                           mmax=10 ** 15.0,
                                           volume=50,
                                           nvols=26,
                                           physical_units=True)
    del dt['Bolshoi']

    mbin0 = 10 ** mbin0
    #title
    ax1.set_title('Dark Matter Halo Mass Functions (galpropz.dat)')

    #mark redshift
    for a, b in zip(mbin0[::-1], mf0[::-1]):
        if b > 10 ** -5:
            break
    ax1.annotate('$z \sim %.0f$' % redshift,
            (0.98 * a, 3 * 10 ** -6), size='x-small')

    #Analytical MFs
    xST = dt['Sheth-Tormen'][0]
    yST = dt['Sheth-Tormen'][1] * fudge
    sh = ax1.plot(xST, yST, 'b-', lw=1.3)
    #PS
    xPS = dt['Press-Schecter'][0]
    yPS = dt['Press-Schecter'][1] * fudge
    ps = ax1.plot(xPS, yPS, 'g--', lw=1.1)

    #MF from Bolshoi
    bolshoi = ax1.plot(mbin0, mf0, 'ro:', ms=5)

    #delete data to save memory, dt is not needed any longer
    del dt

    #plot the residuals
    if redshift < 1.5:
        #interploate to right x scale
        mfintST = N.interp(xST, mbin0, mf0)
        mfintPS = N.interp(xPS, mbin0, mf0)
        #yST = N.interp(mbin0, xST, yST)
        #yPS = N.interp(mbin0, xPS, yPS)
        #make the plot
        ax2.annotate('$z \sim %.0f$' % redshift,
                (1.5 * 10 ** 9, 1.05), xycoords='data',
                     size=10)
        ax2.axhline(1.0, color='b')
        ax2.plot(xST, mfintST / yST, 'b-')
        ax2.plot(xPS, mfintPS / yPS, 'g-')
        #ax2.plot(mbin0, mf0 / yST, 'b-')
        #ax2.plot(mbin0, mf0 / yPS, 'g-')

    ax1.set_xscale('log')
    ax2.set_xscale('log')
    ax1.set_yscale('log')

    ax1.set_ylim(10 ** -6, 10 ** -0)
    ax2.set_ylim(0.45, 1.55)
    ax1.set_xlim(10 ** 9, 10 ** 15)
    ax2.set_xlim(10 ** 9, 10 ** 15)

    ax1.set_xticklabels([])

    ax2.set_xlabel(r'$M_{\mathrm{vir}} \quad [M_{\odot}]$')
    ax1.set_ylabel(r'$\mathrm{d}N / \mathrm{d}\log_{10}(M_{\mathrm{vir}}) \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    ax2.set_ylabel(r'$\frac{\mathrm{galpropz.dat}}{\mathrm{Model}}$')

    ax1.legend((bolshoi, sh, ps),
            ('Bolshoi', 'Sheth-Tormen', 'Press-Schecter'),
                                shadow=True, fancybox=True,
                                numpoints=1)


def compareGalpropzToBolshoiTrees(analyticalData,
                                  BolshoiTrees,
                                  redshifts,
                                  h,
                                  outputdir,
                                  nvols=18,
                                  no_phantoms=True,
                                  galid=True):
    #data storage
    data = {}

    #figure definitions
    left, width = 0.1, 0.8
    rect1 = [left, 0.1, width, 0.2]
    rect2 = [left, 0.3, width, 0.65]

    #note that this is only available on tuonela.stsci.edu
    simuPath = '/Users/niemi/Desktop/Research/run/newtree1/'
    simuDB = 'sams.db'

    #star the figure
    fig = P.figure()
    ax1 = fig.add_axes(rect2)  #left, bottom, width, height
    ax2 = fig.add_axes(rect1)

    #set title
    if galid:
        ax1.set_title('Dark Matter Halo Mass Functions (gal\_id = 1; 26 volumes)')
    else:
        ax1.set_title('Dark Matter Halo Mass Functions (galpropz: 26 volumes)')


    #loop over the data and redshift range
    for redsh, BolshoiTree, anaData in zip(sorted(redshifts.itervalues()),
                                           BolshoiTrees,
                                           analyticalData):
        #skip some redshifts
        if redsh < 1.0 or redsh == 2.0276 or redsh == 5.1614\
           or redsh == 6.5586 or redsh == 3.0584:
            continue
            #if redsh == 1.0064 or redsh == 3.0584 or redsh == 4.0429 or \
        #   redsh == 8.2251:
        #    continue

        #change this to logging afterwords
        logging.debug(redsh)
        logging.debug(BolshoiTree)
        logging.debug(anaData)

        rlow = redsh - 0.02
        rhigh = redsh + 0.02

        if galid:
            query = '''select mhalo from galpropz where
                       galpropz.zgal > {0:f} and galpropz.zgal < {1:f} and
                       galpropz.gal_id = 1'''.format(rlow, rhigh)
        else:
            query = '''select mhalo from galpropz where
                       galpropz.zgal > {0:f} and
                       galpropz.zgal < {1:f}'''.format(rlow, rhigh)

        logging.debug(query)

        data['SAM'] = db.sqlite.get_data_sqlite(simuPath, simuDB, query) * 1e9

        #calculate the mass functions from the SAM data, only x volumes
        mbin0SAM, mf0SAM = df.diffFunctionLogBinning(data['SAM'],
                                                     nbins=30,
                                                     h=h,
                                                     mmin=1e9,
                                                     mmax=1e15,
                                                     volume=50.0,
                                                     nvols=nvols,
                                                     physical_units=True)
        mbin0SAM = 10 ** mbin0SAM
        #mf0SAM = mf0SAM * 1.7

        #read the Bolshoi merger trees
        data['Bolshoi'] = io.readBolshoiDMfile(BolshoiTree, 0, no_phantoms)

        #calculate the mass functions from the full Bolshoi data
        mbin0Bolshoi, mf0Bolshoi = df.diffFunctionLogBinning(data['Bolshoi'] / h,
                                                             nbins=30,
                                                             h=h,
                                                             mmin=1e9,
                                                             mmax=1e15,
                                                             volume=50.0,
                                                             nvols=125,
                                                             physical_units=True)
        mbin0Bolshoi = 10 ** mbin0Bolshoi

        #Analytical MFs
        #get Rachel's analytical curves
        #M dN/dM dNcorr/dM dN/dlog10(M) dN/dlog10(Mcorr)
        d = N.loadtxt(anaData)
        data['Press-Schecter'] = N.array([d[:, 0], d[:, 3]])
        data['Sheth-Tormen'] = N.array([d[:, 0], d[:, 4]])
        #ST
        sh = ax1.plot(data['Sheth-Tormen'][0],
                      data['Sheth-Tormen'][1],
                      'k-', lw=0.9)
        #PS
        #ps = ax1.plot(data['Press-Schecter'][0],
        #              data['Press-Schecter'][1],
        #              'g--', lw = 1.1)

        #MF from Bolshoi
        bolshoiax = ax1.plot(mbin0Bolshoi,
                             mf0Bolshoi,
                             'ro--', ms=4)

        #MF from the SAM run
        samax = ax1.plot(mbin0SAM,
                         mf0SAM,
                         'gs--', ms=4)

        #mark redshift
        for a, b in zip(mbin0Bolshoi[::-1], mf0Bolshoi[::-1]):
            if b > 10 ** -5:
                break
        ax1.annotate('$z \sim {0:.2f}$'.format(redsh),
                (0.6 * a, 3 * 10 ** -6), size='x-small')

        #plot the residuals
        if redsh < 1.5:
            #make the plot
            ax2.annotate('$z \sim {0:.2f}$'.format(redsh),
                    (1.5 * 10 ** 9, 1.05), xycoords='data',
                         size=10)
            ax2.axhline(1.0, color='k')
            msk = mf0SAM / mf0Bolshoi > 0
            ax2.plot(mbin0SAM[msk],
                     mf0SAM[msk] / mf0Bolshoi[msk],
                     'r-')

    ax1.set_xscale('log')
    ax2.set_xscale('log')
    ax1.set_yscale('log')

    ax1.set_ylim(1e-6, 10 ** -0)
    ax2.set_ylim(0.45, 1.55)
    ax1.set_xlim(2e9, 4e14)
    ax2.set_xlim(2e9, 4e14)

    ax1.set_xticklabels([])

    ax2.set_xlabel(r'$M_{\mathrm{vir}} \quad [M_{\odot}]$')
    ax1.set_ylabel(r'$\mathrm{d}N / \mathrm{d}\log_{10}(M_{\mathrm{vir}}) \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    ax2.set_ylabel(r'$\frac{\mathrm{galpropz.dat}}{\mathrm{IsoTree}}$')

    ax1.legend((sh, bolshoiax, samax),
            ('Sheth-Tormen', 'Bolshoi', 'galpropz'),
                                     shadow=True, fancybox=True,
                                     numpoints=1)

    if galid:
        P.savefig(outputdir + 'IsotreesVSgalpropzGalID.pdf')
    else:
        P.savefig(outputdir + 'IsotreesVSgalpropz.pdf')


if __name__ == '__main__':
    #Hubble constant
    h = 0.7
    #output directory
    wrkdir = os.getenv('HOME') + '/Dropbox/Research/Bolshoi/dm_halo_mf/'
    outdir = wrkdir + 'plots/'
    #logging
    log_filename = 'plotDarkMatterMassFunction.log'
    logging = lg.setUpLogger(outdir + log_filename)
    #find files
    simus = g.glob(wrkdir + 'simu/*.txt')
    sheth = g.glob(wrkdir + 'analytical/*sheth*_?_??-fit.dat')
    press = g.glob(wrkdir + 'analytical/*press*_?_??-fit.dat')
    warren = g.glob(wrkdir + 'analytical/*warren*_?_??-fit.dat')
    #analytical 2, Rachel's code
    analytical = g.glob(os.getenv('HOME') + '/Dropbox/Research/Bolshoi/var/z*')

    #figure definitions
    left, width = 0.1, 0.8
    rect1 = [left, 0.1, width, 0.2]
    rect2 = [left, 0.3, width, 0.65]


    #    #make the individual plots
    #    fig = P.figure()
    #    ax1 = fig.add_axes(rect2)  #left, bottom, width, height
    #    ax2 = fig.add_axes(rect1)
    #    for a, b, c, d in zip(simus, sheth, press, warren):
    #        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
    #        data = {'Bolshoi' : a,
    #                'Sheth-Tormen': b,
    #                'Press-Schecter': c,
    #                'Warren' : d}
    #
    #        if b.find('_1_01') > -1 or b.find('_6_56') > -1 or b.find('_3_06') > -1 or b.find('_5_16') > -1:
    #            continue
    #        else:
    #            logging.debug('Plotting redshift %.2f dark matter mass functions', redshift)
    #            print a, b, c, d
    #            plot_mass_function(redshift, h, True, data)
    #    P.savefig(outdir + 'DMmfzNoPhantoms1.pdf')
    #    P.close()
    #
    #    #make the individual plots 2
    #    fig = P.figure()
    #    ax1 = fig.add_axes(rect2)
    #    ax2 = fig.add_axes(rect1)
    #    for a, b, c, d in zip(simus, sheth, press, warren):
    #        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
    #        data = {'Bolshoi' : a,
    #                'Sheth-Tormen': b,
    #                'Press-Schecter': c,
    #                'Warren' : d}
    #
    #        if b.find('_1_01') > -1 or b.find('_6_56') > -1 or b.find('_3_06') > -1 or b.find('_5_16') > -1:
    #            continue
    #        else:
    #            logging.debug('Plotting redshift %.2f dark matter mass functions', redshift)
    #            print a, b, c, d
    #            plot_mass_function(redshift, h, False, data)
    #    P.savefig(outdir + 'DMmfz1.pdf')
    #    P.close()
    #
    #    #make the individual plots 3
    #    fig = P.figure()
    #    ax1 = fig.add_axes(rect2)
    #    ax2 = fig.add_axes(rect1)
    #    for a, b, c, d in zip(simus, sheth, press, warren):
    #        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
    #        data = {'Bolshoi' : a,
    #                'Sheth-Tormen': b,
    #                'Press-Schecter': c,
    #                'Warren' : d}
    #
    #        if b.find('_1_01') > -1 or b.find('_6_56') > -1 or b.find('_3_06') > -1 or b.find('_5_16') > -1:
    #            logging.debug('Plotting redshift %.2f dark matter mass functions', redshift)
    #            print a, b, c, d
    #            plot_mass_function(redshift, h, True, data)
    #    P.savefig(outdir + 'DMmfzNoPhantoms2.pdf')
    #    P.close()
    #
    #    #make the individual plots 4
    #    fig = P.figure()
    #    ax1 = fig.add_axes(rect2)
    #    ax2 = fig.add_axes(rect1)
    #    for a, b, c, d in zip(simus, sheth, press, warren):
    #        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
    #        data = {'Bolshoi' : a,
    #                'Sheth-Tormen': b,
    #                'Press-Schecter': c,
    #                'Warren' : d}
    #
    #        if b.find('_1_01') > -1 or b.find('_6_56') > -1 or b.find('_3_06') > -1 or b.find('_5_16') > -1:
    #            logging.debug('Plotting redshift %.2f dark matter mass functions', redshift)
    #            print a, b, c, d
    #            plot_mass_function(redshift, h, False, data)
    #    P.savefig(outdir + 'DMmfz2.pdf')
    #    P.close()
    #
    ##############################
    #    #With Rachel's analytical
    #    #make the individual plots
    #    fig = P.figure()
    #    ax1 = fig.add_axes(rect2)  #left, bottom, width, height
    #    ax2 = fig.add_axes(rect1)
    #    for a, b in zip(simus, analytical):
    #        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
    #        data = {'Bolshoi' : a,
    #                'Analytical': b}
    #
    #        if round(redshift,1) not in [1.0, 2.0, 4.0, 8.2]:
    #            logging.debug('Plotting redshift %.2f dark matter mass functions' % redshift)
    #            print a, b
    #            plot_mass_functionAnalytical2(redshift, h, True, data)
    #    P.savefig(outdir + 'DMmfzNoPhantoms1RAnalytical.pdf')
    #    P.close()
    #
    #    #make the individual plots 2
    #    fig = P.figure()
    #    ax1 = fig.add_axes(rect2)
    #    ax2 = fig.add_axes(rect1)
    #    for a, b in zip(simus, analytical):
    #        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
    #        data = {'Bolshoi' : a,
    #                'Analytical': b}
    #
    #        if round(redshift,1) not in [1.0, 2.0, 4.0, 5.2]:
    #            logging.debug('Plotting redshift %.2f dark matter mass functions' % redshift)
    #            print a, b
    #            plot_mass_functionAnalytical2(redshift, h, False, data)
    #    P.savefig(outdir + 'DMmfz1RAnalytical.pdf')
    #    P.close()
    #
    #    #make the individual plots 3
    #    fig = P.figure()
    #    ax1 = fig.add_axes(rect2)
    #    ax2 = fig.add_axes(rect1)
    #    for a, b in zip(simus, analytical):
    #        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
    #        data = {'Bolshoi' : a,
    #                'Analytical': b}
    #
    #        if round(redshift,1) in [1.0, 4.0, 6.6]:
    #            logging.debug('Plotting redshift %.2f dark matter mass functions', redshift)
    #            print a, b
    #            plot_mass_functionAnalytical2(redshift, h, True, data)
    #    P.savefig(outdir + 'DMmfzNoPhantoms2RAnalytical.pdf')
    #    P.close()
    #
    #    #make the individual plots 4
    #    fig = P.figure()
    #    ax1 = fig.add_axes(rect2)
    #    ax2 = fig.add_axes(rect1)
    #    for a, b in zip(simus, analytical):
    #        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
    #        data = {'Bolshoi' : a,
    #                'Analytical': b}
    #
    #        if round(redshift,1) in [1.0, 4.0, 6.6]:
    #            logging.debug('Plotting redshift %.2f dark matter mass functions' % redshift)
    #            print a, b
    #            plot_mass_functionAnalytical2(redshift, h, False, data)
    #    P.savefig(outdir + 'DMmfz2RAnalytical.pdf')
    #    P.close()
    #
    #################################
    #    #Haloes from galpropz.dat
    #
    #    sheth = g.glob(wrkdir + 'analytical/*sheth*_?_?-fit.dat')
    #    press = g.glob(wrkdir + 'analytical/*press*_?_?-fit.dat')
    #    warren = g.glob(wrkdir + 'analytical/*warren*_?_?-fit.dat')
    #
    #    #make the individual plots 2
    #    fig = P.figure()
    #    ax1 = fig.add_axes(rect2)
    #    ax2 = fig.add_axes(rect1)
    #    for a, c, d in zip(sheth, press, warren):
    #        redshift = float(a.split('tormen_')[1].split('-fit')[0].replace('_', '.'))
    #        data = {'Sheth-Tormen': a,
    #                'Press-Schecter': c,
    #                'Warren' : d}
    #
    #        if a.find('_2_0') > -1 or a.find('_6_0') > -1 or a.find('_3_0') > -1 or a.find('_5_0') > -1 or a.find('_0_0') > -1:
    #            continue
    #        else:
    #            logging.debug('Plotting redshift %.2f dark matter mass functions' % redshift)
    #            print a, c, d
    #            plotDMMFfromGalpropz(redshift, h, data)
    #    P.savefig(outdir + 'DMmfz1GalpropZ.pdf')
    #    P.close()
    #
    #    #a new plot
    #    fig = P.figure()
    #    ax1 = fig.add_axes(rect2)
    #    ax2 = fig.add_axes(rect1)
    #    for a in analytical:
    #        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
    #        data = {'Analytical': a}
    #        if round(redshift,1) in [1.0, 4.0, 8.0]:
    #            logging.debug('Plotting redshift %.2f dark matter mass functions (Analytical 2)' % redshift)
    #            print a
    #            plotDMMFfromGalpropzAnalytical2(redshift, h, data)
    #    P.savefig(outdir + 'DMmfz1GalpropZAnalytical2.pdf')
    #    P.close()
    ########################################
    #Compare dark matter halo mass functions of Rachel's SAM and Bolshoi trees
    redshifts = {0.9943: 0.0057,
                 0.4984: 1.0064,
                 0.2464: 3.0584,
                 0.1983: 4.0429,
                 0.1323: 6.5586,
                 0.1084: 8.2251,
                 0.1623: 5.1614,
                 0.3303: 2.0276}

    compareGalpropzToBolshoiTrees(analytical, simus, redshifts, h, outdir)
    #compareGalpropzToBolshoiTrees(analytical, simus, redshifts, h, outdir, galid=False)