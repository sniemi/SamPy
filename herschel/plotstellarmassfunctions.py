'''
@todo: Normalization is wrong here. One should use something like 1/V_max
where the volume in which a given galaxy could be observed, should be the
co-moving volume.
'''
import matplotlib
matplotlib.rc('text', usetex = False)
matplotlib.rc('xtick', labelsize=12) 
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rc('lines', markeredgewidth=2.0)
matplotlib.rcParams['lines.linewidth'] = 1.8
matplotlib.rcParams['legend.fontsize'] = 9
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
#matplotlib.use('PDF')
#matplotlib.use('Agg')
matplotlib.use('PS')

import numpy as N
import pylab as P
import re, os
import db.sqlite

def diff_function(data, column = 0, log = False,
                  wgth = None, mmax = 15.5, mmin = 9.0,
                  nbins = 35, h = 0.7, volume = 250, nvols = 1,
                  physical_units = False, verbose = False):
    '''
    Calculates a differential function from data.
    '''
    #number of galaxies
    one = False
    if len(N.shape(data)) == 1:
        ngal = len(data)
        one = True
    else:
        ngal = len(data[:,column])
    
    #if data are in physical units or not, use h
    if not physical_units:
        h = 1.0
    
    #if wgth is None then make weights based on the volume etc.
    if wgth == None:
        weight = N.zeros(ngal) + (1./(nvols*(float(volume)/h)**3))
    else:
        weight = wgth

    #if log have been taken from the data or not
    if not log:
        d = N.log10(data[:,column])
        mmin = N.log10(mmin)
        mmax = N.log10(mmax)
    else:
        d = data[:,column]   

    #bins 
    dm = (mmax - mmin) / float(nbins)
    mbin = (N.arange(nbins)+0.5)*dm + mmin

    if verbose:
        print '\nNumber of galaxies = %i' % ngal
        print 'min = %f, max = %f' % (mmin, mmax)
        print 'df =', dm
        print 'h =', h

    #mass function
    mf = N.zeros(nbins)
    nu = N.zeros(nbins)
    
    #find out bins
    ibin = N.floor((d - mmin)/dm)

    #make a mask of suitable bins
    mask = (ibin >= 0) & (ibin < nbins)

    #calculate the sum in each bin
    for i in range(nbins):
        mf[i] = N.sum(weight[ibin[mask] == i])
        nu[i] = len(ibin[ibin[mask] == i])

    if verbose:
        print 'Results:\n', mbin
        print mf / dm
        print nu
    return mbin, mf / dm, nu
 
def plot_stellarmasses(path, database, cut, redshifts,
                       out_folder, obs_data,
                       area = 2.25,
                       ymin = 10**3, ymax = 2*10**6,
                       xmin = 0.5, xmax = 100,
                       nbins = 15, sigma = 3.0,
                       write_out = False):
    '''
    160 (arcminutes squared) = 0.0444444444 square degrees
    Simulation was 10 times the GOODS realization, so
    area = 0.44444444, thus, the weighting is 1/0.44444444
    i.e. 2.25.
    @param sigma: sigma level of the errors to be plotted
    @param nbins: number of bins (for simulated data)
    @param area: actually 1 / area, used to weight galaxies
    '''
    #fudge factor to handle errors that are way large
    fudge = ymin

    #subplot numbers
    columns = 2
    rows = 3 

    #get data
    query = '''select galprop.mstar from galprop, FIR where
    galprop.gal_id = FIR.gal_id and
    galprop.halo_id = FIR.halo_id and %s''' % cut
    masses_limit = db.sqlite.get_data_sqlite(path, database, query)
    query = '''select galprop.mstar from galprop, FIR where
    galprop.gal_id = FIR.gal_id and
    galprop.halo_id = FIR.halo_id'''    
    masses_total = db.sqlite.get_data_sqlite(path, database, query)

    #make the figure
    fig = P.figure(figsize = (10, 10))
    P.subplots_adjust(wspace = 0.0, hspace = 0.0)
    ax = P.subplot(rows, columns, 1)

    #weight each galaxy
    wghts = N.zeros(len(masses_total)) + area
    #calculate the differential stellar mass function
    #with log binning
    b, n, nu =  diff_function(masses_total,
                              wgth = wghts, 
                              mmax = xmax,
                              mmin = xmin,
                              nbins = nbins,
                              log = True)
    #get the knots
    x = 10**b
    y = n
    #plot the knots
    mtot = ax.plot(x, y, 'k-')
    #poisson error
    mask = nu > 0
    err = area * N.sqrt(nu[mask]) * sigma
    up = y[mask] + err
    lw = y[mask] - err
    lw[lw < ymin] = ymin
    stot = ax.fill_between(x[mask], up, lw, color = '#728FCE')   
     
    #limited mass
    wghts = N.zeros(len(masses_limit)) + area
    b, n, nu =  diff_function(masses_limit,
                              wgth = wghts, 
                              mmax = xmax,
                              mmin = xmin,
                              nbins = nbins,
                              log = True)
    #get the knots
    x = 10**b
    y = n
    #plot the knots
    mlim = ax.plot(x, y, 'r-')
    #poisson error
    mask = nu > 0
    err = area * N.sqrt(nu[mask]) * sigma
    up = y[mask] + err
    lw = y[mask] - err
    lw[lw < ymin] = ymin
    slim = ax.fill_between(x[mask], up, lw, color = 'red')
    
    #write to the file if needed, using appending so might get long...
    if write_out:
        fh = open(out_folder + 'outputTotal.txt', 'a')
        fh.write('#Mstellar[log10(M_sun)] dN/dlog10(M_sun) high low\n')
        for aa, bb, cc, dd in zip(x[mask], y[mask], up ,lw):
            fh.write('%e %e %e %e\n' % (aa, bb, cc, dd))
        fh.close()

    #add annotation
    ax.annotate('Total', (0.5, 0.9), xycoords='axes fraction',
               ha = 'center')

    #set scale
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlim(10**xmin, 10**xmax)
    ax.set_ylim(ymin, ymax)
    ax.set_xticklabels([])


    ptot = P.Rectangle((0, 0), 1, 1, fc='#728FCE')
    plim = P.Rectangle((0, 0), 1, 1, fc='red')
    sline = '%i$\sigma$ errors' % sigma
    P.legend((mtot, ptot, plim), 
             ('All Galaxies', sline, '$S_{250} > 5$ mJy'))

    #redshift limited plots
    for i, red in enumerate(redshifts):
        query = '''select galprop.mstar from galprop, FIR where
        galprop.gal_id = FIR.gal_id and galprop.halo_id = FIR.halo_id
        and %s''' % (red)
        mtotal = db.sqlite.get_data_sqlite(path, database, query)
        query = '''select galprop.mstar from galprop, FIR where
        galprop.gal_id = FIR.gal_id and galprop.halo_id = FIR.halo_id
        and %s and %s''' % (cut, red)
        mlimit = db.sqlite.get_data_sqlite(path, database, query)
        
        #modify redshift string
        tmp = red.split()
        rtitle = r'$%s < z \leq %s$' % (tmp[2], tmp[6])

        #make a subplot
        axs = P.subplot(rows, columns, i+2)

        #weights
        wghts = N.zeros(len(mtotal)) + area
        b, n, nu =  diff_function(mtotal,
                                  wgth = wghts, 
                                  mmax = xmax,
                                  mmin = xmin,
                                  nbins = nbins,
                                  log = True)
        x = 10**b
        y = n
        #plot the knots
        axs.plot(x, y, 'k-')
        #poisson error
        mask = nu > 0
        err = area * N.sqrt(nu[mask]) * sigma
        up = y[mask] + err
        lw = y[mask] - err
        lw[lw < ymin] = ymin
        axs.fill_between(x[mask], up, lw, color = '#728FCE')
        
        #limited mass
        wghts = N.zeros(len(mlimit)) + area
        b, n, nu =  diff_function(mlimit,
                                  wgth = wghts, 
                                  mmax = xmax,
                                  mmin = xmin,
                                  nbins = nbins,
                                  log = True)
        x = 10**b
        y = n
        #plot the knots
        axs.plot(x, y, 'r-')
        #poisson error
        mask = nu > 0
        err = area * N.sqrt(nu[mask]) * sigma
        up = y[mask] + err
        lw = y[mask] - err
        lw[lw < ymin] = ymin
        axs.fill_between(x[mask], up, lw, color = 'red')

        #write to output
        if write_out:
            fh = open(out_folder + 'outputredshiftbin%i.txt' % i, 'a')
            fh.write('#' + rtitle+'\n')
            fh.write('#Mstellar[log10(M_sun)] dN/dlog10(M_sun) high low\n')
            for aa, bb, cc, dd in zip(x[mask], y[mask], up, lw):
                fh.write('%e %e %e %e\n' % (aa, bb, cc, dd))
            fh.close()

        #add annotation
        axs.annotate(rtitle, (0.5, 0.9), xycoords='axes fraction',
                     ha = 'center')

        #set scales
        axs.set_xscale('log')
        axs.set_yscale('log')
        axs.set_xlim(10**xmin, 10**xmax)
        axs.set_ylim(ymin, ymax)

        #remove unnecessary ticks and add units
        if i % 2 == 0:
            axs.set_yticklabels([])
        if i == 2 or i == 3:
            axs.set_xlabel(r'$M_{\star} \quad [M_{\odot}]$')
            if i == 2:
                axs.set_xticks(axs.get_xticks()[1:])
        else:
            axs.set_xticklabels([])
        if i == 1:
            axs.set_ylabel(r'$\frac{dN}{d\log_{10}M_{\star}} \quad []$')
            
    #save figure
    P.savefig(out_folder+'stellarmassfunction.ps')
    P.close()

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero/'
    database = 'sams.db'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/stellar_mass_functions/'
    obs_data = hm+'/Dropbox/Research/Herschel/obs_data/'

    #5sigma limits derived by Kuang
    depths = {'pacs100_obs': 1.7,
              'pacs160_obs': 4.5,
              'spire250_obs': 5.0,
              'spire350_obs': 9.0,
              'spire500_obs': 10.0
              }

    #luminosity cut
    cut = 'FIR.spire250_obs > 5.0e-3 and FIR.spire250_obs < 10e6'
    cut = 'FIR.spire250 > 9'


    redshifts = ['FIR.z >= 0.0 and FIR.z <= 0.5',
                 'FIR.z > 0.5 and FIR.z <= 1.0',
                 'FIR.z > 1.0 and FIR.z <= 2.0',
                 'FIR.z > 2.0 and FIR.z <= 5.0']
    
    plot_stellarmasses(path, database, cut, redshifts,
                       out_folder, obs_data,
                       xmin = 8, xmax = 12,
                       ymin = 1, ymax = 10**7,
                       nbins = 20, sigma = 5.0)#,
                       #write_out = True)


    print 'All done...'