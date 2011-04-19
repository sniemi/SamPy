import numpy as np

__author__ = 'Sami-Matias Niemi'


def randomUnitSphere(points=1):
    '''
    This function returns random positions
    on a unit sphere. The number of random
    points returned can be controlled with
    the optional points keyword argument.
    :param points
    '''

    #get random variables
    u = np.random.rand(points)
    v = np.random.rand(points)
    #to spherical coordinates
    #cannot randomize theta and phi
    #directly because the values would
    #be packed to poles otherwise because
    #(the area element has sin(phi)!
    theta = 2. * np.pi * u
    phi = np.arccos(2. * v - 1)

    #pack all the results to a dictionary
    out = {'theta': theta,
           'phi': phi,
           'points': points}

    return out