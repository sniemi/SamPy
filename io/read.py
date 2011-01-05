'''
This file contains some helper functions to
parse different data files.

@author: Sami-Matias Niemi
'''
import numpy as N

def readBolshoiDMfile(filename, column, no_phantoms):
    '''
    This little helper function can be used to read
    dark matter halo masses from files produced from
    the merger trees of the Bolshoi simulation.
    @param filename: name of the file
    @param column: which column to grep
    @param no_phantoms: wchich dark matter mass to read
    @return: NumPy array of dark matter halo masses   
    '''
    out = []
    fh = open(filename, 'r')
    line = fh.readline()
    while line:
        if no_phantoms:
            if int(float(line.split()[2])) == 0:
                out.append(float(line.split()[column]))
        else:
            out.append(float(line.split()[column]))
        line = fh.readline()
    return N.array(out)
