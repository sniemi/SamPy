import numpy as N
import pyfits as PF
import pylab as P

# Note that the lamp spectrum can be in the raw, but would not be
# present in the frame that is used in the HST. Thus, this test is
# not entirely accurate.

climit = 67.
f3 = 'lb3y01c5q_rawtag_b.fits'
f6 = 'lb6d01giq_rawtag_b.fits'

d3 = PF.open(f3)[1].data
d6 = PF.open(f6)[1].data

min3 = N.min(d3.RAWX)
max3 = N.max(d3.RAWX)

min6 = N.min(d6.RAWX)
max6 = N.max(d6.RAWX)

time3 = 15.
time6 = 15.

bins3 = N.arange(max3)[::4]
bins6 = N.arange(max6)[::4]

n3, b3 = N.histogram(d3.RAWX[d3.TIME < 15.02], bins=bins3)
n6, b6 = N.histogram(d6.RAWX[d6.TIME < 15.02], bins=bins6)

wid3 = N.abs(b3[0] - b3[1])
wid6 = N.abs(b6[0] - b6[1])

print 'Max count rate in %s is %4.2f (avg over 15s)' % (f3, N.max(n3)/time3)
print 'Max count rate in %s is %4.2f (avg over 15s)' % (f6, N.max(n6)/time6)

#plot 1
fig = P.figure()
ax = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

bars1 = ax.bar(b3[:-1], n3/time3, width=(wid3*0.98))
ax2.set_xlabel('Super Pixels (in dispersion direction)')
ax.set_ylabel('Count Rate (counts / s)')
ax.set_xlim(min3, max3/4.)
bars1 = ax2.bar(b3[:-1], n3/time3, width=(wid3*0.98))
ax2.axhline(climit, label = 'Local count rate limit')
ax2.set_ylabel('Count Rate (counts / s)')
_tmp = b3[n3 == N.max(n3)] + wid3
ax2.set_xlim(_tmp[0] - 12, _tmp[0] + 12)
P.annotate('Zero order light of 11530 visit 01',
               xy = (0.5, 0.95), 
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction')
P.annotate('Local count rate limit %4.1f' % climit,
               xy = (0.5, 0.83), 
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction')
P.annotate('Max Count Rate %4.1f cts/s (averaged over %5.1f s)' % (N.max(n3)/time3, time3),
               xy = (0.5, 0.3), 
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction')
P.legend(shadow = True, fancybox = True)
P.savefig('lb3y01c5q.pdf')
P.close()


#plot2
fig = P.figure()
ax = fig.add_subplot(211)
ax2 = fig.add_subplot(212)

bars1 = ax.bar(b6[:-1], n6/time6, width=(wid6*0.98))
ax2.set_xlabel('Super Pixels (in dispersion direction)')
ax.set_ylabel('Count Rate (counts / s)')
ax.set_xlim(min6, max6/4.)
bars1 = ax2.bar(b6[:-1], n6/time6, width=(wid6*0.98))
ax2.axhline(climit, label = 'Local count rate limit')
ax2.set_ylabel('Count Rate (counts / s)')
_tmp = b6[n6 == N.max(n6)] + wid6
ax2.set_xlim(_tmp[0] - 12, _tmp[0] + 12)
P.annotate('Zero order light of 11528 visit 01',
               xy = (0.5, 0.95), 
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction')
P.annotate('Local count rate limit %4.1f' % climit,
               xy = (0.5, 0.83), 
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction')
P.annotate('Max Count Rate %4.1f cts/s (averaged over %5.1f s)' % (N.max(n6)/time6, time6),
               xy = (0.5, 0.3), 
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction')
P.legend(shadow = True, fancybox = True)
P.savefig('lb6d01giq.pdf')
P.close()

