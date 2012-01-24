"""
This script can be used to make a few plots showing the Stokes parameters for Vela.

:requires: pyfits
:requires: matplotlib
:requires: Kapteyn Python package
:requires: pyregion

:author: Sami-Matias Niemi
:contact: sammy@sammyniemi.com

:version: 0.1
"""
from time import time
import pyregion
import numpy as np
import pyfits as pf
from kapteyn import maputils
from matplotlib import pyplot as plt
from pyregion.mpl_helper import properties_func_default


def func(x):
    nx = ny = x
    annim.set_blur(True, nx, ny, new=True)


def fixed_color(shape, saved_attrs):
    attr_list, attr_dict = saved_attrs
    attr_dict['color'] = 'black'
    kwargs = properties_func_default(shape, (attr_list, attr_dict))
    return kwargs


if __name__ == '__main__':
    start = time()

    #plot set up
    units = r'$\log_{10}()$'
    limy = limx = (200, 2100)
    rows = 3
    cols = 2

    #plotting
    fig = plt.figure(figsize=(16, 20))

    #first frame
    frame1 = fig.add_subplot(rows, cols, 1)
    f = maputils.FITSimage('StokesISmooth15.fits')
    frame1.set_title(f.filename, y=1.01)
    f.set_limits(limx, limy)
    f = maputils.FITSimage(externalheader=f.hdr, externaldata=np.log10(f.boxdat))
    mplim = f.Annotatedimage(frame1, cmap="spectral", clipmin=-5.5, clipmax=-3)
    mplim.Image()
    cb = mplim.Colorbar(fontsize=8)
    cb.set_label(label=units, fontsize=9)
    grat = mplim.Graticule()
    grat.setp_ticklabel(plotaxis=['top', 'right'], visible=False)
    grat.setp_ticklabel(wcsaxis=1, fmt='s')   # Exclude seconds in label
    grat.setp_gratline(wcsaxis=0, linestyle=':', zorder=1)
    grat.setp_gratline(wcsaxis=1, linestyle=':', zorder=1)
    #region file
    r = pyregion.open('region_forHST.reg').as_imagecoord(pf.open('StokesISmooth15.fits')[0].header)
    patch_list, artist_list = r.get_mpl_patches_texts(fixed_color)
    for p in patch_list:
        frame1.add_patch(p)
    for t in artist_list:
        frame1.add_artist(t)
    mplim.plot()
    #print "Proposed levels:", cont.clevels
    print "clip min, max:", mplim.clipmin, mplim.clipmax

    f = maputils.FITSimage('StokesUSmooth15.fits')
    f.set_limits(limx, limy)
    frame2 = fig.add_subplot(rows, cols, 2)
    frame2.set_title(f.filename, y=1.01)
    f = maputils.FITSimage(externalheader=f.hdr, externaldata=np.log10(f.boxdat))
    mplim = f.Annotatedimage(frame2, cmap="spectral", clipmin=-6, clipmax=-4)
    mplim.Image()
    cb = mplim.Colorbar(fontsize=8)
    cb.set_label(label=units, fontsize=9)
    grat = mplim.Graticule()
    grat.setp_ticklabel(plotaxis=['top', 'right'], visible=False)
    grat.setp_ticklabel(wcsaxis=1, fmt='s')   # Exclude seconds in label
    grat.setp_gratline(wcsaxis=0, linestyle=':', zorder=1)
    grat.setp_gratline(wcsaxis=1, linestyle=':', zorder=1)
    cont = mplim.Contours()
    #region file
    r = pyregion.open('region_forHST.reg').as_imagecoord(pf.open('StokesUSmooth15.fits')[0].header)
    patch_list, artist_list = r.get_mpl_patches_texts(fixed_color)
    for p in patch_list:
        frame2.add_patch(p)
    for t in artist_list:
        frame2.add_artist(t)
    mplim.plot()
    print "clip min, max:", mplim.clipmin, mplim.clipmax

    f = maputils.FITSimage('StokesQSmooth15.fits')
    f.set_limits(limx, limy)
    frame3 = fig.add_subplot(rows, cols, 3)
    frame3.set_title(f.filename, y=1.01)
    f = maputils.FITSimage(externalheader=f.hdr, externaldata=np.log10(f.boxdat))
    mplim = f.Annotatedimage(frame3, cmap="spectral", clipmin=-8, clipmax=-2)
    mplim.Image()
    cb = mplim.Colorbar(fontsize=8)
    cb.set_label(label=units, fontsize=9)
    grat = mplim.Graticule()
    grat.setp_gratline(wcsaxis=0, linestyle=':', zorder=1)
    grat.setp_gratline(wcsaxis=1, linestyle=':', zorder=1)
    grat.setp_ticklabel(plotaxis=['top', 'right'], visible=False)
    grat.setp_ticklabel(wcsaxis=1, fmt='s')   # Exclude seconds in label
    #region file
    r = pyregion.open('region_forHST.reg').as_imagecoord(pf.open('StokesQSmooth15.fits')[0].header)
    patch_list, artist_list = r.get_mpl_patches_texts(fixed_color)
    for p in patch_list:
        frame3.add_patch(p)
    for t in artist_list:
        frame3.add_artist(t)
    mplim.plot()
    print "clip min, max:", mplim.clipmin, mplim.clipmax

    f = maputils.FITSimage('PolIntSmooth15.fits')
    f.set_limits(limx, limy)
    frame4 = fig.add_subplot(rows, cols, 4)
    frame4.set_title(f.filename, y=1.01)
    f = maputils.FITSimage(externalheader=f.hdr, externaldata=np.log10(f.boxdat))
    mplim = f.Annotatedimage(frame4, cmap="spectral", clipmin=-7.5, clipmax=-1)
    mplim.Image()
    cb = mplim.Colorbar(fontsize=8)
    cb.set_label(label=units, fontsize=9)
    grat = mplim.Graticule()
    grat.setp_gratline(wcsaxis=0, linestyle=':', zorder=1)
    grat.setp_gratline(wcsaxis=1, linestyle=':', zorder=1)
    grat.setp_ticklabel(plotaxis=['top', 'right'], visible=False)
    grat.setp_ticklabel(wcsaxis=1, fmt='s')   # Exclude seconds in label
    #region file
    r = pyregion.open('region_forHST.reg').as_imagecoord(pf.open('PolIntSmooth15.fits')[0].header)
    patch_list, artist_list = r.get_mpl_patches_texts(fixed_color)
    for p in patch_list:
        frame4.add_patch(p)
    for t in artist_list:
        frame4.add_artist(t)
    mplim.plot()
    print "clip min, max:", mplim.clipmin, mplim.clipmax

    f = maputils.FITSimage('NormPolIntSmooth15.fits')
    f.set_limits(limx, limy)
    frame5 = fig.add_subplot(rows, cols, 5)
    frame5.set_title(f.filename, y=1.01)
    f = maputils.FITSimage(externalheader=f.hdr, externaldata=np.log10(f.boxdat))
    mplim = f.Annotatedimage(frame5, cmap="spectral", clipmin=-1.9, clipmax=0)
    mplim.Image()
    cb = mplim.Colorbar(fontsize=8)
    cb.set_label(label=units, fontsize=9)
    grat = mplim.Graticule()
    grat.setp_gratline(wcsaxis=0, linestyle=':', zorder=1)
    grat.setp_gratline(wcsaxis=1, linestyle=':', zorder=1)
    grat.setp_ticklabel(plotaxis=['top', 'right'], visible=False)
    grat.setp_ticklabel(wcsaxis=1, fmt='s')   # Exclude seconds in label
    #region file
    r = pyregion.open('region_forHST.reg').as_imagecoord(pf.open('NormPolIntSmooth15.fits')[0].header)
    patch_list, artist_list = r.get_mpl_patches_texts(fixed_color)
    for p in patch_list:
        frame5.add_patch(p)
    for t in artist_list:
        frame5.add_artist(t)
    mplim.plot()
    print "clip min, max:", mplim.clipmin, mplim.clipmax

    f = maputils.FITSimage('POL120V_drz_single_sci.fits')
    f.set_limits(limx, limy)
    frame6 = fig.add_subplot(rows, cols, 6)
    frame6.set_title(f.filename.replace('_', '\_'), y=1.01)
    f = maputils.FITSimage(externalheader=f.hdr, externaldata=np.log10(f.boxdat))
    mplim = f.Annotatedimage(frame6, cmap="spectral", clipmin=-7, clipmax=-4)
    mplim.Image()
    cb = mplim.Colorbar(fontsize=8)
    cb.set_label(label=r'$\log_{10}(cps)$', fontsize=9)
    grat = mplim.Graticule()
    grat.setp_gratline(wcsaxis=0, linestyle=':', zorder=1)
    grat.setp_gratline(wcsaxis=1, linestyle=':', zorder=1)
    grat.setp_ticklabel(plotaxis=['top', 'right'], visible=False)
    grat.setp_ticklabel(wcsaxis=1, fmt='s')   # Exclude seconds in label
    #region file
    r = pyregion.open('region_forHST.reg').as_imagecoord(pf.open('POL120V_drz_single_sci.fits')[0].header)
    patch_list, artist_list = r.get_mpl_patches_texts(fixed_color)
    for p in patch_list:
        frame6.add_patch(p)
    for t in artist_list:
        frame6.add_artist(t)
    mplim.plot()
    print "clip min, max:", mplim.clipmin, mplim.clipmax

    plt.savefig('Vela.pdf')
    plt.close()


    #    #interactive:
    #    f = maputils.FITSimage('StokesUSmooth15.fits')
    #    fig = plt.figure(figsize=(9,7))
    #    frame = fig.add_subplot(1,1,1)
    #    fr2 = fig.add_axes([0.3,0.01,0.4,0.03])
    #    valinit = 1.0
    #    sl = Slider(fr2, "Sigma: ", 0.1, 5.0, valinit=valinit)
    #    sl.on_changed(func)
    #
    #    annim = f.Annotatedimage(frame)
    #    annim.Image()
    #    annim.plot()
    #    func(valinit)
    #    annim.interact_toolbarinfo()
    #    annim.interact_imagecolors()
    #    annim.interact_writepos()
    #
    #    plt.show()


    elapsed = time() - start
    print 'Processing took {0:.1f} minutes'.format(elapsed / 60.)