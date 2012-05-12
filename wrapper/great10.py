"""
This little wrapper can be used to run GREAT10 photon shooting code using multiprocessing.

:author: Sami-Matias Niemi
:contact: smn2@mssl.ucl.ac.uk
"""
import glob as g
import multiprocessing
import subprocess
import os


def work(command):
    return subprocess.call(command, shell=True)


if __name__ == '__main__':
    #system definition
    linux = True

    if linux:
        cores = 16
        bin='/disk/xray10/smn2/euclid-sim/G10/code/makegalimage'
        inputs = g.glob('/disk/xray10/smn2/euclid-sim/G10/cats/*.dat')
    else:
        cores = 4
        bin='/Users/smn2/EUCLID/G10/code/makegalimage'
        inputs = g.glob('/Users/smn2/EUCLID/G10/cats/*.dat')

    needed = []
    #check if FITS file already exists
    for input in inputs:
        if not os.path.isfile(input+'.fits'):
            needed.append(input)

    print 'Will process %i files' %len(needed)

    #use multiprocess pool
    commands = [bin + ' ' + f + ' > /dev/null' for f in needed]
    pool = multiprocessing.Pool(processes=cores)
    pool.map(work, commands)

    print 'All done...'