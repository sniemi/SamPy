
def transformation(x, y, theta1, lam0):
    from math import sin, cos, asin, atan, sqrt
    rho = sqrt(x**2. + y**2.)
    c = atan(rho)

    #rho == 0. ????
    if (rho == 0.):
        theta = 0.
        lam = 0.
    else:
        theta = asin((cos(c)*sin(theta1)) + (y*sin(c)*cos(theta1)/rho))
        lam = lam0 + atan((x*sin(c))/((rho*cos(theta1)*cos(c)) - (y*sin(theta1)*sin(c))))

    return theta, lam

#CHANGE THESE:
#starting coordinates:
x0 = 0.2
y0 = 0.
#end coordinates:
x1 = 0.0000001
y1 = 0.

import math
#central lattitude and longitude respectively:
theta2 = 30./180.*math.pi #30 degrees?
#theta1 = math.pi/2. #pole?
theta1 = 80./180.*math.pi #80 degrees
#theta1 = 0. #equator?

lam0 = 0.

#transformations
answ1 = transformation(x0,y0,theta1,lam0)
tr1 = transformation(x1,y1,theta1,lam0)
tr2 = transformation(x1,y1,theta2,lam0)
answ21 = answ1[0] - tr1[0]
answ22 = answ1[1] - tr1[1]

print "Teloffset/Slitoffset Test!\n"
print "Starting coordinates:"
print "x = %6.2f\ny = %6.2f" % (x0, y0)
#print "Corresponds to:\n"
#print "theta = %f\nlambda = %f" % (answ1[0], answ1[1])

print "\nMoving Telescope:\n"
print "delta(x) = %6.2f\ndelta(y) = %6.2f\n" % (x0-x1, y0-y1)
print "Corresponds to movement of:\n"
print "delta(DEC) = %f\ndelta(RA) = %f" % (answ21, answ22)

import numpy as N
import pylab as P

xchange = N.arange(-0.5,0.5,0.01) 
y = 0.

decx1 = []; rax1 = []; decy1 = []; ray1 = []
decx2 = []; rax2 = []; decy2 = []; ray2 = []

for x in xchange:
    decx1.append((transformation(x, y, theta1, lam0)[0] - tr1[0]))
    rax1.append((transformation(x, y, theta1, lam0)[1] - tr1[1]))
    decx2.append((transformation(x, y, theta2, lam0)[0] - tr2[0]))
    rax2.append((transformation(x, y, theta2, lam0)[1] - tr2[1]))

x = 0.
ychange = N.arange(-0.5,0.5,0.01)

for y in ychange:
    decy1.append((transformation(x, y, theta1, lam0)[0] - tr1[0]))
    ray1.append((transformation(x, y, theta1, lam0)[1] - tr1[1]))
    decy2.append((transformation(x, y, theta2, lam0)[0] - tr2[0]))
    ray2.append((transformation(x, y, theta2, lam0)[1] - tr2[1]))


ychange -= y1
xchange -= x1

P.subplot(211)
P.plot(xchange, rax1,'b-.', label='RA, 80deg')
P.plot(xchange, decx1,'r-', label='DEC, 80deg')
P.plot(xchange, rax2, 'g--', label='RA, 30deg')
P.plot(xchange, decx2,'y.', label='DEC, 30deg')
P.xlabel("x Movement")
P.ylabel("Telescope Movement (in arbitrary units)")
P.legend()

P.subplot(212)
P.plot(ychange, ray1, 'b-.', label='RA, 80deg')
P.plot(ychange, decy1, 'r-', label='DEC, 80deg')
P.plot(ychange, ray2, 'g--', label='RA, 30deg')
P.plot(ychange, decy2, 'y.', label='DEC, 30deg')
P.xlabel("y Movement")
P.ylabel("Telescope Movememnt (in arbitrary units)")

P.legend()
P.show()




#from coords to x,y
#lattitude
#theta = 80
#longitude
#lam = 80
#central longitude
#lam0 = 0
#central lattitude
#theta1  = 0
#c = (sin(theta1)*sin(theta)+(cos(theta1)*cos(theta)*cos(lam-lam0)))
#x = (cos(theta)*sin(lam-lam0) / (cos(c)))
#y = ((cos(theta1)*sin(theta)) - (sin(theta1)*cos(theta)*cos(lam - lam0))) / (cos(c))
#print
#print "x = %f\ny = %f" % (x,y)
#print
