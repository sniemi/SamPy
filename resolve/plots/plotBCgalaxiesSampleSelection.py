import matplotlib
matplotlib.use('PDF')
matplotlib.rcParams['font.size'] = 17
matplotlib.rc('xtick', labelsize=14)
matplotlib.rc('axes', linewidth=1.1)
matplotlib.rcParams['legend.fontsize'] = 11
matplotlib.rcParams['legend.handlelength'] = 3
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import pylab as P
from matplotlib import cm
import SamPy.db.sqlite as sq



def simplePlot(query, xlabel, ylabel, output, out_folder):
    #get data, all galaxies
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    col = data[:, 0]
    ew = data[:, 1]
    ewerr = data[:, 2]

    #make the figure
    fig = P.figure()
    fig.subplots_adjust(left=0.09, bottom=0.08,
                        right=0.93, top=0.95,
                        wspace=0.0, hspace=0.0)
    ax1 = fig.add_subplot(111)

    ax1.errorbar(col, ew, yerr=ewerr, ls='None', marker='s', ms=2)

    ax1.set_xlabel(xlabel)
    ax1.set_ylabel(ylabel)
    
    P.savefig(out_folder + output)



if __name__ == '__main__':

    path = '/srv/one/sheila/sniemi/catalogs/'
    out_folder = '/srv/one/sheila/sniemi/plots/'
    db = 'catalogs.db'
    type = '.pdf'

    print 'Begin plotting'
    print 'Input DB: ', path + db

    query = '''select sd.petroMag_g - sd.petroMag_r, sd.ew, sd.ewErr from dr7data as sd'''
    xlab = r'g - r'
    ylab = r'$EW(\mathrm{H}_{\alpha})$'
    simplePlot(query, xlab, ylab,'BCgalaxiesSampleSel1'+type, out_folder)

    query = '''select sd.petroMag_u - sd.petroMag_z, sd.ew, sd.ewErr from dr7data as sd'''
    xlab = r'u - z'
    ylab = r'$EW(\mathrm{H}_{\alpha})$'
    simplePlot(query, xlab, ylab,'BCgalaxiesSampleSel2'+type, out_folder)

    print 'All done'
