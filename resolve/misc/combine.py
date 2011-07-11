'''
Simple script to median combine FITS files.
'''
import pyfits as PF
import numpy as np
import glob as g

def combineFITS(files,
                exstension=0):
    '''
    A simple function that median combines FITS files
    '''

    #get data, ignore missing END
    fhs = [PF.open(x, ignore_missing_end=True) for x in files]
    datalist = [x[extension].data for x in fhs]

    #check that the files are of the same size
    if len(set(x.shape for x in datalist)) > 1:
        print 'Images not of same size! Aborted!'
        import sys;
        sys.exit()

    #median combine
    median = np.median(datalist, axis=0)

    #write an output
    hdu = PF.PrimaryHDU(median)
    hdulist = PF.HDUList([hdu])
    hdulist.writeto('combined.fits')


if __name__ == '__main__':
    #find all fits files
    files = g.glob('*.fits')
    #combine files
    combineFITS(files)