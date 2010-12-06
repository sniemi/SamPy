'''
@todo: rewrite this, it's not very well done...
'''
import numpy as N

def hess_plot(xdata, ydata, weight, 
              xmin, xmax, nxbins, 
              ymin, ymax, nybins,
              pmax = 1.0, pmin = 0.1):

    #x = stellar mass
    #y = gas fraction 
    dx = (xmax - xmin) / float(nxbins)
    mbin = xmin + (N.arange(nxbins))*dx + dx/2.

    dy = (ymax - ymin) / float(nybins)
    ybin = ymin + (N.arange(nybins))*dy + dy/2.

    yhist = N.zeros((nybins, nxbins))

    nogas = N.zeros(nxbins)

    yhist_num = N.zeros((nybins, nxbins))
    #number of h in each bin
    nh = N.zeros(nxbins)

    #compute gas fraction distribution in stellar mass bin
    #this should be rewritten...                                                                                 
    for i in range(len(xdata)):
        imbin = int(N.floor((xdata[i] - xmin)/dx))
        if imbin >= 0 and imbin < nxbins:
            nh[imbin] = nh[imbin]+ weight[i]
            iy = int(N.floor((ydata[i] - ymin)/dy))
            if iy >= 0 and iy < nybins:
                yhist[iy, imbin] = yhist[iy, imbin] + weight[i]
                yhist_num[iy, imbin] = yhist_num[iy, imbin] + 1
    
    #conditional distributions in Mh bins                                                                        
    for i in range(nxbins):
        if nh[i] > 0.0:
            yhist[:,i] /= nh[i]

    #s = N.log10(pmax) - N.log10(yhist)
    s = N.log10(pmax) - N.log10(yhist)
    smax = N.log10(pmax) - N.log10(pmin)
    smin = N.log10(pmax)

    s[yhist <= 0.0] = 2.0 * smax
    s[yhist_num <= 1] = 2.0 * smax

    return s, smin, smax
