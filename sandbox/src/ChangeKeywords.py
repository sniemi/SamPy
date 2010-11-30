'''
Created on Dec 4, 2009

@author: niemi
'''
import pyfits as PF
import glob as G

filelist = G.glob('*.fits')

changelist = {'PFLTFILEL': 'coadd_comb_reject_l.fits',
              'PFLTFILEM': 'coadd_comb_reject_m.fits'}

for file in filelist:
    fd = PF.open(file, mode='update')
    phdr = fd[0].header
    hdr1 = fd[1].header

    try:
        if 'M' in phdr['OPT_ELEM']:
            phdr['PFLTFILE'] = changelist['PFLTFILEM']
        else:
            phdr['PFLTFILE'] = changelist['PFLTFILEL']
    except:
        pass
    
    #for key in changelist:
    #    phdr[key] = changelist[key]
        
    fd.close()
    print 'Keywords of file %s have been modified...' % file
    
print 'Script ends...'
