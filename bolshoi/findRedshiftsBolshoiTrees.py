'''
This little module can be used to find redshift information from N-body simulation data.

:author: Sami-Niemi
'''
import glob as g
import fileinput as f
#From Sami's repo
import astronomy.conversions as conv


def FindRedshiftInfo(files, columns):
    '''
    Finds redshift information from files when the column
    information has been specified.

    :param: files
    :param: columns
    '''

    scales = []

    #loop over files and save all the scales
    for file in files:
        for line in f.input(file):
            if not line.startswith('#'):
                tmp = line.split()
                scales.append(tmp[columns['scale']])

    #find out individual scales
    individuals = sorted(set(scales))

    #loop over the sorted scales
    for scale in individuals[::-1]:
        print scale, conv.redshiftFromScale(float(scale))

if __name__ == '__main__':
    files = g.glob('/Users/niemi/Desktop/Research/Bolshoi/bolshoi_newisotrees/*.dat')

    columns = {'mvir' : 9,
               'orig_mvir' : 10,
               'phantom' : 8,
               'scale': 0
               }

    FindRedshiftInfo(files[0], columns)