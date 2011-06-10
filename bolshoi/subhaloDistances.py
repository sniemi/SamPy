'''
Find sub-halo galaxy distances from the main halo as a function of redshift, halo mass, etc.

:requires: astLib.astCoords
:requires: cosmocalc
:requires: NumPy

:author: Sami-Matias Niemi
:cotact: niemi@stsci.edu
'''
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
from cosmocalc import cosmocalc
import os
#From SamPy
import db.sqlite as sq
import smnIO.write as wr
import smnIO.read as read
import astronomy.datamanipulation as dm

__author__ = 'Sami-Matias Niemi'

def mkRedshiftPlot(x, y, outFolder):
    '''
    Generate a redshift plot
    '''
    aa = []
    bb = []

    fig = P.figure(figsize = (12, 12))
    ax = fig.add_subplot(121)
    for r, a in zip(x, y):
        if a.shape[0] > 0:
            tmp = [r for foo in range(len(a))]
            ax.scatter(tmp, a, s=1, c='b', marker='o')
            aa += tmp
            bb += a.tolist()
#        else:
#            print 'Odd...'
#            print r
#            print a

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
    P.savefig(outFolder + 'test.png')

def getDiameterDistances(data, redshift=0):
    out = {}
    for x in set(data[:, redshift]):
        out[x] = cosmocalc(x, 71.0, 0.28)['PS_kpc'] #in kpc / arc seconds
    return out

def findValues(data, group=3):
    '''
    Finds redshift and physical distance from raw data.
    Data are first grouped by group=3 column
    '''
    conversion = 0.000277777778 # degree to arcsecond

    ddist = getDiameterDistances(data)

    redshift = []
    pdist = []
    for x in set(data[:, group]):
        #find all galaxies
        tmp = data[data[:, group] == x]

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
        physical_distance = (sep / dd) / conversion

        #append the results
        redshift.append(z)
        pdist.append(physical_distance)

    dict = {'redshift' : redshift,
            'physical_distance' : pdist}

    return dict

def getAndProcessData(home, outfile='SubDists.pkl'):
    #constants
    path = home + '/Desktop/CANDELS/lightConeRuns/goodsn/'
    db = 'sams.db'

    #SQL query where all the magic happens
    query = '''select l1.redshift, l1.ra, l1.dec, l1.halo_id, l1.gal_id from lightcone l1
               inner join
               (
               select l2.halo_id, l2.gal_id from lightcone l2 where
               l2.halo_id in (select halo_id from lightcone group by halo_id having count(*) > 1)
               intersect
               select l3.halo_id, l3.gal_id from lightcone l3
               group by l3.halo_id, l3.gal_id having count(*) == 1
               )
               using (halo_id, gal_id)
               '''

    #pull out data
    data = sq.get_data_sqliteSMNfunctions(path, db, query)

    #group data
    grouped = findValues(data)

    #dump it to a picked file
    wr.cPickleDumpDictionary(grouped, outfile)

    return grouped

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    outFolder = hm + '/Dropbox/'

    # Pull out the information and process data
    #grouped = getAndProcessData(hm)
    # or read it from a pickled file
    grouped = read.cPickledData('SubDists.pkl')

    #make some plots
    mkRedshiftPlot(grouped['redshift'],
                   grouped['physical_distance'],
                   outFolder)