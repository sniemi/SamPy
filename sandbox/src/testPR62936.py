'''
@author: Sami-Matias Niemi
'''

import sys
import pyfits as PF

basename = sys.argv[1]

filelist = [basename + '_rawtag_a.fits',
            basename + '_corrtag_a.fits',
            basename + '_rawtag_b.fits',
            basename + '_corrtag_b.fits',
            basename + '_lampflash.fits']

for file in filelist:
    try:
        header = PF.open(file)[1].header
        data = PF.open(file)[1].data
    except:
        print 'Cannot open file %s...' % file
        break
    
    print '\nFile: ', file
    
    try:
        print 'GLOBRATE = ', header['GLOBRATE']
    except: pass
    
    try:
        print 'GLOBRT_A = ', header['GLOBRT_A']
        print 'GLOBRT_B = ', header['GLOBRT_B']
    except: pass
    
    for key in header.ascardlist().keys():
        if 'SHIFT1' in key:
            print key, header[key]
        if 'SHIFT2' in key:
            print key, header[key]
        if 'DPIXEL' in key:
            print key, header[key]

#for line in data:
#    error = False
#    for x in range(3,7):
#        if len(str(abs(line[x]-int(line[x]))))-2 != 4: error = True
#    if error: print 'No 4 decimals: ', line