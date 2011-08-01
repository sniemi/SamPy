'''
Fits slit image to a direct image to find x and y positions.

Currently the script uses a slit image. In the future however
we probably want to use the spectrum itself because there is
no guarantee that a slit confirmation image has always been
taken.

:todo: try to do the minimalization with scipy.optmize or
some other technique which might be faster and/or more
robust.

:todo: in the future one should allow rotation in the
fitting as well. This is a major complication and one
should think hard how to implement it correctly.

:requires: PyFITS
:requires: NumPy
:requires: matplotlib

:author: Sami-Matias Niemi
'''
import matplotlib
#matplotlib.rc('text', usetex=True)
#matplotlib.rcParams['font.size'] = 17
import sys
from optparse import OptionParser
import pyfits as PF
import pylab as P
import numpy as np
import matplotlib.patches as patches
from matplotlib import cm
import scipy.optimize as optimize
import scipy.ndimage.interpolation as interpolation
#SMN
import SamPy.smnIO.write
import SamPy.smnIO.read
import SamPy.image.manipulation as m


import scipy.ndimage.filters as f

def findSlitPositions(slitImage, threshold=1000):
    '''
    Finds slit positions from a slit image.

    This method uses the Sobel filter in scipy.ndimage.filters

    :todo: this is not ready!

    :param: filename

    '''
    #sobel filter
    filtered = f.sobel(slitImage, axis=1)
    #create a mask above the threshold
    msk = filtered > threshold
    masked = filtered[msk]
    #indices
    y, x = np.indices(slitImage.shape)

    yargs = y[msk]

    return masked

def slitPosition(input, xy):
    '''
    Find slit positions from a confirmation image.

    The script assumes that slits are illuminated and that
    background gives at least 10 per cent increase for the
    slit data.

    :note: modper factor is used to modify the mean background to autolocate the slits.

    :param: input: input data
    :param: xy: x and y minimum and maximum position to identify a single slit

    :rtype: dictionary
    '''
    #size modifier
    sizemod = 1

    #modifier
    modper = 1.1

    #shape of the input array
    shape = input.shape

    #check indices, rows and columns
    row, col = np.indices(shape)

    #create an intial mask
    #msk = input > val
    mn = (np.mean(input[2000:3000, 2000:3000]))
    msk = input > (mn * modper)
    rm = col[msk]
    cm = row[msk]

    #mask the appropriate slit
    msk = ((rm > xy['xmin']) & (rm < xy['xmax'])) & ((cm < xy['ymax']) & (cm > xy['ymin']))

    row = rm[msk]
    col = cm[msk]

    #check the ends
    minrow = np.min(row) + sizemod
    maxrow = np.max(row) - sizemod
    mincol = np.min(col) + sizemod
    maxcol = np.max(col) - sizemod

    #get the width and height of the slit image
    xymins = (minrow, mincol)
    height = maxcol - mincol
    width = maxrow - minrow

    out = {}
    out['xy'] = xymins
    out['width'] = width
    out['height'] = height
    out['ymin'] = mincol
    out['ymax'] = maxcol
    out['xmin'] = minrow
    out['xmax'] = maxrow
    out['values'] = input[mincol:maxcol + 1, minrow:maxrow + 1]
    out['shape'] = shape
    out['throughput'] = 1.0

    return out


def readSlitPositions(slitfile, slitdata):
    '''
    Reads slit positions from a slitfile and slitdata from another file.

    This file should follow DS9 format, i.e.:
    box 1545  871 7 499 0
    box 1512 1522 7 614 0
    box 1482 2175 7 499 0

    :note: slit image positions, not the slit positions on the sky!

    :param: slitfile: name of the slit file
    :param: slitdata: slitdata array

    :param: low: a shift for the lower slit
    :param: up: a shift for the upper slit

    :rtype: dictionary
    '''

    slits = []

    filedata = open(slitfile, 'r').readlines()
    for i, line in enumerate(filedata):
        out = {}
        tmp = line.split()
        out['width'] = int(tmp[3])
        out['height'] = int(tmp[4])
        out['ymin'] = int(tmp[2]) - (out['height'] / 2)
        out['ymax'] = int(tmp[2]) + (out['height'] / 2)
        out['xmin'] = int(tmp[1]) - (out['width'] / 2)
        out['xmax'] = int(tmp[1]) + (out['width'] / 2)
        out['xy'] = (out['xmin'], out['ymin'])
        out['shape'] = slitdata.shape
        out['throughput'] = 1.0
        out['values'] = slitdata[out['ymin']:out['ymax'] + 1, out['xmin']:out['xmax'] + 1]

        if i == 0:
            out['name'] = 'low'
        elif i == 2:
            out['name'] = 'up'
        else:
            out['name'] = 'mid'

        slits.append(out)

    return slits


def generateSlitMask(slits, throughput=False):
    '''
    This function can be used to generate a slit mask from given slits.
    '''
    if len(set([x['shape'] for x in slits])) > 1:
        print 'Shape of the slits do not match'

    #slitmask
    slitmask = np.zeros(slits[0]['shape'])

    for slit in slits:
        if throughput:
            val = slit['throughput']
        else:
            val = 1.0

        slitmask[slit['ymin']:slit['ymax'] + 1,
        slit['xmin']:slit['xmax'] + 1] = val

    return slitmask


def generateSkyMask(slits, offsetx=0, offsety=0):
    '''
    This function can be used to generate a slit mask on the sky
    '''

    skymask = np.zeros(slits[0]['shape'])
    for slit in slits:
        skymask[slit['ymin'] + offsety:slit['ymax'] + 1 + offsety,
        slit['xmin'] + offsetx:slit['xmax'] + 1 + offsetx] = 1

    return skymask


def generateSlitImages(slits, output, type='.pdf'):
    '''
    Generatesdiagnostic plots from slit image.
    '''
    #generate a separate image of the slit data of each slit image.
    for i, slit in enumerate(slits):
        fig = P.figure()
        ax = fig.add_subplot(111)

        #take log10 from the slit data
        ax.imshow(np.log10(slit['values'] * slit['throughput']),
                  origin='lower')

        #rotate x axis labels
        for tl in ax.get_xticklabels():
            tl.set_rotation(40)

        P.savefig(output + str(i + 1) + type)
        P.close()


def overPlotSlits(slits, imdata, output, type='.pdf', logscale=True):
    '''
    Overplot the slits 
    '''
    fig = P.figure()
    b = P.gca()
    ax = fig.add_subplot(111)

    #show image
    if logscale:
        imdata[imdata > 0] = np.log10(imdata[imdata > 0])
        ax.imshow(imdata, origin='lower')
    else:
        ax.imshow(imdata, origin='lower')

    for slit in slits:
        b.add_patch(patches.Rectangle(slit['xy'],
                                      slit['width'],
                                      slit['height'],
                                      fill=False))

    #rotate x axis labels
    for tl in ax.get_xticklabels():
        tl.set_rotation(40)

    P.savefig(output + type)

    #zoom-in version
    ax.set_xlim(1300, 1700)
    ax.set_ylim(1000, 2000)
    P.savefig(output + 'Zoomed' + type)
    P.close()


def writeDS9RegionFile(slits, output='skyslits.reg'):
    '''
    Writes a DS9 region file for all the slits.
    Draws a rectangle around each slit.
    '''
    fh = open(output, 'w')
    for slit in slits:
        #DS0 box format is x, y, width, height, but x and y are the centre point
        string = 'box %i %i %i %i 0\n' % (slit['xy'][0] + slit['width'] / 2,
                                          slit['xy'][1] + slit['height'] / 2,
                                          slit['width'],
                                          slit['height'])
        fh.write(string)
    fh.close()


def approxSkyPosition(lowslit, midslit, upslit):
    '''
    Generates an approximated sky position for slits.
    Assumes that both slits are shifted 553 pixels in y direction.
    Such an assumption is crude, but should allow a starting point.

    :note: this functions modifies the slit throughput as well

    :todo: one should refine this after measuring the sky position accurately.
    '''
    #throughputs for the two slits which use glass
    lwthr = 0.6
    upthr = 0.6

    #positions, estimated, shuold be updated
    lw = 553
    up = 553

    lowslit['ymin'] += lw
    lowslit['ymax'] += lw
    lowslit['xy'] = (lowslit['xy'][0], lowslit['xy'][1] + lw)
    lowslit['throughput'] = 1. / lwthr

    upslit['ymin'] -= up
    upslit['ymax'] -= up
    upslit['xy'] = (upslit['xy'][0], upslit['xy'][1] - up)
    upslit['throughput'] = 1. / upthr

    return lowslit, midslit, upslit


def chiSquare(model, obs):
    '''
    Simple chi**2 calculation
    '''
    r = np.sum((obs - model) ** 2 / model)
    return r

def fitfunct(x, y, directimage, slits):
    #get data from direct image
    dirdata=[]
    for slit in slits:
        d = directimage[slit['ymin'] + int(y):slit['ymax'] + 1 + int(y),
                        slit['xmin'] + int(x):slit['xmax'] + 1 + int(x)]
        dirdata.append(d)

    obs = np.hstack((dirdata[0].ravel(),
                     dirdata[1].ravel(),
                     dirdata[2].ravel()))
    obs /= np.max(obs)
    return obs

def errorf(params, directimage, slits, data):
    return fitfunct(params[0], params[1], directimage, slits) - data

def fitSlitsToDirectImageLSQ(slits, directimage, params = [-1, -1]):
    '''
    Uses scipy.optimize.leastsq
    '''
    #generates a model array from the slit values, takes into account potential
    #throughput of a slit
    data = np.hstack((slits[0]['values'].ravel() * slits[0]['throughput'],
                      slits[1]['values'].ravel() * slits[1]['throughput'],
                      slits[2]['values'].ravel() * slits[2]['throughput']))
    data /= np.max(data)

    p = optimize.leastsq(errorf,
                         params,
                         args=(directimage, slits, data),
                         full_output=True,
                         ftol=1e-18,
                         xtol=1e-18)
    return p

def fitSlitsToDirectImage(slits, directimage,
                          xran=25, yran=25, step=1,
                          rot=0.5, rotstep=0.02, rotation=True,
                          normalize='True', debug=True):
    '''
    Fits a slit image to a direct image.
    This functions does not collapse the slit image, but uses each pixel.
    By default the counts are normalized to a peak count, but this can
    be controlled using the optional keyword normalize.

    :param: slits
    :param: directimage
    :param: xran, +/- x-range to cover
    :param: yran, +/- y-range to cover
    :param: step, size of pixel steps in x and y
    :param: rot, +/- rotation angle in degrees
    :param: rotstep, step in degrees
    :param: normalize, wheter slit and direct image values should be normalized or not
    :param: debug, print debugging information

    :rtype: dictionary
    '''

    #generates a model array from the slit values, takes into account potential
    #throughput of a slit
    model = np.hstack((slits[0]['values'].ravel() * slits[0]['throughput'],
                       slits[1]['values'].ravel() * slits[1]['throughput'],
                       slits[2]['values'].ravel() * slits[2]['throughput']))

    if normalize:
        model /= np.max(model)

    norm = len(model)

    #generate rotations
    if rotation:
        rotations = np.arange(-rot, rot, rotstep)
        rotations[(rotations < 1e-8) & (rotations > -1e-8)] = 0.0
        #make a copy of the direct image
        origimage = directimage.copy()
    else:
        rotations = [0,]

    out = []
    #loop over a range of rotations,  x and y positions around the nominal position and record x, y and chisquare
    for r in rotations:
        if rotation:
            directimage = interpolation.rotate(origimage, r)
        for x in range(-xran, xran, step):
            for y in range(-yran, yran, step):
                dirdata = []
                #get data from direct image
                for slit in slits:
                    data = directimage[slit['ymin'] + y:slit['ymax'] + 1 + y,
                           slit['xmin'] + x:slit['xmax'] + 1 + x].copy()
                    dirdata.append(data)

                obs = np.hstack((dirdata[0].ravel(),
                                 dirdata[1].ravel(),
                                 dirdata[2].ravel()))

                if normalize:
                    obs /= np.max(obs)

                chisq = chiSquare(model, obs)
                out.append([r, x, y, chisq, chisq / norm])

                if debug:
                    print r, x, y, chisq, chisq / norm

    #return dictionary
    r = {}
    r['rot'] = r
    r['rotation_step'] = rotstep
    r['xran'] = xran
    r['yran'] = yran
    r['model'] = model
    r['output'] = np.array(out)
    return r


def fakeSlitData(slits, fakeimgdata):
    '''
    Cuts out imaging data to test the fitting algorithm.
    '''
    for slit in slits:
        slit['values'] = fakeimgdata[slit['ymin']:slit['ymax'] + 1, slit['xmin']:slit['xmax'] + 1]
    return slits


def plotMinimalization(data, output='minim', type='.png'):
    '''
    Generates a two dimensional map of the minimalization.

    :param: data
    '''
    d = data['output']
    #begin image
    P.figure()
    P.scatter(d[:, 1],
              d[:, 2],
              c=1. / np.log10(d[:, 3]),
              s=55,
              cmap=cm.get_cmap('jet'),
              edgecolor='none',
              alpha=0.5)
    P.xlim(-data['xran'], data['xran'])
    P.ylim(-data['yran'], data['yran'])
    P.xlabel('X [pixels]')
    P.ylabel('Y [pixels]')
    P.savefig(output + 'Map' + type)
    P.close()

    #second figure
    P.figure()
    P.scatter(d[:, 1], d[:, 3], s=2)
    P.xlim(-data['xran'], data['xran'])
    P.xlabel('X [pixels]')
    P.ylabel('$\chi^{2}$')
    P.savefig(output + 'XCut' + type)
    P.close()

    #second figure
    P.figure()
    P.scatter(d[:, 2], d[:, 3], s=2)
    P.xlim(-data['yran'], data['yran'])
    P.xlabel('Y [pixels]')
    P.ylabel('$\chi^{2}$')
    P.savefig(output + 'YCut' + type)
    P.close()


def outputMinima(inputfile, slitfile, slitpos, data, output='min.txt', stdout=True):
    '''
    Outputs the results to a file and also the screen if stdout = True.
    '''
    tmp = data['output'][np.argmin(data['output'][:, 3]), :]
    str = '{0:>s}\t{1:>s}\t{2:>s}\t{3:.1f}\t{4:.0f}\t{5:.0f}\t{6:.1f}'.format(inputfile, slitfile, slitpos, tmp[0], tmp[1], tmp[2], tmp[3])

    #to screen
    if stdout:
        print '\n\ndirect image    slit image    slit pos \t\t rot \t x \t y \t chi**2'
        print str

    #to file
    fh = open(output, 'a')
    fh.write(str + '\n')
    fh.close()


def processArgs(just_print_help=False):
    '''
    Processes command line arguments
    '''
    parser = OptionParser()

    parser.add_option("-s", "--slit", dest="slit",
                      help="Name of the slit image file", metavar="string")
    parser.add_option("-f", "--fitting", dest="fitImage",
                      help='Name of the direct image to which the slit data will be fitted', metavar='string')
    parser.add_option("-d", "--debug", dest="debug", action='store_true',
                      help='Debugging mode on')
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Verbose mode on")
    parser.add_option("-p", "--position", dest="position",
                      help="Name of the slit position file", metavar="string")
    parser.add_option("-b", "--blur", action="store_true", dest="blur",
                      help="Whether the input direct image should be gaussian blurred or not")
    parser.add_option("-a", "--automatic", action="store_true", dest="automatic",
                      help="If on tries to determine slit positions automatically from the slit image")
    if just_print_help:
        parser.print_help()
    else:
        return parser.parse_args()


def main(opts, args):
    '''
    Driver function
    '''

    if (opts.slit is None or opts.fitImage is None):
        processArgs(True)
        sys.exit(1)

    #rename the commmand line options
    slit = opts.slit
    fitImage = opts.fitImage
    #slit position file defaults to slit.reg
    if (opts.position is None):
        slitPos = 'slit.reg'
        print 'Using {0:>s} for slit positions'.format(slitPos)
    else:
        slitPos = opts.position
        #debugging mode, where slit data are being faked
    debug = opts.debug
    #whether the data should be blurred or not
    blur = opts.blur
    #boolean to control whether the slit positions should be found automatically or not
    automatic = opts.automatic

    #load images
    img = PF.open(fitImage, ignore_missing_end=True)[0].data
    if img.shape[0] == 1:
        img = img[0]
    slitimage = PF.open(slit, ignore_missing_end=True)[0].data
    if slitimage.shape[0] == 1:
        slitimage = slitimage[0]


    if blur:
        img = m.blurImage(img, 4)

    if automatic:
        #gets the slit positions automatically, does not work perfectly
        upslit = slitPosition(slitimage, {'xmin': 1460, 'xmax': 1500, 'ymin': 1900, 'ymax': 2500})
        midslit = slitPosition(slitimage, {'xmin': 1500, 'xmax': 1525, 'ymin': 1200, 'ymax': 1850})
        lowslit = slitPosition(slitimage, {'xmin': 1530, 'xmax': 1550, 'ymin': 600, 'ymax': 1130})
        slits = (upslit, midslit, lowslit)
        generateSlitImages(slits, 'slits')
        #updates the slit positions to sky positions
        slits = approxSkyPosition(lowslit, midslit, upslit)
        writeDS9RegionFile(slits)
    else:
        slits = readSlitPositions(slitPos, slitimage)
        generateSlitImages(slits, 'slits')
        slits = approxSkyPosition(*slits)
        writeDS9RegionFile(slits)

    if debug:
        slits = fakeSlitData(slits, img)

    #pickles the data
    #SamPy.smnIO.write.cPickleDumpDictionary(slits, 'slits.pk')
    #slits = SamPy.smnIO.read.cPickledData('slits.pk')

    #generates diagnostic plots and writes the slit positions for DS9 inspection
    overPlotSlits(slits, img, 'overplottedLog')

    #a = fitSlitsToDirectImageLSQ(slits, img)
    #print a
    #import sys; sys.exit()

    #find the chisqr minimum and make a diagnostic plot
    minimals = fitSlitsToDirectImage(slits, img, xran=40, yran=40, step=1)
    plotMinimalization(minimals)

    #output some info
    outputMinima(fitImage, slit, slitPos, minimals)


if __name__ == '__main__':
    #Gets the command line arguments and call main function
    main(*processArgs())