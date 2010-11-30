
#11/06/2008 Sami-Matias Niemi for NOT

from scipy import optimize
from numpy import *
#from math import *

class Parameter:
    def __init__(self, value):
        self.value = value

    def set(self, value):
        self.value = value

    def __call__(self):
        return self.value

def fitSMN(function, parameters, y, x):
	def f(params):
		i = 0
		for p in parameters:
			p.set(params[i])
			i += 1
		return y - function(x)
	
	if x is None: x = arange(y.shape[0])
	p = [param() for param in parameters]
	plsq = optimize.leastsq(f,p)
    #pbest = leastsq(residuals,p0,args=(data,t),full_output=1)
	return plsq[0]

def pevalSMN(function, x):
	return function(x)

#END

#from scipy import *
#from matplotlib import *
#from pylab import *
#from scipy.optimize import leastsq
#"""
#Example of curve fitting for
#a1*exp(-k1*t) + a2*exp(-k2*t)
#"""
#def dbexpl(t,p):
#    return(p[0]*exp(-p[1]*t) + p[2]*exp(-p[3]*t))
#a1,a2 = 1.0, 1.0
#k1,k2 = 0.05, 0.2
#t=arange(0,100,0.1)
#data = dbexpl(t,[a1,k1,a2,k2]) + 0.02*randn(len(t))
#def residuals(p,data,t):
#    err = data - dbexpl(t,p)
#    return err
#p0 = [0.5,1,0.5,1] # initial guesses
#guessfit = dbexpl(t,p0)
#pbest = leastsq(residuals,p0,args=(data,t),full_output=1)
#bestparams = pbest[0]
#cov_x = pbest[1]
#print 'best fit parameters ',bestparams
#print cov_x
#datafit = dbexpl(t,bestparams)
#plot(t,data,'x',t,datafit,'r',t,guessfit)
#xlabel('Time')
#title('Curve-fitting example')
#grid(True)
#show()
