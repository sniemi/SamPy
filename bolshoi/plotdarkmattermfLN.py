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
#From Sami's repo
import astronomy.differentialfunctions as df
import io.read as io

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
    #is the Bolshoi masses in M_solar or M_solar / h
    mbin0, mf0 = df.mass_function(dt['Bolshoi'],
                                  nbins = 40, h = 1., 
                                  mmin = 20, mmax = 35)
    del dt['Bolshoi']
    #title
    if no_phantoms:
        ax1.set_title('Bolshoi Dark Matter Mass Functions (no phantoms)')
    else:
        ax1.set_title('Bolshoi Dark Matter Mass Functions')

    #MF from Bolshoi
    bolshoi = ax1.plot(mbin0, mf0, 'ro:', ms = 4) 

    #mark redshift
    for a, b in zip(mbin0[::-1], mf0[::-1]):
        if b > 10**-5:
            break
    ax1.annotate('$z \sim %.1f$' % redshift,
                (0.98*a, 3*10**-6), size = 'x-small')

    #Analytical MFs
    #1st column: mass (Msolar/h)
    #2nd column: (dn/dM)*dM, per Mpc^3 (NOT h^3/Mpc^3)
    xST = dt['Sheth-Tormen'][:,1]
    #from (dN / dM) * dM to dN / dlnM using the chain rule
    #scaled with N.exp(h), because ln binning
    swap = 1. / (N.log(xST[4]) - N.log(xST[3])) * N.exp(h) 
    yST = dt['Sheth-Tormen'][:,2] / h3 * swap
    sh = ax1.plot(xST, yST, 'b-', lw = 1.3)
    #PS
    xPS = dt['Press-Schecter'][:,1]
    #scaled with N.exp(h), because ln binning
    swap = 1. / (N.log(xPS[1]) - N.log(xPS[0])) * N.exp(h)
    yPS = dt['Press-Schecter'][:,2] / h3 * swap
    ps = ax1.plot(xPS, yPS, 'g-', lw = 1.1)
    #Warren
    xW = dt['Warren'][:,1]
    #scaled with N.exp(h), because ln binning
    swap = 1. / (N.log(xW[1]) - N.log(xW[0])) * N.exp(h)
    yW = dt['Warren'][:,2] / h3 * swap
    wr = ax1.plot(xW, yW, 'y--', lw = 0.8)

    #delete data to save memory, dt is not needed anylonger
    del dt

    #plot the residuals
    if round(float(redshift), 1) < 1.5:
        #interploate to right x scale
        yST = N.interp(mbin0, xST, yST)
        yPS = N.interp(mbin0, xPS, yPS)
        yW = N.interp(mbin0, xW, yW)
        #make the plot
        ax2.annotate('$z \sim %.1f$' % redshift,
                     (1.5*10**9, 1.05), xycoords='data',
                     size = 10)
        ax2.axhline(1.0, color = 'b')
        ax2.plot(mbin0, mf0 / yST, 'b-')
        ax2.plot(mbin0, mf0 / yPS, 'g-')
        ax2.plot(mbin0, mf0 / yW, 'y-')

    ax1.set_xscale('log')
    ax2.set_xscale('log')
    ax1.set_yscale('log')

    ax1.set_ylim(10**-6, 1)
    ax2.set_ylim(0.45, 1.55)
    ax1.set_xlim(10**9, 10**15)
    ax2.set_xlim(10**9, 10**15)
    
    ax1.set_xticklabels([])

    ax2.set_xlabel(r'$M_{vir} \quad [h^{-1}M_{\odot}]$')
    ax1.set_ylabel(r'$\mathrm{d}N / \mathrm{d}ln(M_{vir}) \quad [h^{3}\mathrm{Mpc}^{-3} \mathrm{dex}^{-1}]$')
    ax2.set_ylabel(r'$\frac{\mathrm{Bolshoi}}{\mathrm{Model}}$')

    ax1.legend((bolshoi, sh, ps, wr),
               ('Bolshoi', 'Sheth-Tormen', 'Press-Schecter', 'Warren'),
               shadow = True, fancybox = True,
               numpoints = 1)

if __name__ == '__main__':
    #Hubble constant
    h = 0.7
    #output directory
    wrkdir = '/Users/niemi/Desktop/Research/dm_halo_mf/'
    #find files
    simus = g.glob(wrkdir + 'simu/*.txt')
    #Note that these are in (dN / dM) * dM; per Mpc^3 (NOT h^3/Mpc^3)
    sheth = g.glob(wrkdir + 'analytical/*sheth*.dat')
    press = g.glob(wrkdir + 'analytical/*press*.dat')
    warren = g.glob(wrkdir + 'analytical/*warren*.dat')

    #make the individual plots
    fig = P.figure()
    left, width = 0.1, 0.8
    rect1 = [left, 0.1, width, 0.2]
    rect2 = [left, 0.3, width, 0.65]
    ax1 = fig.add_axes(rect2)  #left, bottom, width, height
    ax2 = fig.add_axes(rect1)
    for a, b, c, d in zip(simus, sheth, press, warren):
        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
        data = {'Bolshoi' : a,
                'Sheth-Tormen': b,
                'Press-Schecter': c,
                'Warren' : d}

        if b.find('_1_01') > -1 or b.find('_6_56') > -1 or b.find('_3_06') > -1 or b.find('_5_16') > -1:
            continue
        else:
            print 'Plotting redshift %.2f dark matter mass functions' % redshift
            print a, b, c, d
            plot_mass_function(redshift, h, True, data)
    P.savefig(wrkdir + 'out/DMmfzNoPhantomsLN1.pdf')
    P.close()
    
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

        if b.find('_1_01') > -1 or b.find('_6_56') > -1 or b.find('_3_06') > -1 or b.find('_5_16') > -1:
            continue
        else:
            print 'Plotting redshift %.2f dark matter mass functions' % redshift
            print a, b, c, d
            plot_mass_function(redshift, h, False, data)
    P.savefig(wrkdir + 'out/DMmfzLN1.pdf')
    P.close()
    
    #make the individual plots 3
    fig = P.figure()
    ax1 = fig.add_axes(rect2) 
    ax2 = fig.add_axes(rect1)
    for a, b, c, d in zip(simus, sheth, press, warren):
        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
        data = {'Bolshoi' : a,
                'Sheth-Tormen': b,
                'Press-Schecter': c,
                'Warren' : d}

        if b.find('_1_01') > -1 or b.find('_6_56') > -1 or b.find('_3_06') > -1 or b.find('_5_16') > -1:
            print 'Plotting redshift %.2f dark matter mass functions' % redshift
            print a, b, c, d
            plot_mass_function(redshift, h, True, data)
    P.savefig(wrkdir + 'out/DMmfzNoPhantomsLN2.pdf')
    P.close()

    #make the individual plots 4
    fig = P.figure()
    ax1 = fig.add_axes(rect2) 
    ax2 = fig.add_axes(rect1)
    for a, b, c, d in zip(simus, sheth, press, warren):
        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
        data = {'Bolshoi' : a,
                'Sheth-Tormen': b,
                'Press-Schecter': c,
                'Warren' : d}

        if b.find('_1_01') > -1 or b.find('_6_56') > -1 or b.find('_3_06') > -1 or b.find('_5_16') > -1:
            print 'Plotting redshift %.2f dark matter mass functions' % redshift
            print a, b, c, d
            plot_mass_function(redshift, h, False, data)
    P.savefig(wrkdir + 'out/DMmfzLN2.pdf')
    P.close()