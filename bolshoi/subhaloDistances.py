"""
Find subhalo galaxy distances from the main halo as a function of redshift, halo mass, etc.

:requires: astLib.astCoords
:requires: cosmocalc
:requires: NumPy

:author: Sami-Matias Niemi
:cotact: niemi@stsci.edu
"""
import matplotlib

matplotlib.use('Agg')
matplotlib.rc('text', usetex=True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('axes', linewidth=1.1)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 3
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import pylab as P
import numpy as N
import astLib.astCoords as Coords
import os
import db.sqlite as sq
import smnIO.write as wr
import astronomy.datamanipulation as dm
import cosmology.distances as dist

def mkRedshiftPlot(x, y, outFolder):
    """
    Generate a redshift plot
    """
    aa = []
    bb = []

    fig = P.figure(figsize=(12, 12))
    ax = fig.add_subplot(111)
    for r, a in zip(x, y):
        if a.shape[0] > 0:
            tmp = [r for foo in range(len(a))]
            ax.scatter(tmp, a, s=2, c='b', marker='o')
            aa += tmp
            bb += a.tolist()

    #percentiles
    xbin_midd, y50d, y16d, y84d = dm.percentile_bins(N.array(aa),
                                                     N.array(bb),
                                                     0,
                                                     9.5)
    md = (y50d > 0) & (y16d > 0) & (y84d > 0)
    ax.plot(xbin_midd[md], y50d[md], 'r-')
    ax.plot(xbin_midd[md], y16d[md], 'r--')
    ax.plot(xbin_midd[md], y84d[md], 'r--')

    ax.set_xlabel('Redshift')
    ax.set_ylabel('Projected Distance [kpc]')

    #ax.set_xlim(0, 1.01)
    ax.set_ylim(0, 1e2)

    P.savefig(outFolder + 'test.png')
    P.close()


def mkMassPlot(x, y, outFolder):
    """
    Generate a mass plot
    """
    aa = []
    bb = []

    fig = P.figure(figsize=(12, 12))
    ax = fig.add_subplot(111)
    for r, a in zip(x, y):
        if a.shape[0] > 0:
            if len(a[a > 2e3]) < 1:
                tmp = [r for foo in range(len(a))]
                ax.scatter(tmp, a, s=2, c='b', marker='o')
                aa += tmp
                bb += a.tolist()

    #percentiles
    xbin_midd, y50d, y16d, y84d = dm.percentile_bins(N.array(aa),
                                                     N.array(bb),
                                                     9.0,
                                                     11.5,
                                                     nxbins=10)
    md = (y50d > 0) & (y16d > 0) & (y84d > 0)
    ax.plot(xbin_midd[md], y50d[md], 'r-')
    ax.plot(xbin_midd[md], y16d[md], 'r--')
    ax.plot(xbin_midd[md], y84d[md], 'r--')

    ax.set_xlabel(r'$\log_{10} ( M_{\mathrm{dm}} \ [M_{\odot}] )$')
    ax.set_ylabel('Projected Distance [kpc]')

    #ax.set_xlim(9, 12)
    ax.set_ylim(0, 1e2)

    P.savefig(outFolder + 'test2.png')


def findValues(data, group=3):
    """
    Finds redshift and physical distance from raw data.
    Data are first grouped by group=3 column
    """
    conversion = 0.000277777778 # degree to arcsecond

    ddist = dist.getDiameterDistances(data)

    redshift = []
    pdist = []
    mhalo = []
    for x in set(data[:, group]):
        #find all galaxies
        tmp = data[data[:, group] == x]

        if len(tmp) > 1:
            #redshift
            z = tmp[0][0]

            #look the diameter distance from the lookup table
            dd = ddist[z]

            #the first halo, assume it to be the main halo
            RADeg1 = tmp[0][1]
            decDeg1 = tmp[0][2]
            #the following haloes, assume to be subhaloes
            RADeg2 = tmp[1:, 1]
            decDeg2 = tmp[1:, 2]

            #calculate the angular separation on the sky
            sep = Coords.calcAngSepDeg(RADeg1, decDeg1, RADeg2, decDeg2)

            #convert to physical distance on that redshift
            physical_distance = sep * dd / conversion

            #append the results
            redshift.append(z)
            pdist.append(physical_distance)
            mhalo.append(tmp[0][5])

    dict = {'redshift': redshift,
            'physical_distance': pdist,
            'mhalo': mhalo}

    return dict


def getAndProcessData(home, outfile='SubDists2.pkl'):
#constants
#    path = home + '/Desktop/CANDELS/lightConeRuns/goodsn/'
    path = home + '/Research/CANDELS/goodsn/'
    db = 'sams.db'

    #SQL query where all the magic happens
    query = """select l1.redshift, l1.ra, l1.dec, l1.halo_id, l1.gal_id, l1.mhalo from testing l1
               inner join
               (
               select l2.halo_id, l2.gal_id from testing l2 where
               l2.halo_id in (select halo_id from testing group by halo_id having count(*) > 1)
               intersect
               select l3.halo_id, l3.gal_id from testing l3
               group by l3.halo_id, l3.gal_id having count(*) == 1
               )
               using (halo_id, gal_id) where
               l1.redshift > 0.1 and
               l1.redshift < 6.0
               """

    #pull out data
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    #wr.cPickleDumpDictionary(data, 'data.pkl')

    #group data
    grouped = findValues(data)

    #dump it to a picked file
    wr.cPickleDumpDictionary(grouped, outfile)

    return grouped


def quickTest(home):
    from cosmocalc import cosmocalc

    path = home + '/Research/CANDELS/goodsn/'
    db = 'sams.db'

    #id = 1278065
    #id = 1372770
    id = 1369900

    #pull out data
    data = sq.get_data_sqliteSMNfunctions(path, db, 'select redshift, ra, dec from lightcone where halo_id = %i' % id)

    #redshift
    z = data[0][0]

    #look the diameter distance from the lookup table
    dd = cosmocalc(z, 71.0, 0.28)['PS_kpc']

    #the first halo, assume it to be the main halo
    RADeg1 = data[0][1]
    decDeg1 = data[0][2]
    #the following haloes, assume to be subhaloes
    RADeg2 = data[1:, 1]
    decDeg2 = data[1:, 2]

    print dd

    #calculate the angular separation on the sky
    sep = Coords.calcAngSepDeg(RADeg1, decDeg1, RADeg2, decDeg2)

    conversion = 0.000277777778 # degree to arcsecond

    print (sep / conversion)

    physical_distance = sep * dd / conversion

    print physical_distance

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    outFolder = hm + '/Dropbox/Research/CANDELS/'

    # Pull out the information and process data
    #grouped = getAndProcessData(hm)
    # or read it from a pickled file
    #grouped = read.cPickledData(hm + '/Dropbox/Research/CANDELS/SubDists2.pkl')

    #make some plots
    #mkRedshiftPlot(grouped['redshift'],
    #               grouped['physical_distance'],
    #               outFolder)
    #    mkMassPlot(grouped['mhalo'],
    #               grouped['physical_distance'],
    #               outFolder)

    quickTest(hm)