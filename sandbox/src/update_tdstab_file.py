'''
SMN, Aug 30, 2009.
'''
import pyfits as PF
import numpy as N
import datetime as D

tds = 'u7d20377l_tds.fits'
path = '/grp/hst/cdbs/lref/'

#open the old one
fh = PF.open(path+tds)
data  = fh[1].data

#print fh.info()
#print fh[1].header

time = data[0][6]
slope = N.zeros(len(data[0][7]))
inter = N.ones(len(data[0][8]))
text = 'INFLIGHT 01/09/2009 01/05/2010'

ln = 60
wave_a = N.arange(ln) * (1500. - 937.) / (ln - 1) + 937.
wave_b = N.arange(ln) * (1400. - 896.) / (ln - 1) + 896. 

#new data
newdata = [('G130M', 'PSA', 'FUVA', ln, 3, wave_a, time, slope, inter, text),
           ('G130M', 'PSA', 'FUVB', ln, 3, wave_b, time, slope, inter, text)
           ]

for x, line in enumerate(data):
    if line[0] == 'G130M' and line[1] == 'PSA' and line[2] == 'FUVA':
        data[x] = newdata[0]
    if line[0] == 'G130M' and line[1] == 'PSA' and line[2] == 'FUVB':
        data[x] = newdata[1]

#update the first header
hdu = fh[0].header
hdu.add_history('updated G130M wavelength range to cover the new settings.')
hdu.add_history('Written at %s UTC.' % D.datetime.utcnow())

fh.writeto('new_tds.fits')
fh.close()
