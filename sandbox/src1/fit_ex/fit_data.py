from pylab import *
from scipy import *
import scipy.io.array_import

filename=('tgdata.dat')
data = scipy.io.array_import.read_array(filename)

tY = data[:,1]
tX = data[:,0]

fitfunc = lambda p, x:  p[0]*(1-exp(-(p[2]*x)**p[4])) + p[1]*(1-exp(-(p[3]*(x))**p[5]))
errfunc = lambda p, x, y: fitfunc(p,x) -y          # Distance to the target function
A1_0=4
A2_0=3
k1_0=0.5
k2_0=0.04
n1_0=2
n2_0=1
p0 = [A1_0,A2_0,k1_0,k2_0,n1_0,n2_0]                       # Initial guess for the parameters
p1,success = optimize.leastsq(errfunc, p0[:], args = (tY, tX))

time = linspace(tX.min(),tY.max(),100)
plot(tX,tY,"ro",time,fitfunc(p1,time),"r-")        # Plot of the data and the fit

title("fittin probs")
xlabel("time [ms]")
ylabel("displacement [um]")
legend(('x position', 'x fit', 'y position', 'y fit'))

ax = axes()

#text(0.8, 0.07,'x freq :  %.3f kHz \n y freq :  %.3f kHz'
#         %(1/p1[1],1/p2[1]), fontsize = 16,
#         horizontalalignment='center', verticalalignment='center',
#         transform = ax.transAxes)

show() 
