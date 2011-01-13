'''
Observational constrains related to black hole
masses in galaxies.

@requires: NumPy

@version: 0.1

@author: Sami-Matias Niemi
@contact: niemi@stsci.edu
'''
import numpy as N

#This should be global, as all observational data are in the same place
#Note however that because the data is in Dropbox the absolute path
#may not be the same. Thus the home directory is tracked using the HOME
#environment variable
observation_path = os.getenv('HOME')+'/Dropbox/Research/Observations/'

def MassesHaeringRix():
    '''
    The full data file contains:
    Galaxy Type M_{bh} mbherrp mbherrm mbhexp Ref sigma
    L_{bulge} \Upsilon M_bulge Ref dist
    @return: bluge mass, black hole mass, ellipticals, spirals, S0s
    '''
    file = observation_path + 'haering_rix/table1.dat'
    data = N.loadtxt(file, comments = ';')
    m_bulge = N.log10(data[:,10])
    m_bh = N.log10(data[:,2] * data[:,5])
    ellip = data[:,1] == 0
    s0 = data[:,1] == 1
    spiral = data[:,1] == 2
    return m_bulge, m_bh, ellip, spiral, s0
