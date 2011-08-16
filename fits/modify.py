"""
FITS file modifications such as rebinning and rotation with the WCS being updated.

:requires: SamPy
:requires: PyFITS
:requires: pywcs
:requires: NumPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import os
import pyfits as pf
import numpy as np
import pywcs
import SamPy.image.manipulation as manipulate
import SamPy.image.transform as transform


def hrebin(imagefile, newx, newy, output='rebinned.fits', ext=0, total=False):
    """
    Expand or contract a FITS image and update the header.
    Based on IDL routine hrebin.pro, but removed some functionality

    :todo: remove the pywcs dependency
    :todo: there might be something wrong how the surface brightness is conserved

    :param: imagefile: name of the FITS file to be rebinned
    :param: newx:  size of the new image in the X direction, integer scalar
    :param: newy: size of the new image in the Y direction, integer scalar
    :param: output: Name of the outputfile or None
    :param: ext: the FITS extension of the header and data

    :return: None or updated img and hdr
    """
    fh = pf.open(imagefile)
    oldhdr = fh[ext].header
    oldimg = fh[ext].data
    fh.close()

    wcs = pywcs.WCS(oldhdr)

    #old size
    xsize = oldhdr['NAXIS1']
    ysize = oldhdr['NAXIS2']

    #ratios
    xratio = newx / float(xsize)
    yratio = newy / float(ysize)
    #change in aspect ratio
    lambd = yratio / xratio
    #Ratio of pixel areas
    pix_ratio = xratio * yratio

    #chech whether the new size is an exact match
    exact = (xsize % newx == 0) | (newx % xsize == 0) and \
            (ysize % newy == 0) | (newy % ysize == 0)

    #rebin based on whether the rebinning is exact or not
    if exact:
        oldimg = manipulate.frebin(oldimg, newx, newy, total=total)
    else:
        oldimg = manipulate.frebin(oldimg, newx, newy, total=total)

    #start updating the new header
    oldhdr['NAXIS1'] = int(newx)
    oldhdr['NAXIS2'] = int(newy)
    #add comment orig size and new size
    oldhdr.add_comment('rebinned...')

    #Correct the position of the reference pixel.
    #Note that CRPIX values are given in FORTRAN (first pixel is (1,1)) convention
    crpix = wcs.wcs.crpix

    #update astrometry
    if exact and xratio > 1:
        crpix1 = (crpix[0] - 1.0) * xratio + 1.0
    else:
        crpix1 = (crpix[0] - 0.5) * xratio + 0.5

    if exact and yratio > 1:
        crpix2 = (crpix[1] - 1.0) * yratio + 1.0
    else:
        crpix2 = (crpix[1] - 0.5) * yratio + 0.5

    oldhdr['CRPIX1'] = crpix1
    oldhdr['CRPIX2'] = crpix2

    #distortion correction, not implemented
    #oldhdr['CDELT1'] /= xratio
    #oldhdr['CDELT2'] /= yratio

    oldhdr['CD1_1'] /= xratio
    oldhdr['CD1_2'] /= yratio
    oldhdr['CD2_1'] /= xratio
    oldhdr['CD2_2'] /= yratio

    oldhdr['BSCALE'] /= pix_ratio

    #write out a new FITS file
    hdu = pf.PrimaryHDU(oldimg)
    hdu.header = oldhdr
    if os.path.isfile(output):
        os.remove(output)
    hdu.writeto(output)

    return oldimg, oldhdr


def hrot(imagefile, angle, xc=None, yc=None, ext=0, output='rotated.fits', pivot=False):
    """
    Rotate an image and create new FITS header with updated astrometry.
    
    param: xc: X Center of rotation (None for center of image)
    param: yc: Y Center of rotation (None for center of image)
    param: angle: rotation angle, in degrees
    """
    #read in the file
    fh = pf.open(imagefile)
    hdr = fh[ext].header
    img = fh[ext].data
    fh.close()

    wcs = pywcs.WCS(hdr)

    ysize, xsize = img.shape

    xc_new = (xsize - 1) / 2.
    yc_new = (ysize - 1) / 2.

    shape = img.shape
    if xc is None:
        xc = shape[1]/2.0
    if yc is None:
        yc = shape[0]/2.0

    #do the actual rotation
    A = transform.makeCenteredRotation(angle, (xc, yc))
    imgrot = transform.Image(img, A)    

    #update astrometry
    theta = np.deg2rad(angle)
    rot_mat = np.matrix([[np.cos(theta), np.sin(theta)],
                        [-np.sin(theta), np.cos(theta)]])
    
    #WCS info
    crpix = wcs.wcs.crpix
    cd = wcs.wcs.cd
    
    ncrpix = (rot_mat.T * (crpix - 1 - np.matrix([xc, yc])).T + 1).T

    if pivot:
        ncrpix = np.array([xc, yc]) + ncrpix
    else:
        ncrpix = np.array([xc_new, yc_new]) + ncrpix

    hdr['CRPIX1'] = ncrpix[0,0]
    hdr['CRPIX2'] = ncrpix[0,1]

    newcd = np.asmatrix(cd) * rot_mat
    hdr['CD1_1'] = newcd[0,0]
    hdr['CD1_2'] = newcd[0,1]
    hdr['CD2_1'] = newcd[1,0]
    hdr['CD2_2'] = newcd[1,1]
    
    #crota = np.rad2deg(np.arctan(newcd[1,0], newcd[1,1]))
    #hdr['CROTA1'] = crota
    #hdr['CROTA2'] = crota

    #write out a new FITS file
    hdu = pf.PrimaryHDU(imgrot)
    hdu.header = hdr
    if os.path.isfile(output):
        os.remove(output)
    hdu.writeto(output)
    
    return imgrot, hdr
    
    
if __name__ == "__main__":
    file = 'frame-r-004145-5-0083.fits'
    hrebin(file, 4096, 2978, output='rebinned.fits')
    hrot('rebinned.fits', 50.0, xc=None, yc=None)
