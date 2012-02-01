import matplotlib
matplotlib.use('PDF')
from itertools import izip, count
import pyfits as pf
import numpy as np
import scipy.stats
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import NullFormatter


input = 'flt.fits'
sigma = 5


#function begins
inp = input.replace('.fits', '')

fh = pf.open(input)
data = fh[1].data
org = data.copy()
dqarr = fh[3].data

medians = []

for i, l, dq in izip(count(), data, dqarr):
    msk = ~(dq > 0)
    d = l[msk]
    #mask additionally everything above x sigma
    sig = np.median(d) + sigma*np.std(d)
    msk2 = d < sig
    median = np.median(d[msk2])
    print i, median
    if ~np.isnan(median):
        data[i] -= median
        medians.append(median)
    else:
        print 'Will not remove nan median on line %i' % i

medians = np.asarray(medians)
#medmed1 = np.median(medians)
medmed2 = np.median(org[~(dqarr > 0)])

data += medmed2

#print medmed1, medmed2

fh.writeto(inp+'destriped.fits')
fh.close()


plt.figure()
plt.title(inp)
ims = plt.imshow(data / org, origin='lower', vmin=0.98, vmax=1.02)
cb = plt.colorbar(ims)
cb.set_label('Destriped / Original')
plt.savefig(inp+'ratio.pdf')
plt.close()


nullfmt = NullFormatter()

#KDE1
#est1 = []
#vals = medians-medmed1
#kde = scipy.stats.gaussian_kde(vals)
#for x in np.arange(np.int(np.min(vals)), np.int(np.max(vals)), 0.1):
#    y = kde.evaluate(x)[0]
#    est1.append([x, y])
#est1 = np.asarray(est1)
#KDE2
est2 = []
vals = medians-medmed2
kde = scipy.stats.gaussian_kde(vals)
for x in np.arange(np.int(np.min(vals)), np.int(np.max(vals)), 0.1):
    y = kde.evaluate(x)[0]
    est2.append([x, y])
est2 = np.asarray(est2)


#plt.figure()
#gs = gridspec.GridSpec(2, 1, height_ratios=[4,1])
#gs.update(wspace=0.0, hspace=0.0, top=0.96, bottom=0.07)
#axScatter = plt.subplot(gs[0])
#axHist = plt.subplot(gs[1])
#axScatter.set_title(inp)
#axScatter.plot(medians-medmed1, np.arange(len(medians)), 'bo')
#axScatter.xaxis.set_major_formatter(nullfmt)
#n, bins, patches = axHist.hist(medians-medmed1, bins=35, normed=True)
#axHist.plot(est1[:,0], est1[:,1], 'r-', label='Gaussian KDE')
#axHist.set_xlabel('Medians')
#axScatter.set_ylabel('Row')
#axScatter.set_ylim(-2, 2046)
#axHist.legend()
#plt.savefig(inp+'dist1.pdf')
#plt.close()

plt.figure()
gs = gridspec.GridSpec(2, 1, height_ratios=[4,1])
gs.update(wspace=0.0, hspace=0.0, top=0.96, bottom=0.07)
axScatter = plt.subplot(gs[0])
axHist = plt.subplot(gs[1])
axScatter.set_title(inp)
axScatter.plot(medians-medmed2, np.arange(len(medians)), 'bo')
axScatter.xaxis.set_major_formatter(nullfmt)
n, bins, patches = axHist.hist(medians-medmed2, bins=35, normed=True)
axHist.plot(est2[:,0], est2[:,1], 'r-', label='Gaussian KDE')
axHist.set_xlabel('Medians')
axScatter.set_ylabel('Row')
axScatter.set_ylim(-1, 2046)
axHist.legend()
plt.savefig(inp+'dist.pdf')
plt.close()
