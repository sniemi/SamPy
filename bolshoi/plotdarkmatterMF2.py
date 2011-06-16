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
matplotlib.use('AGG')
import pylab as P
import numpy as N
import glob as g
import os
#From Sami's repo
import db.sqlite
import astronomy.differentialfunctions as df
import smnIO.read as io
import log.Logger as lg

def plotMassFunction(simus, sheth, outdir, h, simuPath, simuDB,
                     noPhantoms=True):
    '''
    This function plots dark matter halo mass functions from
    file(s) given in simus. The usual usage is that simus
    contain a list of file names. These files should contain
    dark matter halo masses derived from the Bolshoi isotree
    files.

    This function uses a fudge factor = 2.0 because
    Jenkins et al. paper
    (http://adsabs.harvard.edu/abs/2001MNRAS.321..372J)
    has sqrt(2./pi) while
    Rachel's code has 1/(sqrt(2*pi))
    The ratio of these two definitions is the fudge factor.    
    '''

    #fudge factor
    fudge = 2.0

    #figure definitions
    left, width = 0.1, 0.8
    rect1 = [left, 0.1, width, 0.2]
    rect2 = [left, 0.3, width, 0.65]

    for i, file in enumerate(simus):
        #get the redshift
        redshift = float(file.split('z')[1][:5])
        logging.debug('Plotting redshift %.2f dark matter mass functions', redshift)
        #different redshift ranges
        if redshift < 1.8:
            rlow = redshift - 0.02
            rhigh = redshift + 0.02
        else:
            rlow = redshift - 0.1
            rhigh = redshift + 0.1

        #read bolshoi data
        BoshoiData = io.readBolshoiDMfile(file, 0, noPhantoms)

        #calculate the mass functions from the Bolshoi data
        mbin0, mf0 = df.diffFunctionLogBinning(BoshoiData/h,
                                               nbins=35,
                                               h=h,
                                               mmin=1e9,
                                               mmax=1e15,
                                               volume=50.0,
                                               nvols=18)

        #use chain rule to get dN / dM
        #dN/dM = dN/dlog10(M) * dlog10(M)/dM
        #d/dM (log10(M)) = 1 / (M*ln(10))
        mf0 *= 1. / (mbin0 * N.log(10))
        #put mass back to power
        mbin0 = 10**mbin0

        #get the SAMs data
        #if round(redshift, 2) < 0.08:
        if i < 1:
            query = '''select mhalo from galprop where galprop.gal_id = 1'''
            GalpropData = 10**db.sqlite.get_data_sqlite(simuPath, simuDB, query)
        else:
            query = '''select mhalo from galpropz where 
                       galpropz.zgal > {0:f} and galpropz.zgal < {1:f} and
                       galpropz.gal_id = 1'''.format(rlow, rhigh)
            GalpropData = db.sqlite.get_data_sqlite(simuPath, simuDB, query) * 1e9
        logging.debug(query)


        #calculate the mass functions from the SAM data, only x volumes
        mbin0SAM, mf0SAM = df.diffFunctionLogBinning(GalpropData,
                                                     nbins=35,
                                                     h=h,
                                                     mmin=1e9,
                                                     mmax=1e15,
                                                     volume=50.0,
                                                     nvols=15)
        #use chain rule to get dN / dM
        #dN/dM = dN/dlog10(M) * dlog10(M)/dM
        #d/dM (log10(M)) = 1 / (M*ln(10))
        mf0SAM *= 1. / (mbin0SAM * N.log(10))
        mbin0SAM = 10**mbin0SAM

        #start a figure
        fig = P.figure(figsize=(10,10))
        ax1 = fig.add_axes(rect2)  #left, bottom, width, height
        ax2 = fig.add_axes(rect1)

        #title
        if noPhantoms:
            ax1.set_title('$z \sim %.2f$ (no phantoms)' % redshift)
        else:
            ax1.set_title('$z \sim %.2f$' % redshift)

        #Analytical MFs
        #0th column: log10 of mass (Msolar, NOT Msolar/h)
        #1st column: mass (Msolar/h)
        #2nd column: (dn/dM)*dM, per Mpc^3 (NOT h^3/Mpc^3)
        logging.debug(sheth[i])
        dt = N.loadtxt(sheth[i])
        xST = 10**dt[:, 0]
        yST = dt[:, 2] * fudge
        sh = ax1.plot(xST, yST, 'b-', lw=1.3)

        #MF from Bolshoi
        bolshoi = ax1.plot(mbin0, mf0, 'ro:', ms=5)

        #MF from the SAM run
        samax = ax1.plot(mbin0SAM, mf0SAM, 'gs--', ms=4)

        #plot the residuals
        ax2.axhline(1.0, color='k')
        ax2.plot(mbin0, mf0 / mf0SAM, 'm-')
        #interploate to right x scale
        mfintST1 = N.interp(xST, mbin0, mf0)
        mfintST2 = N.interp(xST, mbin0SAM, mf0SAM)
        ax2.plot(xST, mfintST1 / yST, 'r-')
        ax2.plot(xST, mfintST2 / yST, 'g-')

        ax1.set_ylim(1e-7, 1e-1)
        ax2.set_ylim(0.45, 1.55)
        ax1.set_xlim(1e9, 1e15)
        ax2.set_xlim(1e9, 1e15)

        ax1.set_xscale('log')
        ax2.set_xscale('log')
        ax1.set_yscale('log')

        ax1.set_xticklabels([])

        ax2.set_xlabel(r'$M_{\mathrm{vir}} \quad [M_{\odot}]$')
        ax1.set_ylabel(r'$\mathrm{d}N / \mathrm{d}M_{\mathrm{vir}} \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
        ax2.set_ylabel(r'$\frac{\mathrm{Bolshoi}}{\mathrm{Model}}$')

        ax1.legend((bolshoi, samax, sh),
                   ('Bolshoi', 'galpropz', 'Sheth-Tormen'),
                   shadow=True, fancybox=True, numpoints=1)

        P.savefig(outdir + 'DMMF{0:d}.png'.format(i))
        P.close()


if __name__ == '__main__':
    #Hubble constant
    h = 0.7

    #note that this is only available on tuonela.stsci.edu
    simuPath = '/Users/niemi/Desktop/Research/run/newtree1/'
    simuDB = 'sams.db'

    #output directory
    wrkdir = os.getenv('HOME') + '/Dropbox/Research/Bolshoi/dm_halo_mf/'
    outdir = wrkdir + 'newplots/'

    #logging
    log_filename = 'plotDarkMatterMassFunction.log'
    logging = lg.setUpLogger(outdir + log_filename)

    #find files
    sheth = g.glob(wrkdir + 'analytical/*sheth*tormen*-fit.dat')
    simus = g.glob(os.getenv('HOME') + '/Desktop/Research/dmHaloes/dmMFz*.txt')

    plotMassFunction(simus, sheth, outdir, h, simuPath, simuDB)
