from numpy import *
x = array([1.1, 1.8, 7.3, 3.4])
y = array([2.3, 9.3, 1.5, 5.7])

deltax = x - reshape(x, len(x),1)
deltay = y - reshape(y, (len(y),1))
print deltax

dist = sqrt(deltax**2 + deltay**2)
dist = dist + identity(len(x))*dist.max() # eliminate self matching
print dist

print argmin(dist) # prints closest point corresponding to each coord.


