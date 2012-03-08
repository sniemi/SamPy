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
import numpy as np
import astLib.astCoords as Coords
import os
import SamPy.db.sqlite as sq
import SamPy.smnIO.write as wr
import SamPy.smnIO.read as read
import SamPy.astronomy.datamanipulation as dm
import SamPy.cosmology.distances as dist
import SamPy.astronomy.conversions as conv
from cosmocalc import cosmocalc
from time import time
from matplotlib import cm
import mpl_toolkits.axes_grid.inset_locator as inset_locator


def _findValues(data, group=3):
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


def _getAndProcessData(home, outfile='SubDists2.pkl'):
    """
    Retrieve data.
    """
    path = home + '/Research/CANDELS/v2s/'
    db = 'sams.db'

    #SQL query where all the magic happens.. or doesn't
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

    #group data
    grouped = _findValues(data)

    #dump it to a picked file
    wr.cPickleDumpDictionary(grouped, outfile)

    return grouped


def quickTest(id=1242422, output='SingleHalo.pdf',
              db='database.db', path='Users/sammy/Research/CANDELS/v2/'):
    """
    A single halo test.

    :param id: halo_id of the testable dark matter halo
    :type id: int
    :param output: name of the output file
    :type output: string
    :param db: name of the SQLite database file
    :type db: string
    :param path: full path of the database file
    :type path: string

    :return: None
    """
    #pull out data
    query = 'select redshift, ra, dec, mhalo, rhalo from lcone where halo_id = {0:d}'.format(id)
    data = sq.get_data_sqliteSMNfunctions(path, db, query)

    #redshift
    z = data[0, 0]

    #calculate the separations
    inp = dict(RA1=data[0, 1], DEC1=data[0, 2], RA2=data[1:, 1], DEC2=data[1:, 2])
    result = conv.physicalSeparation(inp, z)
    print result

    #make a plot
    text = r'halo\_id=%i, z=%.3f, mass=%.2f, scale=%.3f' % (id, z, data[0,3], result['scale'])

    P.figure(figsize=(12,12))
    ax1 = P.subplot(221)
    ax2 = P.subplot(222)
    ax3 = P.subplot(223)
    ax4 = P.subplot(224)

    ax1.hist(result['distance']/(1e3*data[0, 4]), bins=12)
    ax2.hist(result['distance'], bins=12)

    RAs, DECs = (inp['RA2']-inp['RA1'])*1e4, (inp['DEC2']-inp['DEC1'])*1e4
    ax3.scatter(RAs, DECs, c='b', s=100, marker='o', alpha=0.45)
    ax3.scatter(0, 0, c='k', s=120, marker='s')

    s4 = ax4.scatter(RAs, DECs, c=data[1:, 3], s=80,
                     marker='o', alpha=0.6, cmap=cm.get_cmap('jet'), vmin=9.5, vmax=11.0)
    ax4.scatter(0, 0, c='k', s=120, marker='s')

    inset_axes = inset_locator.inset_axes(ax4, width='80%', height='1.5%', loc=9)
    c = P.colorbar(s4, cax=inset_axes, orientation='horizontal')
    c.set_label(r'$\log_{10} \left( M_{dm} [\mathrm{M}_{\odot}] \right )$', fontsize=13)
    for j in c.ax.get_xticklabels():
        j.set_fontsize(12)

    ax1.set_xlabel(r'Projected Distance / Radius of the Main Halo')
    ax2.set_xlabel(r'Projected Distance [kpc]')
    ax3.set_xlabel(r'$\Delta$RA [$10^{-4}$ deg]')
    ax4.set_xlabel(r'$\Delta$RA [$10^{-4}$ deg]')
    ax3.set_ylabel(r'$\Delta$DEC [$10^{-4}$ deg]')

    P.annotate(text,
        (0.5, 0.95), xycoords='figure fraction',
        ha='center', va='center', fontsize=12)

    P.savefig(output)


def getDataSlow(db='database.db', path='Users/sammy/Research/CANDELS/v2/'):
    """
    Get data from the lcone table in db.

    :param db: name of the SQLite database file.
    :type db: string
    :param path: full path of the database file
    :type path: string

    :Warning: This is extremely slow way to pull out data from a database.
              Should be rewritten using table joins etc. so that less queries
              could be performed.

    :return: redshift, halo mass and radius, projected distances of subhalo galaxies [kpc],
             halo_id of the main halo
    :rtype: dict
    """

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
        qr = 'select halo_id from lcone where %s gal_id > 1' % red
        #qr = 'select halo_id from lcone where %s mhalo > 12.7' % red
        #pull out data
        ids = sq.get_data_sqliteSMNfunctions(path, db, qr)

        uids = np.unique(ids)
        print len(uids), 'haloes'

        saveid = []
        saveorig = []
        savedist = []
        savemhalo = []
        saverhalo = []
        saveredshift = []

        #we should now look for each unique id
        for id in uids:
            query = 'select redshift, ra, dec, halo_id, mhalo, rhalo from lcone where halo_id = {0:d}'.format(id)
            #print query
            data = sq.get_data_sqliteSMNfunctions(path, db, query)

            #if multiples, then don't take it
            if len(set(data[:, 0])) > 1:
                print 'skipping', id
                continue
            if len(data[:, 1]) < 2:
                print 'no subhaloes', id, data[:, 1]
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

            #these are all the main halo parameters
            saveredshift.append(z)
            saveid.append(int(data[0, 3]))
            savemhalo.append(data[0, 4])
            saverhalo.append(data[0, 5])

            savedist.append(physical_distance)
            saveorig.append(id)

        out = dict(halo_ids=saveid, distances=savedist, original=saveorig,
                   mhalo=savemhalo, rhalo=saverhalo, redshift=saveredshift)

        wr.cPickleDumpDictionary(out, 'distances%i.pickle' % (i+1))


def plotDistributionRedshift(output='DistancesRedshift.pdf', normalize=True, average=False):
    """
    Projected separation as a function of redshift bin.

    :param output: name of the output file
    :type output: string
    :param normalize: whether to normalize the projected distance with the size of the main halo
    :type normalize: bool
    :param average: whether to take the average of the subhalo distances or not
    :type average: bool

    :return: None
    """
    #title = r'$\log_{10} \left( M_{dm} [\mathrm{M}_{\odot}]  \right) > 12.7$'
    title = 'No Halo Mass Limit'

    fig = P.figure()

    redshifts = ['redshift < 0.5 and',
                 'redshift >= 0.5 and redshift < 1.0 and',
                 'redshift >= 1.0 and redshift < 2.0 and',
                 'redshift >= 2.0 and redshift < 3.0 and',
                 'redshift >= 3.0 and redshift < 4.0 and',
                 'redshift >= 4.0 and redshift < 5.0 and',
                 'redshift >= 5.0 and redshift < 6.0 and',
                 'redshift >= 6.0 and redshift < 7.0 and']

    for i, red in enumerate(redshifts):
        #read the pickled data in
        data = read.cPickledData('distances%i.pickle' % (i+1))

        #collect distance information and normalize and average if needed
        distances = []
        for dists, rhalo in zip(data['distances'], data['rhalo']):
            tmp = []
            for value in dists:
                if normalize:
                    tmp.append(value/(1e3*rhalo))
                else:
                    tmp.append(value)
            if average:
                distances.append(np.mean(np.asarray(tmp)))
            else:
                distances += tmp

        ax = P.subplot(4, 2, i+1)

        #write the redshift of the subplot
        tmp = red.split()
        if i > 0:
            txt = r'$' + tmp[2] + ' \leq z < ' + tmp[6] +'$'
        else:
            txt = r'$z < 0.5$'
        ax.text(0.5, 0.9, txt, ha='center', va='center', fontsize=12, transform=ax.transAxes)

        #plot histogram if enough data
        if len(distances) > 1:
            ax.hist(distances, bins=20)

    #add one x-label
    P.annotate('Projected Distances / Virial Radius of the Main Halo',
               (0.5, 0.03), xycoords='figure fraction',
               ha='center', va='center', fontsize=12)

    #write title and save figure
    P.annotate(title, (0.5, 0.95), xycoords='figure fraction', ha='center', va='center', fontsize=12)
    P.savefig(output)


if __name__ == '__main__':
    start = time()

    quickTest(id=1334)
    #getDataSlow()
    #plotDistributionRedshift()

    elapsed = time() - start
    print 'Processing took {0:.1f} minutes'.format(elapsed / 60.)

