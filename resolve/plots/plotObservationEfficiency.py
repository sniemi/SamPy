import matplotlib
matplotlib.use('PDF')
matplotlib.rcParams['font.size'] = 15
matplotlib.rc('xtick', labelsize=13)
matplotlib.rc('axes', linewidth=1.1)
matplotlib.rcParams['legend.fontsize'] = 10
matplotlib.rcParams['legend.handlelength'] = 3
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
import numpy as np
import pylab as P
from matplotlib import cm
import SamPy.db.sqlite as sq


def PlotGALEXNUV(output, out_folder):
    query = '''select g.nuv_mag, g.nuv_magerr, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, galex as g, galex_distinct as gt
               where o.flag = "C" and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and k.name = r.name and
               r.dr7objid = gt.sdssid and
               gt.sdssid = g.sdssid
               group by k.name'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    ycomp = data[:, 2]
    xcomperr = data[:, 1]

    query = '''select g.nuv_mag, g.nuv_magerr, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, galex as g, galex_distinct as gt
               where o.flag = "TS" and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and k.name = r.name and
               r.dr7objid = gt.sdssid and
               gt.sdssid = g.sdssid
               group by k.name'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    ysalt = data[:, 2]
    xsalterr = data[:, 1]

    #make the figure
    fig = P.figure()
    fig.subplots_adjust(left=0.09, bottom=0.08,
                        right=0.93, top=0.95,
                        wspace=0.0, hspace=0.0)
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'GALEX NUV [mag]')
    ax1.set_ylabel(r'EXPTIME [min]')

    ax1.set_ylim(5, 85)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotHaflux(output, out_folder):
    query = '''select d.h_alpha_flux, d.h_alpha_flux_err, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr8specobjid = d.specobjid
               group by k.name'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = data[:, 1]
    ycomp = data[:, 2]

    query = '''select d.h_alpha_flux, d.h_alpha_flux_err, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr8specobjid = d.specobjid
               group by k.name'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = data[:, 1]
    ysalt = data[:, 2]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'$H_{\alpha}$ [1e-17 erg/s/cm$^{2}$]')
    ax1.set_ylabel(r'EXPTIME [min]')

    ax1.set_xscale('log')
    ax1.set_xlim(5, 1e4)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotHaEW(output, out_folder):
    query = '''select d.h_alpha_eqw, d.h_alpha_eqw_err, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr8specobjid = d.specobjid
               group by k.name'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = -1. * data[:, 0]
    xcomperr = data[:, 1]
    ycomp = data[:, 2]

    query = '''select d.h_alpha_eqw, d.h_alpha_eqw_err, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr8specobjid = d.specobjid
               group by k.name'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = -1. * data[:, 0]
    xsalterr = data[:, 1]
    ysalt = data[:, 2]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'-EW($H_{\alpha}$) [AA]')
    ax1.set_ylabel(r'EXPTIME [min]')

    ax1.set_xscale('log')

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotHaDR7(output, out_folder):
    query = '''select d.ew, d.ewErr, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr7data as d
               where o.flag = "C" and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr7specobjid = d.specobjid
               group by k.name'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = data[:, 1]
    ycomp = data[:, 2]

    query = '''select d.ew, d.ewErr, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr7data as d
               where o.flag = "TS" and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr7specobjid = d.specobjid
               group by k.name'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = data[:, 1]
    ysalt = data[:, 2]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'-EW($H_{\alpha}$) from DR7 [AA]')
    ax1.set_ylabel(r'EXPTIME [min]')

    ax1.set_xscale('log')
    #ax1.set_xlim(5, 1e4)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8u(output, out_folder):
    query = '''select d.petroMag_u, d.petroMagErr_u, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               d.petroMagErr_u < 5 and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr8specobjid = d.specobjid
               group by k.name'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = data[:, 1]
    ycomp = data[:, 2]

    query = '''select d.petroMag_u, d.petroMagErr_u, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               d.petroMagErr_u < 5 and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr8specobjid = d.specobjid
               group by k.name'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = data[:, 1]
    ysalt = data[:, 2]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'PetroMag_U from DR8 [mag]')
    ax1.set_ylabel(r'EXPTIME [min]')

    ax1.set_xlim(14, 21)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8g(output, out_folder):
    query = '''select d.petroMag_g, d.petroMagErr_g, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               d.petroMagErr_g < 5 and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr8specobjid = d.specobjid
               group by k.name'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = data[:, 1]
    ycomp = data[:, 2]

    query = '''select d.petroMag_g, d.petroMagErr_g, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               d.petroMagErr_g < 5 and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr8specobjid = d.specobjid
               group by k.name'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = data[:, 1]
    ysalt = data[:, 2]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'PetroMag_g from DR8 [mag]')
    ax1.set_ylabel(r'EXPTIME [min]')

    ax1.set_xlim(13, 18.5)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8ug(output, out_folder):
    query = '''select d.petroMag_u - d.petroMag_g,
               d.petroMagErr_u*d.petroMagErr_u + d.petroMagErr_g*d.petroMagErr_g, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               d.petroMagErr_g < 5 and
               d.petroMagErr_u < 5 and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr8specobjid = d.specobjid
               group by k.name'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = np.sqrt(data[:, 1])
    ycomp = data[:, 2]

    query = '''select d.petroMag_u - d.petroMag_g,
               d.petroMagErr_u*d.petroMagErr_u + d.petroMagErr_g*d.petroMagErr_g, sum(k.exptime)
               from kindata as k, observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               d.petroMagErr_g < 5 and
               d.petroMagErr_u < 5 and
               k.paflag = 1 and k.obsshift = "Z" and
               k.name = o.name and
               k.name = r.name and
               r.dr8specobjid = d.specobjid
               group by k.name'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = np.sqrt(data[:, 1])
    ysalt = data[:, 2]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'U - g from DR8 [mag]')
    ax1.set_ylabel(r'EXPTIME [min]')

    ax1.set_xlim(0.5, 2.5)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8ugHa(output, out_folder):
    query = '''select d.petroMag_u - d.petroMag_g,
               d.petroMagErr_u*d.petroMagErr_u + d.petroMagErr_g*d.petroMagErr_g,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               d.petroMagErr_g < 5 and
               d.petroMagErr_u < 5 and
               o.name = r.name and
               r.dr8specobjid = d.specobjid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = np.sqrt(data[:, 1])
    ycomp = data[:, 2]
    ycomperr = data[:, 3]

    query = '''select d.petroMag_u - d.petroMag_g,
               d.petroMagErr_u*d.petroMagErr_u + d.petroMagErr_g*d.petroMagErr_g,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               d.petroMagErr_g < 5 and
               d.petroMagErr_u < 5 and
               o.name = r.name and
               r.dr8specobjid = d.specobjid'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = np.sqrt(data[:, 1])
    ysalt = data[:, 2]
    ysalterr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, yerr=ycomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, yerr=ysalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'U - g from DR8 [mag]')
    ax1.set_ylabel(r'$H_{\alpha}$ [1e-17 erg/s/cm$^{2}$]')

    ax1.set_yscale('log')
    ax1.set_ylim(2, 1e4)
    ax1.set_xlim(0.5, 2.5)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8urHa(output, out_folder):
    query = '''select d.petroMag_u - d.petroMag_r,
               d.petroMagErr_u*d.petroMagErr_u + d.petroMagErr_r*d.petroMagErr_r,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               d.petroMagErr_r < 5 and
               d.petroMagErr_u < 5 and
               o.name = r.name and
               r.dr8specobjid = d.specobjid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = np.sqrt(data[:, 1])
    ycomp = data[:, 2]
    ycomperr = data[:, 3]

    query = '''select d.petroMag_u - d.petroMag_r,
               d.petroMagErr_u*d.petroMagErr_u + d.petroMagErr_r*d.petroMagErr_r,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               d.petroMagErr_r < 5 and
               d.petroMagErr_u < 5 and
               o.name = r.name and
               r.dr8specobjid = d.specobjid'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = np.sqrt(data[:, 1])
    ysalt = data[:, 2]
    ysalterr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, yerr=ycomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, yerr=ysalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'U - r from DR8 [mag]')
    ax1.set_ylabel(r'$H_{\alpha}$ [1e-17 erg/s/cm$^{2}$]')

    ax1.set_yscale('log')
    ax1.set_ylim(2, 1e4)
    ax1.set_xlim(0.5, 3.0)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8NUVrHa(output, out_folder):
    query = '''select g.nuv_mag - d.petroMag_r,
               g.nuv_magerr*g.nuv_magerr + d.petroMagErr_r*d.petroMagErr_r,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d, galex as g, galex_distinct as gt
               where o.flag = "C" and
               o.name = r.name and
               r.dr8specobjid = d.specobjid and
               r.dr7objid = gt.sdssid and
               gt.sdssid = g.sdssid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = np.sqrt(data[:, 1])
    ycomp = data[:, 2]
    ycomperr = data[:, 3]

    query = '''select g.nuv_mag - d.petroMag_r,
               g.nuv_magerr*g.nuv_magerr + d.petroMagErr_r*d.petroMagErr_r,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d, galex as g, galex_distinct as gt
               where o.flag = "TS" and
               o.name = r.name and
               r.dr8specobjid = d.specobjid and
               r.dr7objid = gt.sdssid and
               gt.sdssid = g.sdssid'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = np.sqrt(data[:, 1])
    ysalt = data[:, 2]
    ysalterr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, yerr=ycomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, yerr=ysalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'NUV - r$_{DR8}$ [mag]')
    ax1.set_ylabel(r'$H_{\alpha}$ [1e-17 erg/s/cm$^{2}$]')

    ax1.set_yscale('log')
    ax1.set_ylim(2, 1e4)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8NUVzHa(output, out_folder):
    query = '''select g.nuv_mag - d.petroMag_z,
               g.nuv_magerr*g.nuv_magerr + d.petroMagErr_z*d.petroMagErr_z,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d, galex as g, galex_distinct as gt
               where o.flag = "C" and
               o.name = r.name and
               r.dr8specobjid = d.specobjid and
               r.dr7objid = gt.sdssid and
               gt.sdssid = g.sdssid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = np.sqrt(data[:, 1])
    ycomp = data[:, 2]
    ycomperr = data[:, 3]

    query = '''select g.nuv_mag - d.petroMag_z,
               g.nuv_magerr*g.nuv_magerr + d.petroMagErr_z*d.petroMagErr_z,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d, galex as g, galex_distinct as gt
               where o.flag = "TS" and
               o.name = r.name and
               r.dr8specobjid = d.specobjid and
               r.dr7objid = gt.sdssid and
               gt.sdssid = g.sdssid'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = np.sqrt(data[:, 1])
    ysalt = data[:, 2]
    ysalterr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, yerr=ycomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, yerr=ysalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'NUV - z$_{DR8}$ [mag]')
    ax1.set_ylabel(r'$H_{\alpha}$ [1e-17 erg/s/cm$^{2}$]')

    ax1.set_yscale('log')
    ax1.set_ylim(2, 1e4)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8u50Ha(output, out_folder):
    query = '''select d.petroR50_u, d.petroR50Err_u,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               o.name = r.name and
               r.dr8specobjid = d.specobjid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = data[:, 1]
    ycomp = data[:, 2]
    ycomperr = data[:, 3]

    query = '''select d.petroR50_u, d.petroR50Err_u,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               o.name = r.name and
               r.dr8specobjid = d.specobjid'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = data[:, 1]
    ysalt = data[:, 2]
    ysalterr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, yerr=ycomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, yerr=ysalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'R50U from DR8 [arcsec]')
    ax1.set_ylabel(r'$H_{\alpha}$ [1e-17 erg/s/cm$^{2}$]')

    ax1.set_yscale('log')
    ax1.set_ylim(2, 1e4)
    ax1.set_xlim(0.5, 30)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8g50Ha(output, out_folder):
    query = '''select d.petroR50_g, d.petroR50Err_g,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               o.name = r.name and
               r.dr8specobjid = d.specobjid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = data[:, 1]
    ycomp = data[:, 2]
    ycomperr = data[:, 3]

    query = '''select d.petroR50_g, d.petroR50Err_g,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               o.name = r.name and
               r.dr8specobjid = d.specobjid'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = data[:, 1]
    ysalt = data[:, 2]
    ysalterr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, yerr=ycomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, yerr=ysalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'R50g from DR8 [arcsec]')
    ax1.set_ylabel(r'$H_{\alpha}$ [1e-17 erg/s/cm$^{2}$]')

    ax1.set_yscale('log')
    ax1.set_ylim(2, 1e4)
    #ax1.set_xlim(0.5, 50)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8uHa(output, out_folder):
    query = '''select d.petroMag_u, d.petroMagErr_u,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               o.name = r.name and
               d.petroMagErr_u < 5 and
               r.dr8specobjid = d.specobjid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = data[:, 1]
    ycomp = data[:, 2]
    ycomperr = data[:, 3]

    query = '''select d.petroMag_u, d.petroMagErr_u,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               o.name = r.name and
               d.petroMagErr_u < 5 and
               r.dr8specobjid = d.specobjid'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = data[:, 1]
    ysalt = data[:, 2]
    ysalterr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, yerr=ycomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, yerr=ysalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'U from DR8 [mag]')
    ax1.set_ylabel(r'$H_{\alpha}$ [1e-17 erg/s/cm$^{2}$]')

    ax1.set_yscale('log')
    ax1.set_ylim(2, 1e4)
    #ax1.set_xlim(0.5, 50)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8ur50Ha(output, out_folder):
    query = '''select d.petroR50_u - d.petroR50_r,
               petroR50Err_u*petroR50Err_u* + petroR50Err_r*petroR50Err_r,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               o.name = r.name and
               petroR50Err_u > 0 and petroR50Err_r > 0 and
               r.dr8specobjid = d.specobjid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = np.sqrt(data[:, 1])
    ycomp = data[:, 2]
    ycomperr = data[:, 3]

    query = '''select d.petroR50_u - d.petroR50_r,
               petroR50Err_u*petroR50Err_u* + petroR50Err_r*petroR50Err_r,
               d.h_alpha_flux, d.h_alpha_flux_err
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               o.name = r.name and
               petroR50Err_u > 0 and petroR50Err_r > 0 and
               r.dr8specobjid = d.specobjid'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = np.sqrt(data[:, 1])
    ysalt = data[:, 2]
    ysalterr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, yerr=ycomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, yerr=ysalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'R50u - R50r from DR8 [arcsec]')
    ax1.set_ylabel(r'$H_{\alpha}$ [1e-17 erg/s/cm$^{2}$]')

    ax1.set_yscale('log')
    ax1.set_ylim(2, 1e4)
    ax1.set_xlim(-5, 10)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8ug50u50(output, out_folder):
    query = '''select d.petroR50_u - d.petroR50_g,
               d.petroR50Err_u*d.petroR50Err_u* + d.petroR50Err_g*d.petroR50Err_g,
               d.petroR50_u, d.petroR50Err_u
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               o.name = r.name and
               d.petroR50Err_u > 0 and d.petroR50Err_r > 0 and
               r.dr8specobjid = d.specobjid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = np.sqrt(data[:, 1])
    ycomp = data[:, 2]
    ycomperr = data[:, 3]

    query = '''select d.petroR50_u - d.petroR50_g,
               d.petroR50Err_u*d.petroR50Err_u* + d.petroR50Err_g*d.petroR50Err_g,
               d.petroR50_u, d.petroR50Err_u
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               o.name = r.name and
               d.petroR50Err_u > 0 and d.petroR50Err_r > 0 and
               r.dr8specobjid = d.specobjid'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = np.sqrt(data[:, 1])
    ysalt = data[:, 2]
    ysalterr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, yerr=ycomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, yerr=ysalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'R50u - R50g from DR8 [arcsec]')
    ax1.set_ylabel(r'R50u [arcsec]')

    ax1.set_ylim(0, 30)
    ax1.set_xlim(-5, 10)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8ug50u(output, out_folder):
    query = '''select d.petroR50_u - d.petroR50_g,
               d.petroR50Err_u*d.petroR50Err_u* + d.petroR50Err_g*d.petroR50Err_g,
               d.petroMag_u,  d.petroMagErr_u
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               o.name = r.name and
               petroR50Err_u > 0 and petroR50Err_r > 0 and d.petroMagErr_u < 5 and
               r.dr8specobjid = d.specobjid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = np.sqrt(data[:, 1])
    ycomp = data[:, 2]
    ycomperr = data[:, 3]

    query = '''select d.petroR50_u - d.petroR50_g,
               d.petroR50Err_u*d.petroR50Err_u* + d.petroR50Err_g*d.petroR50Err_g,
               d.petroMag_u,  d.petroMagErr_u
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               o.name = r.name and
               petroR50Err_u > 0 and petroR50Err_r > 0 and d.petroMagErr_u < 5 and
               r.dr8specobjid = d.specobjid'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = np.sqrt(data[:, 1])
    ysalt = data[:, 2]
    ysalterr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, yerr=ycomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, yerr=ysalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'R50u - R50r from DR8 [arcsec]')
    ax1.set_ylabel(r'u [mag]')

    #ax1.set_ylim(0, 30)
    ax1.set_xlim(-5, 10)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


def PlotDR8u50g(output, out_folder):
    query = '''select d.petroR50_g, d.petroR50Err_g,
               d.petroMag_u,  d.petroMagErr_u
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "C" and
               o.name = r.name and
               petroR50Err_u > 0 and petroR50Err_g > 0 and
               r.dr8specobjid = d.specobjid'''
    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xcomp = data[:, 0]
    xcomperr = data[:, 1]
    ycomp = data[:, 2]
    ycomperr = data[:, 3]

    query = '''select d.petroR50_g, d.petroR50Err_g,
               d.petroMag_u,  d.petroMagErr_u
               from observations as o, RESOLVEmasterfile as r, dr8data as d
               where o.flag = "TS" and
               o.name = r.name and
               petroR50Err_u > 0 and petroR50Err_g > 0 and
               r.dr8specobjid = d.specobjid'''

    data = sq.get_data_sqliteSMNfunctions(path, db, query)
    xsalt = data[:, 0]
    xsalterr = data[:, 1]
    ysalt = data[:, 2]
    ysalterr = data[:, 3]

    #make the figure
    fig = P.figure()
    ax1 = fig.add_subplot(111)

    ax1.errorbar(xcomp, ycomp, xerr=xcomperr, yerr=ycomperr, ls='None', c='b',
                 marker='s', ms=3, label='Completed (C)')
    ax1.errorbar(xsalt, ysalt, xerr=xsalterr, yerr=ysalterr, ls='None', c='r',
                 marker='o', ms=3, label='SALT? (TS)')

    ax1.set_xlabel(r'R50g from DR8 [arcsec]')
    ax1.set_ylabel(r'u [mag]')

    #ax1.set_ylim(0, 30)
    #ax1.set_xlim(-5, 10)

    P.legend(shadow=True, fancybox=True, numpoints=1)
    P.savefig(out_folder + output)


if __name__ == '__main__':
    path = '/srv/one/sheila/sniemi/catalogs/'
    out_folder = '/srv/one/sheila/sniemi/plots/'
    db = 'catalogs.db'
    type = '.pdf'

    print 'Begin plotting'
    print 'Input DB: ', path + db

    PlotGALEXNUV('Observations1'+type, out_folder)
    PlotHaflux('Observations2'+type, out_folder)
    PlotHaEW('Observations3'+type, out_folder)
    PlotHaDR7('Observations4' + type, out_folder)
    PlotDR8u('Observations5' + type, out_folder)
    PlotDR8g('Observations6' + type, out_folder)
    PlotDR8ug('Observations7' + type, out_folder)
    PlotDR8ugHa('Observations8' + type, out_folder)
    PlotDR8urHa('Observations9' + type, out_folder)
    PlotDR8NUVrHa('Observations10' + type, out_folder)
    PlotDR8NUVzHa('Observations11' + type, out_folder)
    PlotDR8u50Ha('Observations12' + type, out_folder)
    PlotDR8g50Ha('Observations13' + type, out_folder)
    PlotDR8uHa('Observations14' + type, out_folder)
    PlotDR8ur50Ha('Observations15' + type, out_folder)
    PlotDR8ug50u50('Observations16' + type, out_folder)
    PlotDR8ug50u('Observations17' + type, out_folder)
    PlotDR8u50g('Observations18' + type, out_folder)

    print 'All done'
