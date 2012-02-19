"""
Quick and dirty data reduction, suitable for INT WFC imaging data.

:author: Sami-Matias Niemi
:contact: sammy@sammyniemi.com
"""
from pyraf import iraf
from iraf import noao, imred, ccdred
from itertools import groupby
import pyfits, numpy, glob


def mkbiasINTWFC(filelist, type='median'):
    """
    Creates a master bias from given list of bias frames.
    Saves each extension to a different FITS file.

    Reads readnoise and gain from the FITS header, as each WFC chip has
    different values.

    :note: This function has been written specifically for INT WFC.

    :param filelist:
    :type filelist:
    :param type: combining parameter (default = median)
    :type type: string

    :return: None
    """
    input1 = ''
    for line in filelist:
        input1 += line[0] + '[1],'
    input2 = input1.replace('[1]', '[2]')
    input3 = input1.replace('[1]', '[3]')
    input4 = input1.replace('[1]', '[4]')
    inputs = [input1, input2, input3, input4]

    #note there are four SCI extensions
    for ext, input in enumerate(inputs):
        iraf.unlearn('zerocombine')
        iraf.zerocombine(input=input[:-1],
                         output='BIAS%i.fits' % (ext+1),
                         combine=type,
                         rdnoise='READNOIS',
                         gain='GAIN')


def mkflatINTWFC(data, combine='median', reject='avsigclip'):
    """
    Creates a master flat from a given list of flat frames.

    Reads readnoise and gain from the FITS header, as each WFC chip has
    different values.

    :note: ccdproc
    """
    for filter in data:
        input1 = ''
        for file in data[filter]:
            input1 += file + '[1],'

        input2 = input1.replace('[1]', '[2]')
        input3 = input1.replace('[1]', '[3]')
        input4 = input1.replace('[1]', '[4]')

        inputs = [input1, input2, input3, input4]

        for ext, input in enumerate(inputs):
            print input
            iraf.unlearn('flatcombine')
            iraf.flatcombine(input=input[:-1],
                             output='FLAT_{0:>s}_{1:d}.fits'.format(filter, ext + 1),
                             combine=combine,
                             reject=reject,
                             rdnoise='READNOIS',
                             gain='GAIN')


def makeflat(data):
    """
    Creates a master flat from a given list of flat frames.
    """
    for filter in data:
        for ext in [1,2,3,4]:
            bias = pyfits.getdata('BIAS%i.fits' % ext, 0)

            filedata = [pyfits.getdata(x, ext) for x in data[filter]]
            hdrs = [pyfits.open(x)[ext].header for x in data[filter]]

            if len(set(x.shape for x in filedata))  > 1:
                print "Flat images are not of same size!"

            #subtracts overscan and BIAS from all flats
            i = 0
            for image, hdr in zip(filedata, hdrs):

                biassec = hdr['BIASSEC'].strip().replace('[', '').replace(']','').replace(',',':').split(':')
                trimsec = hdr['TRIMSEC'].strip().replace('[', '').replace(']','').replace(',',':').split(':')

                overscan = numpy.median(image[int(biassec[2])+1:int(biassec[3])-2,
                                              int(biassec[0])+1:int(biassec[1])-2].copy().ravel())

                if overscan > 5000:
                    image = (1.*image) - bias
                else:
                    image = (1.*image) - (bias/overscan) - overscan

                norm = numpy.median(image[int(trimsec[2])+10:int(trimsec[3])-10,
                                          int(trimsec[0])+10:int(trimsec[1])-10].copy().ravel())

                tmp = image / norm
                tmp[tmp < 0] = 1.

                filedata[i] = tmp

                i += 1

            #calculates the median of all biases
            flat = numpy.median(filedata, axis=0)

            del filedata

            newhdu = pyfits.PrimaryHDU(flat)
            newhdu.writeto('FLAT_%s_%i.fits' % (filter, ext))


def reduceData(data):
    for filter in data:
        for file in data[filter]:
            fh = pyfits.open(file)
            images = []
            for ext in [1,2,3,4]:
                bias = pyfits.getdata('BIAS%i.fits' % ext, ext=0)
                flat = pyfits.getdata('FLAT_%s_%i.fits' % (filter, ext), ext=0)

                image = fh[ext].data
                hdr = fh[ext].header

                biassec = hdr['BIASSEC'].strip().replace('[', '').replace(']','').replace(',',':').split(':')

                overscan = numpy.median(image[int(biassec[2])+1:int(biassec[3])-1,
                                              int(biassec[0])+1:int(biassec[1])-1].copy().ravel())

                print 'subtracting bias of about ', numpy.mean(bias)

                if overscan > 5000:
                    img = (1.*image) - bias
                else:
                    img = (1.*image) - (bias/overscan) - overscan

                img /= flat
                images.append(img)

            fh.close()

            fh = pyfits.open(file)
            for ext in [1,2,3,4]:
                fh[ext].data = images[ext-1]

            fh.writeto('RED%s' % (file))



def writeFilelist(list, output):
    out = open(output, 'w')
    for file in list:
        out.write(file[0] + ' ' + file[1] + '\n')
    out.close()


def groupByFilter(data):
    newass = {}

    f2d = [(a[0], a[1]) for a in data]
    f2d = sorted(f2d, key=lambda x: x[1])

    for key, group in groupby(f2d, lambda x: x[1]):
        tmp = []
        print '\nnew group found:'
        for member in group:
            print member
            tmp.append(member[0])
        newass[key] = tmp

    return newass


if __name__ == '__main__':
    #find all FITS files
    fits = glob.glob('INT*.fits')

    #find file types
    bias = []
    flat = []
    sci = []
    for file in fits:
        hdr = pyfits.open(file)[0].header

        out = [file, hdr['WFFBAND'].strip()]

        if 'BIAS' in hdr['OBSTYPE']:
            bias.append(out)
        elif 'FLAT' in hdr['OBSTYPE']:
            flat.append(out)
        elif 'TARGET' in hdr['OBSTYPE']:
            sci.append(out)
        else:
            print file

    files = dict(bias=bias, flats=flat, science=sci)

    ##create BIAS
    #writeFilelist(files['bias'], output='bias.list')
    #mkbiasINTWFC(files['bias'])

    ##create FLAT fields
    #writeFilelist(files['flats'], output='flat.list')
    #grp = groupByFilter(files['flats'])
    ##mkflatINTWFC(grp)
    #makeflat(grp)

    #perform correction
    writeFilelist(files['science'], output='science.list')
    grp = groupByFilter(files['science'])
    reduceData(grp)