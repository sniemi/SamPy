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
#From Sami's Repo
import db.sqlite
import astronomy.stellarMFs as SMF
import astronomy.differentialfunctions as df
import plot.tools as pt

def stellarmassfunc_plot(path, database, redshifts,
                         output_folder, outfile,
                         mmax = 12.5, mmin = 8.0, 
                         nbins = 30, nvolumes = 26,
                         single_volume = 50.0,
                         h = 0.7, lowlim = -4.9):
    '''
    Plots stellar mass functions as a function of redshift.
    Compares to observations.
    '''
    #get a colour scheme
    cols = pt.give_colours()

    #scale the SAM's output masses
    multiply = 1e9

    #make the figure and axes instance
    fig = P.figure()
    ax = fig.add_subplot(111)

    #get obs constrains
    obs, ids = SMF.stellarMfs()
    o = []
    o.append(['$z \sim 1$: Perez-Gonzalez et al. 2007', (obs.id == 1) & (obs.z_low > 0.99) & (obs.z_up < 1.4)])
    #o.append(['$z \sim 1$: Drory et al. 2004', (obs.id == 5) & (obs.z_low > 1.) & (obs.z_up < 1.2)])
    o.append(['$z \sim 2$: Perez-Gonzalez et al. 2007', (obs.id == 1) & (obs.z_low > 1.99) & (obs.z_up < 2.6)])
    #o.append(['$z \sim 2$: Fontana et al. 2006', (obs.id == 6) & (obs.z_low > 1.99) & (obs.z_up < 3.01)])
    #o.append(['$z \sim 2$: Marchesini et al. 2008', (obs.id == 7) & (obs.z_low > 1.99) & (obs.z_up < 3.01)])
    o.append(['$z \sim 3$: Perez-Gonzalez et al. 2007', (obs.id == 1) & (obs.z_low > 2.99) & (obs.z_up < 3.6)])
    o.append(['$z \sim 4$: Perez-Gonzalez et al. 2007', (obs.id == 1) & (obs.z_low > 3.49) & (obs.z_up < 4.1)])

    highred = SMF.highRedshiftMFs()

    #make the observational plots
    for i, line in enumerate(o):
        label, mask = line[0], line[1]
        ms = obs.mstar[mask]
        mf = obs.mf[mask]
        errl = obs.err_low[mask]
        errh = obs.err_up[mask]
        msk = mf > - 15.0
        ax.errorbar(ms[msk],
                    mf[msk],
                    yerr = [errh[msk], errl[msk]],
                    color = cols[i],
                    ls = ':',
                    label = label)

    for i, key in enumerate(sorted(highred.iterkeys())):
        if key !=  'stellar_mass':
            ax.plot(highred['stellar_mass'],
                    highred[key],
                    color = cols[i+2],
                    ls = ':',
                    marker = 's',
                    label = '$%s:$ Gonzalez et al. 2011' % key.replace('=', '\sim'))
    

    #plot the different redshifts
    for ii, redshift in enumerate(redshifts):
        #get redshift, add 0.1 so that int/floor returns the closest int
        tmp = redshift.split()
        rd = int(float(tmp[2]) + 0.1)
        
        #generate the SQL query
        query = '''select mstar_disk, mbulge, gal_id from galpropz where ''' + redshift
        query += ' and mstar_disk >= 0.0 and mbulge >= 0.0'
        query += ' and mstar_disk + mbulge > 0.0'
       
        #get data from the SQLite3 db
        dat = db.sqlite.get_data_sqlite(path, database, query)
        #rename data for convenience
        disk = dat[:,0] 
        bulge = dat[:,1]
        mstar = N.log10((disk * multiply) + (bulge * multiply))
        #make a dictionary of data
        data = {}
        data['stellar_mass'] = mstar
        data['bulge_mass'] = bulge
        data['galaxy_id'] = dat[:,2]
        
        #debug output
        ngal = len(mstar)
        logging.debug('%i galaxies found at z = %i' % (ngal, rd))
        
        #calculate the stellar mass functions
        mfs = df.stellarMassFunction(data,
                                     mmin = mmin-0.2,
                                     #mmax = mmax,
                                     nvols = nvolumes,
                                     nbins = nbins-2*rd,
                                     verbose = True)
        
        #plot the simulation data
        ax.plot(mfs['mass_bins'],
                mfs['mf_stellar_mass'],
                color = cols[ii],
                label = '$z \sim %i$: Bolshoi + SAM' % rd)
#        ax.plot(mfs['mass_bins'],
#                mfs['mf_central_galaxies'],
#                color = cols[ii],
#                ls = '--',
#                label = '$z \sim %i$: Bolshoi + SAM (CG)' % rd)
        
    #set axes scales and labels
    ax.set_xlim(mmin, 12.0)
    ax.set_ylim(lowlim, -1.0)
    ax.set_xlabel(r'$\log_{10} \left ( M_{\star} \ [\mathrm{M}_{\odot}] \right )$')
    ax.set_ylabel(r'$\log_{10} \left ( \frac{\mathrm{d}N}{\mathrm{d}\log_{10} M_{\star}} \right ) \quad [\mathrm{Mpc}^{-3}\ \mathrm{dex}^{-1}] $')
    #set small ticks
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

    P.legend(shadow = True, fancybox = True, numpoints = 1)
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
    path = hm + '/Dropbox/Research/Bolshoi/run/trial2/'
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

#    logging.debug('Making the second plot')
#    redshifts = ['galpropz.zgal >= 0.9 and galpropz.zgal <= 1.3',
#                 'galpropz.zgal >= 1.9 and galpropz.zgal <= 2.5',
#                 'galpropz.zgal >= 2.9 and galpropz.zgal <= 3.5',
#                 'galpropz.zgal >= 3.5 and galpropz.zgal <= 4.1']
#    main(redshifts, path, database, outpath, 'stellarmf2')
