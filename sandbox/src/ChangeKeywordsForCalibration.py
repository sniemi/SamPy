'''
Created on Dec 4, 2009

@author: niemi
'''
import pyfits as PF
import glob as G

filelist = G.glob('*raw*.fits')

changelist = {'LAMPTAB': '../nuv_smov1_r_lamp.fits',
              'DISPTAB': '../nuv_disp_smov_1.fits'}

for file in filelist:
    fd = PF.open(file, mode='update')
    phdr = fd[0].header
    hdr1 = fd[1].header

    for key in changelist:
        phdr[key] = changelist[key]
        
    fd.close()
    print 'Keywords of file %s have been modified...' % file
    
print 'Script ends...'
