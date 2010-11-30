'''
Created on Dec 9, 2009

@author: niemi
'''

import pyfits as PF
import numpy as N
import glob as G

size = 600/2

totalM = []
totalE = []

txts = G.glob('*.txt')

for txt in txts:
    files = open(txt).readlines()
    for file in files:
        data = PF.open(file)[1].data
        gain = PF.open(file)[0].header['ATODGAIN']
        read = PF.open(file)[0].header['READNSE']
        
        #whole data
        std = N.std(data)
        mean = N.mean(data)
        rms = N.sqrt(mean**2 + std**2)
        
        #100 x 100 pixs at centre
        sh = N.shape(data)
        x , y = sh[0]/2, sh[1]/2
        xmin = x - size if x - size > 0 else 0
        xmax = x + size if x + size <= sh[0] else sh[0]
        ymin = y - size if y - size > 0 else 0
        ymax = y + size if y + size <= sh[1] else sh[1]
        
        ds = data[ymin:ymax, xmin:xmax]
        stds = N.std(ds)
        means = N.mean(ds)
        rmss = N.sqrt(means**2 + stds**2)
        
        #Poisson
        #snr = mean / N.sqrt(mean)
        #snrs = means / N.sqrt(mean)
        snr = N.sqrt(gain*mean + read**2) / gain
        snrs = N.sqrt(gain*means + read**2) / gain
        
        print '-'*30 + 'Statistics of %s' %file[:-1] + '-'*30
        print '%15s'*5 % ('array', 'mean', 'stdev', 'rms', 'SNR')
        print '%15s%16.5f%16.6f%16.6f%16.5f' % ('Full', mean, std, rms, snr)
        print '%15s%16.5f%16.6f%16.6f%16.5f\n' % ('Centre', means, stds, rmss, snrs)

        totalM.append(means)
        totalE.append(means*gain)

print 'Total number of electors per pixel at the centre is around %.0f' % N.sum(N.array(totalE))
print 'Total SNR is around %12.6f' % (N.sqrt(N.sum(N.array(totalM))))