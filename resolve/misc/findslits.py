import pyfits as PF
import pylab as P
import numpy as np
import matplotlib.patches as patches
#SMN
import SamPy.smnIO.write
import SamPy.smnIO.read

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


def readSlitPositions(slitfile, slitdata, low=552, up=552):
    '''
    Reads slit positions from a slitfile and slitdata from another file.

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
        out['ymin'] = int(tmp[2]) - (out['height']/2)
        out['ymax'] = int(tmp[2]) + (out['height']/2)
        out['xmin'] = int(tmp[1]) - (out['width']/2)
        out['xmax'] = int(tmp[1]) + (out['width']/2)
        out['xy'] = (out['xmin'], out['ymin'])
        out['shape'] = slitdata.shape
        out['throughput'] = 1.0

        if i == 0:
            #first is low
            out['values'] = slitdata[out['ymin']-low:out['ymax']+1-low, out['xmin']:out['xmax']+1]
            #last is up
        elif i == 2:
            out['values'] = slitdata[out['ymin']+up:out['ymax']+1+up, out['xmin']:out['xmax']+1]
        else:
            out['values'] = slitdata[out['ymin']:out['ymax']+1, out['xmin']:out['xmax']+1]

        slits.append(out)

    return slits


def generateSlitMask(slits, offsetx=0, offsety=0, throughput=False, slitValue=False):
    '''
    This function can be used to generate a slit mask from given slits.
    '''
    #slit mask
    if len(set([x['shape'] for x in slits])) > 1:
        print 'Shape of the slits do not match'
    #else, take the shape of the first one
    slitmask = np.zeros(slits[0]['shape'])

    for slit in slits:
        if throughput:
            val = slit['throughput']
        else:
            val = 1.0

        if slitValue:
            val *= slit['values']
            
        slitmask[slit['ymin'] + offsety:slit['ymax'] + 1 + offsety,
                 slit['xmin'] + offsetx:slit['xmax'] + 1 + offsetx] = val
    return slitmask



def generatePlots(input, slits, type='.pdf'):
    '''
    Generates diagnostic plots from slit image.
    '''
    fig = P.figure()
    b = P.gca()
    ax = fig.add_subplot(111)

    #show image
    ax.imshow(np.log10(input), origin='lower')

    for slit in slits:
        b.add_patch(patches.Rectangle(slit['xy'],
                                      slit['width'],
                                      slit['height'],
                                      fill=False))

    #rotate xticks
    for tl in ax.get_xticklabels():
        tl.set_rotation(40)

    P.savefig('slit.pdf')
    P.close()

    #generate a separate image of the slit data of each slit image.
    for i, slit in enumerate(slits):
        fig = P.figure()
        ax = fig.add_subplot(111)

        #take log10 from the slit data
        ax.imshow(np.log10(slit['values']),
                  origin='lower')

        #rotate x axis labels
        for tl in ax.get_xticklabels():
            tl.set_rotation(40)
            
        P.savefig('slit' + str(i + 1) + type)
        P.close()


def overPlotSlits(slits, image, output, type='.pdf', ext=0, logscale=True):
    '''
    Overplot the slits 
    '''
    imdata = PF.open(image, ignore_missing_end=True)[ext].data[0]

    fig = P.figure()
    b = P.gca()
    ax = fig.add_subplot(111)

    #show image
    if logscale:
        ax.imshow(np.log10(imdata), origin='lower')
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


def writeDS9RegionFile(slits, output='ds9Slit.reg'):
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
    Assumes that both slits are shifted 550 pixels in y direction.
    Such an assumption is crude, but should allow a starting point.

    :note: this functions modifies the slit throughput as well

    :todo: one should refine this after measuring the sky position accurately.
    '''
    #throughputs for the two slits which use glass
    lwthr = 1 #0.56
    upthr = 1 #0.56

    #positions, estimated, shuold be updated
    lw = 552
    up = 552

    lowslit['ymin'] += lw
    lowslit['ymax'] += lw
    lowslit['xy'] = (lowslit['xy'][0], lowslit['xy'][1] + lw)
    lowslit['throughput'] = 1./lwthr

    upslit['ymin'] -= up
    upslit['ymax'] -= up
    upslit['xy'] = (upslit['xy'][0], upslit['xy'][1] - up)
    upslit['throughput'] = 1./upthr

    return lowslit, midslit, upslit


def chiSquare(observed, expected):
    return np.sum((observed - expected)**2/expected)
    

def fitSlitImageToDirectImage(directimage, slitimage, slits, xran=25, yran=25, step=1):
    '''
    This is a really stupid way of finding the x and y position of the slits.

    :todo: Try to implement smarter and faster algorithm

    :rtype: dictionary
    '''
    #erturn dictionary
    r = {}

    #obtain a slitmask based on slits without any offsets
    model = slitimage * generateSlitMask(slits, throughput=True, slitValue=True)
    modeldata = model[model > 0]

    #nomalize
    #modeldata /= np.max(modeldata)

    #normalization factor
    norm = len(modeldata) - 1

#    P.imshow(np.log10(model), origin='lower')
#    P.xlim(1300, 1700)
#    P.ylim(1000, 2000)
#    P.savefig('model.pdf')
#    P.close()

    r['model'] = model
    del model

    out = []
    ii = 0
    #loop over a range of x and y positions around the nominal position and record x, y and chisquare
    for x in range(-xran, xran, step):
        for y in range(-yran, yran, step):
            #update the noAnotMask position with offsets and multiply with the direct image
            comparison = directimage * generateSlitMask(slits, offsetx=x, offsety=y)
            compdata = comparison[comparison > 0]

            #normalize
            #compdata /= np.max(compdata)

            chisq = chiSquare(compdata, modeldata)

            out.append([x, y, chisq, chisq/norm])

            #for debugging
            ii += 1
            print x, y, chisq, chisq/norm
            str = 'x%iy%i' % (x, y)
            r[str] = comparison
#            P.figure()
#            P.imshow(np.log10(comparison)   , origin='lower')
#            P.xlim(1300, 1700)
#            P.ylim(1000, 2000)
#            P.show()
#            tmp = raw_input()
#            #P.savefig('%icomparison.pdf' % ii)
#            P.close()

    r['output'] = np.array(out)
    return r


def fakeSlitData(slits, fakeimgdata):
    '''
    This function can be used to cut out imaging data to test the fitting algorithm
    '''
    for slit in slits:
        slit['values'] = fakeimgdata[slit['ymin']:slit['ymax']+1, slit['xmin']:slit['xmax']+1]
    return slits

if __name__ == '__main__':
    #boolean to control whether the slit positions should be found automatically or not
    automatic = False
    #debugging mode, where slit data are being faked
    debug = True

    #input test data
    slitimage = PF.open('47_Tucsi_0.fits')[0].data[0]
    #I don't get why there needs to be an extra [0]... PYFITS has changed?

    if automatic:
        #gets the slit positions automatically, does not work perfectly
        upslit = slitPosition(slitimage, {'xmin': 1460, 'xmax': 1500, 'ymin': 1900, 'ymax': 2500})
        midslit = slitPosition(slitimage, {'xmin': 1500, 'xmax': 1525, 'ymin': 1200, 'ymax': 1850})
        lowslit = slitPosition(slitimage, {'xmin': 1530, 'xmax': 1550, 'ymin': 600, 'ymax': 1130})
        slits = (upslit, midslit, lowslit)
        generatePlots(slitimage, slits)
        #updates the slit positions to sky positions
        slits = approxSkyPosition(lowslit, midslit, upslit)
        writeDS9RegionFile(slits)
    else:
        slits = readSlitPositions('slit.reg', slitimage)
        #generatePlots(slitimage, slits)

    #pickles the data
    #SamPy.smnIO.write.cPickleDumpDictionary(slits, 'slits.pk')
    #slits = SamPy.smnIO.read.cPickledData('slits.pk')

    #generates diagnostic plots and writes the slit positions for DS9 inspection
    #overPlotSlits(slits, '47_Tuci_0.fits', 'overplottedLog')

    #the image to which one wants the stuff to be fitted
    img = PF.open('47_Tuci_0.fits')[0].data[0]

    if debug:
        slits = fakeSlitData(slits, img)

    minimals = fitSlitImageToDirectImage(img, slitimage, slits, xran=10, yran=10, step=5)

    tmp = minimals['output'][np.argmin(minimals['output'][:,2]),:]
    print tmp
