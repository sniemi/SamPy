'''
SMN, Aug 30, 2009.
'''
import pyfits as PF
import numpy as N
import datetime as D

disp = 'u8n1751tl_disp.fits'
path = '/grp/hst/cdbs/lref/'

newdisp = [('FUVA', 'G130M', 'PSA', 1055, 2, N.array([1043.5527, 0.0099807, 0., 0.]), 0., 0.),
           ('FUVB', 'G130M', 'PSA', 1055, 2, N.array([890.76997, 0.0099392, 0., 0.]), 0., 0.),
           ('FUVA', 'G130M', 'PSA', 1096, 2, N.array([1084.2128, 0.0099684, 0., 0.]), 0., 0.),
           ('FUVB', 'G130M', 'PSA', 1096, 2, N.array([931.25844, 0.0099357, 0., 0.]), 0., 0.)
            ]

#open the old one
fh = PF.open(path+disp)
data  = fh[1].data

#print fh.info()
#print fh[1].header

#size of the old
nrows_old = data.shape[0]
nrows_old2 = fh[1].header['naxis2']
if nrows_old != nrows_old2:
    print 'ERROR, the number of rows does not match!'

nrows_new = nrows_old + len(newdisp)

#make new fits file from the old data
ofd = PF.HDUList(PF.PrimaryHDU(header = fh[0].header))
hdu = PF.new_table(fh[1].columns, nrows = nrows_new)

#append new data
for x in range(len(newdisp)):
    for i in range(len(fh[1].columns)):
        hdu.data.field(i)[nrows_old + x] = newdisp[x][i]

#write the output
ofd.append(hdu)
ofd.writeto('new_disp.fits')
fh.close()

#update the first header
fh = PF.open('new_disp.fits', mode = 'update')
hdu = fh[0].header
hdu.add_history('Added some new dispersion settings:')
for line in newdisp:
    strg = ''
    for x in line:
        strg += str(x) + ' '
    hdu.add_history(strg)
hdu.add_history('Written at %s UTC.' % D.datetime.utcnow())

fh.close()
