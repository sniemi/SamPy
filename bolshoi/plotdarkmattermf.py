'''
Plots a dark matter halo mass function at different
redshifts. Input data are from the Bolshoi simulation.
@author: Sami-Matias Niemi

@todo: modify so that the plot shows residuals at the
bottom of the actual image. Make two plots with different
redshift bins.
'''
import matplotlib
matplotlib.use('PDF')
matplotlib.rc('text', usetex = True)
import pylab as P
import numpy as N
import glob as g
#Sami's repo
import astronomy.differentialfunctions as df

def read_file(filename, column, no_phantoms):
    out = []
    fh = open(filename, 'r')
    line = fh.readline()
    while line:
        if no_phantoms:
            if int(float(line.split()[2])) == 0:
                out.append(float(line.split()[column]))
        else:
            out.append(float(line.split()[column]))
        line = fh.readline()
    return N.array(out)

def plot_mass_function(redshift, h, no_phantoms, *data):
    #Hubble constants
    h3 = h**3
    h4 = h**4

    #read data
    dt = {}
    for x in data[0]:
        if 'Bolshoi' in x:
            dt[x] = read_file(data[0][x], 0, no_phantoms)
        else:
            dt[x] = N.loadtxt(data[0][x])

    #calculate the mass functions from the Bolshoi data
    mbin0, mf0 = df.mass_function(dt['Bolshoi'],
                                  nbins = 50, h = 1., 
                                  mmin = 20, mmax = 35)
    del dt['Bolshoi']

    #make the plots
    ax = P.subplot(111)
    #title
    if no_phantoms:
        P.title('Bolshoi Dark Matter Mass Functions (no phantoms)')
    else:
        P.title('Bolshoi Dark Matter Mass Functions')

    #simulated mf
    bolshoi = ax.plot(mbin0, mf0, 'ro-') 

    #mark redshift
    for a, b in zip(mbin0[::-1], mf0[::-1]):
        if b > 10**-4:
            break
    ax.annotate('z = %.1f' % redshift,
                (a, 2*10**-5), size = 'small')


    #analytical mfs
#    for a in dt:
#        #from (dN / dM) * dM to dN / dlnM using the chain rule
#        x = dt[a][:,1]
#        dm = x[1] - x[0]
#        swap = 1. / (N.log(x[1]) - N.log(x[0])) / h4
#        #swap = 1. / N.log(dm)
#        print dm, swap
#        y = dt[a][:,2]  * swap
#        ax.plot(x, y)#, label = a)

    #from (dN / dM) * dM to dN / dlnM using the chain rule
    x = dt['Sheth-Tormen'][:,1]
    #scaled with h3 and N.exp(h), because ln binning
    swap = 1. / (N.log(x[1]) - N.log(x[0])) / h3 * N.exp(h)
    y = dt['Sheth-Tormen'][:,2] * swap
    sh = ax.plot(x, y, 'b-')

    x = dt['Press-Schecter'][:,1]
    #scaled h4 because on h in masses
    y = dt['Press-Schecter'][:,2] * swap
    ps = ax.plot(x, y, 'g-')

#    x = dt['Warren'][:,1]
#    #scaled h4 because on h in masses
#    y = dt['Warren'][:,2] * swap
#    wr = ax.plot(x, y, 'y-')

    #save memory
    del dt

    ax.set_xscale('log')
    ax.set_yscale('log')

    ax.set_xlim(3*10**9, 10**15)
#    ax.set_ylim(10**-6, 2*10**-1)
    ax.set_ylim(10**-6, 2*10**-1)

    ax.set_xlabel(r'$M_{vir} \quad [h^{-1}M_{\odot}]$')
#    ax.set_ylabel(r'$\textrm{d}N / \textrm{d}ln(M_{vir}) \quad [h^{3}\textrm{Mpc}^{-3} \textrm{dex}^{-1}]$')
    ax.set_ylabel(r'$\textrm{d}N / \textrm{d}ln(M_{vir}) \quad [h^{3}\textrm{Mpc}^{-3}]$')

    P.legend((bolshoi, sh, ps), ('Bolshoi', 'Sheth-Tormen', 'Press-Schecter'), shadow = True, fancybox = True)
#    P.legend((bolshoi, sh, wr), ('Bolshoi', 'Sheth-Tormen', 'Warren'), shadow = True, fancybox = True)



if __name__ == '__main__':
    #constants
    h = 0.7

    wrkdir = '/Users/niemi/Desktop/Research/dm_halo_mf/'

    #find files
    simus = g.glob(wrkdir + 'simu/*.txt')
    #note that these are in dN / DM
    sheth = g.glob(wrkdir + 'analytical/*sheth*.dat')
    press = g.glob(wrkdir + 'analytical/*press*.dat')
    warren = g.glob(wrkdir + 'analytical/*warren*.dat')

    #make the individual plots
    for a, b, c, d in zip(simus, sheth, press, warren):
        redshift = float(a.split('z')[1].split('.')[0].replace('_', '.'))
        data = {'Bolshoi' : a,
                'Sheth-Tormen': b,
                'Press-Schecter': c,
                'Warren' : d}

        if b.find('_1_01') > -1 or b.find('_2_03') > -1 or b.find('_3_06') > -1 or b.find('_5_16') > -1:
            continue
        else:
            print 'Plotting redshift %.2f dark matter mass functions' % redshift
            print a, b, c, d
            plot_mass_function(redshift, h, True, data)
#            plot_mass_function(redshift, h, False, data)

    P.savefig(wrkdir + 'out/DMmfzNoPhantoms.pdf')
#    P.savefig(wrkdir + 'out/DMmfz.pdf')
    P.close()
