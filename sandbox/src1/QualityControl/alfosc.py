#!/usr/bin/python
# -*- coding: utf-8 -*-

#
# Python version of this script, based on the IDL one
#
# (C) 2007, Ricardo Cárdenes for the Nordic Optical Telescope

# res = GETENV('NAMEOFFILE')

import numpy
import pyfits
import sys
from sigclip import stdev as scstdev
from math import sqrt
from collections import defaultdict
from mx.DateTime import DateTime

def betalight(names, verbose = False):
# Read Images and their headers and reorder in case they were taken with
# some other BIAS script than the correct one
    nimages = len(names)
    if nimages != 4:
        print "I need four images. You provided me with %d" % nimages
        return

    if verbose: print 'start reading of MEF images'
    # files is a list of FITS files, already open for use
    files = [(pyfits.open(x), x) for x in names]

    # We want to sort the files attending to their decreasing mean value
    # To to this, we prepare a list of "tuples". Each tuple will contain
    # three values: the mean value of the file, a reference to the file
    # itself, and its name. It seems redundant to have the files listed
    # in two places, but it is not. Python copy references, not whole
    # values, so it's cheap to do like this.
    #
    # You can use a FITS object like a sequence. Each element of the
    # sequence is a FITS HDU. In ALFOSC files, file[0] is the Primary HDU
    # and file[1] is the first image (the only one).
    l = [ (fitsfile[1].data.mean(), fitsfile, name)
               for (fitsfile, name)
               in files ]

    # And now we get the list of sorted files. How? Well, when you sort
    # a list of tuples, what Python does is: sort using the first element,
    # and if there's a coincidence, use the second element, and if ... You
    # get the idea. "l" is a list of tuples having the mean value of the
    # file as a first element and thus "sorted(l)" will return the tuples
    # of "l" sorted by mean value.
    # Then we discard that mean value to create sortedfits.
    sl = sorted(l, reverse = True)
    sortednames = [x[2] for x in sl]
    sortedfits = [x[1] for x in sl]

    # The we produce a list of the first image (fistfile[1]) data, for
    # everyone of those sorted FITS files. Alse a list of primary headers.
    # We assign them also to discrete variables (f1, f2, ... hf1, hf2, ...)
    # for later use.
    datalist = [fitsfile[1].data for fitsfile in sortedfits]
    f1, f2, b1, b2 = datalist
    headerlist = [fitsfile[1].header for fitsfile in sortedfits]
    hf1, hf2, hb1, hb2 = headerlist

    if verbose: print 'end reading of MEF images'

    # Test that the images are of the same size
    # We could do it, for example, comparing the shape of the first
    # data with the second one, and then with the third one, and then
    # with the fourth one.
    # That's a direct but a bit cumbersome way to do it. Instead, we
    # use "set". set is a native type to Python that behaves as... a
    # set ;). That means it will contain only one copy of a value. Eg:
    #
    #  >>> set([1, 2, 3, 1, 2, 4, 1, 2, 5])
    #  set([1, 2, 3, 4, 5])
    #
    # so... if this set of image shapes has more than one element...
    # at least one of them is different to the others.
    if len(set(x.shape for x in datalist)) > 1:
        print 'Images not of same size! Aborted!'
        return
    if verbose: print 'Images are the same size'

    # Cut edges out of the images
    #
    # Images should be 101 x 101 pixels, since that is the size of the
    # image of betalight on alfosc
    bsize	= 16
    nareas	= int(float(f1.shape[1])/bsize)

    ysize, xsize = f1.shape
    c1 = c3 = nareas - 1
    c2 = xsize
    c4 = ysize

    if xsize < 200 or ysize < 200:
        cf1 = f1[c3:c4, c1:c2]
        cf2 = f2[c3:c4, c1:c2]
        cb1 = b1[c3:c4, c1:c2]
        cb2 = b2[c3:c4, c1:c2]
    else:
        cf1 = f1[50:ysize-50, 50:xsize-50]
        cf2 = f2[50:ysize-50, 50:xsize-50]
        cb1 = b1[50:ysize-50, 50:xsize-50]
        cb2 = b2[50:ysize-50, 50:xsize-50]

    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    # ; Measure some easy statistical properties for the user to see ;
    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    # This empty class is just for convenience. That way we can set arbitrary
    # attributes to its instances. See below
    class Dummy(object): pass
    stats = []
        
    if verbose:
        print ("%14s" + "%13s"*5) % ("Name", "Min", "Max",
                                     "StDev", "Mean", "Median")
    frmt = "%-14s%13.2f%13.2f%13.2f%13.2f%13.2f"
    for img, name in zip((cf1, cf2, cb1, cb2), sortednames):
        st = Dummy()
        st.min, st.max = img.min(), img.max()
        st.stdev, st.mean, st.median, st.nrejects = scstdev(img)
        stats.append(st)

        if verbose:
            print frmt % (name, st.min, st.max, st.stdev, st.mean, st.median)

    if verbose: print

    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    # ; Check difference of bias frames, should be smaller than the stdev ;
    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    biasdiff = abs(stats[2].mean - stats[3].mean)
    if biasdiff > stats[2].stdev or biasdiff > stats[3].stdev:
        print
        print " Difference of averages of bias frames", biasdiff
        print " is larger than the standard deviation"
        print " of either of the bias images         ", stats[2].stdev, stats[3].stdev
        print " Aborted! "
        return

    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    # ; Divide image to areas (subimages) of 16x16 pix and ;
    # ; calculate statistics of individual areas           ;
    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    class ImgPiece(object):
        def __init__(self, frame):
            st, ma, me, nrej = scstdev(frame)
            self.frame  = frame
            self.min    = frame.min()
            self.max    = frame.max()
            self.std    = st
            self.mean   = ma
            self.median = me

    # The original script did this on three loops, what of course is
    # the obvious way. Python is not lightning fast when it comes to
    # long loops, but for this small 101x101  (36 16x16 squares)

    # The original also creates a 3D array shaped (nareas*nareas, 5, 4).
    # Instead, I create a dict structured like this:
    #
    #    pieces[n] -> [ImgPiece(flat1[n]), ..., ImgPiece(bias2[n])]
    #
    # Where "n" is the number for a 16x16 area

    pieces = defaultdict(list)
    for img in (cf1, cf2, cb1, cb2):
        for ycoord in range(0, nareas):
            vert = ycoord * bsize
            row = img[vert: vert + bsize]
            base = ycoord * nareas
            for xcoord in range(0, nareas):
                horiz = xcoord * bsize
                pieces[base + xcoord].append(ImgPiece(row[:,horiz:horiz + bsize]))

    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    # ; Calculate COUNTS, BIAS, RON and GAIN for individual areas    ;
    # ;                                                              ;
    # ; gain = ( ( flat1 + flat2 ) - ( bias1 + bias2) ) /            ;
    # ;	( STDEV( flat1 - flat2 )^2 - STDEV(bias1 - bias2 )^2 ) ;
    # ;                                                              ;
    # ; ron  = gain * STDEV( bias1 - bias2 ) / SQRT( 2 )             ;
    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    gaintbl = []
    rontbl  = []

    sqrt2 = sqrt(2)
    for l in range(0, nareas*nareas):
        pf1, pf2, pb1, pb2 = pieces[l]
        stdFlats = (scstdev(pf1.frame - pf2.frame)[0])
        stdBias  = (scstdev(pb1.frame - pb2.frame)[0])
        gaintbl.append( ((pf1.mean+pf2.mean) - (pb1.mean+pb2.mean)) /
                        (stdFlats**2 - stdBias**2) )
        rontbl.append( stdBias / sqrt2 )

    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    # ; Take the individual measurements of the subimages and ;
    # ; do sigma clipping on them                             ;
    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    std, gain, _, nr1 = scstdev(gaintbl)
    gainerr  = std / sqrt(numpy.array(gaintbl).size - nr1)

    std, mean, _, nr2 = scstdev(rontbl)
    ron      = gain * mean
    ronerr   = gain * std / sqrt(numpy.array(rontbl).size - nr2)

    # Ok
    fltmean = numpy.array([(x[0].mean, x[1].mean) for x in pieces.values()])
    std, counts, _, nr3 = scstdev(fltmean)
    counterr = std / sqrt(fltmean.size - nr3)

    # Ok
    biasmean = numpy.array([(x[2].mean, x[3].mean) for x in pieces.values()])
    std, bias, _, nr4 = scstdev(biasmean)
    biaserr  = std / sqrt(biasmean.size - nr3)

    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    # ; Print results to screen, these values are the ones going to DB ;
    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    if verbose:
        print "  COUNTS:%7.1f +/- %6.2f" % (counts, counterr)
        print "  BIAS:  %7.1f +/- %6.2f" % (bias, biaserr)
        print "  GAIN:  %7.4f +/- %6.4f" % (gain, gainerr)
        print "  RON:   %7.4f +/- %6.4f" % (ron, ronerr)
        print

    results = Dummy()
    results.counts   = counts
    results.counterr = counterr
    results.bias     = bias  
    results.biaserr  = biaserr 
    results.gain     = gain
    results.gainerr  = gainerr
    results.ron      = ron
    results.ronerr   = ronerr

    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    # ; extract required keywords from the FITS header ;
    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    # Obtain the primary HDU headers from the first file
    hf0 = files[0][0][0].header

    #                      012345678901234567890
    # Format for DATE-AVG: 2008-01-22T14:53:12.5
    date_avg = hf0['DATE-AVG']
    results.date  = DateTime(int(date_avg[0:4]), # year
                             int(date_avg[5:7]), # month
                             int(date_avg[8:10]) # day
                             ).mjd
    results.time  = hf0['UT']
    results.amp   = hf0['AMPLMODE']
    results.gmode = hf0['GAINM']
    if verbose:
        print "amp   ", results.amp
        print "gmode ", results.gmode

    return results

def insertIntoDB(server, user, passwd, db, data, verbose = False):
    import MySQLdb

    if verbose: print "Inserting into DB!"

    # TODO: Should do some error-catching
    conn = MySQLdb.connect(host   = server,
                           user   = user,
                           passwd = passwd,
                           db     = db)
    curs = conn.cursor()

    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
    # ; extract all previous data from DB for comparison ;
    # ;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

    nrows = curs.execute("SELECT * FROM qc_alfosc_CCD8")
    # curs.description returns a list where each element contains
    # information for a field in the table. We keep only the first
    # element of each description, which is the name for the field.
    # This way we have an index of fields
    fields = [x[0] for x in curs.description]

    # Some magic to make the following much easier
    # Needs extra explanation
    class DBField(object):
        def __init__(self, index, data):
            if len(index) != len(data):
                raise RuntimeError("# of Indexes is not == to # of fields")
            for fieldName, fieldValue in zip(index, data):
                setattr(self, fieldName, fieldValue)
    previous = [DBField(fields, x) for x in curs.fetchall()]

    # Test for counts
    counts, counterr = (numpy.array([x.counts for x in previous]),
                        numpy.array([x.counterr for x in previous]))

    if (3.0 * counterr.mean()) < abs(counts.mean() - data.counts):
        print "number of counts differs over 3 sigma from previous!"
    if (3.0 * counterr.var()) < abs(counterr.mean() - data.counterr):
        print "error in number of counts differs too much from previous!"

    # Test for bias
    bias, biaserr    = (numpy.array([x.bias for x in previous]),
                        numpy.array([x.biaserr for x in previous]))
    
    if (3.0 * biaserr.mean()) < abs(bias.mean() - data.bias):
        print "bias differs over 3 sigma from previous!"
    if (3.0 * biaserr.var()) < abs(biaserr.mean() - data.biaserr):
        print "error in bias differs over 3 sigma from previous!"

    # Test for gain
    gain, gainerr    = (numpy.array([x.gain for x in previous]),
                        numpy.array([x.gainerr for x in previous]))
    
    if (3.0 * gainerr.mean()) < abs(gain.mean() - data.gain):
        print "gain differs over 3 sigma from previous!"
    if (3.0 * gainerr.mean()) < abs(gainerr.mean() - data.gainerr):
        print "error in gain differs over 3 sigma from previous!"

    # Test for ron
    ron, ronerr      = (numpy.array([x.ron for x in previous]),
                        numpy.array([x.ronerr for x in previous]))
    
    if (3.0 * ronerr.mean()) < abs(ron.mean() - data.ron):
        print "ron differs over 3 sigma from previous!"
    if (3.0 * ronerr.mean()) < abs(ronerr.mean() - data.ronerr):
        print "error in ron differs over 3 sigma from previous!"

    # Don't write anything (yet)

# outcmd	= 'mysql -B -e ''INSERT INTO '+table+' ('+fields+') VALUES (('	$
# 	+STRING(counts)+'),('+STRING(counterr)+'),('			$
# 	+STRING(bias)+'),('+STRING(biaserr)+'),('+STRING(gain)+'),('	$
# 	+STRING(gainerr)+'),('+STRING(ron)+'),('+STRING(ronerr)+'),('	$
# 	+STRING(date)+'),('+STRING(time)+'),("'+amp+'"),("'+gmode	$
#         +'"),("'+names[0]+'"),("'+names[1]+'"),("'+names[2]+'"),("'+names[3]$
# 	+'"))'' -q -n -D '+database+' -h '+server+' -u '+user+' -p'	$
# 	+password

if __name__ == '__main__':
    import string
    import os.path
    from getopt import getopt

    intoDB = False
    verbose = False

    (opts, args) = getopt(sys.argv[1:], 'v', ['db'])
    for opt, val in opts:
        if opt == '--db': intoDB = True
        if opt == '-v':   verbose = True

    if len(args) < 1:
        print "Let me know the PATH to the first image"
        sys.exit(-1)

    path, fname = os.path.split(args[0])
    # Test for a valid ALFOSC file name:
    if fname[-5:].lower() != '.fits':
        print "Is this a FITS file? I can't recognize the extension"
        sys.exit(-1)
    au, al = string.ascii_uppercase, string.ascii_lowercase
    if fname[0] not in au or fname[1] not in au:
        print "Not a valid ALFOSC file name"
        sys.exit(-1)
    if fname[2] not in al or fname[3] not in al:
        print "Not a valid ALFOSC file name"
        sys.exit(-1)
    try:
        number = int(fname[4:-5])
    except ValueError:
        print "Not a valid ALFOSC file name"
        sys.exit(-1)
    prefix, extension = fname[:4], fname[-5:]
    filenames = [os.path.join(path, "%s%06d%s" % (prefix, number + offset, extension))
                    for offset in range(0, 4)]

    # Test for the existence of those files
    if False in (os.path.exists(x) for x in filenames):
        print "One or more of the next files are missing:"
        for f in filenames:
            print "   " + f
        sys.exit(-1)

    res = betalight(filenames, verbose)
    if res and intoDB: # res != None -> We got results
        insertIntoDB('eeva', 'qc_user', 'qc_pass', 'QC', res, verbose)
