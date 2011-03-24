'''
Plots a dark matter halo mass function at different
redshifts. Input data are from the Bolshoi simulation.
@author: Sami-Matias Niemi
'''
import matplotlib
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 15
matplotlib.rc('xtick', labelsize = 14) 
matplotlib.rc('axes', linewidth = 1.2)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
matplotlib.use('PDF')
import pylab as P
import numpy as N
import glob as g
import logging, os
#From Sami's repo
import astronomy.differentialfunctions as df
import io.read as io
import db.sqlite

def plot_mass_function(redshift, h, no_phantoms, *data):
    #Hubble constants
    h3 = h**3
    #read data
    dt = {}
    for x in data[0]:
        if 'Bolshoi' in x:
            dt[x] = io.readBolshoiDMfile(data[0][x], 0, no_phantoms)
        else:
            dt[x] = N.loadtxt(data[0][x])

    #calculate the mass functions from the Bolshoi data
    mbin0, mf0, nu0 = df.diff_function_log_binning(dt['Bolshoi'],
                                                   nbins = 40,
                                                   h = 1., 
                                                   mmin = 10**9.2,
                                                   mmax = 10**15.0)
    del dt['Bolshoi']
#    mf0 *= 1. / (mbin0 * N.log(10))   
    mf0 *= (mbin0[1] - mbin0[0]) / (N.log(10)*10**(mbin0[1] - mbin0[0]))   
#    mf0 *= mbin0 / (N.log(10)*10**(mbin0[1] - mbin0[0]))   
    print (mbin0[1] - mbin0[0]) /(N.log(10)*10**(mbin0[1] - mbin0[0]))

    mbin0 = 10**mbin0
    #title
    if no_phantoms:
        ax1.set_title('Bolshoi Dark Matter Mass Functions (no phantoms)')
    else:
        ax1.set_title('Bolshoi Dark Matter Mass Functions')

    #mark redshift
    for a, b in zip(mbin0[::-1], mf0[::-1]):
        if b > 10**-6:
            break
    ax1.annotate('$z \sim %.1f$' % redshift,
                (0.98*a, 3*10**-6), size = 'x-small')

    #Analytical MFs
    #1st column: mass (Msolar/h)
    #2nd column: (dn/dM)*dM, per Mpc^3 (NOT h^3/Mpc^3)
    xST = dt['Sheth-Tormen'][:,1] / h
    yST = dt['Sheth-Tormen'][:,2] / h3 / h / h
    sh = ax1.plot(xST, yST, 'b-', lw = 1.3)
    #PS
    xPS = dt['Press-Schecter'][:,1] / h 
    yPS = dt['Press-Schecter'][:,2] / h3 / h / h
    ps = ax1.plot(xPS, yPS, 'g--', lw = 1.1)

    #MF from Bolshoi
    bolshoi = ax1.plot(mbin0, mf0, 'ro:', ms = 5) 

    #delete data to save memory, dt is not needed any longer
    del dt

    #plot the residuals
    if round(float(redshift), 1) < 1.5:
        #interploate to right x scale
        yST = N.interp(mbin0, xST, yST)
        yPS = N.interp(mbin0, xPS, yPS)
        #make the plot
        ax2.annotate('$z \sim %.1f$' % redshift,
                     (1.5*10**9, 1.05), xycoords='data',
                     size = 10)
        ax2.axhline(1.0, color = 'b')
        ax2.plot(mbin0, mf0 / yST, 'b-')
        ax2.plot(mbin0, mf0 / yPS, 'g-')

    ax1.set_xscale('log')
    ax2.set_xscale('log')
    ax1.set_yscale('log')

    ax1.set_ylim(10**-7, 10**-1)
    ax2.set_ylim(0.45, 1.55)
    ax1.set_xlim(10**9, 10**15)
    ax2.set_xlim(10**9, 10**15)
    
    ax1.set_xticklabels([])

    ax2.set_xlabel(r'$M_{\mathrm{vir}} \quad [h^{-1}M_{\odot}]$')
    ax1.set_ylabel(r'$\mathrm{d}N / \mathrm{d}M_{\mathrm{vir}} \quad [h^{3}\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    ax2.set_ylabel(r'$\frac{\mathrm{Bolshoi}}{\mathrm{Model}}$')

    ax1.legend((bolshoi, sh, ps),
               ('Bolshoi', 'Sheth-Tormen', 'Press-Schecter'),
               shadow = True, fancybox = True,
               numpoints = 1)
    
def plotDMMFfromGalpropz(redshift, h, *data):
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    path = hm + '/Desktop/Research/run/trial1/'
    database = 'sams.db'
    
    rlow = redshift - 0.4
    rhigh = redshift + 0.1
    
    query = '''select mhalo from galpropz where
               galpropz.zgal > %f and galpropz.zgal <= %f and
               galpropz.gal_id = 1
    ''' % (rlow, rhigh)
    
    print query
    
    #Hubble constants
    h3 = h**3
    #read data
    dt = {}
    for x in data[0]:
        if 'Bolshoi' in x:
            dt[x] = db.sqlite.get_data_sqlite(path, database, query)*1e9
        else:
            dt[x] = N.loadtxt(data[0][x])

    #calculate the mass functions from the Bolshoi data
    mbin0, mf0, nu0 = df.diff_function_log_binning(dt['Bolshoi'],
                                                   nbins = 30,
                                                   h = 0.7, 
                                                   mmin = 10**9.2,
                                                   mmax = 10**15.0,
                                                   volume = 50,
                                                   nvols = 8,
                                                   physical_units = True)
    del dt['Bolshoi']
    #use chain rule to get dN / dM
    #dN/dM = dN/dlog10(M) * dlog10(M)/dM
    #d/dM (log10(M)) = 1 / (M*ln(10)) 
    #mf0 *= 1. / (mbin0 * N.log(10))
    mf0 *= 1. / (mbin0 * N.log(10))   
    mbin0 = 10**mbin0
    #title
    ax1.set_title('Dark Matter Halo Mass Functions (galpropz.dat)')

    #mark redshift
    for a, b in zip(mbin0[::-1], mf0[::-1]):
        if b > 10**-6:
            break
    ax1.annotate('$z \sim %.1f$' % redshift,
                (0.98*a, 3*10**-6), size = 'x-small')

    #Analytical MFs
    #0th column: log10 of mass (Msolar, NOT Msolar/h)
    #1st column: mass (Msolar/h)
    #2nd column: (dn/dM)*dM, per Mpc^3 (NOT h^3/Mpc^3)
    xST = 10**dt['Sheth-Tormen'][:,0]
    yST = dt['Sheth-Tormen'][:,2] * h
    sh = ax1.plot(xST, yST, 'b-', lw = 1.3)
    #PS
    xPS = 10**dt['Press-Schecter'][:,0]
    yPS = dt['Press-Schecter'][:,2] * h
    ps = ax1.plot(xPS, yPS, 'g--', lw = 1.1)

    #MF from Bolshoi
    bolshoi = ax1.plot(mbin0, mf0, 'ro:', ms = 5) 

    #delete data to save memory, dt is not needed any longer
    del dt

    #plot the residuals
    if round(float(redshift), 1) < 1.5:
        #interploate to right x scale
        yST = N.interp(mbin0, xST, yST)
        yPS = N.interp(mbin0, xPS, yPS)
        #make the plot
        ax2.annotate('$z \sim %.1f$' % redshift,
                     (1.5*10**9, 1.05), xycoords='data',
                     size = 10)
        ax2.axhline(1.0, color = 'b')
        ax2.plot(mbin0, mf0 / yST, 'b-')
        ax2.plot(mbin0, mf0 / yPS, 'g-')

    ax1.set_xscale('log')
    ax2.set_xscale('log')
    ax1.set_yscale('log')

    ax1.set_ylim(5*10**-8, 10**-1)
    ax2.set_ylim(0.45, 1.55)
    ax1.set_xlim(10**9, 10**15)
    ax2.set_xlim(10**9, 10**15)
    
    ax1.set_xticklabels([])

    ax2.set_xlabel(r'$M_{\mathrm{vir}} \quad [M_{\odot}]$')
    ax1.set_ylabel(r'$\mathrm{d}N / \mathrm{d}M_{\mathrm{vir}} \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    ax2.set_ylabel(r'$\frac{\mathrm{galpropz.dat}}{\mathrm{Model}}$')

    ax1.legend((bolshoi, sh, ps),
               ('Bolshoi', 'Sheth-Tormen', 'Press-Schecter'),
               shadow = True, fancybox = True,
               numpoints = 1)

def plotDMMFfromGalpropzAnalytical2(redshift, h, *data):
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    path = hm + '/Desktop/Research/run/trial1/'
    database = 'sams.db'
    
    rlow = redshift - 0.6
    rhigh = redshift + 0.1
    
    query = '''select mhalo from galpropz where
               galpropz.zgal > %f and galpropz.zgal <= %f and
               galpropz.gal_id = 1
    ''' % (rlow, rhigh)
    
    #Hubble constants
    h3 = h**3
    #read data
    dt = {}
    for x in data[0]:
        if 'Bolshoi' in x:
            dt[x] = db.sqlite.get_data_sqlite(path, database, query)*1e9
            print len(dt[x])
        else:
            #M dN/dM dNcorr/dM dN/dlog10(M) dN/dlog10(Mcorr)
            d = N.loadtxt(data[0][x])
            dt['Press-Schecter'] = N.array([d[:,0], d[:,3]])
            dt['Sheth-Tormen'] = N.array([d[:,0], d[:,4]])

    #calculate the mass functions from the Bolshoi data
    mbin0, mf0, nu0 = df.diff_function_log_binning(dt['Bolshoi'],
                                                   nbins = 30,
                                                   h = 0.7, 
                                                   mmin = 10**9.2,
                                                   mmax = 10**15.0,
                                                   volume = 50,
                                                   nvols = 8,
                                                   physical_units = True)
    del dt['Bolshoi']
    #use chain rule to get dN / dM
    #dN/dM = dN/dlog10(M) * dlog10(M)/dM
    #d/dM (log10(M)) = 1 / (M*ln(10)) 
    #mf0 *= 1. / (mbin0 * N.log(10))   
    mbin0 = 10**mbin0
    #title
    ax1.set_title('Dark Matter Halo Mass Functions (galpropz.dat)')

    #mark redshift
    for a, b in zip(mbin0[::-1], mf0[::-1]):
        if b > 10**-6:
            break
    ax1.annotate('$z \sim %.1f$' % redshift,
                (0.98*a, 3*10**-6), size = 'x-small')

    #Analytical MFs
    xST = dt['Sheth-Tormen'][0]
    yST = dt['Sheth-Tormen'][1]
    sh = ax1.plot(xST, yST, 'b-', lw = 1.3)
    #PS
    xPS = dt['Press-Schecter'][0]
    yPS = dt['Press-Schecter'][1]
    ps = ax1.plot(xPS, yPS, 'g--', lw = 1.1)

    #MF from Bolshoi
    bolshoi = ax1.plot(mbin0, mf0, 'ro:', ms = 5) 

    #delete data to save memory, dt is not needed any longer
    del dt

    #plot the residuals
    if round(float(redshift), 1) < 1.5:
        #interploate to right x scale
        yST = N.interp(mbin0, xST, yST)
        yPS = N.interp(mbin0, xPS, yPS)
        #make the plot
        ax2.annotate('$z \sim %.1f$' % redshift,
                     (1.5*10**9, 1.05), xycoords='data',
                     size = 10)
        ax2.axhline(1.0, color = 'b')
        ax2.plot(mbin0, mf0 / yST, 'b-')
        ax2.plot(mbin0, mf0 / yPS, 'g-')

    ax1.set_xscale('log')
    ax2.set_xscale('log')
    ax1.set_yscale('log')

    ax1.set_ylim(10**-6, 10**-0)
    ax2.set_ylim(0.45, 1.55)
    ax1.set_xlim(10**9, 10**15)
    ax2.set_xlim(10**9, 10**15)
    
    ax1.set_xticklabels([])

    ax2.set_xlabel(r'$M_{\mathrm{vir}} \quad [M_{\odot}]$')
    ax1.set_ylabel(r'$\mathrm{d}N / \mathrm{d}\log_{10}(M_{\mathrm{vir}}) \quad [\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    ax2.set_ylabel(r'$\frac{\mathrm{galpropz.dat}}{\mathrm{Model}}$')

    ax1.legend((bolshoi, sh, ps),
               ('Bolshoi', 'Sheth-Tormen', 'Press-Schecter'),
               shadow = True, fancybox = True,
               numpoints = 1)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    #Hubble constant
    h = 0.7
    #output directory
    wrkdir = os.getenv('HOME') + '/Dropbox/Research/Bolshoi/dm_halo_mf/'
    outdir = wrkdir + 'plots/'
    #find files
    simus = g.glob(wrkdir + 'simu/*.txt')
    #Note that these are in (dN / dM) * dM; per Mpc^3 (NOT h^3/Mpc^3)
    sheth = g.glob(wrkdir + 'analytical/*sheth*.dat')
    press = g.glob(wrkdir + 'analytical/*press*.dat')
    warren = g.glob(wrkdir + 'analytical/*warren*.dat')
    #analytical 2, Rachel's code
    analytical = g.glob(os.getenv('HOME') +'/Dropbox/Research/Bolshoi/var/z*')


    #make the individual plots
    fig = P.figure()
    left, width = 0.1, 0.8
    rect1 = [left, 0.1, width, 0.2]
    rect2 = [left, 0.3, width, 0.65]
    ax1 = fig.add_axes(rect2)  #left, bottom, width, height
    ax2 = fig.add_axes(rect1)
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
#            logging.debug('Plotting redshift %.2f dark matter mass functions' % redshift)
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
#            logging.debug('Plotting redshift %.2f dark matter mass functions' % redshift)
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
#            print 'Plotting redshift %.2f dark matter mass functions' % redshift
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
#            logging.debug('Plotting redshift %.2f dark matter mass functions' % redshift)
#            print a, b, c, d
#            plot_mass_function(redshift, h, False, data)
#    P.savefig(outdir + 'DMmfz2.pdf')
#    P.close()
#    
    #make the individual plots 2
    fig = P.figure()
    ax1 = fig.add_axes(rect2) 
    ax2 = fig.add_axes(rect1)
    for a, b, c, d in zip(simus, sheth, press, warren):
        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
        data = {'Bolshoi' : a,
                'Sheth-Tormen': b,
                'Press-Schecter': c,
                'Warren' : d}

        if b.find('_2_03') > -1 or b.find('_6_56') > -1 or b.find('_3_06') > -1 or b.find('_5_16') > -1 or b.find('_0_01') > -1:
            continue
        else:
            logging.debug('Plotting redshift %.2f dark matter mass functions' % redshift)
            print a, b, c, d
            plotDMMFfromGalpropz(redshift, h, data)
    P.savefig(outdir + 'DMmfz1GalpropZ.pdf')
    P.close()

    #a new plot
    fig = P.figure()
    ax1 = fig.add_axes(rect2) 
    ax2 = fig.add_axes(rect1)
    for a, b in zip(simus, analytical):
        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
        data = {'Bolshoi' : a,
                'Analytical': b}
        if redshift in [1.01, 4.04, 8.23]: #3.06, 6.56]:
            logging.debug('Plotting redshift %.2f dark matter mass functions (Analytical 2)' % redshift)
            print a, b
            plotDMMFfromGalpropzAnalytical2(redshift, h, data)
    P.savefig(outdir + 'DMmfz1GalpropZAnalytical2.pdf')
    P.close()