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
import numpy as np


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


def NUVgHa(output, out_folder):
    query = '''select g.nuv_mag - d.petroMag_r,
               g.nuv_magerr*g.nuv_magerr + d.petroMagErr_r*d.petroMagErr_r,
               d.h_alpha_flux, d.h_alpha_flux_err
               from dr8data as d, galex as g, RESOLVEmasterfile as r where
               d.h_alpha_flux_err > 0 and  d.h_alpha_flux_err < 1e2 and
               g.nuv_magerr > 0 and g.nuv_magerr < 2 and d.petroMagErr_r > 0 and
               d.petroMagErr_r < 2 and
               r.dr8specobjid = d.specobjid and r.dr7objid = g.sdssid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x = data[:, 0]
    xerr = np.sqrt(data[:, 1])
    y = data[:, 2]
    yerr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(x, y, xerr=xerr, yerr=yerr, ls='None', c='r',
                 marker='o', ms=1.5)

    ax1.set_xlabel(r'NUV - r')
    ax1.set_ylabel(r'$H_{\alpha}$ [1e-17 erg/s/cm$^{2}$/AA]')

    ax1.set_yscale('log')

    P.savefig(out_folder + output)


def grHa(output, out_folder):
    query = '''select d.petroMag_g - d.petroMag_r,
               d.petroMagErr_g*d.petroMagErr_g + d.petroMagErr_r*d.petroMagErr_r,
               d.h_alpha_flux, d.h_alpha_flux_err
               from dr8data as d  where
               d.h_alpha_flux_err > 0 and  d.h_alpha_flux_err < 1e2 and
               d.petroMagErr_r > 0 and d.petroMagErr_r < 0.1 and
               d.petroMagErr_g > 0 and d.petroMagErr_g < 0.1'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x = data[:, 0]
    xerr = np.sqrt(data[:, 1])
    y = data[:, 2]
    yerr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(x, y, xerr=xerr, yerr=yerr, ls='None', c='r',
                 marker='o', ms=1.5)

    ax1.set_xlabel(r'g - r')
    ax1.set_ylabel(r'$H_{\alpha}$ [1e-17 erg/s/cm$^{2}$/AA]')

    ax1.set_yscale('log')
    ax1.set_xlim(-0.1, 1.8)

    P.savefig(out_folder + output)


def grR23(output, out_folder):
    query = '''select d.petroMag_g - d.petroMag_r,
               d.petroMagErr_g*d.petroMagErr_g + d.petroMagErr_r*d.petroMagErr_r,
               (d.oii_3726_flux + d.oiii_4959_flux + d.oiii_5007_flux)/d.h_beta_flux
               from dr8data as d  where
               d.petroMagErr_r > 0 and d.petroMagErr_r < 0.2 and
               d.petroMagErr_g > 0 and d.petroMagErr_g < 0.2 and
               d.oii_3726_flux > 0 and d.oiii_4959_flux > 0 and
               d.oiii_5007_flux > 0 and d.h_beta_flux > 0 and
               d.oii_3726_flux < 1e6 and d.oiii_4959_flux < 1e6 and
               d.oiii_5007_flux < 1e6 and d.h_beta_flux < 1e6'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x = data[:, 0]
    xerr = np.sqrt(data[:, 1])
    y = np.log10(data[:, 2])
    #yerr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(y, x, yerr=xerr, ls='None', c='r', marker='o', ms=1.5)

    ax1.set_ylabel(r'g - r')
    ax1.set_xlabel(r'log (R$_{23}$)')

    P.savefig(out_folder + output)


def grmetallicity(output, out_folder):
    query = '''select d.petroMag_g - d.petroMag_r,
               d.petroMagErr_g*d.petroMagErr_g + d.petroMagErr_r*d.petroMagErr_r,
               (d.oii_3726_flux + d.oiii_4959_flux + d.oiii_5007_flux)/d.h_beta_flux
               from dr8data as d  where
               d.petroMagErr_r > 0 and d.petroMagErr_r < 0.15 and
               d.petroMagErr_g > 0 and d.petroMagErr_g < 0.15 and
               d.oii_3726_flux > 0 and d.oiii_4959_flux > 0 and
               d.oiii_5007_flux > 0 and d.h_beta_flux > 0 and
               d.oii_3726_flux < 1e7 and d.oiii_4959_flux < 1e7 and
               d.oiii_5007_flux < 1e7 and d.h_beta_flux < 1e7'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    x = data[:, 0]
    xerr = np.sqrt(data[:, 1])
    y = np.log10(data[:, 2])
    #from Tremonti et al. 2004, ApJ, 613, 898
    met = 9.185 - 0.313*y - -0.264*y**2 - 0.321*y**3

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(x, met, xerr=xerr, ls='None', c='r', marker='o', ms=1.5)

    ax1.set_xlabel(r'g - r')
    ax1.set_ylabel(r'12 + log(O/H)')

    ax1.set_ylim(6.8, 9.4)
    ax1.set_xlim(0.0, 1.1)

    P.savefig(out_folder + output)


if __name__ == '__main__':
    path = '/srv/one/sheila/sniemi/catalogs/'
    out_folder = '/srv/one/sheila/sniemi/plots/'
    db = 'catalogs.db'
    type = '.pdf'

    print 'Begin plotting'
    print 'Input DB: ', path + db

    #NUVgHa('BCgalaxiesSampleSel3' + type, out_folder)
    #grHa('BCgalaxiesSampleSel4' + type, out_folder)
    #grR23('BCgalaxiesSampleSel5' + type, out_folder)
    grmetallicity('BCgalaxiesSampleSel6' + type, out_folder)

#    query = '''select sd.petroMag_g - sd.petroMag_r, sd.ew, sd.ewErr from dr7data as sd'''
#    xlab = r'g - r'
#    ylab = r'$EW(\mathrm{H}_{\alpha})$'
#    simplePlot(query, xlab, ylab, 'BCgalaxiesSampleSel1' + type, out_folder)
#
#    query = '''select sd.petroMag_u - sd.petroMag_z, sd.ew, sd.ewErr from dr7data as sd'''
#    xlab = r'u - z'
#    ylab = r'$EW(\mathrm{H}_{\alpha})$'
#    simplePlot(query, xlab, ylab, 'BCgalaxiesSampleSel2' + type, out_folder)

    print 'All done'
