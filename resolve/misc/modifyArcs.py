"""
Modifies arc FITS files to include a sky line from the science image.

Will combine a small part of the arc file with the science image
that includes the sky line and copies this part to the original
arc. Will take a sky line from each science frame and generate
a corresponding arc file. Renames all arcs and includes the science
file name in the arc name for easy identification.

The script calls IRAF from the command line as follows::

  cl -0 < command_file.cl

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu
:version: 0.2
"""
import glob as g
import sys, os
from optparse import OptionParser


def generateIRAFcopy(scis, arcs, matches, x, out='modifyArcs.cl'):
    """
    Generates a file that can be fed to IRAF
    to generate a punch of temp files for data.

    :param scis: a list of science image names
    :type scis: list
    :param arcs: a list of arc image names
    :type arcs: list
    :param matches: a mapping between a science image and arc images
    :type matches: dictionary
    :param x: a list of x coordinate positions to describe the cutout region
              from the science image. These values shuold bracket the sky line.
    :type x: list
    :param out: name of the IRAF command file
    :type out: string

    :return: None
    """
    fh = open(out, 'w')
    fh.write('images\nimmatch\n')
    for arc in arcs:
        for a in arc:
            fh.write('imcopy %s[%i:%i,*] tmp%s\n' % (a, x[0], x[1], a))

    for sci in scis:
        for s in sci:
            fh.write('imcopy %s[%i:%i,*] tmp%s\n' % (s, x[0], x[1], s))

    for key, values in matches.iteritems():
        fl = key[:-5]
        for val in values:
            fh.write('imcombine input="tmp%s,tmp%s" output=ar%s.%s combine=sum\n' % (key, val, fl, val))
            fh.write('imcopy %s arc%s.%s\n' % (val, fl, val))
            fh.write('imcopy ar%s.%s arc%s.%s[%i:%i,*]\n' % (fl, val, fl, val, x[0], x[1]))

    fh.write('logout\n')
    fh.close()


def findClosestArcs(scis, arcs, tol=8):
    """
    Tries to match science frames with arcs
    that have been taken close in time.

    :param scis: a list of science file names
    :type scis: list
    :param arcs: a list of arc file names
    :type arcs: list
    :param tol: tolerance how many files before and after the arcs are being identified.
    :type tol: int

    :return: out, mapping between science images and corresponding arcs
    :rtype: dictionary
    """
    out = {}
    for i, sci in enumerate(scis):
        for s in sci:
            #sequence number
            tmp = s.split('.')
            snumb = int(tmp[0][-4:])

            matcha = ''
            matchb = ''
            #loop over the arcs
            for t in range(1, tol + 1, 1):
                newnumba = snumb + t
                newnumbb = snumb - t
                for a in arcs[i]:
                    anumb = int(a.split('.')[0][-4:])
                    if newnumba == anumb and len(matcha) < 1:
                        #one could also check the header
                        #to make sure that this is right
                        matcha = a
                    if newnumbb == anumb and len(matchb) < 1:
                        #one could also check the header
                        #to make sure that this is right
                        matchb = a
            out[s] = [matcha, matchb]
    return out


def writeArcLists():
    """
    Writes filelists with arc file names.

    :return: None
    """
    for i in range(1, 4, 1):
        arcs = g.glob('arc*spec*Ne*slice%i.fits' % i)
        fh = open('arclist%i' % i, 'w')
        for a in arcs:
            fh.write(a + '\n')
        fh.close()


def processArgs(printHelp=False):
    """
    Processes command line arguments.
    """
    parser = OptionParser()

    parser.add_option('-b', '--binning',
                      dest='binning',
                      help='Binning of the data, either 2 for 2x2 or 3 for 3x3',
                      metavar='integer')
    if printHelp:
        parser.print_help()
    else:
        return parser.parse_args()


if __name__ == '__main__':
    opts, args = processArgs()

    if opts.binning is None:
        processArgs(True)
        sys.exit(1)

    if opts.binning.strip() == '3':
        xcuts = [15, 80]     #this is for binning 3x3, change if needed
    elif opts.binning.stip() == '2':
        xcuts = [8, 160]   #this is for binning 2x2, change if needed
    else:
        processArgs(True)
        sys.exit(1)

    #find all science files
    sciencefiles1 = g.glob('ft*spec*.slice1.fits')
    sciencefiles2 = g.glob('ft*spec*.slice2.fits')
    sciencefiles3 = g.glob('ft*spec*.slice3.fits')
    scis = [sciencefiles1, sciencefiles2, sciencefiles3]

    #find all arcs
    arcfiles1 = g.glob('ft*.Ne.slice1.fits')
    arcfiles2 = g.glob('ft*.Ne.slice2.fits')
    arcfiles3 = g.glob('ft*.Ne.slice3.fits')
    arcs = [arcfiles1, arcfiles2, arcfiles3]

    if len(sciencefiles1) == 0 or len(sciencefiles2) == 0 or\
       len(sciencefiles3) == 0 or len(arcfiles1) == 0 or\
       len(arcfiles2) == 0 or len(arcfiles3) == 0:
        sys.exit('Cannot find files, will exit...')

    #generate the IRAF command file
    matches = findClosestArcs(scis, arcs)
    generateIRAFcopy(scis, arcs, matches, x=xcuts)

    #call IRAF
    os.system('cl -o < modifyArcs.cl')

    #write arclists
    writeArcLists()