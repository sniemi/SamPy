'''
This script can be used to calculate colour difference for stellar objects.
The colour difference is in STMAG and comparison is to V band.

Created on Oct 6, 2009

@author: Sami-Matias Niemi
'''

import pyraf
from pyraf.iraf import stsdas,hst_calib,synphot
import iraf

__author__ = 'Sami-Matias Niemi'
__version__ = '0.1'


def CalcPhot(temps, waves, window, metallicity, gravity, model, tomag):
    '''
    Calculates the colour difference for a given temperature, gravity,
    metallicity, and wavelength. The window specifies the wavelength
    window which is used around the give wavelength. Model should be either
    ck04models or k93models.
    '''
    results = []
    for temp in temps:
        for wave in waves:
            box = 'box(%i,%i)' % (wave, window)
            nor = 'rn(icat(%s,%i,%f,%f),band(v),0,vegamag)' % (model,temp,metallicity,gravity)
            try:
                tmp = iraf.calcphot(box, nor, tomag, Stdout=1)
            except:
                tmp = 'err'
            results.append([temp, wave, tmp])
    return results

def WriteTable(results):
    '''
    Writes CalcPhot output to a table with clean layout.
    '''
    temp = []
    wave = []
    colo = []
    for line in results:
        t = line[0]
        w = line[1]
        try:
            c = '%13.2f' % float(line[2][-1].split()[-1])
        except:
            c = '   N/A'
        temp.append(t)
        wave.append(w)
        colo.append(c)
    
    fh = open('Table.txt', 'w')
    columns = 0
    for t in temp:
        if t == temp[0]:
            columns += 1
    
    hdr = 'Temp (K)'
    for i in range(columns):
        hdr += '%13i' % wave[i]
    fh.write(hdr + '\n')
    
    rounds = 0
    for temp in temps:
        line = '%8i' % temp
        for i in range(columns):
            line += '%s' % colo[rounds + i]
        fh.write(line + '\n')
        rounds += columns
        
    fh.close()
    

if __name__ == '__main__':     
    
    window = 10
    waves = [1000, 1200, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000]
    #temps = [50000, 30000, 20000, 15000, 10000, 9000, 8000, 7000, 6000, 5000, 4000, 3000]
    temps = [45000, 30000, 20000, 15000, 10000, 9000, 8000, 7000, 6000, 5000, 4000, 3000]
    
    model = 'ck04models' # OLD:'k93models'
    metallicity = 0.0
    gravity = 4.5
    tomag = 'stmag'

    res = CalcPhot(temps, waves, window, metallicity, gravity, model, tomag)
    WriteTable(res)
    