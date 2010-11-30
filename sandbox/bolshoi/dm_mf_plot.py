import matplotlib
matplotlib.use('PDF')
matplotlib.rc('text', usetex = True)
import pylab as P
import numpy as N
import glob as g

def mass_function(data, column = 0, log = False,
                  wght = None, mmin = 9, mmax = 15.0, 
                  nbins = 35, h = 0.7, volume = 250, nvols = 1,
                  verbose = False):
    '''
    Calculates a mass function from data.
    Returns differential mass function and bins:
    dN / dlnM
    @TODO: add calculating the cumulative mass function.
    '''
    #output
    mf = []

    #if log have been taken from the data or not
    if not log:
        if len(data.shape) > 1:
            dat = N.log(data[:, column]) # * h)
        else:
            dat = N.log(data) #*h)
    else:
        if len(data.shape) > 1:
            dat = data[:, column] #* h
        else:
            dat = data #*h
    del data

    #number of galaxies
    ngal = len(dat)

    #set weights if None given
    if wght == None:
        wght = N.zeros(ngal) + (1./(nvols*(float(volume)/h)**3))

    #bins
    mbin = N.linspace(mmin, mmax, nbins)
    #on could alos use N.logspace()
    dm = mbin[1] - mbin[0]

    if verbose:
        print 'Number of galaxies = %i' % ngal
        print 'dlnM =', dm
        print 'h =', h

    #loop over the mass bins
    for i, thismass in enumerate(mbin):
        if i == 0 :
            prev = thismass
            continue
        mask = (dat > prev) & (dat <= thismass)
        mf.append(N.sum(wght[mask]))
        prev = thismass

    #swqp it to the middle of the bin and drop the last
    mbin = mbin[:-1] + dm

    mf = N.array(mf)
    
    if not log:
        mbin = N.e**mbin
        if verbose:
            print '\nResults:', mbin, mf/dm
        return mbin, mf/dm
    else:
        if verbose:
            print '\nResults:', mbin, mf/dm
        return mbin, mf/dm


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
    mbin0, mf0 = mass_function(dt['Bolshoi'], nbins = 50, h = 1., 
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
    #scaled h4 because on h in masses
    swap = 1. / (N.log(x[1]) - N.log(x[0])) / h4 
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

    #find files
    simus = g.glob('./simu/*.txt')
    #note that these are in dN / DM
    sheth = g.glob('./analytical/*sheth*.dat')
    press = g.glob('./analytical/*press*.dat')
    warren = g.glob('./analytical/*warren*.dat')

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

    P.savefig('./out/DMmfzNoPhantoms.pdf')
#    P.savefig('./out/DMmfz.pdf')
    P.close()
