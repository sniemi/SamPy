import sys
from pylab import *
from scipy import optimize
from numpy import *
import Gnuplot

#USAGE:
#python fit_template.py filename xcolumn ycolumn

#CHANGE THESE
#initial parameters
A1_0 = 4
A2_0 = 3
k1_0 = 0.5
k2_0 = 0.04
n1_0 = 2
n2_0 = 1
pname = (['A1','A2','k1','k2','n1','n2'])
p0 = [A1_0,A2_0,k1_0,k2_0,n1_0,n2_0]
#function to be fitted
def f(x): return A1_0()*(1-exp(-(k1_0()*x)**n1_0())) + A2_0()*(1-exp(-(k2_0()*(x))**n2_0()))

#some help definitions
def residuals(p, y, x):
        err = y-peval(x,p)
        return err
#more help
def peval(x, p):
        return p[0]*(1-exp(-(p[2]*x)**p[4])) + p[1]*(1-exp(-(p[3]*(x))**p[5]))

#reads commandline arguments
filename = sys.argv[1]
xcolumn = eval(sys.argv[2])
ycolumn = eval(sys.argv[3])

#reads file
xdata, ydata = loadtxt(sys.argv[1], usecols=[xcolumn,ycolumn], unpack=True)

#Change fitfunc to be suitable
fitfunc = lambda p, x:  p[0]*(1-exp(-(p[2]*x)**p[4])) + p[1]*(1-exp(-(p[3]*(x))**p[5]))
errfunc = lambda p, x, y: fitfunc(p,x) - y
plsq = optimize.leastsq(residuals, p0, args=(ydata, xdata), maxfev=2000)

#shorter definition
g = Gnuplot.Gnuplot(debug=1)

#plot original data
g.xlabel('Xlabel')
g.ylabel('Ylabel')
d = Gnuplot.Data(xdata,ydata,title='Title', with='points')
g.plot(d)
g.hardcopy('plot.eps',enhanced=1,color=1)
g.reset()

fitt = Gnuplot.Data(xdata,peval(xdata,plsq[0]),title='Fit',with='lines lt -1')
g.plot(d,fitt)
#raw_input('Please press return to continue...\n')
g.hardcopy('withfit.eps', enhanced=1, color=1)
g.reset()

#prints fitting parameters
print "Final parameters"
for i in range(len(pname)):
        print "%s = %.4f " % (pname[i], p0[i])

#END
