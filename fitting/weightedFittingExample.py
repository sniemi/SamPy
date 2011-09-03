"""
Simple fitting example and how to take into account individual weights.
"""
from scipy.optimize.minpack import curve_fit
import numpy as np
from numpy.random import rand
import pylab

def first_order(x, a0, a1):
    return a0 + a1 * x


def second_order(x, a0, a1, a2):
    return a0 + a1 * x + a2 * (x ** 2)


def third_order(x, a0, a1, a2, a3):
    return a0 + a1 * x + a2 * (x ** 2) + a3 * (x ** 3)

if __name__ == '__main__':
    #Make data
    x = np.arange(10)
    y = x ** 3 + 2.0 * x ** 2 + 3.0 * x + 4.0
    l1 = pylab.plot(x, y, 'b')
    #Introduce scatter
    scatter = (rand(10) - 0.5) * 1e2
    scatter[1] *= 2.1
    scatter[5] *= 2.5
    scatter[7] *= 0.01
    print scatter
    ys = y + scatter
    #Make weight
    weight = scatter

    #Fit without weighting
    popt, pcov = curve_fit(third_order, x, ys)
    #Fit with weighting
    popt1, pcov1 = curve_fit(third_order, x, ys, sigma=weight)
    yfit = third_order(x, popt[0], popt[1], popt[2], popt[3])
    yfit1 = third_order(x, popt1[0], popt1[1], popt1[2], popt1[3])
    l2 = pylab.errorbar(x, ys, yerr=scatter, fmt='go')
    l3 = pylab.plot(x, yfit, linestyle='--', color='r')
    l4 = pylab.plot(x, yfit1, linestyle='--', color='c')
    pylab.legend((l1, l2[0], l3, l4),
        ('Starting Data', 'Scattered Data', 'Unweighted', 'Weighted'), loc='best')

    pylab.xlim(-0.1, 10.3)
    pylab.show()

    #raw_input('Enter')
