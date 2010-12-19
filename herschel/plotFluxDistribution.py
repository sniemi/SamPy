import matplotlib
matplotlib.use('PS')
matplotlib.rc('text', usetex = True)
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize = 13) 
matplotlib.rc('ytick', labelsize = 13) 
matplotlib.rc('axes', linewidth = 1.2)
matplotlib.rcParams['legend.fontsize'] = 12
matplotlib.rcParams['legend.handlelength'] = 5
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import numpy as N
import pylab as P
import os
#Sami's repo
import db.sqlite
import astronomy.conversions as cv

def plot_flux_dist(table, zmin, zmax, depths, colname,
                   path, database, out_folder,
                   solid_angle = 10*160.,
                   fluxbins = 22,
                   ymin = 1e-7, ymax = 1,
                   bins = 8, H0 = 70.0, WM=0.28):
    
    query = '''select %s from %s where %s.z >= %.4f and %s.z < %.4f
             and FIR.spire250_obs < 1e4''' % \
            (colname, table, table, zmin, table, zmax)
    #get fluxes in mJy
    fluxes = db.sqlite.get_data_sqlite(path, database, query)*1e3

    #mass bins
    fd = (zmax - zmin) / float(bins)
    #number of rows for subplots
    rows = int(N.sqrt(bins))
    #min and max x values
    xmin = 0.0
    xmax = 50
    fbins = N.linspace(xmin, xmax, fluxbins)
    df = fbins[1] - fbins[0]
    
    #calculate volume
    comovingVol = cv.comovingVolume(solid_angle, 0, zmax,
                                    H0 = H0, WM = WM)
    #weight each galaxy
    wghts = (N.zeros(len(fluxes)) + (1./comovingVol)) / df    
    
    #make the figure
    fig = P.figure()
    P.subplots_adjust(wspace = 0.0, hspace = 0.0)

    ax = fig.add_subplot(int(bins/rows)-1, rows + 1, 1)

    ax.hist(fluxes, bins = fbins,
            log = True,
            weights = wghts)
    if depths.has_key(colname):
        P.axvline(depths[colname], color = 'g',
                  ls = '--')

    P.text(0.5, 0.9,
           r'$ %.1f \leq z < %.1f $' % (zmin, zmax),
           horizontalalignment='center',
           verticalalignment='center',
           transform = ax.transAxes,
           fontsize = 12)
    
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    
    ax.set_xticklabels([])
    ax.set_yticks(ax.get_yticks()[:-1])
    
    
    #redshift limited plots
    zm = zmin
    for i in range(bins):
        zmax = zm + fd

        query = '''select %s from %s where %s.z >= %.4f and %s.z < %.4f
                and FIR.spire250_obs < 1e4''' % \
                (colname, table, table, zm, table, zmax)        

        fluxes = db.sqlite.get_data_sqlite(path, database, query)*1e3

        #calculate volume
        comovingVol = cv.comovingVolume(solid_angle, zm, zmax, 
                                        H0 = H0, WM = WM)
        #weight each galaxy
        wghts = (N.zeros(len(fluxes)) + (1./comovingVol)) / df
    

        ax = fig.add_subplot(int(bins/rows)-1, rows+1, i+2)
          
        ax.hist(fluxes, bins = fbins,
                log = True,
                weights = wghts)
        if depths.has_key(colname):
            P.axvline(depths[colname], color = 'g',
                      ls = '--')

        P.text(0.5, 0.9,
               r'$ %.1f \leq z < %.1f $' % (zm, zmax),
               horizontalalignment='center',
               verticalalignment='center',
               transform = ax.transAxes,
               fontsize = 12)

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)

        if i == 2 or i == 5:
            ax.set_yticks(ax.get_yticks()[:-1])
        else:
            ax.set_yticklabels([])

        if i == 5 or i == 6 or i == 7:
            ax.set_xticks(ax.get_xticks()[:-1])
        else:
            ax.set_xticklabels([])
        
        if i == 6:
            ax.set_xlabel(r'$S_{250}$ [mJy]')

        if i == 2:
            ax.set_ylabel(r'$\frac{dN}{dS}$ [Mpc$^{-3}$  dex$^{-1}$]')

        zm = zmax

    #save figure
    P.savefig(out_folder + 'FluxDist250.ps')
    P.close()

if __name__ == '__main__':
    #constants
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero/'
    database = 'sams.db'
    out_folder = hm + '/Dropbox/Research/Herschel/plots/flux_dist/'
    #5sigma limits derived by Kuang
    depths = {'pacs100_obs': 1.7,
              'pacs160_obs': 4.5,
              'spire250_obs': 5.0,
              'spire350_obs': 9.0,
              'spire500_obs': 10.0
              }
    #passbands to be plotted
#    bands = ['pacs70_obs',
#             'pacs100_obs',
#             'pacs160_obs',
#             'spire250_obs',
#             'spire350_obs',
#             'spire500_obs']
    bands = ['spire250_obs']

    #plot the flux distributions
    for band in bands:
        plot_flux_dist('FIR', 0.0, 4.0, depths,
                       band, path, database,
                       out_folder)
