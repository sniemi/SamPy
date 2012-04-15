"""
Quick analysis of the simulated data. Returns very simple statistics.

:requires: PyFITS
:requires: NumPy

:author: Sami-Matias Niemi
:contact: smn2@mssl.ucl.ac.uk

:version: 0.1
"""
import pprint
import pyfits as pf
import numpy as np


def calculateStats(data, bias=1032.8):
    """
    Calculates some simple statistics from the data.
    """
    datab = data.copy() - bias

    mean = np.mean(data)
    meanb = np.mean(datab)

    median = np.median(data)
    medianb = np.median(datab)

    std = np.std(data)
    stdb = np.std(datab)

    max = np.max(data)
    maxb = np.max(datab)

    min = np.min(data)
    minb = np.min(datab)

    res = dict(mean=mean, meanb=meanb,
               median=median, medianb=medianb,
               std=std, stdb=stdb,
               max=max, maxb=maxb,
               min=min, minb=minb)

    pprint.pprint(res)

    return res


def calcualateFlux(data, str='meanb', exptime=565, zeropoint=1.70594e10):
    magnitude = - np.log10(data[str] / (exptime * zeropoint)) / 0.4
    microJy = 10**((23.9 - magnitude)/2.5)

    print 'background flux (ABmag, microJy):'
    print magnitude, microJy


if __name__ == '__main__':
    input = 'Q0_01_01_intact.fits'
    data = pf.open(input)[0].data
    print input
    results = calculateStats(data)
    calcualateFlux(results)
    print '\n'

    input = 'cleanImage.fits'
    data = pf.open(input)[0].data
    print input
    results = calculateStats(data)
    calcualateFlux(results)
    print '\n'

    input = 'VISnoBackr.fits'
    data = pf.open(input)[0].data
    print input
    results = calculateStats(data, bias=1000)
    calcualateFlux(results)