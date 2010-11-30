# solve Laplace's equation for 500x500 grid
# boundary conditions: 0 around edges, 100 for central 100x100 block
from numpy import *

thresh = .1
grid = zeros((500,500))
prevgrid = grid.copy()
grid[200:300,200:300] = 100
done = False
i = 0
while not done:
    i += 1
    prevgrid[:,:] = grid
    # next step is just average of 4 neighboring points
    grid[1:-1,1:-1] = 0.25*(
        grid[:-2,1:-1]
      + grid[2:,1:-1]
      + grid[1:-1,:-2]
      + grid[1:-1,2:])
    grid[200:300,200:300] = 100.
    diff = abs(grid - prevgrid)
    dmax = diff.max()
    print i, dmax
    if dmax < thresh: done = True        
        
 
