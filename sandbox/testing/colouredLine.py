import numpy as N
import matplotlib.pyplot as P
from matplotlib.collections import LineCollection
#from matplotlib.colors import ListedColormap, BoundaryNorm

x = N.arange(10)
y = N.arange(10)*0.1234 + 2

points = N.array([x, y]).T.reshape(-1, 1, 2)
segments = N.concatenate([points[:-1], points[1:]], axis=1)

print points
print segments

#cmap = ListedColormap(['r', 'g', 'b'])
#norm = BoundaryNorm([-1, -0.5, 0.5, 1], cmap.N)

P.scatter(x, y, c = x, s = 0)

lc = LineCollection(segments, cmap = P.get_cmap('jet'), norm = P.Normalize(x.min(), x.max()))
lc.set_array(x)
lc.set_linewidth(3)
P.gca().add_collection(lc)

P.xlim(x.min(), x.max())

P.draw()

P.show()
