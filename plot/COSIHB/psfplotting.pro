;This script is part of the COS instrument HB plotting 
;Makes a surface plot around the PSF

;Change these for different file and position
filename = './data/laa701a8q_flt.fits'
extension = 1
centrex = 485
centrey = 280
displacement = 5

;calculates the area to be shown
xmin = centrex - displacement
xmax = centrex + displacement

ymin = centrey - displacement
ymax = centrey + displacement

;reads data
data = mrdfits(filename, extension)
imgdata = data[xmin:xmax, ymin:ymax]

set_plot, 'ps'
device, filename='./Graphics/COSImagingPSF.ps', /encapsulated, xsize=8, ysize=10, /inches, bits_per_pixel=8
surfr, ax = 15, az = 45
;plots contours smoothed
smoothedContour = min_curve_surf(imgdata)
contour, imgdata, nlevels=5, /t3d, zvalue=0.0, xtitle='X Pixels', ytitle='Y Pixels',xthick=3, ythick=3, zthick=3, charsize=2,/fill
contour, imgdata, nlevels=5, /t3d, zvalue=0.0, xtitle='X Pixels', ytitle='Y Pixels',xthick=3, ythick=3, zthick=3, charsize=2, /overplot
;overplots surface
surface, imgdata, /t3d, /noerase, zstyle=1, xtitle='X Pixels', ytitle='Y Pixels',xthick=3, ythick=3, zthick=3, charsize=2, ztitle='Counts / s', thick=3, zrange=[0, max(imgdata) + 5], charthick=3
device, /close_file

device, filename='./Graphics/COSImagingPSFshade_surf.ps', /encapsulated, xsize=8, ysize=10, /inches, bits_per_pixel=8
loadct, 15
set_shading, light=[1, 1, 1]
shade_surf, imgdata, charsize=2, xtitle='X Pixels', ytitle='Y Pixels', ztitle='Counts / s', thick=3, zrange=[0, max(imgdata)+5], zthick=3, ythick=3, xthick=3, charthick=3, pixels=1500, ax = 25, az = 35
surface, imgdata, /noerase, charsize=2, xtitle='X Pixels', ytitle='Y Pixels', ztitle='Counts / s', thick=3, zrange=[0, max(imgdata)+5], zthick=3, ythick=3, xthick=3, charthick=3, pixels=1500, ax = 25, az = 35
device, /close_file

device, filename='./Graphics/COSImagingPSFNormalized.ps', /encapsulated, xsize=8, ysize=10, /inches
surface, imgdata/max(imgdata), charsize=2, zstyle=1, xtitle='X Pixels', ytitle='Y Pixels', ztitle='Normalized Counts', thick=3, zrange=[0, 1], zthick=3, ythick=3, xthick=3, charthick=3, pixels=1500, ax = 15, az = 45
device, /close_file


exit
