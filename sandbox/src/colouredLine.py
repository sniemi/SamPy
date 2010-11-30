import numpy as N
import matplotlib.pyplot as P
from matplotlib.collections import LineCollection

x = N.arange(10)
y = N.arange(10)*0.1234 + 2

points = N.array([x, y]).T.reshape(-1, 1, 2)
segments = N.concatenate([points[:-1], points[1:]], axis=1)

fig = P.figure(1)

ax = P.axes()
ax.set_xlim(N.min(x), N.max(x))
ax.set_ylim(N.min(y),N.max(y))

lc = LineCollection(segments, cmap = P.get_cmap('jet'), norm = P.Normalize(x.min(), x.max()))
lc.set_array(x)
lc.set_linewidth(5)

ax.add_collection(lc)

axcb = fig.colorbar(lc)
axcb.set_label('Counts')
ax.set_title('Line Collection with mapped colors')

#P.sci(lc) # This allows interactive changing of the colormap.

P.show()
