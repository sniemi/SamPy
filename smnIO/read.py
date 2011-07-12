'''
Reading Data
============

This file contains some helper functions to
parse different data files.

:author : Sami-Matias Niemi
:contact : sniemi@unc.edu
:version : 0.1

:requires: NumPy
:requires: SamPy.astronomy.basics
:requires: SamPy.smnIO.sexutils
'''
import SamPy.smnIO.sextutils as su
import SamPy.astronomy.basics
import numpy as np
import cPickle

__author__ = 'Sami-Matias Niemi'

def readBolshoiDMfile(filename, column, no_phantoms):
    '''
    This little helper function can be used to read
    dark matter halo masses from files produced from
    the merger trees of the Bolshoi simulation.

    :param filename: name of the file
    :param column: which column to grep
    :param no_phantoms: which dark matter mass to read

    :type filename: string
    :type column: int
    :type no_phantoms: boolean

    :return: dark matter halo masses
    :rtype: NumPy array
    '''
    out = []
    fh = open(filename, 'r')
    line = fh.readline()
    while line:
        if no_phantoms:
            if int(float(line.split()[2])) == 0:
                out.append(float(line.split()[column]))
        else:
            out.append(float(line.split()[column]))
        line = fh.readline()
    return np.array(out)


def GFBasicData(path, AB=True):
    '''
    Reads Rachel's SAMs output data.
    If AB = True then the function converts
    Johnson U, B, V, and K bands to Vega system.

    :note: This is really ineffective way of reading in
           data and should be used only when a rather
           small simulation is being processed.

    :param path: path in which the files are located
    :param AB: whether Johnson U, B, V, and K bands are converted to Vega system or not.

    :type path: string
    :type AB: boolean

    '''
    AB = astronomy.basics.JohnsonToABmagnitudes()

    print 'Reading files from {0:>s}'.format(path)

    galfile = path + 'galphot.dat'
    galdustfile = path + 'galphotdust.dat'
    profile = path + 'galprop.dat'
    halofile = path + 'halos.dat'

    g = su.se_catalog(galfile)
    gdust = su.se_catalog(galdustfile)
    p = su.se_catalog(profile)
    h = su.se_catalog(halofile)

    print 'Found {0:d} haloes'.format(len(h))
    print 'Found {0:d} galaxies'.format(len(g))

    if AB:
        print 'Coverting Johnson U, B, V, and K bands to vega system'
        g.uj = g.uj - AB['AB_vega_U']
        g.bj = g.bj - AB['AB_vega_B']
        g.vj = g.vj - AB['AB_vega_V']
        g.k = g.k - AB['AB_vega_K']
        #bulge
        g.uj_bulge = g.uj_bulge - AB_vega_U
        g.bj_bulge = g.bj_bulge - AB_vega_B
        g.vj_bulge = g.vj_bulge - AB_vega_V
        g.k_bulge = g.k_bulge - AB_vega_K
        #dusty
        gdust.uj = gdust.uj - AB_vega_U
        gdust.bj = gdust.bj - AB_vega_B
        gdust.vj = gdust.vj - AB_vega_V
        gdust.j = gdust.k - AB_vega_K

    return g, gdust, p, h


def cPickledData(filename):
    '''
    Reads in cPickled data and returns it
    '''
    inp = open(filename)
    out = cPickle.load(inp)
    return out