'''
SMN, Aug 30, 2009.
'''
import pyfits as PF
import numpy as N
import datetime as D
import pylab as P
import idlsave

def plot(data):
    for line in data:
        P.semilogy(line[4], line[5], label = line[0] + ' %i' % line[2], lw = 2)
    P.xlabel('Wavelength [AA]')
    P.ylabel('Sensitivity [(count/s/pixel) / (erg/s/cm**2/angstrom)]')
    P.legend()
    P.savefig('sensitivity.pdf')

phot = 'u8k1433ql_phot.fits'
path = '/grp/hst/cdbs/lref/'

newdata = idlsave.read('new_g130_fuv.idl')

new_wave_start = newdata.wi[0]
new_wave_stop = newdata.wi[-1]
ln = 2730
new_wave = N.arange(ln) * (new_wave_stop - new_wave_start) / (ln - 1) + new_wave_start

ns0 = N.interp(new_wave, newdata.wi, newdata.ssx[0])
ns1 = N.interp(new_wave, newdata.wi, newdata.ssx[1])
ns2 = N.interp(new_wave, newdata.wi, newdata.ssx[2])
ns3 = N.interp(new_wave, newdata.wi, newdata.ssx[3])

newphot = [('FUVA', 'G130M', 1055, 'PSA', new_wave, ns1),
           ('FUVB', 'G130M', 1055, 'PSA', new_wave, ns0),
           ('FUVA', 'G130M', 1096, 'PSA', new_wave, ns3),
           ('FUVB', 'G130M', 1096, 'PSA', new_wave, ns2)
           ]

plot(newphot)

#open the old one
fh = PF.open(path+phot)
data  = fh[1].data

#print fh.info()
#print fh[1].header
#print data

#size of the old
nrows_old = data.shape[0]
nrows_old2 = fh[1].header['naxis2']
if nrows_old != nrows_old2:
    print 'ERROR, the number of rows does not match!'
#size of the new table
nrows_new = nrows_old + len(newphot)
#make new fits file from the old data
ofd = PF.HDUList(PF.PrimaryHDU(header = fh[0].header))
hdu = PF.new_table(fh[1].columns, nrows = nrows_new)

#append new data
for x in range(len(newphot)):
    for i in range(len(fh[1].columns)):
        hdu.data.field(i)[nrows_old + x] = newphot[x][i]

#write the output
ofd.append(hdu)
ofd.writeto('new_phot.fits')
fh.close()

#update the first header
fh = PF.open('new_phot.fits', mode = 'update')
hdu = fh[0].header
hdu.add_history('Added some data:')
for line in newphot:
    strg = '%s %s %i' % (line[0], line[1], line[2])
    hdu.add_history(strg)
hdu.add_history('Written at %s UTC.' % D.datetime.utcnow())

fh.close()
