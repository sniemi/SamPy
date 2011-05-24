import matplotlib
matplotlib.use('Agg')
matplotlib.rc('text', usetex=True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize=13)
matplotlib.rc('ytick', labelsize=13)
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import os, re
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator, NullFormatter
from matplotlib import cm
#Sami's repo
import db.sqlite
import astronomy.conversions as cv
import sandbox.MyTools as M

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
    ymin = -2.05
    ymax = 2.5
    solid_angle = 100 * 160.
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
                                    H0=H0,
                                    WM=WM)

    #weight each galaxy
    wghtsx = (np.zeros(len(xdata)) + (1. / comovingVol)) / dfx
    wghtsy = (np.zeros(len(ydata)) + (1. / comovingVol)) / dfy

    #no labels, null formatter
    nullfmt = NullFormatter()

    # definitions for the axes
    left, width = 0.1, 0.65
    bottom, height = 0.1, 0.65
    bottom_h = left_h = left + width + 0.02

    rect_scatter = [left, bottom, width, height]
    rect_histx = [left, bottom_h, width, 0.2]
    rect_histy = [left_h, bottom, 0.2, height]

    #make a figure
    fig = plt.figure(figsize=(12, 12))

    axScatter = plt.axes(rect_scatter)
    axHistx = plt.axes(rect_histx)
    axHisty = plt.axes(rect_histy)

    #no labels
    axHistx.xaxis.set_major_formatter(nullfmt)
    axHisty.yaxis.set_major_formatter(nullfmt)

    #the scatter plot
    axScatter.scatter(xdata, ydata,
                      marker='o',
                      s=0.5,
                      c='k')

    #KDE
    x = M.AnaKDE([xdata, ydata])
    x_vec, y_vec, zm, lvls, d0, d1 = x.contour(np.linspace(xmin-0.1, xmax+0.1, 50),
                                               np.linspace(ymin-0.1, ymax+0.1, 50),
                                               return_data=True)
    axScatter.contourf(x_vec, y_vec, zm,
                       levels=np.linspace(0.002, 0.92*np.max(zm), 10),
                       cmap=cm.get_cmap('gist_yarg'),
                       alpha=0.8)

    #draw a line to the detection limit, 5mJy (at 250)
    axScatter.axhline(np.log10(5),
                      color='green',
                      ls='--',
                      lw=1.8)

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
    x2 = axHistx.hist(xdata[ydata > np.log10(5)],
                      bins=xbins,
                      weights=wghtsx[ydata > np.log10(5)],
                      log=True,
                      color='gray',
                      hatch='x')
    #set legend of x histogram
    plt.legend((x1[2][0], x2[2][0]),
               ('All Galaxies', r'$S_{160}> 5\ \mathrm{mJy}$'),
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
    axScatter.xaxis.set_minor_locator(MultipleLocator(0.5 / 5.))
    axScatter.xaxis.set_minor_formatter(NullFormatter())
    axScatter.yaxis.set_minor_locator(MultipleLocator(1. / 5.))
    axScatter.yaxis.set_minor_formatter(NullFormatter())
    #xhist
    axHistx.xaxis.set_minor_locator(MultipleLocator(0.5 / 5.))
    axHistx.xaxis.set_minor_formatter(NullFormatter())
    #yhist
    axHisty.yaxis.set_minor_locator(MultipleLocator(1. / 5.))
    axHisty.yaxis.set_minor_formatter(NullFormatter())

    plt.savefig(output)


def plotFluxRedshiftDistribution(path,
                                 database,
                                 out_folder,
                                 band = 'spire250_obs'):
    query = '''select FIR.%s, FIR.z
    from FIR where
    FIR.%s > 1e-6 and
    FIR.z >= 1.9 and
    FIR.z < 4.1 and
    FIR.%s < 1e5
    ''' % (band, band, band)
    #get data
    data = db.sqlite.get_data_sqlite(path, database, query)
    #convert fluxes to mJy
    flux = np.log10(data[:, 0] * 1e3) # log of mJy
    redshift = data[:, 1]

    #get wavelength
    try:
        wave = re.search('\d\d\d', band).group()
    except:
        #pacs 70 has only two digits
        wave = re.search('\d\d', band).group()

    #xlabels
    xlabel = r'$z$'
    ylabel = r'$\log_{10} ( S_{%s} \ [\mathrm{mJy}] )$' % wave

    #output folder and file name
    output = "%sFluxRedshiftDist%s.png"% (out_folder, wave)

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

    #plotFluxRedshiftDistribution(path, database, out_folder)
    plotFluxRedshiftDistribution(path, database, out_folder, band='pacs160_obs')