import glob
import os

def fixLigconeRAs(files):
    '''
    Fixes the problem that some lightcones
    had negative RAs. The fix is extemely crude
    one only adds 360 to the RA value.

    :param files: a list of files to be fixed
    :type files: list
    '''

    for filename in files:
        removeFile = True
        fh = open(filename, 'r')
        out = open(filename+'_mod', 'w')
        line = fh.readline()
        while line:
            if line.startswith('#'):
                out.write(line)
            else:
                tmp = line.split()
                ra = float(tmp[2])
                if ra < 0.0:
                    removeFile = False
                    newra = ra + 360.0
                    newstr = '{0:>s} {1:>s} {2:f} {3:>s} {4:>s}\n'.format(tmp[0], tmp[1], newra, tmp[3], tmp[4])
                    out.write(newstr)
            line = fh.readline()

        fh.close()
        out.close()

        if removeFile:
            os.remove(filename+'_mod')
        else:
            print 'File {0:>s} was modified...'.format(filename)
            

if __name__ == '__main__':
    files = glob.glob('*/lightcone.dat')
    fixLigconeRAs(files)

    

