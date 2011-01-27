def make_axes(parent, **kw):
    orientation = kw.setdefault('orientation', 'vertical')
    fraction = kw.pop('fraction', 0.15)
    shrink = kw.pop('shrink', 1.0)
    aspect = kw.pop('aspect', 20)
    pb = parent.get_position(original=True).frozen()
    if orientation == 'vertical':
        location = kw.pop('location', 1)
        pad = kw.pop('pad', 0.05)
        if location:
            x1 = 1.0-fraction
            pb1, pbx, pbcb = pb.splitx(x1-pad, x1)
            pbcb = pbcb.shrunk(1.0, shrink).anchored('C', pbcb)
            anchor = (0.0, 0.5)
            panchor = (1.0, 0.5)
        else:
            pbcb, pbx, pb1 = pb.splitx(fraction, fraction+pad)
            pbcb = pbcb.shrunk(1.0, shrink).anchored('C', pbcb)
            anchor = (1.0, 0.5)
            panchor = (0.0, 0.5)
    else:
        location = kw.pop('location', 0)
        pad = kw.pop('pad', 0.15)
        if location:
            y1 = 1.0-fraction
            pb1, pbx, pbcb = pb.splity(y1-pad, y1)
            pbcb = pbcb.shrunk(shrink, 1.0).anchored('C', pbcb)
            anchor = (0.5, 0.0)
            panchor = (0.5, 1.0)
        else:
            pbcb, pbx, pb1 = pb.splity(fraction, fraction+pad)
            pbcb = pbcb.shrunk(shrink, 1.0).anchored('C', pbcb)
            anchor = (0.5, 1.0)
            panchor = (0.5, 0.0)
        aspect = 1.0/aspect
    parent.set_position(pb1)
    parent.set_anchor(panchor)
    fig = parent.get_figure()
    cax = fig.add_axes(pbcb)
    cax.set_aspect(aspect, anchor=anchor, adjustable='box')
    return cax, kw

import numpy as np
import matplotlib.pyplot as plt

data = np.random.rand(50,50)

fig = plt.figure()

ax = fig.add_subplot(2, 2, 1)
im = ax.pcolor(data)
cax,kw = make_axes(ax, orientation='vertical', location=0.0)
fig.colorbar(im, ax=ax, cax=cax, **kw)
ax.set_title('Vertical, 0.0')

ax = fig.add_subplot(2, 2, 2)
im = ax.pcolor(data)
cax,kw = make_axes(ax, orientation='vertical', location=1.0)
fig.colorbar(im, ax=ax, cax=cax, **kw)
ax.set_title('Vertical, 1.0')

ax = fig.add_subplot(2, 2, 3)
im = ax.pcolor(data)
cax,kw = make_axes(ax, orientation='horizontal', location=0.0)
fig.colorbar(im, ax=ax, cax=cax, **kw)
ax.set_title('Horizontal, 0.0')

ax = fig.add_subplot(2, 2, 4)
im = ax.pcolor(data)
cax,kw = make_axes(ax, orientation='horizontal', location=1.0)
fig.colorbar(im, ax=ax, cax=cax, **kw)
ax.set_title('Horizontal, 1.0')

plt.show()
