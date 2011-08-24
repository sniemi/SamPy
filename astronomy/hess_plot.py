'''
This file contains a function that can be used to 
generate a Hess plot.
'''
import numpy as N

def hess_plot(xdata, ydata, weight,
              xmin, xmax, nxbins,
              ymin, ymax, nybins,
              pmax=1.0, pmin=0.1):
    '''
    This function can be used to calculate a hess plot
    i.e. the conditional probability 2D histogram.

    :param xdata: 1D NumPy array containing data in x dim.
    :param ydata: 1D NumPy array containing data in y dim.
    :param weight: 1D NumPy array containing weight for
                   each data point
    :param xmin: a minimum x value to be considered
    :param xmax: a maximum x value to be considered
    :param nxbins: the number of bins in x dim.
    :param nybins: the number of bins in y dim.
    :param pmax: 1.0
    :param pmin: 0.1

    :return: 2D array, min, max
    '''
    #xbins
    xbin = N.linspace(xmin, xmax, nxbins + 1)
    dx = xbin[1] - xbin[0]
    xmids = xbin[:-1] + dx / 2.
    #ybins
    ybin = N.linspace(ymin, ymax, nybins + 1)
    dy = ybin[1] - ybin[0]
    ymids = ybin[:-1] + dy / 2.

    yhist = N.zeros((nybins, nxbins))
    yhist_num = N.zeros((nybins, nxbins))

    #number of h in each xbin
    nh = N.zeros(nxbins)

    for i, x in enumerate(xbin[:-1]):
        xmask = (xdata >= x) & (xdata < x + dx)
        if len(xdata[xmask]) > 0:
            nh[i] = N.sum(weight[xmask])
            for j, y in enumerate(ybin[:-1]):
                ymask = (xdata >= x) & (xdata < x + dx) & (ydata >= y) & (ydata < y + dy)
                if len(ydata[ymask]) > 0:
                    yhist[j, i] = N.sum(weight[ymask])
                    yhist_num[j, i] = len(ydata[ymask])

    #conditional distributions in Mh bins                                                                        
    for i in range(nxbins):
        if nh[i] > 0.0:
            yhist[:, i] /= nh[i]

    s = N.log10(pmax) - N.log10(yhist)
    smax = N.log10(pmax) - N.log10(pmin)
    smin = N.log10(pmax)

    s[yhist <= 0.0] = 2.0 * smax
    s[yhist_num <= 1] = 2.0 * smax

    return s, smin, smax


def hess_plot_old(xdata, ydata, weight,
                  xmin, xmax, nxbins,
                  ymin, ymax, nybins,
                  pmax=1.0, pmin=0.1):
    '''
    :note: obsolete, do not use this version!
    '''
    dx = (xmax - xmin) / float(nxbins)
    mbin = xmin + (N.arange(nxbins)) * dx + dx / 2.

    dy = (ymax - ymin) / float(nybins)
    ybin = ymin + (N.arange(nybins)) * dy + dy / 2.

    yhist = N.zeros((nybins, nxbins))

    nogas = N.zeros(nxbins)

    yhist_num = N.zeros((nybins, nxbins))
    #number of h in each bin
    nh = N.zeros(nxbins)

    #this should be rewritten...                                                                                 
    for i in range(len(xdata)):
        imbin = int(N.floor((xdata[i] - xmin) / dx))
        if imbin >= 0 and imbin < nxbins:
            nh[imbin] = nh[imbin] + weight[i]
            iy = int(N.floor((ydata[i] - ymin) / dy))
            if iy >= 0 and iy < nybins:
                yhist[iy, imbin] = yhist[iy, imbin] + weight[i]
                yhist_num[iy, imbin] = yhist_num[iy, imbin] + 1

    #conditional distributions in Mh bins                                                                        
    for i in range(nxbins):
        if nh[i] > 0.0:
            yhist[:, i] /= nh[i]

    s = N.log10(pmax) - N.log10(yhist)
    smax = N.log10(pmax) - N.log10(pmin)
    smin = N.log10(pmax)

    s[yhist <= 0.0] = 2.0 * smax
    s[yhist_num <= 1] = 2.0 * smax

    return s, smin, smax

if __name__ == '__main__':
    '''
    This is just to test that the new Hess and old Hess
    function results agree
    '''
    import db.sqlite as sq
    import os
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero/'
    db = 'sams.db'

    bulge = 0.4;
    pmin = 0.05;
    pmax = 1.0
    xbin1 = 15;
    ybin1 = 15
    xbin2 = 15;
    ybin2 = 15
    xmin1 = 7.9;
    xmax1 = 11.7
    ymin = 0.1;
    ymax = 10

    query1 = '''select galprop.mstar, galprop.r_disk, Pow10(galprop.mbulge - galprop.mstar)
                from FIR, galprop where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                galprop.tmerge > 0.5 and
                FIR.spire250_obs > 1e-15 and
                FIR.spire250_obs < 1e6
                '''
    #get data
    data = N.array(sq.get_data_sqlitePowerTen(path, db, query1))
    #slice the data
    disks = data[:, 2] <= bulge
    xd1 = data[:, 0][disks]
    yd1 = data[:, 1][disks]
    #old algorithm
    so1, somin1, somax1 = hess_plot_old(xd1, yd1, N.ones(len(xd1)),
                                        xmin1, xmax1, xbin1,
                                        ymin, ymax, ybin1,
                                        pmax=pmax, pmin=pmin)

    #new algorithm
    sn1, snmin1, snmax1 = hess_plot(xd1, yd1, N.ones(len(xd1)),
                                    xmin1, xmax1, xbin1,
                                    ymin, ymax, ybin1,
                                    pmax=pmax, pmin=pmin)

    print somin1 == snmin1
    print
    print somax1 == snmax1
    print
    print sn1
    print
    print N.round(so1, 4) == N.round(sn1, 4)
    print
    print N.round(so1 - sn1, 4)

