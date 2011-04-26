'''
This script can be used to run aXe.

'''
import pyfits as PF
from pyraf import iraf
from pyraf.iraf import stsdas, hst_calib, slitless, axe, wfc3
import glob as g
import shutil as s
import os

def generate_input_image_list(filter, grism):
    '''
    Format : [name of grism image] [object catalogue] [name of direct image]
    @todo: this is not robust and may find wrong images!!! Should be redone!
    '''
    gr = {}
    im = {}
    dr_image = {}

    #find all grism images
    flts = g.glob('./save/*_flt.fits')
    for f in flts:
        hdr = PF.getheader(f, 0)
        if grism in hdr['FILTER']:
            gr[f] = hdr['DATE-OBS']
        else:
            im[f] = hdr['DATE-OBS']

    #find the closest direct image
    for gt in gr:
        for i in im:
            if gr[gt] == im[i]:
                #match
                dr_image[gt] = i

    out = open(filter+'.lis', 'w')
    for gt in gr:
        line = gt[7:] + ' ' + gt.replace('.fits', '_1.cat')[7:] + ' '
        line += dr_image[gt][7:] + '\n'
        out.write(line)
    out.close()
    
if __name__ == '__main__':

    ##############################################################
    #Change these if needed

    #path to look files from
    input = './reduced/'

    input_catalog = 'F160W'

    grism = 'G141'

    conf = 'WFC3.IR.G141.V1.0.conf'

    sky = 'WFC3.IR.G141.sky.V1.0.fits'

    ###############################################################

    #change the working directory
    os.chdir(input)

    #create the AxE output structre
    aXeFolders = ['save', 'IMDRIZZLE', 'CONF',
                  'DATA', 'OUTPUT', 'DRIZZLE']
    for fold in aXeFolders:
        if not os.path.isdir(fold):
            print 'No aXe file structure in ', input
            print 'Cannot continue... will exit.'
            import sys; sys.exit()

    #build input list
    generate_input_image_list(input_catalog, grism)

    #run axe preprations

    #copy files around
    s.copy(input_catalog+'.lis', './IMDRIZZLE/')
    for a in g.glob('./save/*.fits'):
        s.copy(a, './DATA/'+a[7:])
    for a in g.glob('./IMDRIZZLE/i*.cat'):
        s.copy(a, './DATA/'+a[12:])

    #note: one could change the dimensions in
    axe.iolprep('./IMDRIZZLE/'+input_catalog+'_drz.fits', './IMDRIZZLE/'+input_catalog+'.cat', dimension_info='+100,0,0,0')

    #run axeprep
    axe.axeprep(input_catalog+'.lis', conf, backgr='yes', backims=sky, norm='no')

    #run axecore
    axe.axecore.unlearn()
    axe.axecore(input_catalog+'.lis', conf, extrfwhm='4.0', drzfwhm='3.0', back='no',
                backfwhm='0.0', orient='no', slitless_geom='no', cont_model='gauss',
                sampling='drizzle')

    #combining dithered exposures
    axe.drzprep.unlearn()
    axe.drzprep(input_catalog+'.lis', conf, back='no')

    #run the aXe drizzle
    axe.axedrizzle.unlearn()
    axe.axedrizzle(input_catalog+'.lis', conf, '4.0 3.0', back='no', driz_separate='yes',
                   combine_nsigmas='4.0 3.0', driz_cr_snr='5.0 4.0', driz_cr_grow='1',
                   driz_cr_scale='1.2 0.7')


    print 'All done'
