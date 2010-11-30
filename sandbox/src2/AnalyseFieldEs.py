
def histograms():
    temp = {'DMmass':
            {#'column' : 25,
             'column' : 12,
            'file' : 'DMmass',
            'bins' : 20,
            'min' : 1.,
            'max' : 7000.}
            ,
            'vmax':
            {'column' : 28, 
            'file' : 'vmax',
            'bins' : 25,
            'min' : 10.,
            'max' : 1000.}
            ,
            'coldGas':
            {'column' : 29, 
            'file' : 'coldGas',
            'bins' : 25,
            'min' : 1.,
            'max' : 3.0}
            ,
            'stellarMass':
            {'column' : 30,
            'file' : 'stellarMass',
            'bins' : 25,
            'min' : 1.,
            'max' : 30.}
            ,
            'sfr':
            {'column' : 40,
            'file' : 'sfr',
            'bins' : 15,
            'min' : 1,
            'max' : 10}
            ,
            'magb':
            {'column' : 45,
            'file' : 'magb',
            'bins' : 20,
            'min' : -24,
            'max' : -19}
            ,
            'massWeightedAge':
            {'column' : 60, 
            'file' : 'massWeightedAge',
            'bins' : 20,
            'min' : 1,
            'max' : 13}
            ,
            'colour':
            {'column' : 'xx',
            'file' : 'colour',
            'bins' : 30,
            'min' : 0.2,
            'max' : 2.0}
            ,
            'companions':
            {'column': 'yy',
             'file' : 'companions',
             'bins' : 35,
             'min' : 0,
             'max' : 35}
            ,
            'morphology':
            {'column': 62,
             'file' : 'morphology',
             'bins' : 20,
             'min' : -9,
             'max' : -4}
            }

    return temp

def SMNhistogram(file, data1, data2, bins, min, max, save, volume):
    import numpy as N
    import pylab as P
    from math import log

    fig = P.figure()
    ax = fig.add_subplot(111)

    colour1 = "0.8" # "r"
    colour2 = "0.4" # "b"
    pattern1 = 'x'
    pattern2 = '/'

    if file == 'DMmass':
        #E histogram
        (nE, binsE) = N.histogram(N.log(data2), bins=bins, range = (log(min),log(max)))
        widE = binsE[0] - binsE[1]

        #fEs histogram
        (nfE, binsfE) = N.histogram(N.log(data1), bins=bins, range = (log(min),log(max)))
        widfE = binsfE[0] - binsfE[1]

    else:
        #E histogram
        (nE, binsE) = N.histogram(data2, bins=bins, range = (min,max))
        widE = binsE[0] - binsE[1]

        #fEs histogram
        (nfE, binsfE) = N.histogram(data1, bins=bins, range = (min,max))
        widfE = binsfE[0] - binsfE[1]

    #print nE/volume

    #E histogram
    if file == 'companions':
        #bars1 = ax.bar((binsfE-widfE), nfE/volume, width=(widfE*0.9), log=True, label = 'Large Sphere', align = 'edge',
        #               color = colour1, edgecolor = 'k', alpha = 0.6, lw = 1.5)
        bars1 = ax.bar((binsfE[:bins]-widfE), nfE/volume, width=(widfE*0.8), log=True, label = 'Large Sphere',
                       color = colour1, edgecolor = 'k', alpha = 0.6, lw = 1.5)
        for bar in bars1: bar.set_hatch(pattern1)
    else:
#        bars1 = ax.bar((binsE-widE), nE/volume, width=(widE*0.9), log=True, label = 'Es', align = 'edge', 
#                       color = colour1, edgecolor = 'k', alpha = 0.4, lw = 1.5)
        bars1 = ax.bar((binsE[:bins]-widE), nE/volume, width=(widE*0.8), log=True, label = 'Es', align = 'edge', 
                       color = colour1, edgecolor = 'k', alpha = 0.4, lw = 1.5)
        for bar in bars1: bar.set_hatch(pattern1)

    #fE histogram
    if file == 'companions':
#        bars2 = ax.bar((binsE-widE), nE/volume, width=(widE*.9), log=True, label = 'Small Sphere', align = 'edge',
#                       color = colour2, edgecolor = 'k', alpha = 0.4, lw = 1.5)
        bars2 = ax.bar((binsE[:bins]-widE), nE/volume, width=(widE*.8), log=True, label = 'Small Sphere', align = 'edge',
                       color = colour2, edgecolor = 'k', alpha = 0.4, lw = 1.5)
        for bar in bars2: bar.set_hatch(pattern2)
    else:
#        bars2 = ax.bar((binsfE-widfE), nfE/volume, width=(widfE*.9), log=True, label = 'IfEs', align = 'edge',
#                       color = colour2, edgecolor = 'k', alpha = 0.6, lw = 1.5)
        bars2 = ax.bar((binsfE[:bins]-widfE), nfE/volume, width=(widfE*.8), log=True, label = 'IfEs', align = 'edge',
                       color = colour2, edgecolor = 'k', alpha = 0.6, lw = 1.5)
        for bar in bars2: bar.set_hatch(pattern2)

    if (file == 'vmax'): P.xlabel("$V_{max}$ (kms$^{-1}$)")
    if (file == 'coldGas'): P.xlabel('Mass in cold gas $(10^{10}h^{-1}$M$_{\odot}$)')
    if (file == 'stellarMass'): P.xlabel('Stellar Mass $(10^{10}h^{-1}$M$_{\odot}$)')
    if (file == 'sfr'): P.xlabel('Star Formation Rate (M$_{\odot})$yr$^{-1}$')
    if (file == 'magb'): P.xlabel('Absolute rest frame B Magnitude (Vega)')
    if (file == 'massWeightedAge'): P.xlabel('Mass Weighted Age ($10^{9}$yr)')
    if (file == 'DMmass'): P.xlabel('$\log$(Virial Dark Matter Mass) $(10^{10}h^{-1}$M$_{\odot}$)')
    if (file == 'colour'): P.xlabel('B - R (mag)')
    if (file == 'companions'): P.xlabel('Number of Companions')
    if (file == 'morphology'): P.xlabel('Morphology T')

    #P.title("Mass Distributions")
    P.ylabel("Number Density ($h^{3}$Mpc$^{-3}$)")
    P.ylim(3.*10.**-8., 10.**-4.)
    P.legend()

    if file == 'DMmass': 
        #P.xscale('log')
        P.ylim(3.*10.**-8., 10.**-4.)

    if save : P.savefig(file+'.eps')
    else: P.show()
    
    P.close()


def main(saved):
    import scipy.stats as S
    import numpy as N

    #Constants
    save = saved
    bmag = 45
    volume = 5.*194.**3.
    type = 9

    #Reads data
    ET4 = N.loadtxt("EllipticalsT4.out")
    fEsall = N.loadtxt("FieldEllipticals.out")
    
    #marks only the ones which fulfil criterion
    indices = N.where(ET4[:,bmag] <= -19.) 
    ET4magb = ET4[indices]

    #Takes away three that are actually subhaloes...
    ind = N.where(fEsall[:,type] == 0)
    fEs = fEsall[ind]

    hists = histograms()

    print '\nNumber of fEs and Es:\n %i %i' % (len(fEs), len(ET4magb))
    
    for plot in hists:   
        column = hists[plot]['column']
        file = hists[plot]['file']
        bins = hists[plot]['bins']
        min =  hists[plot]['min']
        max =  hists[plot]['max']

        if (file == 'colour'):
            temp = fEs[:,45] - fEs[:,47]
            temp1 = ET4magb[:,45] - ET4magb[:,47]
        elif (file == 'companions'):
            temp = fEs[:,63] + fEs[:,64]
            temp1 = fEs[:,64]
        else:
            temp = fEs[:,column]
            temp1 = ET4magb[:,column]

        SMNhistogram(file, temp, temp1, bins, min, max, save, volume)
        
        D, p = S.ks_2samp(temp, temp1)
        print '\nKolmogorov-Smirnov statistics for %s:' % file
        print 'D-value = %e \np-value = %e' % (D, p)


        print '\nStatistics 1st fEs and then Es:'
        print ("%20s" + "%15s"*7) % ("Name", "1st Quart", "Median", "3rd Quart", "Max", "Min", "Mean", "Stdev")
        frmt = "%14s & %12.2f & %12.2f & %12.2f & %12.2f & %12.2f & %12.2f & %12.2f"
        frmt1 = "IfEs &" + frmt
        frmt2 = "Es   &" + frmt
        print frmt1 % (file, S.scoreatpercentile(temp, 25), 
                      N.median(temp), S.scoreatpercentile(temp, 75),
                      N.max(temp), N.min(temp), N.mean(temp), N.std(temp))
        print frmt2 % (file, S.scoreatpercentile(temp1, 25), 
                      N.median(temp1), S.scoreatpercentile(temp1, 75),
                      N.max(temp1), N.min(temp1), N.mean(temp1), N.std(temp1))

if (__name__ == '__main__'):
    main(saved = True)
