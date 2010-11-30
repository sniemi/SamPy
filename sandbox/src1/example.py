import pylab as P

every = 3

ax1 = P.subplot(111)

xdata = range(10)

ax1.plot(xdata)

yticks = ax1.get_yticks()
ax1.set_yticks(yticks[::every])
ax1.set_xticks([2,3,9])
ax1.set_xticklabels(['foo', 'bar', 'doo'])

P.savefig('example.png')

