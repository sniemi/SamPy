"""
Plots ratios between STIS CCD imaging flats.

:requires: NumPy
:requires: PyFITS
:requires: matplotlib

TESTED:
Python 2.5.1
NumPy: 1.4.0.dev7576
PyFITS: 2.2.2
matplotlib 1.0.svn

:date: Created on November 18, 2009

:version: 0.15: test release (SMN)

:author: Sami-Matias Niemi (niemi@stsci.edu)
"""

__author__ = 'Sami-Matias Niemi'
__version__ = '0.15'

def Idetifiers():
    """
    0th extension header keywords.
    Used to select and pair FITS files.
    """
    common = {'PROPOSID': 11853,
              'SCLAMP': 'TUNGSTEN',
              'OBSMODE': 'ACCUM',
              'CCDAMP': 'D',
              'CCDGAIN': 4}

    clear = {'APERTURE': '50CCD',
             'PROPAPER': '50CCD',
             'FILTER': 'Clear',
             'APER_FOV': '50x50'}

    f28x50lp = {'APERTURE': 'F28X50LP',
                'PROPAPER': 'F28X50LP',
                'FILTER': 'Long_Pass',
                'APER_FOV': '28x50'}

    return common, clear, f28x50lp


def ImStats(im1, im2, scale):
    """
    Calculates some basic image statistics from 
    two images given.
    
    :return: ratio, image1 mean, image1 std, ratio mean
    """
    ratio = (im1 * scale) / im2
    ratiosub = ratio[500:600, 500:600]
    im1sub = im1[500:600, 500:600]
    imean = N.mean(im1sub)
    istd = N.std(im1sub)
    rmean = N.mean(ratiosub)
    return ratio, imean, istd, rmean

if __name__ == '__main__':
    import matplotlib

    try:
        matplotlib.use('PDF')
    except:
        pass
    from matplotlib import cm
    import pyfits as PF
    import pylab as P
    import numpy as N
    import glob

    filelist = glob.glob('*_raw.fits')

    if len(filelist) < 1:
        import sys

        print 'No _raw.fits files were found. Will exit now...'
        sys.exit(-5)

    common, clear, f28 = Idetifiers()

    for val1, name1 in enumerate(filelist):
        right = True
        fh1 = PF.open(name1)
        hdr10 = fh1[0].header
        for key in common:
            if common[key] != hdr10[key]:
                right = False
        if right:
            print 'Finding a pair for ', name1
            for val2, name2 in enumerate(filelist):
                if name1 != name2 and val2 > val1:
                    right2 = True
                    ClearB = True
                    F28B = True
                    fh2 = PF.open(name2)
                    hdr20 = fh2[0].header
                    for key in common:
                        if common[key] != hdr20[key]:
                            right2 = False
                    if right2:
                        for key in clear:
                            if clear[key] != hdr10[key] or clear[key] != hdr20[key]:
                                ClearB = False
                        if ClearB:
                            print 'Clear Pair:', name1, name2
                            exp1 = hdr10['TEXPTIME']
                            exp2 = hdr20['TEXPTIME']
                            scale = 1.
                            if exp1 != exp2:
                                print 'Exposure times do not match, will scale...'
                                scale = exp2 / exp1
                                #images
                            im1 = fh1[1].data
                            im2 = fh2[1].data
                            ratio, m, s, rm = ImStats(im1, im2, scale)
                            #plotting
                            P.title('Scaled Ratio of %s / %s' % (name1, name2))
                            ims = P.imshow(ratio, cmap=cm.gist_yarg, origin='lower',
                                           interpolation=None)
                            cb = P.colorbar(ims, orientation='vertical')
                            cb.set_label('Ratio')
                            str = 'APERTURE = ' + hdr10['APERTURE'] +\
                                  ', FILTER = ' + hdr10['FILTER'] +\
                                  ', APER_FOV = ' + hdr10['APER_FOV'] +\
                                  '\n SCLAMP = ' + hdr10['SCLAMP'] +\
                                  ', TDATEOBS1 = ' + hdr10['TDATEOBS'] +\
                                  ', TDATEOBS2 = ' + hdr20['TDATEOBS']
                            P.annotate(str,
                                       xy=(0.5, 0.03),
                                       horizontalalignment='center',
                                       verticalalignment='center',
                                       size='x-small',
                                       xycoords='figure fraction')
                            str2 = 'File = %s, box([500:600,500:600]), Mean = %6.2f, Stdev = %4.1f, SNR = %4.1f, Mean Ratio = %5.4f' % (
                            name1, m, s, m / s, rm)
                            P.annotate(str2,
                                       xy=(0.5, 0.97),
                                       horizontalalignment='center',
                                       verticalalignment='center',
                                       size='x-small',
                                       xycoords='figure fraction')
                            P.savefig(name1[:-5] + '.pdf')
                            P.close()

                        for key in f28:
                            if f28[key] != hdr10[key] or f28[key] != hdr20[key]:
                                F28B = False
                        if F28B:
                            print 'F28 Pair', name1, name2
                            exp1 = hdr10['TEXPTIME']
                            exp2 = hdr20['TEXPTIME']
                            scale = 1.
                            if exp1 != exp2:
                                print 'Exposure times do not match, will scale...'
                                scale = exp2 / exp1
                                #images
                            im1 = fh1[1].data
                            im2 = fh2[1].data
                            ratio, m, s, rm = ImStats(im1, im2, scale)
                            #plotting
                            P.title('Scaled Ratio of %s / %s' % (name1, name2))
                            ims = P.imshow(ratio, cmap=cm.gist_yarg, origin='lower',
                                           interpolation=None)
                            cb = P.colorbar(ims, orientation='vertical')
                            cb.set_label('Ratio')
                            str = 'APERTURE = ' + hdr10['APERTURE'] +\
                                  ', FILTER = ' + hdr10['FILTER'] +\
                                  ', APER_FOV = ' + hdr10['APER_FOV'] +\
                                  '\n SCLAMP = ' + hdr10['SCLAMP'] +\
                                  ', TDATEOBS1 = ' + hdr10['TDATEOBS'] +\
                                  ', TDATEOBS2 = ' + hdr20['TDATEOBS']
                            P.annotate(str,
                                       xy=(0.5, 0.03),
                                       horizontalalignment='center',
                                       verticalalignment='center',
                                       size='x-small',
                                       xycoords='figure fraction')
                            str2 = 'File = %s, box([500:600,500:600]), Mean = %6.2f, Stdev = %4.1f, SNR = %4.1f, Mean Ratio = %5.4f' % (
                            name1, m, s, m / s, rm)
                            P.annotate(str2,
                                       xy=(0.5, 0.97),
                                       horizontalalignment='center',
                                       verticalalignment='center',
                                       size='x-small',
                                       xycoords='figure fraction')
                            P.savefig(name1[:-5] + '.pdf')
                            P.close()

                    fh2.close()
        fh1.close()