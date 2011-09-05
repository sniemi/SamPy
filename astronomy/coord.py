"""
Provides matching for a list of RAs and DECs.

:requires: astLib.astCoords
:requires: NumPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import math
import numpy as np
from numpy.core.records import fromarrays
import astLib.astCoords as astCoords

def match(ra1, dec1, ra2, dec2, tol, allmatches=False):
    """
    Given two sets of numpy arrays of ra,dec and a tolerance tol
    (float), returns an array of integers with the same length as the
    first input array.  If integer > 0, it is the index of the closest
    matching second array element within tol arcsec.  If -1, then there
    was no matching ra/dec within tol arcsec.

    if allmatches = True, then for each object in the first array,
    return the index of everything in the second arrays within the
    search tolerance, not just the closest match.

    :note: does not force one-to-one mapping

    Note to get the indices of objects in ra2, dec2 without a match:
    imatch = match(ra1, dec1, ra2, dec2, 2.)
    inomatch = numpy.setdiff1d(np.arange(len(ra2)), set(imatch))
    """
    DEG_PER_HR = 360. / 24.             # degrees per hour
    DEG_PER_MIN = DEG_PER_HR / 60.      # degrees per min
    DEG_PER_S = DEG_PER_MIN / 60.       # degrees per sec
    DEG_PER_AMIN = 1. / 60.             # degrees per arcmin
    DEG_PER_ASEC = DEG_PER_AMIN / 60.   # degrees per arcsec
    RAD_PER_DEG = math.pi / 180.        # radians per degree
    
    isorted = ra2.argsort()
    sdec2 = dec2[isorted]
    sra2 = ra2[isorted]

    LIM = tol * DEG_PER_ASEC

    match = []

    #this is faster but less accurate
    # use mean dec, assumes decs similar
    #decav = np.mean(sdec2.mean() + dec1.mean())
    #RA_LIM = LIM / np.cos(decav * RAD_PER_DEG)

    for ra, dec in zip(ra1, dec1):
        #slower but more accurate
        RA_LIM = LIM / np.cos(dec * RAD_PER_DEG)

        i1 = sra2.searchsorted(ra - RA_LIM)
        i2 = i1 + sra2[i1:].searchsorted(ra + RA_LIM)
        close = []
        for j in xrange(i1, i2):
            decdist = np.abs(dec - sdec2[j])
            if decdist > LIM:
                continue
            else:
                # if ras and decs are within LIM, then
                # calculate actual separation
                disq = astCoords.calcAngSepDeg(ra, dec, sra2[j], sdec2[j])
                close.append((disq, j))

        close.sort()
        if not allmatches:
            # Choose the object with the closest separation inside the
            # requested tolerance, if one was found.
            if len(close) > 0:
                min_dist, jmin = close[0]
                if min_dist < LIM:
                    match.append((isorted[jmin], min_dist))
                    continue
                    # otherwise no match
            match.append((-1, -1))
        else:
            # append all the matching objects
            jclose = []
            seps = []
            for dist, j in close:
                if dist < LIM:
                    jclose.append(j)
                    seps.append(dist)
                else:
                    break
            match.append(fromarrays([isorted[jclose], seps],
                                                           dtype=[('ind', 'i8'), ('sep', 'f8')]))

    if not allmatches:
        # return both indices and separations in a recarray
        temp = np.rec.fromrecords(match, names='ind,sep')
        # change to arcseconds
        temp.sep *= 3600.
        temp.sep[temp.sep < 0] = -1.
        return temp
    else:
        return match


def indmatch(ra1, dec1, ra2, dec2, tol, one=True):
    """
    Finds objects in ra1, dec1 that have a matching object in ra2,dec2
    within tol arcsec.

    Returns i1, i2 where i1 are indices into ra1,dec1 that have
    matches, and i2 are the indices into ra2, dec2 giving the matching
    objects.

    :param: one, whether one-to-one mapping should be done
    """
    m = match(ra1, dec1, ra2, dec2, tol)
    c = m.ind > -1
    i1 = c.nonzero()[0]
    i2 = m.ind[c]
    if one:
        dl = 0
        # :todo: this is horribly written, shuold do better
        for x in i2:
            tmp = np.where(i2 == x)[0]
            if len(tmp) > 1:
                #found a duplicate
                keeps = i1[tmp]
                rm = i2[tmp][0]
                dists = astCoords.calcAngSepDeg(ra2[rm], dec2[rm],
                                                ra1[keeps], dec1[keeps])
                smaller = np.argmin(dists)
                delete = tmp[tmp != tmp[smaller]]
                i1 = np.delete(i1, delete)
                i2 = np.delete(i2, delete)
                dl += len(delete)
        print 'removed %i double matches, left the closest match' % dl

    return i1, i2


def unique_radec(ra, dec, tol):
    """
    Find unique ras and decs in a list of coordinates.

    RA and Dec must be array sof the same length, and in degrees.

    tol is the tolerance for matching in arcsec. Any coord separated by
    less that this amount are assumed to be the same.

    Returns two arrays.  The first is an array of indices giving the
    first occurence of a unique coordinate in the input list.  The
    second is a list giving the indices of all coords that were
    matched to a given unique coord.

    The matching algorithm is confusing, but hopefully correct and not too
    slow. Potential for improvement...
    """
    matches = match(ra, dec, ra, dec, tol, allmatches=True)
    imatchflat = []
    for m in matches:
        imatchflat.extend(m.ind)
        #pdb.set_trace()
    inomatch = np.setdiff1d(np.arange(len(ra)), list(set(imatchflat)))

    assert len(inomatch) == 0
    # Indices giving unique ra, decs
    iunique = []
    # Will be same length as iunique. Gives all indices in original
    # coords that are matched to each unique coord.
    iextras = []
    assigned = set()
    for j, m in enumerate(matches):
        if not (j % 1000):
            print j
            # get the lowest index in this group
        isort = sorted(m.ind)
        ilow = isort[0]
        if ilow not in assigned:
            iunique.append(ilow)
            assigned.add(ilow)
            iextras.append([ilow])
            # assign any extra indices to this unique coord.
            for i in isort[1:]:
                # check not already been assigned to another coord
                if i not in assigned:
                    iextras[-1].append(i)
                    assigned.add(i)

    return np.array(iunique), iextras

