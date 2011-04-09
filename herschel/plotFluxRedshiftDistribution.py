import matplotlib
matplotlib.use('Agg')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize = 13)
matplotlib.rc('ytick', labelsize = 13)
matplotlib.rc('axes', linewidth = 1.2)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, NullFormatter

#Sami's repo
import db.sqlite
import astronomy.conversions as cv

__author__ = 'Sami-Matias Niemi'
__version__ = 0.1


def scatterHistograms(xdata,
                      ydata,
                      xlabel,
                      ylabel,
                      output):
    '''
    This functions generates a scatter plot and
    projected histograms to both axes.
    '''
    #constants
    xmin = 2.0
    xmax = 4.0
    ymin = 1e-2
    ymax = 80
    solid_angle = 100*160.
    H0 = 70.0
    WM = 0.28

    #xbins and ybins
    xbins = np.linspace(xmin, xmax, 30)
    ybins = np.linspace(ymin, ymax, 20)
    dfx = xbins[1] - xbins[0]
    dfy = ybins[1] - ybins[0]

    #calculate volume
    comovingVol = cv.comovingVolume(solid_angle,
                                    xmin,
                                    xmax,
                                    H0 = H0,
                                    WM = WM)

    #weight each galaxy
    wghtsx = (np.zeros(len(xdata)) + (1./comovingVol)) / dfx
    wghtsy = (np.zeros(len(ydata)) + (1./comovingVol)) / dfy

    #no labels, null formatter
    nullfmt = NullFormatter()

    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left+width+0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]

    #make a figure
    fig = plt.figure(figsize=(12,12))

    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)

    #no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    #the scatter plot
    axScatter.scatter(xdata, ydata,
                      marker='o',
                      s = 2,
                      c='k')

    #draw a line to the detection limit, 5mJy (at 250)
    axScatter.axhline(5,
                      color='green',
                      ls = '--',
                      lw = 1.8)

    #scatter labels
    axScatter.set_xlabel(xlabel)
    axScatter.set_ylabel(ylabel)

    #set scatter limits
    axScatter.set_xlim(xmin, xmax)
    axScatter.set_ylim(ymin, ymax)

    #make x histogram
    x1 = axHistx.hist(xdata,
                      bins=xbins,
                      weights=wghtsx,
                      log=True,
                      color='gray')
    x2 = axHistx.hist(xdata[ydata > 5],
                      bins=xbins,
                      weights=wghtsx[ydata > 5],
                      log=True,
                      color='gray',
                      hatch='x')
    #set legend of x histogram
    plt.legend((x1[2][0], x2[2][0]),
               ('All Galaxies', r'$S_{250}> 5\ \mathrm{mJy}$'),
               shadow=False,
               fancybox=False,
               bbox_to_anchor=(0.01, 1.34),
               loc=2,
               borderaxespad=0.)
    #make y histogram
    axHisty.hist(ydata,
                 bins=ybins,
                 orientation='horizontal',
                 weights=wghtsy,
                 log=True,
                 color='gray')

    #set histogram limits
    axHistx.set_xlim(axScatter.get_xlim())
    axHistx.set_ylim(1e-7, 1e-1)
    axHisty.set_ylim(axScatter.get_ylim())
    axHisty.set_xlim(4e-9, 1e-2)

    #set histogram labels
    axHistx.set_ylabel(r'$\frac{\mathrm{d}N}{\mathrm{d}z} \quad [\mathrm{Mpc}^{-3} \  \mathrm{dex}^{-1}]$')
    axHisty.set_xlabel(r'$\frac{\mathrm{d}N}{\mathrm{d}S} \quad [\mathrm{Mpc}^{-3} \  \mathrm{dex}^{-1}]$')

    #remove the lowest ticks from the histogram plots
    #axHistx.set_yticks(axHistx.get_yticks()[:-1])
    #axHisty.set_xticks(axHisty.get_xticks()[:-1])

    #set minor ticks
    axScatter.xaxis.set_minor_locator(MultipleLocator(2/5.))
    axScatter.xaxis.set_minor_formatter(NullFormatter())
    axScatter.yaxis.set_minor_locator(MultipleLocator(20/5.))
    axScatter.yaxis.set_minor_formatter(NullFormatter())

    plt.savefig(output)

def plotFluxRedshiftDistribution(path,
                                 database,
                                 out_folder):

    query = '''select FIR.spire250_obs, FIR.z
    from FIR where
    FIR.spire250_obs > 1e-6 and
    FIR.z >= 2 and
    FIR.z < 4.0 and
    FIR.spire250_obs < 1e5
    '''
    #get data
    data = db.sqlite.get_data_sqlite(path, database, query)
    #convert fluxes to mJy
    flux = data[:,0]*1e3 # in mJy
    redshift = data[:,1]

    #xlabels
    xlabel = r'$z$'
    ylabel = r'$S_{250} \quad [\mathrm{mJy}]$'

    #output folder and file name
    output = "{0:>s}FluxRedshiftDist.png".format(out_folder)

    #generate the plot
    scatterHistograms(redshift,
                      flux,
                      xlabel,
                      ylabel,
                      output)

if __name__ == '__main__':
    #find the home directory, because the output is to dropbox
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')

    #constants
    #path = hm + '/Dropbox/Research/Herschel/runs/reds_zero_dust_evolve/'
    path = hm + '/Research/Herschel/runs/big_volume/'
    database = 'sams.db'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/flux_dist/'

    plotFluxRedshiftDistribution(path, database, out_folder)