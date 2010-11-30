from scipy import *
from scipy.optimize import leastsq
import scipy.io.array_import
from scipy import gplt

def residuals(p, y, x): 
	err = y-peval(x,p) 
	return err

def peval(x, p): 
	return p[0]*(1-exp(-(p[2]*x)**p[4])) + p[1]*(1-exp(-(p[3]*(x))**p[5] ))

filename=('tgdata.dat')
data = scipy.io.array_import.read_array(filename)

y = data[:,1]
x = data[:,0]

A1_0=4
A2_0=3
k1_0=0.5
k2_0=0.04
n1_0=2
n2_0=1
pname = (['A1','A2','k1','k2','n1','n2'])
p0 = array([A1_0 , A2_0, k1_0, k2_0,n1_0,n2_0])
plsq = leastsq(residuals, p0, args=(y, x), maxfev=2000)
gplt.plot(x,y,'title "Meas" with points',x,peval(x,plsq[0]),'title "Fit" with lines lt -1')
gplt.yaxis((0, 7))
gplt.legend('right bottom Left')
gplt.xtitle('Time [h]')
gplt.ytitle('Hydrogen release [wt. %]')
gplt.grid("off")
gplt.output('kinfit.png','png medium transparent size 600,400')

print "Final parameters"
for i in range(len(pname)):
	print "%s = %.4f " % (pname[i], p0[i])
