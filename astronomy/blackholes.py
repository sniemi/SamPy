"""
Observational constrains and simulational results related to black hole masses.

:requires: NumPy

:version: 0.1

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu
"""
import os
import numpy as np

#This should be global, as all observational data are in the same place
#Note however that because the data is in Dropbox the absolute path
#may not be the same. Thus the home directory is tracked using the HOME
#environment variable
observation_path = os.getenv('HOME') + '/Dropbox/Research/Observations/'

def MassesHaeringRix():
    """
    The full data file contains:
    Galaxy Type :math:`M_{bh}` mbherrp mbherrm mbhexp Ref sigma

    .. math::

       L_{bulge} \\Upsilon M_bulge Ref dist

    :return: bulge mass, black hole mass, ellipticals, spirals, S0s
    :rtype: a list
    """
    file = observation_path + 'haering_rix/table1.dat'
    data = np.loadtxt(file, comments=';')
    m_bulge = np.log10(data[:, 10])
    m_bh = np.log10(data[:, 2] * data[:, 5])
    ellip = data[:, 1] == 0
    s0 = data[:, 1] == 1
    spiral = data[:, 1] == 2
    return m_bulge, m_bh, ellip, spiral, s0


def MarconiMassFunction(const=0.362216):
    """
    Marconi et al. BHMF -- columns::

        (1)  Log_{10}[ M_bh / M_sun ]
        (2)  Log_{10}[-1sigma phi(M_bh)]
        (3)  Log_{10}(phi(M_bh)) == dN / [dV*dln(M_bh)], i.e.
             n(M_bh) in Mpc^{-3}*ln(M_bh)^{-1} (number per interval in
              natural log(M_bh))
             -- if you want what is more typically plotted, i.e. number
              per log_{10} interval in M_bh, then you need to multiply
              phi by ln[10], or add Log_{10}(ln[10]) = 0.362216 to the value of
              Log_{10}[Phi] given below
        (4)  log_{10}[+1sigma phi(M_bh)]

    :param constant: ?
    type constant: float

    :return: a list of black hole mass function parameters
    :rtype: a list
    """
    file = observation_path + 'phopkins/rachel_bhmf_data.dat'
    data = np.loadtxt(file, comments=';')
    phi_low = data[:, 1] + const
    phi_med = data[:, 2] + const
    phi_high = data[:, 3] + const
    return data[:, 0], phi_low, phi_med, phi_high