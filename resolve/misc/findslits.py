import pyfits as PF
import pylab as P
import numpy as np
import matplotlib.patches as patches

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
    modper = 1.1
    #check indices, rows and columns
    row, col = np.indices(input.shape)
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
    minrow = np.min(row)
    maxrow = np.max(row)
    mincol = np.min(col)
    maxcol = np.max(col)

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

    return out


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

    P.savefig('slit.pdf')
    P.close()

    #generate a separate image of the slit data of each slit image.
    for i, slit in enumerate(slits):
        P.figure()
        P.imshow(slit['values'], origin='lower')
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
    TODO: one should refine this after measuring the sky position accurately.
    '''
    lw = 550
    up = 550

    lowslit['ymin'] += lw
    lowslit['ymax'] += lw
    lowslit['xy'] = (lowslit['xy'][0], lowslit['xy'][1] + lw)

    upslit['ymin'] -= up
    upslit['ymax'] -= up
    upslit['xy'] = (upslit['xy'][0], upslit['xy'][1] - up)

    return lowslit, midslit, upslit

if __name__ == '__main__':
    #get data
    input = PF.open('47_Tucsi_0.fits')[0].data
    input = input[0] #I don't get why there needs to be an extra [0]... PYFITS has changed?

    upslit = slitPosition(input, {'xmin': 1460, 'xmax': 1500, 'ymin': 1900, 'ymax': 2500})
    midslit = slitPosition(input, {'xmin': 1500, 'xmax': 1525, 'ymin': 1200, 'ymax': 1850})
    lowslit = slitPosition(input, {'xmin': 1530, 'xmax': 1550, 'ymin': 600, 'ymax': 1130})

    slits = (upslit, midslit, lowslit)

    generatePlots(input, slits)

    slits = approxSkyPosition(lowslit, midslit, upslit)
    overPlotSlits(slits, '47_Tuci_0.fits', 'overplottedLog')
    writeDS9RegionFile(slits)