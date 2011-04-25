import numpy as np

__author__ = 'Sami-Matias Niemi'


def randomUnitSphere(points=1):
    '''
    This function returns random positions
    on a unit sphere. The number of random
    points returned can be controlled with
    the optional points keyword argument.
    :param points (int): the number of points drawn
    '''

    #get random values u and v
    u = np.random.rand(points)
    v = np.random.rand(points)
    #Convert to spherical coordinates
    #Note that one cannot randomize theta and phi
    #directly because the values would
    #be packed on the poles due to the fact that
    #the area element has sin(phi)!
    theta = 2. * np.pi * u
    phi = np.arccos(2. * v - 1)

    #pack all the results to a dictionary
    out = {'theta': theta,
           'phi': phi,
           'points': points}

    return out