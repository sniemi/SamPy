import pyfits as PF
import pylab as P
import numpy as N

if __name__ == '__main__':

    path = '/grp/hst/cdbs/comp/cos/'

    file1 = 'cosncm3_g230lc3000_006_syn.fits'
    file2 = 'cosncm3_g230lc3000_005_syn.fits'

    file3 = 'cosncm3_g230lc2950_006_syn.fits'
    file4 = 'cosncm3_g230lc2950_005_syn.fits'

    data1 =PF.open(path + file1)[1].data
    data2 =PF.open(path + file2)[1].data

    data3 =PF.open(path + file3)[1].data
    data4 =PF.open(path + file4)[1].data

    P.figure(1)
    P.plot(data1.field('WAVELENGTH'), data1.field('THROUGHPUT'), label = file1)
    P.plot(data2.field('WAVELENGTH'), data2.field('THROUGHPUT'), label = file2)
    P.plot(data3.field('WAVELENGTH'), data3.field('THROUGHPUT'), label = file3)
    P.plot(data4.field('WAVELENGTH'), data4.field('THROUGHPUT'), label = file4)
    P.legend()
    P.xlabel('Wavelength')
    P.ylabel('Throughput')

    d1 = data1.field('THROUGHPUT')
    d2 = data2.field('THROUGHPUT')
    mask1 = (d2 != N.nan) & (d1 != N.nan) & (d2 != 0.0)
    rat1 = d1[mask1] / d2[mask1]

    d3 = data3.field('THROUGHPUT')
    d4 = data4.field('THROUGHPUT')
    mask2 = (d3 != N.nan) & (d4 != N.nan) & (d4 != 0.0)
    rat2 = d3[mask2] / d4[mask2]


    P.figure(2)
    P.plot(data1.field('WAVELENGTH')[mask1], rat1, label = 'c3000')
    P.plot(data3.field('WAVELENGTH')[mask2], rat2, label = 'c2950')
    P.xlabel('Wavelength')
    P.ylabel('Ratio (new / old)')
    P.ylim(0.95, 1.05)
    P.legend()
    P.show()
