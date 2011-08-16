"""
Basic statistics functions

:requires: NumPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import numpy as np

def chiSquare(model, obs):
    """
    Simple chi**2:
    Sum (observed_frequency - expected_theoretical_frequency)**2 / theoretical_expected_frequency
    calculation

    :param: model
    :param: obs, observed data

    :return: chi**2
    ;rtype: float
    """
    r = np.sum((obs - model)**2 / model)
    return r