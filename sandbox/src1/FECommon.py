import numpy

StrippedDown = {
    'galaxyID' : (0, int),
    'x': (1, float),
    'y' : (2, float),
    'z' : (3, float),
    'mag_bc' : (4, float),
    'mag_bB' : (5, float),
}

MSdata = {
    'galaxyID' : (0, int),
    'lastProg' : (1, int),
    'descedantID' : (2, int),
    'haloID' : (3, int),
    'subHaloID' : (4, int),
    'fofID' : (5, int),
    'treeId' : (6, int),
    'firstProg' : (7, int),
    'nextProg' : (8, int),
    'typee' : (9, int),
    'snapnum' : (10, int),
    'redshift' : (11, float),
    'centralMvir' : (12, float),
    'phkey' : (13, int),
    'x': (14, float),
    'y' : (15, float),
    'z' : (16, float),
    'zIndex': (17, int),
    'ix' : (18, int),
    'iy' : (19, int),
    'iz' : (20, int),
    'velX' : (21, float),
    'velY' : (22, float),
    'velZ' : (23, float),
    'np' : (24, int),
    'mvir' : (25, float),
    'rvir': (26, float),
    'vvir' : (27, float),
    'vmax' : (28, float),
    'coldGas' : (29, float),
    'stellarMass' : (30, float),
    'bulgeMass': (31, float),
    'hotGas' : (32, float),
    'ejectedMass' : (33, float),
    'blackholeMass': (34, float),
    'metalsCG' : (35, float),
    'metalsSM' : (36, float),
    'metalsBM': (37, float),
    'metalsHG' : (38, float),
    'metalsEM' : (39, float),
    'sfr' : (40, float),
    'sfrBulge': (41, float),
    'xrayLum' : (42, float),
    'diskRadius' : (43, float),
    'coolingR' : (44, float),
    'mag_bc' : (45, float),
    'mag_vc' : (46, float),
    'mag_rc' : (47, float),
    'mag_ic' : (48, float),
    'mag_kc' : (49, float),
    'mag_bB' : (50, float),
    'mag_vB' : (51, float),
    'mag_rB' : (52, float),
    'mag_iB' : (53, float),
    'mag_kB' : (54, float),
    'mag_bD' : (55, float),
    'mag_vD' : (56, float),
    'mag_rD' : (57, float),
    'mag_iD' : (58, float),
    'mag_kD' : (59, float),
    'massWAge' : (60, float),
    'random': (61, int)}

class Galaxy(object):
    def __init__(self, line = None, trans = MSdata):
        if type(line) == str:
            data = line.split()
            for key,(index, format) in trans.items():
                setattr(self, key, format(data[index]))
            
    def coords(self):
        return numpy.array( (self.x, self.y, self.z) )

    def vel(self):
        return numpy.array( (self.velX, self.velY, self.velZ) )

def iterateGalaxies(filename, trans = MSdata):
    for line in open(filename):
        yield Galaxy(line, trans)

from ConfigParser import ConfigParser

class Config(object):
    def __init__(self, filename, section):
        import sys
        config = ConfigParser()
        config.read(filename)
        for key,value in config.items(section):
            if key == 'filename':
                setattr(self, key, value)
            else:
                setattr(self, key, float(value))

class Logger(object):
    def __init__(self, filename, verbose = False):
        self.file = open(filename, 'w')
        self.verbose = verbose
    
    def write(self, text):
        print >> self.file, text
        if self.verbose: print text
