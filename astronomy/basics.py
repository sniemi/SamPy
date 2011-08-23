"""
This module contains basic information of different subjects often needed in astronomy such as conversions from one magnitude system to another.

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu
:version: 0.01
"""

__author__ = 'Sami-Matias Niemi'


def JohnsonToABmagnitudes():
    """
    Returned dictionary values can be used to convert
    Johnson U, B, V, and K bands to Vega system.

    :rtype: dictionary
    """
    out = {}
    out['AB_vega_U'] = 0.729977
    out['AB_vega_B'] = -0.0934
    out['AB_vega_V'] = 0.0112
    out['AB_vega_K'] = 1.854
    return out