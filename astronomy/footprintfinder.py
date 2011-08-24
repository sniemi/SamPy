#! /bin/env python

# This program finds the footprint of the illuminated of a fits image on the sky. This 
# footprint is a polygon in pixel (and WCS) coordinates for each chip.
#
# The input fits images images can 
#   - be composed of multiple chips
#   - be concave or convex
#   - have non-straight outlines
#   - have bad/masked pixels
#   - have holes
#   - holes with islands in them
# 
# There is one main free parameter to the code:
#   - -t/--tolerance specifies the maximum distance an illuminated pixel can have from the polygon 
#     footprint.
#
# Requirements: 
#   - pyfits
#   - pylab (included in matplotlib. matplotlib requires numpy)
#
# Author: Felix Stoehr, ST-ECF, 2008
#
# Summary of the algorithm used:
#   1) find pixels that are on the image border 
#   2) create a tree for fast searches and put the pixels from 1 in there (python dictionary)
#   3) find groups of pixels (i.e. to separate different chips)
#   4) for each group with more than a threshold number of pixels
#      5) select the starting corner (lower left corner)
#      6) get group pixels ordered clockwise by having "the right hand on the wall"
#      7) fit a polygon to the border pixels given a tolerance threshold using Douglas&Puecker
#      8) identify if one footprint is in an other
#      9) compute footprint heirarchy
#     10) write output file and convert the polygon pixel values to sky coordinates
#

# ----------------------------------------------------------------------------------------

def main(arguments):

# ----------------------------------------------------------------------------------------
    '''
       This is the main function doing the full loop.

       Note that pyfits reads y,x which is why all the plotting routines are using inverted coordinates.
       For the description of directions in the comments, we use this inverted notation (i.e. as plotted
       on the screen)
    '''
    import pylab, getopt, os

    zerovalue = 0
    minlength = 0.05
    tolerance = 5
    extension = None
    verbose = False
    plotting = False
    writepoints = False
    returnstring = False
    ds9 = False
    date = runtimestring()
    datestring = getdatetime()
    colorlist = ['green', 'red', 'yellow', 'blue', 'magenta', 'cyan']

    print "==================================================================================================="
    alert("\nFootprintfinder\n")
    alert("Copyright (C) Felix Stoehr, 2008 Space Telescope European Coordinating Facility\n")
    alert(date + "\n\n")

    try:
        opts, args = getopt.getopt(arguments.split(), "vpdwrt:z:m:e:h",
            ["verbose", "plotting", "ds9", "writepoints", "returnstring", "tolerance=", "zerovalue=", "minlength",
             "extension", "help"])
    except getopt.GetoptError:
        usage()
        error("ERROR: Could not understand the options!\n\n")
        print "================================================================================================"
        return

    for o, a in opts:
        if o in ("-v", "--verbose"):
            verbose = True
            alert(whocalls(verbose=verbose) + "Verbose ON" + "\n")
        if o in ("-p", "--plotting"):
            plotting = True
            alert(whocalls(verbose=verbose) + "Plotting ON" + "\n")
        if o in ("-z", "--zerovalue"):
            zerovalue = float(a)
            alert(whocalls(verbose=verbose) + "Zerovalue = %f " % zerovalue + "\n")
        if o in ("-t", "--tolerance"):
            tolerance = float(a)
            alert(whocalls(verbose=verbose) + "Tolerance = %f " % tolerance + "\n")
        if o in ("-m", "--minlength"):
            minlength = float(a)
            alert(whocalls(verbose=verbose) + "Minimal borderlength = %f " % minlength + "\n")
        if o in ("-e", "--extension"):
            extension = int(a)
            alert(whocalls(verbose=verbose) + "FITS file extension = %d " % extension + "\n")
        if o in ("-w", "--writepoints"):
            writepoints = True
            alert(whocalls(verbose=verbose) + "writepoints ON \n")
        if o in ("-r", "--returnstring"):
            returnstring = True
            alert(whocalls(verbose=verbose) + "Returnstring ON \n")
        if o in ("-d", "--ds9"):
            ds9 = True
            alert(whocalls(verbose=verbose) + "ds9 output ON \n")
        if o in ("-h", "--help"):
            usage()
            return 0

    if not len(args) == 1:
        usage()
        error("ERROR: No filename specified!\n\n")
        print "==================================================================================================="
        return

    filename = args[0]

    borderpixels, dimshape, wcs = directborder(filename, zerovalue, extension, verbose=verbose)

    while True:
        # This loop is necessary to allow for the rejection of too-small chips (i.e. 1 or 2 corners)
        # In that case, we will use the full chip. If there are only 1 or two pixels a border pixel
        # in the first place, then no non-zero footprint can be computed anyway.
        if len(borderpixels) < 3:
            warning(whocalls(
                verbose=verbose) + "WARNING: %d borderpixel(s) found! That is not enough. Using the whole chip.\n" % len(
                borderpixels))
            borderpixels = []
            # We do create the rectangle surrounding the whole chip here
            for i in range(dimshape[1]):
                borderpixels.append([0, i])
                borderpixels.append([dimshape[0] - 1, i])
            for i in range(1, dimshape[0] - 1):
                borderpixels.append([i, 0])
                borderpixels.append([i, dimshape[1] - 1])
            borderpixels = pylab.array(borderpixels)

        borderdictionary = getborderdictionary(borderpixels, verbose)

        if len(borderdictionary) != len(borderpixels):
            raise Exception('ERROR: Dictionary creation failed. Must stop here.')

        groups, grouplen, groupid, firstid, nextid = getgroups(borderpixels, borderdictionary, verbose)

        # Note: find gives a wrong result if grouplen is a list instead of a pylab array!
        chips = groups[pylab.find(pylab.array(grouplen) > (len(borderpixels) * minlength))]
        print whocalls(verbose=verbose) + "Found %d chips (out of %d groups)." % (len(chips), len(groups))

        footprintlist = []
        simplefootprintlist = []
        orderlist = []
        for chip in chips:
            print whocalls(verbose=verbose) + "Doing chip %d ...." % pylab.find(pylab.array(chips) == chip)[0]
            order = getpixelorder(chip, borderpixels, borderdictionary, groupid, grouplen, firstid, nextid, verbose)
            thistolerance = tolerance
            simplefootprint = simplifyDP(order, borderpixels, thistolerance)
            print whocalls(verbose=verbose) + "Footprint corners simplified:", len(simplefootprint) - 1

            if (len(simplefootprint) - 1) < 3:
                # In some cases, the footprint would be so small, that it has only 1 or 2 corners.
                # Although this might be real, it also could be that if a smaller tolerance value had
                # been chosen, the footprint would be a "real" one. If the number of corners therefore is
                # small, we force a small tolerance value.
                thistolerance = 0.5
                warning(whocalls(
                    verbose=verbose) + "WARNING: Too few corners in this chip. Trying with tolerance=%f\n" % thistolerance)
                simplefootprint = simplifyDP(order, borderpixels, thistolerance)
                warning(whocalls(verbose=verbose) + "WARNING: Footprint corners simplified: %d\n" % (
                    len(simplefootprint) - 1))

            # Now, if even this does not work, do not use this chip at all.
            if (len(simplefootprint) - 1) > 2:
                simplefootprintlist.append(simplefootprint)
            else:
                warning(whocalls(verbose=verbose) + "WARNING: Still too few corners! This footprint will be skipped.\n")

        # In the very rare case, where NO chip is retained because ALL were skipped, we will use the full chip. For this, we do have to
        # go back to the beginning and rerun the footprintfinder using the full exterior border.
        if len(simplefootprintlist) > 0:
            break
        else:
            # This forces the use of the full chip.
            warning(whocalls(verbose=verbose) + "WARNING: No footprint with more than 2 corners found.\n")
            borderpixels = []

    heirarchy = getheirarchy(simplefootprintlist, borderpixels)
    centroid = getcentroid(simplefootprintlist, borderpixels, heirarchy, verbose)

    writeoutput(filename, simplefootprintlist, borderpixels, heirarchy, wcs, centroid, arguments, writepoints, verbose)
    if ds9:
        writeds9output(filename, simplefootprintlist, borderpixels, heirarchy, wcs, centroid, colorlist, verbose)

    print whocalls(verbose=verbose) + "Footprint generation finished successfully."

    if plotting:
        plotfootprints(simplefootprintlist, borderpixels, dimshape, chips, groupid, firstid, nextid, grouplen, heirarchy
                       , centroid, colorlist, verbose)

    alert(whocalls(verbose=verbose) + runtimestring(date) + "\n")
    print "==================================================================================================="

    if returnstring:
        return getreturnstring(simplefootprintlist, borderpixels, heirarchy, centroid, wcs, verbose)

#------------------------------------------------------------------------------------------------

def usage():

#------------------------------------------------------------------------------------------------
    '''
       Help.
    '''
    print """
usage:  footpritfinder.py [options] fitsfilename.fits
output: fitsfilename_footprint.txt

INTRODUCTION
   
   The footprintfinder reads a FITS file, identifies the footprint(s) of the illuminated pixels and
   writes them into an ascii output file.
   
   This output file is written to the local directory and contains the number of footprints
   detected and for each of them the number of footprint corners, information about the footprint
   heirarchy (i.e holes/islands) and then the x y ra dec coordinates. Ra and Dec coordinates will 
   be only computed if the CTYPE1/CTYPE2 are 'RA---TAN/DEC--TAN'.
   
OPTIONS:

   Input:
   -e, --extension      FITS file extension to use. Default=first extension with data. 

   Processing:
   -t, --tolerance      Maximum tolerated distance of a pixel from a polygon line. Default=5.
   -z, --zerovalue      Value of the pixels that should be identified as 'border'. If a pixel value
                        'nan', it is replaced with the zerovalue, too.
   -m, --minlength      Minimal length of a continous footprint border to be taken into account as
                        a fraction of the total number of border pixels. Default=0.05.
   Output:
   -p, --plotting       Plots the footprint. Default=off.   
   -d, --ds9            Writes output file(s) in ds9 region format. One file in image coordinates and 
                        if possible (i.e. projection is RA--TAN, DEC-TAN) a second one in WCS 
                        coordinates are produced. Default=off.
   -w, --writepoints    Writes the polygon coordinates on the screen. Default=off.
   -v, --verbose        Increase verbosity.
   
   Help:
   -h,  --help          Print this help.
   
DETAILS

   The footprintfinder takes .fits .fits.gz or .fits.fz files as input (i.e. using pyfits). If the 
   files are uncompressed, then the code can process the file line by line, which results in a very 
   low memory use. If the files are compressed, then pyfits uncompresses the whole file in memory 
   before reading it. For large compressed files, it may be therefore advantageous to uncompress
   the whole file before running the footprintfinder on it. If not specified otherwise, the first 
   FITS extension that contains any data is used. 
      
   In a first step, the border pixels are identified using a 8-connect border definition. Then a 
   groupfinder with a linking length of sqrt(2) pixel run over the border pixels and groups with 
   more than 5% of all border pixels (can be overridden witm the -m option) are retained. In each
   group, the pixels are ordered starting from the lower left corner using an algorithm that keeps 
   'the-right-hand-on the wall'. If a 90 degree left corner is detected, the normally discarded 
   cornerpixel is added to the list in oder to allow for exact concave footprint polygons. A 
   Douglas-Puecker algorithm is used to reduce the number of polygon corners. Finally, inclusion of
   footprints in others in computed with a standard point-in-polygon algorithm.
   
   The algorithm is fast, robust, can deal with arbitrarily shaped footprints (i.e. concave 
   footprints and even one-pixel-wide lines are possible), returns the full footprint heirarchy and 
   has low memory usage if .fits files are treated. It uses uses only information from the fits 
   image itself.

LICENCE

   This program is free software: you can redistribute it and/or modify
   it under the terms of the GNU General Public License as published by   
   the Free Software Foundation, version 3 of the License.

   This program is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
   GNU General Public License for more details.

   You should have received a copy of the GNU General Public License
   along with this program.  If not, see <http://www.gnu.org/licenses/>.

DOCUMENTATION
   
   A description of the footprintfinder is available in the issue #45 of the ST-ECF newsletter
   
   http://www.spacetelescope.org/about/further_information/newsletters/html/newsletter_45.html

===================================================================================================
   """


#------------------------------------------------------------------------------------------------

def alert(string):

#------------------------------------------------------------------------------------------------
    '''
       prints the string in blue.
    '''
    import sys

    sys.stdout.write("\033[39;34m" + string + "\033[39;29m")


#------------------------------------------------------------------------------------------------

def error(string):

#------------------------------------------------------------------------------------------------
    '''
       prints the string in red.
    '''
    import sys

    sys.stdout.write("\033[39;31m" + string + "\033[39;29m")


#------------------------------------------------------------------------------------------------

def warning(string):

#------------------------------------------------------------------------------------------------
    '''
       prints the string in orange.
    '''
    import sys

    sys.stdout.write("\033[39;33m" + string + "\033[39;29m")


#------------------------------------------------------------------------------------------------

def runtimestring(date=None):

#------------------------------------------------------------------------------------------------
    '''
      returns a string of the current time and if a date is given, adds the running time from that
      date.
    '''
    import time, datetime

    if date == None:
        return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    else:
        thisdate = datetime.datetime.now()
        difference = thisdate - datetime.datetime(*time.strptime(date, "%d/%m/%Y %H:%M:%S")[:6])

        minutes, seconds = divmod(difference.seconds, 60)
        hours, minutes = divmod(minutes, 60)
        hours = hours + difference.days * 24

    return datetime.datetime.strftime(thisdate, "%d/%m/%Y %H:%M:%S") + " (%dh %02dm %02ds)" % (hours, minutes, seconds)


#------------------------------------------------------------------------------------------------

def getdatetime(time=None):

#------------------------------------------------------------------------------------------------
    '''
       returns a SYBSE accepted datetime string. If no datetime object is given, it returns
       the (local) time.
    '''
    import datetime

    if time == None:
        time = datetime.datetime.utcnow()

    return "%04d-%02d-%02d %02d:%02d:%02d" % (time.year, time.month, time.day, time.hour, time.minute, time.second)


#------------------------------------------------------------------------------------------------

def whocalls(level=1, verbose=False):

#------------------------------------------------------------------------------------------------
    '''
       This function returns the caller, the function and the line number.
    '''
    import os, sys

    adjust = 48
    x = sys._getframe(level)
    if verbose:
        return (
            '%s|%s:%s:l=%d' % (
            getdatetime(), os.path.basename(x.f_code.co_filename), x.f_code.co_name, x.f_lineno)).ljust(
            adjust + 20)
    else:
        return ('%s:%s:l=%d' % (os.path.basename(x.f_code.co_filename), x.f_code.co_name, x.f_lineno)).ljust(adjust)


#------------------------------------------------------------------------------------------------

def showprogress(i, n, lastprogress):

#------------------------------------------------------------------------------------------------
    '''
       This function shows the progress of an iteration. i=current number, n=total number.
    '''
    import sys

    progress = int(100.0 * i / n)
    if i == n - 1:
        sys.stdout.write("100%")
    else:
        if progress > lastprogress:
            lastprogress = progress
            if (progress % 10) == 0:
                sys.stdout.write("%d%%" % progress)
                sys.stdout.flush()
            elif (progress % 2) == 0:
                sys.stdout.write(".")
                sys.stdout.flush()

    i = i + 1

    return i, lastprogress


# ----------------------------------------------------------------------------------------

def xy2rd(wcs, x, y):

# ----------------------------------------------------------------------------------------
    '''
       Code as in stsdas.imgtools.xy2rd
       Can not treat distorted images.

    '''
    import pylab

    degtorad = 0.017453292519943295
    radtodeg = 57.295779513082323

    ra0 = wcs['CRVAL1']
    dec0 = wcs['CRVAL2']

    # translate (x,y) to (ra, dec)
    xi = wcs['CD1_1'] * (x - wcs['CRPIX1']) + wcs['CD1_2'] * (y - wcs['CRPIX2'])
    eta = wcs['CD2_1'] * (x - wcs['CRPIX1']) + wcs['CD2_2'] * (y - wcs['CRPIX2'])

    xi = degtorad * xi
    eta = degtorad * eta
    ra0 = degtorad * ra0
    dec0 = degtorad * dec0

    ra = pylab.math.atan2(xi, pylab.math.cos(dec0) - eta * pylab.math.sin(dec0)) + ra0
    dec = pylab.math.atan2(eta * pylab.math.cos(dec0) + pylab.math.sin(dec0),\
                           pylab.math.sqrt((pylab.math.cos(dec0) - eta * pylab.math.sin(dec0)) ** 2 + xi ** 2))

    ra = radtodeg * ra
    dec = radtodeg * dec

    ra = ra % 360.0
    if (ra < 0.0):
        ra = ra + 360.0

    return ra, dec


# ----------------------------------------------------------------------------------------

def rd2xy(wcs, ra, dec):

# ----------------------------------------------------------------------------------------
    '''
       Code as in stsdas.imgtools.xy2rd
       Can not treat distorted images.

       ra dec must be in degrees
    '''
    import pylab

    degtorad = 0.017453292519943295
    radtodeg = 57.295779513082323

    ra0 = wcs['CRVAL1']
    dec0 = wcs['CRVAL2']

    det = wcs['CD1_1'] * wcs['CD2_2'] - wcs['CD1_2'] * wcs['CD2_1']

    if det == 0.0:
        raise Excption("Singular CD matrix!")

    cdinv = pylab.zeros((3, 3))
    cdinv[1, 1] = wcs['CD2_2'] / det
    cdinv[1, 2] = -wcs['CD1_2'] / det
    cdinv[2, 1] = -wcs['CD2_1'] / det
    cdinv[2, 2] = wcs['CD1_1'] / det

    # translate (ra,dec) to (x,y)


    ra0 = degtorad * ra0
    dec0 = degtorad * dec0
    ra = degtorad * ra
    dec = degtorad * dec

    bottom = pylab.math.sin(dec) * pylab.math.sin(dec0) + pylab.math.cos(dec) * pylab.math.cos(dec0) * pylab.math.cos(
        ra - ra0)
    if bottom == 0:
        raise Exception("Unreasonable ra/dec range")

    xi = pylab.math.cos(dec) * pylab.math.sin(ra - ra0) / bottom
    eta = pylab.math.sin(dec) * pylab.math.cos(dec0) - pylab.math.cos(dec) * pylab.math.sin(dec0) * pylab.math.cos(
        ra - ra0) / bottom

    xi = radtodeg * xi
    eta = radtodeg * eta

    x = cdinv[1, 1] * xi + cdinv[1, 2] * eta + wcs['CRPIX1']
    y = cdinv[2, 1] * xi + cdinv[2, 2] * eta + wcs['CRPIX2']

    return x, y

# ----------------------------------------------------------------------------------------

def directborder(filename, zerovalue, extension, epsilon=1e-8, verbose=False):

# ----------------------------------------------------------------------------------------
    '''
       This function reads the data in slices (for low memory usage), cleans it an then
       identifies the borderpixels. Pyfits only allows this kind of access for non-scaled data!

       The crval, crpix amd cdmatrix are read from the file, too.
    '''
    import pyfits, pylab, numpy

    print whocalls(verbose=verbose) + "Reading fits file %s ..." % filename

    try:
        hdulist = pyfits.open(filename)
    except IOError:
        error("\n" + whocalls(verbose=verbose) + "ERROR: the file could not be opened!\n")
        print "==================================================================================================="
        import sys

        sys.exit(1)

    hdu = 0
    if extension == None:
        while True:
            dshape = []
            try:
                dshape = hdulist[hdu]._dimShape()
            except IndexError:
                error("\n" + whocalls(verbose=verbose) + "ERROR: Cannot read file. Is this really a fits file?\n")
                print "==================================================================================================="
                import sys

                sys.exit(1)

            if list(dshape) == []:
                hdu += 1
            else:
                break
    else:
        hdu = extension
    n = list(hdulist[hdu]._dimShape())

    print whocalls(verbose=verbose) + "Found data with %s in hdu %d ..." % (str(n), hdu)

    if verbose:
        print whocalls(verbose=verbose) + "Fits header of this extension:"
        print hdulist[hdu].header

    # reading the WCS information from the header
    wcs = {}
    wcs['CRPIX1'] = hdulist[hdu].header['CRPIX1']
    wcs['CRPIX2'] = hdulist[hdu].header['CRPIX2']
    wcs['CRVAL1'] = hdulist[hdu].header['CRVAL1']
    wcs['CRVAL2'] = hdulist[hdu].header['CRVAL2']
    wcs['CD1_1'] = hdulist[hdu].header['CD1_1']
    wcs['CD1_2'] = hdulist[hdu].header['CD1_2']
    wcs['CD2_1'] = hdulist[hdu].header['CD2_1']
    wcs['CD2_2'] = hdulist[hdu].header['CD2_2']
    wcs['CTYPE1'] = hdulist[hdu].header['CTYPE1']
    wcs['CTYPE2'] = hdulist[hdu].header['CTYPE2']

    if (wcs['CTYPE1'] == "RA---TAN") and (wcs['CTYPE2'] == "DEC--TAN"):
        wcs['wcs_is_possible'] = True
    else:
        warning(whocalls(verbose=verbose) + "WARNING: WCS CTYPE1/CTYPE2 are not RA--TAN/DEC---TAN but %s/%s.\n" % (
            wcs['CTYPE1'], wcs['CTYPE2']))
        warning(whocalls(verbose=verbose) + "WARNING: Only the pixelpositions of the footprints will be available!\n")
        wcs['wcs_is_possible'] = False

    print whocalls(verbose=verbose) + "Cleaning and finding borderpixels ..."
    print whocalls(verbose=verbose),

    count = 0
    lastprogress = -1
    borderpixels = []
    data = pylab.zeros((3, n[1]), 'float32')
    intdata = pylab.zeros((3, n[1]), 'Int8')
    thisarray = pylab.zeros(n[1], 'Int8')
    thatarray = pylab.ones(n[1], 'Int8')

    # now go row by row and find the broderpixels
    for i in range(n[0]):
        data[:, :] = zerovalue
        x1 = max(i - 1, 0)
        x2 = min(i + 2, n[0])
        data[x1 - (i - 1):x2 - (i + 2) + 3, :] = hdulist[hdu].section[x1:x2, :]
        data[numpy.isnan(data)] = zerovalue

        # cleaning the lines
        for j in range(3):
            index = pylab.find(abs(data[j, :] - zerovalue) < epsilon)
            intdata[j, :] = 1
            intdata[j, index] = 0
            index = None

        thisarray[:] = 0
        thisarray += intdata[0, :]
        thisarray += intdata[2, :]
        thisarray[1:] += intdata[1, :-1]
        thisarray[:-1] += intdata[1, 1:]

        thisarray[:-1] += intdata[0, 1:]
        thisarray[:-1] += intdata[2, 1:]
        thisarray[1:] += intdata[0, :-1]
        thisarray[1:] += intdata[2, :-1]

        thisarray *= intdata[1, :]

        index = pylab.find(((thisarray == 0) + (thisarray == 8)).__neg__())

        for j in range(len(index)):
            borderpixels.append([i, index[j]])

        index = None
        count, lastprogress = showprogress(count, n[0], lastprogress)

    print
    return pylab.array(borderpixels), n, wcs


# ----------------------------------------------------------------------------------------

def getborderdictionary(borderpixels, verbose=False):

# ----------------------------------------------------------------------------------------
    '''
       Gets a dictionary of the borderpixels.
    '''
    borderdictionary = {}
    for i in range(len(borderpixels)):
        borderdictionary["%d_%d" % (borderpixels[i, 0], borderpixels[i, 1])] = i

    return borderdictionary


# ------------------------------------------------------------------------------------------------------------------------

def getcloseparticles(i, borderpixels, borderdictionary):

# ------------------------------------------------------------------------------------------------------------------------
    '''
       returns a list of borderpixel ids that are close to the given pixel.
    '''
    closeparticles = []
    for j in range(borderpixels[i, 0] - 1, borderpixels[i, 0] + 2):
        for k in range(borderpixels[i, 1] - 1, borderpixels[i, 1] + 2):
            #print "closep:", i, borderpixels[i][0], borderpixels[i][1]
            #print "j, k   " ,j, k, "%d_%d" % (j,k), borderdictionary.has_key("%d_%d" % (j,k))

            if borderdictionary.has_key("%d_%d" % (j, k)):
                closeparticles.append(borderdictionary["%d_%d" % (j, k)])

    return closeparticles


# ------------------------------------------------------------------------------------------------------------------------

def getgroups(borderpixels, borderdictionary, verbose=False):

# ------------------------------------------------------------------------------------------------------------------------
    '''
       This function finds groups of borderpixels using the bordertree. It is a classical groupfinder.
    '''
    import pylab, sys

    nextid = pylab.ones([len(borderpixels)], 'Int32') * -1
    groupid = pylab.ones([len(borderpixels)], 'Int32') * -1
    groupcount = -1

    print whocalls(verbose=verbose) + "Group finding ..."
    print whocalls(verbose=verbose),
    n = len(borderpixels)
    count = 0
    lastprogress = -1
    for i in range(n):
        count, lastprogress = showprogress(count, n, lastprogress)
        if groupid[i] == -1:
            # If it is not -1, we already have treated it
            closeparticles = getcloseparticles(i, borderpixels, borderdictionary)
            groups = list(set(groupid[closeparticles]))

            if groups == [-1]:
                # a new group has to be created
                groupcount = groupcount + 1
                groupid[i] = groupcount
                nextid[i] = i
            else:
                try:
                    groups.remove(-1)
                except:
                    pass

                if len(groups) == 1:
                    # an already existing group, but only one single group for all particles
                    thisgroup = pylab.find(groupid[closeparticles] != -1)[0]
                    savepointer = nextid[closeparticles[thisgroup]]
                    nextid[closeparticles[thisgroup]] = i
                    nextid[i] = savepointer
                    groupid[i] = groups[0]

                elif len(groups) > 1:
                    # Groups of close by particles (not uniquified nor -1 removed)
                    thisgroups = groupid[closeparticles]
                    groupdict = {}
                    for j in range(len(thisgroups)):
                        if thisgroups[j] != -1:
                            groupdict[thisgroups[j]] = j
                    grouplist = []
                    for key, value in groupdict.items():
                        grouplist.append(value)

                    thisgroups = thisgroups[grouplist]
                    thiscloseparticles = pylab.array(closeparticles)[grouplist]

                    savepointer = nextid[thiscloseparticles[0]]
                    for j in range(len(thiscloseparticles) - 1):
                        nextid[thiscloseparticles[j]] = nextid[thiscloseparticles[j + 1]]
                    nextid[thiscloseparticles[-1]] = i
                    nextid[i] = savepointer

                    newgroupid = min(thisgroups)
                    for g in thisgroups:
                        groupid[pylab.find(groupid == g)] = newgroupid
                    groupid[i] = newgroupid

    print ""
    sys.stdout.flush()

    # rename the groups to continuous indices
    newgroups = list(pylab.sort(list(set(groupid))))
    firstid = []
    grouplen = []
    for j in range(len(newgroups)):
        index = pylab.find(groupid == newgroups[j])
        if not j == newgroups[j]:
            groupid[index] = j
        firstid.append(pylab.find(groupid == j)[0])
        grouplen.append(len(index))

    return pylab.arange(len(newgroups)), pylab.array(grouplen), pylab.array(groupid), pylab.array(firstid), pylab.array(
        nextid)


# ------------------------------------------------------------------------------------------------------------------------

def getpixelorder(chip, borderpixels, borderdictionary, groupid, grouplen, firstid, nextid, verbose):

# ------------------------------------------------------------------------------------------------------------------------
    '''
       This function finds the order of the pixels going round the chip. The array of borderpixelids is returned.
       The orientation is clockwise.
    '''
    import pylab, sys

    print whocalls(verbose=verbose) + "Ordering borderpixels ..."

    # pixelorder to check
    # 5 6 7       (inverted coordinates:    1 0 7
    # 4   0                                 2   6
    # 3 2 1                                 3 4 5)
    #
    #             0     1      2      3       4      5      6     7
    nextcheck = [[0, 1], [-1, 1], [-1, 0], [-1, -1], [0, -1], [1, -1], [1, 0], [1, 1]]

    # repeat for nonwrap search
    nextcheck = nextcheck + nextcheck

    minpixnumber = 4

    # get starting pixel, lower left corner
    maxpix = 100000
    mindist = 100000
    pos = firstid[chip]

    for i in range(grouplen[chip]):
        if (borderpixels[pos, 1] + borderpixels[pos, 0] < mindist):
            maxpix = pos
            mindist = borderpixels[pos, 1] + borderpixels[pos, 0]
        pos = nextid[pos]

        # Get order starting from maxpix:
        # get direction to the north east (i.e. it checks first south east and east which are both not possible because
    # of the choice of the starting point).
    # Vector is the last direction: it points from the centre to the corner (e.g. vector=6 points north)
    pos = maxpix
    vector = 5

    closeparticles = getcloseparticles(pos, borderpixels, borderdictionary)
    order = [pos]
    while (len(order) < minpixnumber) or (pos != maxpix):
        # see what the next borderpixel is that is in clockwise direction
        # the first pixel can't be a border pixel, otherwise it would have been
        # taken already in the last step.
        vector = vector - 2

        for i in range(7):
            if (borderdictionary.has_key(str(borderpixels[pos, 0] + nextcheck[vector + i][0]) + "_" + str(
                borderpixels[pos, 1] + nextcheck[vector + i][1]))):
                break

        iisoneandborder = False
        if i == 1:
            # Check if this is a convex corner
            if (borderdictionary.has_key(str(borderpixels[pos, 0] + nextcheck[vector + i + 1][0]) + "_" + str(
                borderpixels[pos, 1] + nextcheck[vector + i + 1][1]))):
                # If so, add the corner point to the list, too. This is to make sure that the algorithm really gets the exact convex
                # corners.
                iisoneandborder = True
                p = borderdictionary[str(borderpixels[pos, 0] + nextcheck[vector + i + 1][0]) + "_" + str(
                    borderpixels[pos, 1] + nextcheck[vector + i + 1][1])]
                order.append(p)

        pos = borderdictionary[str(borderpixels[pos, 0] + nextcheck[vector + i][0]) + "_" + str(
            borderpixels[pos, 1] + nextcheck[vector + i][1])]
        order.append(pos)

        # Get the next direction, which was the original direction plus where the next border pixel has been found
        if iisoneandborder:
            # If we just have added a convex corner point, use that (i.e -1 corresponds to +7) as the new direction
            vector = (vector + i + 7) % 8
        else:
            vector = (vector + i) % 8

    sys.stdout.flush()
    return order


# ------------------------------------------------------------------------------------------------------------------------

def simplifyDP(order, borderpixels, tolerance):

# ------------------------------------------------------------------------------------------------------------------------

    import pylab

    iscorner = pylab.zeros(len(order))
    iscorner[0] = 1
    simplify(order, borderpixels, 0, len(order) - 1, tolerance, iscorner)
    iscorner[-1] = 1
    return pylab.array(order)[pylab.find(iscorner == 1)]


# ------------------------------------------------------------------------------------------------------------------------

def simplify(order, borderpixels, a, b, tolerance, iscorner):

# ------------------------------------------------------------------------------------------------------------------------

    if a > b:
        return

    maxd2 = -1.0
    maxi = -1
    tolerance2 = tolerance * tolerance

    lenab2 = (borderpixels[order[b], 0] - borderpixels[order[a], 0]) * (
        borderpixels[order[b], 0] - borderpixels[order[a], 0]) +\
             (borderpixels[order[b], 1] - borderpixels[order[a], 1]) * (
                 borderpixels[order[b], 1] - borderpixels[order[a], 1])

    for i in range(a + 1, b):
        lenionab2 = ((borderpixels[order[i], 0] - borderpixels[order[a], 0]) * (
            borderpixels[order[b], 0] - borderpixels[order[a], 0])) +\
                    ((borderpixels[order[i], 1] - borderpixels[order[a], 1]) * (
                        borderpixels[order[b], 1] - borderpixels[order[a], 1]))

        if lenionab2 <= 0:
            d2 = (borderpixels[order[i], 0] - borderpixels[order[a], 0]) * (
                borderpixels[order[i], 0] - borderpixels[order[a], 0]) +\
                 (borderpixels[order[i], 1] - borderpixels[order[a], 1]) * (
                     borderpixels[order[i], 1] - borderpixels[order[a], 1])
        elif lenionab2 > lenab2:
            d2 = (borderpixels[order[i], 0] - borderpixels[order[b], 0]) * (
                borderpixels[order[i], 0] - borderpixels[order[b], 0]) +\
                 (borderpixels[order[i], 1] - borderpixels[order[b], 1]) * (
                     borderpixels[order[i], 1] - borderpixels[order[b], 1])
        else:
            factor = float(lenionab2) / float(lenab2)
            d2 = (borderpixels[order[i], 0] - (
                borderpixels[order[a], 0] + factor * (borderpixels[order[b], 0] - borderpixels[order[a], 0]))) ** 2 +\
                 (borderpixels[order[i], 1] - (
                     borderpixels[order[a], 1] + factor * (borderpixels[order[b], 1] - borderpixels[order[a], 1]))) ** 2

        if (d2 > maxd2):
            maxd2 = d2
            maxi = i

    if maxd2 < tolerance2:
        return
    else:
        iscorner[maxi] = 1
        simplify(order, borderpixels, a, maxi, tolerance, iscorner)
        simplify(order, borderpixels, maxi, b, tolerance, iscorner)


# ------------------------------------------------------------------------------------------------------------------------

def pointinpolygon(x, y, footprint, borderpixels):

# ------------------------------------------------------------------------------------------------------------------------   
    '''
       This function checks weather the point x,y is contained in the polygon given by footprint.
       It is assumed that the first point and the last point are identical!
    '''
    n = len(footprint)
    inside = False

    p1 = borderpixels[footprint[0]]
    for i in range(1, n):
        p2 = borderpixels[footprint[i]]
        if y > min(p1[1], p2[1]):
            if y <= max(p1[1], p2[1]):
                if x <= max(p1[0], p2[0]):
                    if p1[1] != p2[1]:
                        xint = (y - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]) + p1[0]
                    if (p1[0] == p2[0]) or (x <= xint):
                        inside = not inside
        p1 = p2

    return inside


# ------------------------------------------------------------------------------------------------------------------------

def getheirarchy(footprintlist, borderpixels):

# ------------------------------------------------------------------------------------------------------------------------
    '''
       This function checks whether one footprint is contained in an other one.
    '''
    import pylab

    insidelist = []
    for i in range(len(footprintlist)):
        for j in range(len(footprintlist)):
            if i != j:
                inside = pointinpolygon(borderpixels[footprintlist[i][0], 0], borderpixels[footprintlist[i][0], 1],\
                                        footprintlist[j], borderpixels)
                if inside:
                # pylygon i is inside polygon j
                    insidelist.append([i, j])

    heirarchy = [range(len(footprintlist)), len(footprintlist) * [int(0)], len(footprintlist) * [int(0)]]

    # count the number of occurrences of this footprint in others
    occurrence = pylab.zeros(len(footprintlist))
    for i in range(len(insidelist)):
        occurrence[insidelist[i][0]] += 1

    # if a given element occurs exactly one time more than an other
    # and that other is a parent of this one, than that other is the
    # direct parent of the current element. All other inside relations are ignored.
    for i in range(len(insidelist)):
        if occurrence[insidelist[i][0]] == 1 + occurrence[insidelist[i][1]]:
            heirarchy[0][insidelist[i][0]] = insidelist[i][1]
            heirarchy[1][insidelist[i][0]] = int(occurrence[insidelist[i][0]] % 2)
            heirarchy[2][insidelist[i][1]] = 1
    return heirarchy


# ------------------------------------------------------------------------------------------------------------------------

def getcentroid(simplefootprintlist, borderpixels, heirarchy, verbose):

# ------------------------------------------------------------------------------------------------------------------------
    """
       computes the centroid (=barycenter) and area for each polygon as well as the barycenter for the entire set.
       Holes have negative areas, computations are done in pixel space. It is assumed that the scalefactor is 1, i.e.
       that pixels are square.
    """
    centroid = {}
    totalarea = 0.0
    totalcx = 0.0
    totalcy = 0.0

    for fp in range(len(simplefootprintlist)):
        area = 0.0
        cx = 0.0
        cy = 0.0
        cxzero = 0.0
        cyzero = 0.0
        # The last point is indeed a copy of the first point.
        n = len(simplefootprintlist[fp]) - 1
        for i in range(n):
            j = i
            j1 = i + 1
            # If the footprint is a chip or an island, we have to reverse the order to get
            # the points ordered mathematically positively. This will then also give the
            # correct sign for the area computation
            if heirarchy[1][fp] == 0:
                j = n - i
                j1 = j - 1

            # Note that the x,y pixel definition in fits files runs from 1..n (actually, the
            # only really reasonable choice!) and not from 0..n-1 as it is in python.
            x = float(borderpixels[simplefootprintlist[fp][j], 1] + 1)
            y = float(borderpixels[simplefootprintlist[fp][j], 0] + 1)
            x1 = float(borderpixels[simplefootprintlist[fp][j1], 1] + 1)
            y1 = float(borderpixels[simplefootprintlist[fp][j1], 0] + 1)

            area = area + (x * y1 - x1 * y)
            cx = cx + (x + x1) * (x * y1 - x1 * y)
            cy = cy + (y + y1) * (x * y1 - x1 * y)
            cxzero = cxzero + x
            cyzero = cyzero + y

        # Prevent crashes for footprints with exactly zero area. area is set to a tiny value
        # for the unlikely case that _no_ footprint has a non-zero area.
        if area != 0.0:
            area = area * 0.5
            cx = cx / (6.0 * area)
            cy = cy / (6.0 * area)
        else:
            area = 1e-10
            cx = cxzero / n
            cy = cyzero / n

        totalarea = totalarea + area
        totalcx = totalcx + cx * area
        totalcy = totalcy + cy * area

        if verbose:
            print whocalls(verbose=verbose) + "Footprint %d: area=%f, %f, %f" % (fp, area, cx, cy)
        centroid[fp] = [area, cx, cy]

    totalcx = totalcx / totalarea
    totalcy = totalcy / totalarea

    centroid['total'] = [totalarea, totalcx, totalcy]

    if verbose:
        print whocalls(verbose=verbose) + "Total: area=%f, %f, %f" % (area, cx, cy)

    return centroid

# ------------------------------------------------------------------------------------------------------------------------

def writeoutput(filename, simplefootprintlist, borderpixels, heirarchy, wcs, centroid, arguments, writepoints, verbose):

# ------------------------------------------------------------------------------------------------------------------------
    """
       write the footprints to the output file. This file contains all information (including heirarchy) and is
       always produced.
    """
    import pylab
    import os

    outputfilename = os.path.basename(filename[0:filename.find(".fits")]) + "_footprint.txt"
    outputfile = open(outputfilename, "w")
    print >> outputfile, '# Footprint Finder'
    print >> outputfile, '# ================'
    print >> outputfile, '#'
    print >> outputfile, '# footprint-file for "%s"' % os.path.basename(filename)
    print >> outputfile, '# '
    print >> outputfile, '# Arguments: %s' % arguments
    print >> outputfile, '# '
    print >> outputfile, '# Number of chips found, global area [pixel^2], global x_barycenter, global y_barycenter, global ra_barycenter, global dec_barycenter'
    print >> outputfile, '# Chipnumber, number of footprint points, parent chip, is chip/island=0 or hole=1, has interior chip/island/hole=1 or not=0, area [pixel^2], y_barycenter, ra_barycenter, dec_barycenter'
    print >> outputfile, '#    x, y, ra, dec'

    centroid_ra = pylab.nan
    centroid_dec = pylab.nan
    if wcs['wcs_is_possible']:
        centroid_ra, centroid_dec = xy2rd(wcs, centroid['total'][1], centroid['total'][2])
    print >> outputfile, len(simplefootprintlist), centroid['total'][0], centroid['total'][1], centroid['total'][
                                                                                               2], centroid_ra, centroid_dec
    for fp in range(len(simplefootprintlist)):
        centroid_ra = pylab.nan
        centroid_dec = pylab.nan
        if wcs['wcs_is_possible']:
            centroid_ra, centroid_dec = xy2rd(wcs, centroid[fp][1], centroid[fp][2])

        print >> outputfile, fp, len(simplefootprintlist[fp]) - 1, heirarchy[0][fp], heirarchy[1][fp], heirarchy[2][fp],
        centroid[fp][0], centroid[fp][1], centroid[fp][2], centroid_ra, centroid_dec

        for i in range(len(simplefootprintlist[fp]) - 1):
            j = i
            if heirarchy[1][fp] == 0:
                j = len(simplefootprintlist[fp]) - 1 - i

            # Note that the x,y pixel definition in fits files runs from 1..n (actually, the
            # only really reasonable choice!) and not from 0..n-1 as it is in python.
            x = borderpixels[simplefootprintlist[fp][j], 1] + 1
            y = borderpixels[simplefootprintlist[fp][j], 0] + 1
            if wcs['wcs_is_possible']:
                ra, dec = xy2rd(wcs, x, y)
            else:
                ra, dec = (pylab.nan, pylab.nan)
            print >> outputfile, "   %5d %5d %11f %11f" % (x, y, ra, dec)
            if writepoints:
                print "writepoints = %5d %5d    %f %f" % (x, y, ra, dec)

    outputfile.close()
    print whocalls(verbose=verbose) + "Written to %s" % outputfilename


# ------------------------------------------------------------------------------------------------------------------------

def writeds9output(filename, simplefootprintlist, borderpixels, heirarchy, wcs, centroid, colorlist, verbose):

# ------------------------------------------------------------------------------------------------------------------------
    """
       writing ds9 region file(s). One file with the image coordinates, and if possible (i.e. of the projection
       is RA-TAN/DEC-TAN) also a ds9 WCS file.
    """
    import os

    linear = False
    if wcs['wcs_is_possible']:
        linear = True

    outputfilename = os.path.basename(filename[0:filename.find(".fits")]) + "_footprint_ds9_image.reg"
    outputfile = open(outputfilename, "w")
    if linear:
        outputfilename_linear = os.path.basename(filename[0:filename.find(".fits")]) + "_footprint_ds9_linear.reg"
        outputfile_linear = open(outputfilename_linear, "w")

    print >> outputfile, "# Region file format: DS9 version 4.0"
    print >> outputfile, "# Filename: %s " % filename
    print >> outputfile, '# global color=green font="helvetica 12 bold" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source'
    print >> outputfile, "image"

    if linear:
        print >> outputfile_linear, "# Region file format: DS9 version 4.0"
        print >> outputfile_linear, "# Filename: %s " % filename
        print >> outputfile_linear, '# global color=green font="helvetica 12 bold" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 source'
        print >> outputfile_linear, "linear"

    for fp in range(len(simplefootprintlist)):
        coordinatestring = ""
        coordinatestring_linear = ""

        for i in range(len(simplefootprintlist[fp]) - 1):
            j = i
            if heirarchy[1][fp] == 0:
                j = len(simplefootprintlist[fp]) - 1 - i

            # Note that the x,y pixel definition in fits files runs from 1..n (actually, the
            # only really reasonable choice!) and not from 0..n-1 as it is in python.
            x = borderpixels[simplefootprintlist[fp][j], 1] + 1
            y = borderpixels[simplefootprintlist[fp][j], 0] + 1
            coordinatestring = coordinatestring + "%d,%d," % (x, y)
            if linear:
                ra, dec = xy2rd(wcs, x, y)
                coordinatestring_linear = coordinatestring_linear + "%.6f,%.6f," % (ra, dec)

        color = colorlist[fp % (len(colorlist))]

        numberstring = "(" + str(fp) + ")"
        if heirarchy[1][fp] == 0:
            numberstring = str(fp)

        if len(simplefootprintlist) > 1:
            print >> outputfile, 'text %d %d # text={%s} color=%s font="helvetica 12 bold"' % (
                centroid[fp][1], centroid[fp][2], numberstring, color)
            if linear:
                ra, dec = xy2rd(wcs, centroid[fp][1], centroid[fp][2])
                print >> outputfile_linear, 'text %.6f %.6f # text={%s} color=%s font="helvetica 12 bold"' % (
                    ra, dec, numberstring, color)

        coordinatestring = "polygon(" + coordinatestring[:-1] + ") # color=%s width=2" % color
        print >> outputfile, coordinatestring, "\n"
        if linear:
            coordinatestring_linear = "polygon(" + coordinatestring_linear[:-1] + ") # color=%s width=2" % color
            print >> outputfile_linear, coordinatestring_linear, "\n"

    print >> outputfile, 'point %.6f %.6f # point=x color=%s ' % (centroid['total'][1], centroid['total'][2], 'red')
    if linear:
        ra, dec = xy2rd(wcs, centroid['total'][1], centroid['total'][2])
        print >> outputfile_linear, 'point %.6f %.6f # point=x color=%s ' % (ra, dec, 'red')

    outputfile.close()
    print whocalls(verbose=verbose) + "Written to %s" % outputfilename
    if linear:
        outputfile_linear.close()
        print whocalls(verbose=verbose) + "Written to %s" % outputfilename_linear


# ------------------------------------------------------------------------------------------------------------------------

def plotfootprints(simplefootprintlist, borderpixels, dimshape, chips, groupid, firstid, nextid, grouplen, heirarchy,
                   centroid, colorlist, verbose):

# ------------------------------------------------------------------------------------------------------------------------
    """
       This function plots the footprints using matplotlib
    """
    import matplotlib

    matplotlib.interactive(True)

    import pylab

    print whocalls(verbose=verbose) + "Plotting ..."
    pylab.figure(5)
    pylab.clf()
    pylab.hold(True)
    pylab.plot([0], [0], 'w')
    pylab.plot([dimshape[1]], [dimshape[0]], 'w')
    ax = pylab.axes()
    ax.set_autoscale_on(False)
    ax.set_aspect('equal', 'box', 'C')
    pylab.xlim([0, dimshape[1]])
    pylab.ylim([0, dimshape[0]])

    for g in chips:
        index = pylab.find(groupid == g)
        if verbose:
            pylab.plot(borderpixels[index, 1], borderpixels[index, 0], '.',
                       color=colorlist[(g + 1) % len(colorlist)][0])
        pos = firstid[g]
        for i in range(grouplen[g]):
            #pylab.text(borderpixels[pos,1],borderpixels[pos,0],str(pos))
            pos = nextid[pos]

    for fp in range(len(simplefootprintlist)):
        for i in range(len(simplefootprintlist[fp]) - 1):
            j = i
            dj = 1
            numbertext = "(" + str(fp) + ")"
            linestyle = ":"
            if heirarchy[1][fp] == 0:
                j = len(simplefootprintlist[fp]) - 1 - i
                dj = -1
                numbertext = str(fp)
                linestyle = "-"

            pylab.plot([borderpixels[simplefootprintlist[fp][j], 1], borderpixels[simplefootprintlist[fp][j + dj], 1]],\
                [borderpixels[simplefootprintlist[fp][j], 0], borderpixels[simplefootprintlist[fp][j + dj], 0]],
                                                                                                                      linestyle=linestyle
                                                                                                                      ,
                                                                                                                      color=
                                                                                                                      colorlist[
                                                                                                                      fp % len(
                                                                                                                          colorlist)][
                                                                                                                      0])
            if verbose:
                pylab.plot([borderpixels[simplefootprintlist[fp][j], 1]],\
                    [borderpixels[simplefootprintlist[fp][j], 0]], 'ko')
            else:
                pylab.plot([borderpixels[simplefootprintlist[fp][j], 1]],\
                    [borderpixels[simplefootprintlist[fp][j], 0]], 'k.')

        if len(simplefootprintlist) > 1:
            pylab.text(centroid[fp][1], centroid[fp][2], numbertext, horizontalalignment="center",
                       verticalalignment="center", color=colorlist[fp % len(colorlist)][0])

    pylab.plot([centroid['total'][1]], [centroid['total'][2]], 'rx')
    r = ''
    r = raw_input("Hit return to quit ")


# ------------------------------------------------------------------------------------------------------------------------

def getreturnstring(simplefootprintlist, borderpixels, heirarchy, centroid, wcs, verbose):

# ------------------------------------------------------------------------------------------------------------------------   
    """
       returns a simplified version of the footprint information that can be stored in the database

       x, y, ra, dec
       x0,y0,x1,y1,x2,y2,...; x0,y0,x1,y1,x2,y2,...;...
       The points are ordered anti-clickwise (chip) or clockwise (hole)

    """
    returnstring = ""
    for fp in range(len(simplefootprintlist)):
        for i in range(len(simplefootprintlist[fp]) - 1):
            j = i
            if heirarchy[1][fp] == 0:
                j = len(simplefootprintlist[fp]) - 1 - i

            # Note that the x,y pixel definition in fits files runs from 1..n (actually, the
            # only really reasonable choice!) and not from 0..n-1 as it is in python.
            x = borderpixels[simplefootprintlist[fp][j], 1] + 1
            y = borderpixels[simplefootprintlist[fp][j], 0] + 1
            returnstring += "%d,%d," % (x, y)

        returnstring = returnstring[:-1] + ";"

    ra, dec = xy2rd(wcs, centroid['total'][1], centroid['total'][2])
    if verbose:
        print whocalls(verbose=verbose) + "Returning '%d, %d, %f, %f, %s'" % (
            centroid['total'][1], centroid['total'][2], ra, dec, returnstring[:-1])

    return centroid['total'][0], centroid['total'][1], centroid['total'][2], ra, dec, returnstring[:-1]


# ------------------------------------------------------------------------------------------------------------------------
if __name__ == '__main__':
    import sys

    main(" ".join(sys.argv[1:]))
