import numpy as np
import pymc

datapoints = 50

# create some fake data
x = np.arange(datapoints) * 0.45
f = 0.15 * x**2 - 3.35 * x - 7.35
#create some noise and add to the data
noise = np.random.normal(size=datapoints) * 2.5
f += noise
#add crazy outliers
f[15] = -5
f[32] = -15
f[34] = -31

#fit polynomial using the numpy.polyfit
z = np.polyfit(x, f, 2)
print 'The chi-square result: ',  z

#set priors
sig = pymc.Uniform('sig', 0.0, 100.0, value=1.)
#sig = pymc.Normal('sig', 3, 10.0)
a = pymc.Uniform('a', -5.0, 5.0, value= 0.0)
b = pymc.Uniform('b', -5.0, 5.0, value= 0.0)
c = pymc.Uniform('c', -10.0, 10.0, value= 0.0)
d = pymc.Uniform('d', -100.0, 100.0, value= 0.0)

#model
@pymc.deterministic(plot=False)
def quadratic(x=x, a=a, b=b, c=c, d=d):
    return a*x**2 + b*x + c + d

#likelihood
y = pymc.Normal('y', mu=quadratic, tau=1.0/sig**2, value=f, observed=True)