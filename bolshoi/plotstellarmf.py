import matplotlib
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 15
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.2)
matplotlib.rcParams['legend.fontsize'] = 7
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
matplotlib.use('PDF')
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, NullFormatter, LogLocator
import numpy as N
import pylab as P
import os, logging
#Sami's Repo
import db.sqlite
import astronomy.stellarMFs as SMF
import plot.tools as pt

def stellarmassfunc_plot(path, database, redshifts,
                         output_folder, outfile,
                         mmax = 12.5, mmin = 5.0, 
                         nbins = 40, nvolumes = 8,
                         h = 0.7, lowlim = -4.5):
    '''
    Plots stellar mass functions as a function of redshift.
    Compares to observations.
    '''
    cols = pt.give_colours()

    weight = 1./(nvolumes*(50.0/0.7)**3)
    multiply = 10**9

    #make the figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    #obs constrains
    obs, ids = SMF.stellarMfs()
    o = []
    o.append(['$z \sim 1$: Perez-Gonzalez et al. 2007', (obs.id == 1) & (obs.z_low > 0.99) & (obs.z_up < 1.4)])
#    o.append(['$z \sim 1$: Drory et al. 2004', (obs.id == 5) & (obs.z_low > 1.) & (obs.z_up < 1.2)])
    o.append(['$z \sim 2$: Perez-Gonzalez et al. 2007', (obs.id == 1) & (obs.z_low > 1.99) & (obs.z_up < 2.6)])
#    o.append(['$z \sim 2$: Fontana et al. 2006', (obs.id == 6) & (obs.z_low > 1.99) & (obs.z_up < 3.01)])
#    o.append(['$z \sim 2$: Marchesini et al. 2008', (obs.id == 7) & (obs.z_low > 1.99) & (obs.z_up < 3.01)])
    o.append(['$z \sim 3$: Perez-Gonzalez et al. 2007', (obs.id == 1) & (obs.z_low > 2.99) & (obs.z_up < 3.6)])
    o.append(['$z \sim 4$: Perez-Gonzalez et al. 2007', (obs.id == 1) & (obs.z_low > 3.49) & (obs.z_up < 4.1)])

    #obs plots
    for i, line in enumerate(o):
        label, mask = line[0], line[1]
        ms = obs.mstar[mask]
        mf = obs.mf[mask]
        errl = obs.err_low[mask]
        errh = obs.err_up[mask]
        msk = mf >= lowlim
        ax.errorbar(ms[msk],
                    mf[msk],
                    yerr = [errh[msk], errl[msk]],
                    color = cols[i],
                    ls = ':',
                    label = label)

    #plot the different redshifts
    for ii, redshift in enumerate(redshifts):
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

        ax.plot(mbin, mf_star, color = cols[ii],
                label = '$z \sim %i$: Bolshoi + SAM' % rd)

    ax.set_xlim(8.0, 12.1)
    ax.set_ylim(lowlim, -1.0)
    ax.set_xlabel(r'$\log_{10} M_{\star} \quad [M_{\odot}]$')
    ax.set_ylabel(r'$\log_{10} \left ( \frac{\mathrm{d}N}{\mathrm{d}\log_{10} M_{\star}} \right ) \quad [\mathrm{Mpc}^{-3}\ \mathrm{dex}^{-1}]$')
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
    P.savefig(output_folder+ outfile + '.pdf')
    P.close()

def main(redshifts, path, database, output_folder, outfile):
    '''
    Driver function, call this with a path to the data,
    and label you wish to use for the files.
    '''
    stellarmassfunc_plot(path, database, redshifts,
                         output_folder, outfile)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    path = '/Users/niemi/Desktop/Research/run/trial1/'
    database = 'sams.db'
    outpath = hm + '/Dropbox/Research/Bolshoi/stellarMFs/'

    logging.debug('Making the first plot')
    redshifts = ['galpropz.zgal > 0.9 and galpropz.zgal <= 1.1',
                 'galpropz.zgal > 1.9 and galpropz.zgal <= 2.1',
                 'galpropz.zgal > 2.9 and galpropz.zgal <= 3.1',
                 'galpropz.zgal > 3.9 and galpropz.zgal <= 4.1',
                 'galpropz.zgal > 4.9 and galpropz.zgal <= 5.1',
                 'galpropz.zgal > 5.9 and galpropz.zgal <= 6.1',
                 'galpropz.zgal > 6.9 and galpropz.zgal <= 7.1']
    
    main(redshifts, path, database, outpath, 'stellarmf')

    logging.debug('Making the second plot')
    redshifts = ['galpropz.zgal >= 0.9 and galpropz.zgal <= 1.3',
                 'galpropz.zgal >= 1.9 and galpropz.zgal <= 2.5',
                 'galpropz.zgal >= 2.9 and galpropz.zgal <= 3.5',
                 'galpropz.zgal >= 3.5 and galpropz.zgal <= 4.1']

    main(redshifts, path, database, outpath, 'stellarmf2')
