'''
@summary: This script can be used to prepare data for aXe.
The script will create a proper file struture for aXe,
run multidrizzle for direct images, and finally run
SourceExtractor on the drizzled direct images.

@note: This is really badly written, should make a class...

@warning: Not really tested...

@author: Sami-Matias Niemi (niemi@stsci.edu)

@version: 0.1a
'''
import pyfits as PF
from pyraf import iraf
from pyraf.iraf import stsdas, hst_calib, slitless, axe, wfc3
import glob as g
import shutil as s
import os
import sextutils as su

def find_header_info(input_files):
    '''
    Find filter, date of the observation and exposure time information
    from the FITS header. Assumes that this information has been stored
    in the first extension header, like in case of HST.
    @return: Returns a dictionary where each key is the filename and
             value is a list of filter, data-obs and exptime.
    '''
    out = {}
    for file in input_files:
        hdr = PF.open(file)[0].header
        f = os.path.split(file)[1]
        out[f] = [hdr['FILTER'], hdr['DATE-OBS'], hdr['EXPTIME']]
    return out

def find_direct_images(dict, column = 0):
    '''
    Pick out direct images from a dictionary (that could have been
    created using the "find_header_info" function). Assumes that all
    images whose filter names start with an "F" are direct images.
    @return: a list of filenames that are direct images.
    '''
    out = []
    for key in dict:
        if dict[key][column].startswith('F'):
            out.append(key)
    return out

def print_files(headers):
    '''
    Outputs some basic information to the shell.
    '''
    print '\nFILE                            GRATINGS         OBS-DATE             EXPTIME'
    for key in headers:
        st = key + ' '
        for a in headers[key]:
            st += '%20s' % a
        print st

def fixSourceExtractorCatalogue(filter, pivot):
    data = open(filter+'.cat', 'r').readlines()
    s.move(filter+'.cat', filter+'.cat.backup')
    out = open(filter+'.cat', 'w')
    for line in data:
        if 'MAG_AUTO' in line:
            out.write(line.replace('MAG_AUTO', 'MAG_' + pivot))
        else:
            out.write(line)


def make_ds9_regions_file(inputfile, outputfile,
                          size = 10, 
                          xcolumn = 'x_image', ycolumn='y_image'):
    '''
    '''

    data = su.se_catalog(inputfile+'.cat')
    xarray = eval('data.'+xcolumn)
    yarray = eval('data.'+ycolumn)

    out = open(outputfile, 'w')
    for x, y in zip(xarray, yarray):
        circ = 'circle(%f, %f, %f)\n' % (x, y, size)
        out.write(circ)
    out.close()

###############################################################
#input parameters, should be read from a file
#Change these if needed

#path to look files from
input = './nov2010/'

#output directory
out =  './reduced/'

#AxE confs
confs = '/Users/niemi/Desktop/Grisms/confs/'

#SourceExtractro confs
sconfs = '/Users/niemi/Desktop/Grisms/sextractor_defaults/'

#magnitude zero point, needed for SExtractor to calculate
#auto magnitudes, all in AB mags, followed by pivot wavels
filterInformation = {'F140W': [26.46, 'F1392'],
                     'F160W': [25.96, 'F1537'],
                     'F110W': [26.83, 'F1153'],
                     'F125W': [26.25, 'F1249']}

###############################################################

#script starts
if os.path.isdir(out):
    print 'Output directory exists'
else:
    os.mkdir(out)

#find input files
ins = g.glob(input + '*.fits')
ins_headers = find_header_info(ins)

#print all the files
print_files(ins_headers)

#change the working directory
os.chdir(out)

#create the AxE output structre
aXeFolders = ['save', 'IMDRIZZLE', 'CONF',
              'DATA', 'OUTPUT', 'DRIZZLE']
for fold in aXeFolders:
    if not os.path.isdir(fold):
        os.mkdir(fold)

#copy files to save
for f in ins:
    tmp = os.path.split(f)[1]
    if not os.path.isfile('./save/'+tmp):
        s.copy('../'+f, './save/')

#find direct image files
directs = find_direct_images(ins_headers)

#copy config files to right place
for f in g.glob(confs+'*'):
    tmp = os.path.split(f)[1]
    if not os.path.isfile('./CONF/'+tmp):
        s.copy(f, './CONF/')

#copy direct images to ../IMDRIZZLE
for f in directs:
    tmp = os.path.split(f)[1]    
    if not os.path.isfile('./IMDRIZZLE/'+tmp):
        s.copy('./save/'+f, './IMDRIZZLE/')

# find all filters
filters =  set([ins_headers[x][0] for x in ins_headers])

#change directory to ../IMDRIZZLE
os.chdir('./IMDRIZZLE')

#run multidrizzle
multiout = []
for f in filters:
    if f.startswith('F'):
        print '\n\nWill next multidrizzle all %s images' % f
        tmp = [x for x in ins_headers if ins_headers[x][0] == f]
        if len(tmp) < 2:
            print 'Not enough images'
        else:
            #unlearn multidrizzle
            stsdas.multidrizzle.unlearn()
            if os.path.isfile(f):
                'print file %s exists, will not overwrite' % f
            else:
                 #run to ins files
                ins =''
                for x in tmp:
                    ins += x + ','
                stsdas.multidrizzle(ins[:-1], output=f, final_rot = 'INDEF')
                multiout.append(f)

#copy the source extractor confs
for f in g.glob(sconfs+'*.*'):
    s.copy(f, '.')

#solate the science and weight extensions of the co-added images
for f in multiout:
    if os.path.isfile(f+'_drz_sci.fits'):
        print 'Will copy old *drz_sci.fits to tmp'
        s.move(f+'_drz_sci.fits', f+'_drz_sci_tmp.fits')
    if os.path.isfile(f+'_drz_wht.fits'):
        print 'Will copy old *drz_wht.fits to tmp'
        s.move(f+'_drz_wht.fits', f+'_drz_wht_tmp.fits')
    
    iraf.imcopy(f+'_drz.fits[SCI]', f+'_drz_sci.fits')
    iraf.imcopy(f+'_drz.fits[WHT]', f+'_drz_wht.fits')

#run source xtractor
for f in filters:
    if f.startswith('F'):
        mg = filterInformation[f][0]
        cmd = 'sex -c default.sex -WEIGHTIMAGE '+f+'_drz.fits[WHT] '
        cmd += '-MAG_ZEROPOINT ' + str(mg)
        cmd += ' -CATALOG_NAME '+f+'.cat '
        cmd += ' '+f+'_drz_sci.fits'
        print cmd
        os.system(cmd)

#fix source extractor catalogue
for f in filters:
    if f.startswith('F'):
        pv = filterInformation[f][1]
        fixSourceExtractorCatalogue(f, pv)

#make ds9 region files
for f in filters:
    if f.startswith('F'):
        make_ds9_regions_file(f, f+'.reg', size = 10)

#all done
print 'Preparations done...'
