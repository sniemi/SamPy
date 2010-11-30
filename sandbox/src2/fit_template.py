import sys
import Gnuplot
from scipy import optimize
from numpy import *
from fit_help import *

#USAGE:
#python fit_template.py filename xcolumn ycolumn
#DEPENDECY
#fit_help.py

#CHANGE THESE
#initial parameters
A1_0 = Parameter(4)
A2_0 = Parameter(3)
k1_0 = Parameter(0.5)
k2_0 = Parameter(0.04)
n1_0 = Parameter(2)
n2_0 = Parameter(1)
pname = (['A1','A2','k1','k2','n1','n2'])
#p0 = [A1_0,A2_0,k1_0,k2_0,n1_0,n2_0]
#function to be fitted
def func(x): return A1_0()*(1-exp(-(k1_0()*x)**n1_0())) + A2_0()*(1-exp(-(k2_0()*(x))**n2_0()))

#reads commandline arguments
filename = sys.argv[1]
xcolumn = eval(sys.argv[2])
ycolumn = eval(sys.argv[3])

#reads file
xdata, ydata = loadtxt(sys.argv[1], usecols=[xcolumn,ycolumn], unpack=True)

#shorter definition
g = Gnuplot.Gnuplot(debug=1)

#plot original data
g.xlabel('Xlabel')
g.ylabel('Ylabel')
d = Gnuplot.Data(xdata, ydata, title='Title', with='points')
g.plot(d)
g.hardcopy('plot.eps',enhanced=1,color=1)
g.reset()

#fitting
#fit(function, parameters, data)
p0_updated = fitSMN(func, [A1_0,A2_0,k1_0,k2_0,n1_0,n2_0], ydata, xdata)
#updates the parameters
A1_0 = Parameter(p0_updated[0])
A2_0 = Parameter(p0_updated[1])
k1_0 = Parameter(p0_updated[2])
k2_0 = Parameter(p0_updated[3])
n1_0 = Parameter(p0_updated[4])
n2_0 = Parameter(p0_updated[5])
fitted = pevalSMN(func,xdata)

#plot fit
fitt = Gnuplot.Data(xdata, fitted, title='Fit',with='lines lt -1')
g.plot(fitt)
g.hardcopy('fit.eps', enhanced=1, color=1)
g.reset()

#plots with fit
g.plot(d,fitt)
#raw_input('Please press return to continue...\n')
g.hardcopy('plotwithfit.eps', enhanced=1, color=1)
g.reset()

#prints fitting parameters
print "Final parameters"
for i in range(len(pname)):
        print "%s = %.4f " % (pname[i], p0_updated[i])

#save("parameters.txt", p0_updated)

#END
