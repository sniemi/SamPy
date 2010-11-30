import matplotlib
matplotlib.use('PS')
import numpy
import pylab
import sys



#---------------------------------------------
file = sys.argv[1]		#file with data
name = sys.argv[2]		#full Object ID
cyct = float(sys.argv[3])	#cycle time
out  = sys.argv[4]		#Full name of output file (including suffix)
#---------------------------------------------

data = numpy.loadtxt(file, skiprows=3)
pylab.title('%s' % name, fontsize='large')

pylab.subplots_adjust(hspace=0.1)
axd = pylab.subplot(111)
pylab.setp( axd.get_xticklabels(), visible = False)
pylab.setp( axd.get_yticklabels(), visible = False)

a = len(data)
xend = (a + 1) * cyct * 4 * 10 / 60

secs = data[:,1] * cyct * 4 * 10 / 60
px = data[:,2] * 100
delpx = data[:,3] * 100
py = data[:,4] * 100
delpy = data[:,5] * 100


ax1 = pylab.subplot(211)
pylab.plot(secs, px, 'o', linestyle='None', c='k')
pylab.errorbar(secs, px, yerr=delpx, linestyle='None', linewidth=3, c='k')
pylab.axhline(y=0, c='k', linestyle='--')
pylab.setp( ax1.get_xticklabels(), visible = False)
pylab.ylabel("$P_{X}$  [%]", fontsize='large')
#pylab.ylim(-27,-25)

ax2 = pylab.subplot(212, sharex = ax1)
pylab.plot(secs, py, 'o', linestyle='None', c='k')
pylab.errorbar(secs, py, delpy, linestyle='None', linewidth=3, c='k')
pylab.axhline(y=0, c='k', linestyle='--')
pylab.setp( ax1.get_xticklabels(), visible = False)
pylab.ylabel("$P_{Y}$ [%]", fontsize='large')
#pylab.ylim(-3,-2)

pylab.xlabel("Time [min]", fontsize='large')
pylab.xlim(0,xend)

	
pylab.savefig(out)
pylab.show()