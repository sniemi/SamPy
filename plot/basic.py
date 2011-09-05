"""
=======================
Basic Plotting Routines
=======================
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter

__author__ = 'Sami-Matias Niemi'
__version__ = 0.1


def scatterHistograms(xdata,
                      ydata,
                      xlabel,
                      ylabel,
                      binwidth,
                      output):
    """
    This functions generates a scatter plot and projected histograms to both axes.
    """
    nullfmt = NullFormatter() # no labels

    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left+width+0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]

    # start with a Figure
    #plt.figure(1, figsize=(8,8))
    fig = plt.figure()

    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)

    #no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    #the scatter plot
    axScatter.scatter(xdata, ydata)

    # now determine nice limits by hand:
    #binwidth = 0.25
    xymax = np.max([np.max(np.fabs(xdata)), np.max(np.fabs(ydata))])
    lim = (int(xymax/binwidth) + 1) * binwidth

    #scatter labels
    axScatter.set_xlabel(xlabel)
    axScatter.set_ylabel(ylabel)

    #set scatter limits
    axScatter.set_xlim((-lim, lim))
    axScatter.set_ylim((-lim, lim))

    bins = np.arange(-lim, lim + binwidth, binwidth)
    axHistx.hist(xdata, bins=bins)
    axHisty.hist(ydata, bins=bins, orientation='horizontal')

    axHistx.set_xlim(axScatter.get_xlim())
    axHisty.set_ylim(axScatter.get_ylim())

    plt.savefig(output)
