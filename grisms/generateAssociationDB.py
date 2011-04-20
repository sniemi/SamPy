'''
This little script can be used to generate a cPickled
association database that is in the format that the PHLAG
grism pipeline developed by ECF will understand.

The script looks all FITS files in the current working
directory and tries to generate the association database
by matching direct images to grism images. Note that the
matching algorithm is extremely limited and works only if
the direct images and grism images have the same RA or DEC.
Thus, the script is only suitable for the test that will
be carried out in April 2011, as for this test all the
datasets have been hand picked.

This script should not be used unless its limitations
have been understood!
'''
import smnIO.findFiles as f
import pyfits as pf
import cPickle

__author__ = 'Sami-Matias Niemi'
__version__ = 0.01


def createAssociationDB(grismList, directDict,
                        output ='ACSTEST.db'):
    '''
    Email from Martin Kuemmel:
    Concerning the format:
    - Each association (see listing below contains two main entries, the
    first entry (a list)  containing information on the grism images and
    the second a dictionary) containing direct imaging information.

    - The grism image information is a list, which each entry consisting of
     a tuple with four items. The first item is the name of the grism
     image, the second item is the exposure time of the grism image,
     the third item is the name of the associated direct image and the
     fourth item a real number measuring the 'distance' between the grism
     image and the direct image. Very close pairs of grism image - direct
     image have a distance of 0.0. I think there is a very complicated
     formula that measures this distance, however the most important input
     is the pointing on the sky. If a grism and a direct image have the
     same pointing on the sky, they are very close. Also the time
     difference between the direct image and the grism image has some
     influence.

    - The direct image information is a dictionary that contains the filter
     names as keys. For each filter there is a list of tuples with three
     items. The first item is the direct image name, the second item is
     the exposure time and the third item is the overlap with the area covered
     by the grism images of that association. For some reason (I have forgotten),
     this overlap can be more than 1.

    So the two 'dir_min_overlap' that you quote are two different values,
    the first one measuring the distance between the grism image and the
    closest associated direct image (from all possible associated direct
    images, the closest one is chosen), and the second one measuring the
    area overlap with all grism images.

    We did have algorithms and formulas to compute these numbers, but in
    the end it was always some sort of magic with Alberto Micol and Marco
    Lombardi the magicians. I asked Alberto, but he was rather involved in
    NICMOS, and Marco is really far away now, his account at ESO does no
    longer exists and his old computer (standing in front of me) needed a
    new disk some weeks ago.

    So I guess that we can not offer much support on this. In any case,
    WFC3 is a different instrument with 2 complementary grisms and
    different prescriptions for taking associated direct imaging and hence
    a different basis of how data is taken.

    Hope this helped,
    Martin

    ([('J6FL8YKUQ', 764.0, 'J6FL8YKRQ', 0.0),
    ('J6FL8YKWQ', 764.0, 'J6FL8YKRQ', 0.0),
    ('J6FL8YKYQ', 764.0, 'J6FL8YKRQ', 0.0),
    ('J6FL8YL0Q', 764.0, 'J6FL8YKRQ', 0.0),
    ('J6FL8YL2Q', 764.0, 'J6FL8YKRQ', 0.0),
    ('J6FL8YL4Q', 764.0, 'J6FL8YKRQ', 0.0),
    ('J6FL8YL6Q', 764.0, 'J6FL8YKRQ', 0.0),
    ('J6FL8YL8Q', 764.0, 'J6FL8YKRQ', 0.0)],
    {'F850LP':
    [('J8WQ91E8Q', 500.0, 0.89063763040941479),
    ('J8WQ91EAQ', 500.0, 0.89063763040941479),
    ('J8WQ91ECQ', 500.0, 0.89063763040941479),
    ('J6FL7YIDQ', 500.0, 0.97062910394576651),
    ('J6FL8YKRQ', 500.0, 1.011511942107943),
    ('J8WQ91E7Q', 500.0, 0.89063763040941479)]})'''
    out = {}
    tuple = (grismList,
             directDict)
    out['ACSTEST'] = tuple
    print out
    fh = open(output, 'w')
    cPickle.dump(out, fh)
    fh.close()


def findGrismImages(filelist):
    '''
    Finds all direct and grism images from a
    given filelist. Will pull out some information
    such as exposure time and filter from the header.
    Will also record RA and DEC, this could potentially
    be used to calculate the overlap and is currently
    used to match images later.
    '''
    direct = {}
    grism = {}
    for file in filelist:
        fh = pf.open(file)
        hdr0 = fh[0].header
        if 'F' in hdr0['FILTER1']:
            direct[file] = [hdr0['EXPTIME'],
                            hdr0['FILTER1'],
                            hdr0['RA_TARG'],
                            hdr0['DEC_TARG']]
        elif 'F' in hdr0['FILTER2']:
            direct[file] = [hdr0['EXPTIME'],
                            hdr0['FILTER2'],
                            hdr0['RA_TARG'],
                            hdr0['DEC_TARG']]
        else:
            grism[file] = [hdr0['EXPTIME'],
                           hdr0['FILTER1'],
                           hdr0['RA_TARG'],
                           hdr0['DEC_TARG']]
    return direct, grism

def matchDirectImageToGrismImage(direct, grism):
    '''
    Matches direct images to grism images in an extremely
    dummy way. Will just check that either RA or DEC are
    equal. This can potentially lead to crazy results as
    it does not guarantee that there is overlap. Moreover,
    if one has applied a tiny offset to the grism image to
    for example account for the fact that the dispersion
    is always towards the same direction, then this matching
    would fail. One should probably use some header keyword
    information such as POSTARGs together with the RA and DEC
    to find the closest matches. However, for the testing
    that will be performed in April 2011 this dummy way of
    matching should be sufficient.
    '''
    match = {}
    for key1 in direct:
        for key2 in grism:
            if direct[key1][2] == grism[key2][2] or \
                direct[key1][3] == grism[key2][3]:
                #found the exact same coordinates
                #in reality this matching wouldn't
                #be enough as there might be offset
                #so such info should be taken from
                #the header and used
                if key1 in match.keys():
                    match[key1] += [key2, ]
                else:
                    match[key1] = [key2, ]
    return match

def makeDirectImageDictionary(direct, match):
    '''
    Generates a dictionary from the direct image information.
    This dictionary is in the format that ECF used to make
    their association db, so it is more or less ready to be
    pickled. For details, see the comment in createAssociationDB.
    '''
    out = {}
    tmp = []
    for key in match:
        #here we assume that the coverage is full
        #this could/should also be calculated somehow...
        coverage = 1.0
        tmp.append((key.split('_')[0].upper(),
                    direct[key][0], coverage))
    #this assumes that all direct images use the same
    #filter. As this may not be the case, the filters
    #should be matched as well to be on the safe side
    out[direct[direct.keys()[0]][1]] = tmp
    return out

def makeGrismImageList(grism, match):
    '''
    Generates a list of grism images. This list is in the
    format that ECF used to make their association db, so it
    is more or less ready to be pickled. For details,
    see the comment in createAssociationDB.
    '''
    out = []
    for file in grism:
        for key in match:
            if file in match[key]:
                direct = key.split('_')[0].upper()
        #this should be calculated, but we can now
        #assume that the direct image and grism image
        #are with the same pointing
        distance = 0.0
        out.append((file.split('_')[0].upper(),
                    grism[file][0],
                    direct,
                    distance))
    return out
    

if __name__ == '__main__':
    #find all the FITS files in the current working dir
    files = f.findFitsFiles()
    #sort out direct images and grism

    direct, grism = findGrismImages(files)

    #keys are direct images
    match = matchDirectImageToGrismImage(direct, grism)

    #make Direct Image dictionary
    directDict = makeDirectImageDictionary(direct, match)

    #make a list of grism images
    grismList = makeGrismImageList(grism, match)

    #finally make the association DB
    createAssociationDB(grismList, directDict)