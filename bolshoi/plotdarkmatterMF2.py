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
import astronomy.differentialfunctions as df
import smnIO.read as io
import log.Logger as lg

def plotMassFunction(simus, outdir, noPhantoms=True):
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

        BoshoiData = io.readBolshoiDMfile(file, 0, noPhantoms)

        #calculate the mass functions from the Bolshoi data
        mbin0, mf0 = df.diffFunctionLogBinning(BoshoiData / h,
                                               nbins=35,
                                               h=0.7,
                                               mmin=10**9.0,
                                               mmax=10**15.0,
                                               physical_units=True)

        #use chain rule to get dN / dM
        #dN/dM = dN/dlog10(M) * dlog10(M)/dM
        #d/dM (log10(M)) = 1 / (M*ln(10))
        mf0 *= 1. / (mbin0 * N.log(10))
        #put mass back to power
        mbin0 = 10 ** mbin0


        #start a figure
        fig = P.figure()
        ax1 = fig.add_axes(rect2)  #left, bottom, width, height
        ax2 = fig.add_axes(rect1)

        #title
        if noPhantoms:
            ax1.set_title('$z \sim %.2f$ (no phantoms)' % redshift)
        else:
            ax1.set_title('$z \sim %.2f$' % redshift)


#        #Analytical MFs
#        #0th column: log10 of mass (Msolar, NOT Msolar/h)
#        #1st column: mass (Msolar/h)
#        #2nd column: (dn/dM)*dM, per Mpc^3 (NOT h^3/Mpc^3)
#        xST = 10 ** dt['Sheth-Tormen'][:, 0]
#        yST = dt['Sheth-Tormen'][:, 2] * fudge
#        sh = ax1.plot(xST, yST, 'b-', lw=1.3)
#        #PS
#        xPS = 10 ** dt['Press-Schecter'][:, 0]
#        yPS = dt['Press-Schecter'][:, 2] * fudge
#        ps = ax1.plot(xPS, yPS, 'g--', lw=1.1)

        #MF from Bolshoi
        bolshoi = ax1.plot(mbin0, mf0, 'ro:', ms=5)

#        #plot the residuals
#        if round(float(redshift), 1) < 1.5:
#            #interploate to right x scale
#            yST = N.interp(mbin0, xST, yST)
#            yPS = N.interp(mbin0, xPS, yPS)
#            #make the plot
#            ax2.annotate('$z \sim %.1f$' % redshift,
#                    (1.5 * 10 ** 9, 1.05), xycoords='data',
#                         size=10)
#            ax2.axhline(1.0, color='b')
#            ax2.plot(mbin0, mf0 / yST, 'b-')
#            ax2.plot(mbin0, mf0 / yPS, 'g-')

        ax1.set_ylim(10 ** -7, 10 ** -1)
        ax2.set_ylim(0.45, 1.55)
        ax1.set_xlim(10 ** 9, 10 ** 15)
        ax2.set_xlim(10 ** 9, 10 ** 15)

        ax1.set_xscale('log')
        ax2.set_xscale('log')
        ax1.set_yscale('log')

        ax1.set_xticklabels([])

        ax2.set_xlabel(r'$M_{\mathrm{vir}} \quad [M_{\odot}]$')
        ax1.set_ylabel(r'$\mathrm{d}N / \mathrm{d}M_{\mathrm{vir}} \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
        ax2.set_ylabel(r'$\frac{\mathrm{Bolshoi}}{\mathrm{Model}}$')

        #        ax1.legend((bolshoi, sh, ps),
        #                ('Bolshoi', 'Sheth-Tormen', 'Press-Schecter'),
        #                                    shadow=True, fancybox=True,
        #                                    numpoints=1)

        P.savefig(outdir + 'DMMF{0:d}.png'.format(i))
        P.close()


if __name__ == '__main__':
    #Hubble constant
    h = 0.7

    #output directory
    wrkdir = os.getenv('HOME') + '/Dropbox/Research/Bolshoi/dm_halo_mf/'
    outdir = wrkdir + 'newplots/'

    #logging
    log_filename = 'plotDarkMatterMassFunction.log'
    logging = lg.setUpLogger(outdir + log_filename)

    #find files
    simus = g.glob(os.getenv('HOME') + '/Desktop/Research/dmHaloes/dmMFz*.txt')

    plotMassFunction(simus, outdir)
