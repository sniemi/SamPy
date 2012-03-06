"""
Find subhalo galaxy distances from the main halo as a function of redshift, halo mass, etc.

:Warning: All functions are rather poorly written as I was in a hurry.
          One should improve them before using. One could remove several
          loops and do many things with table joins which are now separate loops.

:requires: astLib.astCoords
:requires: cosmocalc
:requires: NumPy

:author: Sami-Matias Niemi
:cotact: sammy@sammyniemi.com
"""
import matplotlib
matplotlib.use('PDF')
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
import SamPy.db.sqlite as sq
import SamPy.smnIO.write as wr
import SamPy.smnIO.read as read
import SamPy.astronomy.datamanipulation as dm
import SamPy.cosmology.distances as dist
from cosmocalc import cosmocalc
from time import time


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
    """
    Retrieve data
    """
    path = home + '/Research/CANDELS/v2s/'
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


def quickTest():
    path = os.getenv('HOME') + '/Research/CANDELS/v2/'
    db = 'goodsn.db'

    #id = 1851653
    id = 2178429
    #id = 1369900

    #pull out data
    data = sq.get_data_sqliteSMNfunctions(path,
                                          db,
                                          'select redshift, ra, dec from lightcone where halo_id = {0:d}'.format(id))

    #redshift
    z = data[0][0]
    print set(data[:, 0])

    #look the diameter distance from the lookup table
    dd = cosmocalc(z, 71.0, 0.28)['PS_kpc']
    print 'Scale 1\"=', dd, 'kpc'

    #the first halo, assume it to be the main halo
    RADeg1 = data[0][1]
    decDeg1 = data[0][2]
    #the following haloes, assume to be subhaloes
    RADeg2 = data[1:, 1]
    decDeg2 = data[1:, 2]

    #calculate the angular separation on the sky
    sep = Coords.calcAngSepDeg(RADeg1, decDeg1, RADeg2, decDeg2)

    conversion = 0.000277777778 # degree to arcsecond

    print (sep / conversion)

    physical_distance = sep * dd / conversion

    print physical_distance


def getDataSlow():
    path = os.getenv('HOME') + '/Research/CANDELS/v2/'
    db = 'goodsn.db'
    conversion = 0.000277777778 # degree to arcsecond

    redshifts = ['redshift < 0.5 and',
                 'redshift >= 0.5 and redshift < 1.0 and',
                 'redshift >= 1.0 and redshift < 2.0 and',
                 'redshift >= 2.0 and redshift < 3.0 and',
                 'redshift >= 3.0 and redshift < 4.0 and',
                 'redshift >= 4.0 and redshift < 5.0 and',
                 'redshift >= 5.0 and redshift < 6.0 and',
                 'redshift >= 6.0 and redshift < 7.0 and']

    for i, red in enumerate(redshifts):
        print red
        #pull out data
        ids = sq.get_data_sqliteSMNfunctions(path, db, 'select halo_id from lcone where %s gal_id > 1 limit 10000' % red)

        saveid = []
        saveorig = []
        savedist = []

        #we should now look for each unique id
        for id in N.unique(ids):
            query = 'select l.redshift, l.ra, l.dec, t.halo_id from lcone l, tmp t where l.halo_id = {0:d} and t.id = l.id'.format(id)
            #print query
            data = sq.get_data_sqliteSMNfunctions(path, db, query)

            #if multiples, then don't take it
            if len(set(data[:, 0])) > 1:
                print 'skipping', id
                continue

            #redshift
            z = data[0, 0]

            #look the diameter distance from the lookup table
            dd = cosmocalc(z, 71.0, 0.28)['PS_kpc']

            #the first halo, assume it to be the main halo
            RADeg1 = data[0, 1]
            decDeg1 = data[0, 2]
            #the following haloes, assume to be subhaloes
            RADeg2 = data[1:, 1]
            decDeg2 = data[1:, 2]

            #calculate the angular separation on the sky
            sep = Coords.calcAngSepDeg(RADeg1, decDeg1, RADeg2, decDeg2)

            physical_distance = sep * dd / conversion

            saveid.append(int(data[0, 3]))
            savedist.append(physical_distance)
            saveorig.append(id)

        out = dict(halo_ids=saveid, distances=savedist, original=saveorig)
        wr.cPickleDumpDictionary(out, 'distances%i.pickle' % (i+1))


def plotDistribution():
    """
    Simple histogram
    """
    data = read.cPickledData('distances.pickle')
    
    distances = []
    for line in data['distances']:
        for value in line:
            distances.append(value)

    fig = P.figure()
    ax = P.subplot(111)
    ax.hist(distances, bins=20)
    ax.set_xlabel('Projected Distances of Subhalo Galaxies [kpc]')
    P.savefig('Distances.pdf')


def plotDistributionRedshift():
    """
    Projected separation as a function of redshift bin
    """
    fig = P.figure()

    redshifts = ['redshift < 0.5 and',
                 'redshift >= 0.5 and redshift < 1.0 and',
                 'redshift >= 1.0 and redshift < 2.0 and',
                 'redshift >= 2.0 and redshift < 3.0 and',
                 'redshift >= 3.0 and redshift < 4.0 and',
                 'redshift >= 4.0 and redshift < 5.0 and',
                 'redshift >= 5.0 and redshift < 6.0 and']

    for i, red in enumerate(redshifts):

        data = read.cPickledData('distances%i.pickle' % i)

        distances = []
        for line in data['distances']:
            for value in line:
                distances.append(value)

        ax = P.subplot(3, 2, i+1)
        ax.hist(distances, bins=20)
        ax.set_xlabel('Projected Distances of Subhalo Galaxies [kpc]')
    P.savefig('DistancesRedshift.pdf')


def findValues():
    data = read.cPickledData('distances.pickle')

    path = os.getenv('HOME') + '/Research/CANDELS/v2/'
    db = 'goodsn.db'

    mhalo = []
    redshift = []
    for id in data['halo_ids']:
        m = sq.get_data_sqliteSMNfunctions(path, db, 'select mhalo from galprop where halo_id = %i' % id)
        z = sq.get_data_sqliteSMNfunctions(path, db, 'select z from galphot where halo_id = %i' %  id)
        mhalo.append(m)
        redshift.append(z)

    data['mhalo'] = mhalo
    data['z'] = redshift

    wr.cPickleDumpDictionary(out, 'values.pickle')




if __name__ == '__main__':
    start = time()

    getDataSlow()
    plotDistributionRedshift()
    #findValues()

    elapsed = time() - start
    print 'Processing took {0:.1f} minutes'.format(elapsed / 60.)

