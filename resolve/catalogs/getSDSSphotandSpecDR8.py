"""
Downloads SDSS DR8 photometric and spectroscopic information.

:note: SamPy.db.sdss may need editing as this is the file where
       the server is defined, and thus defines whether this script
       calls DR7 or 8.

:requires: SamPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import sqlite3
import SamPy.db.sdss as sdss
import SamPy.log.Logger as lg
import SamPy.db.sqlite as sq


def chunks(l, n):
    return [l[i:i+n] for i in range(0, len(l), n)]


def getIds(column, database='catalogs.db'):
    """
    Recover ids from RESOLVEmasterfile table.

    :param column: name of the id column
    :type column: string
    :param database: name of the SQLite3 database file
    :type database: string

    :return: ids
    :rtype: ndarray
    """
    query = 'SELECT %s from RESOLVEmasterfile where %s > 0' % (column, column)
    data = sq.get_data_sqliteSMNfunctions('./', database, query, toNumpy=False)
    return data


def buildQuery(ids):
    """
    Builds a query.

    :param ids: a list of ids to match
    :type ids: list or ndarray
    """
    idlist = 's.specobjid in ('
    for id in ids:
        idlist += str(id[0]) + ', '
    idlist = idlist[:-2] + ')'

    query = "SELECT s.specobjid, p.objid, \
             p.petroMag_u, p.petroMag_g, p.petroMag_r, p.petroMag_i, p.petroMag_z, \
             p.petroMagErr_u, p.petroMagErr_g, p.petroMagErr_r, p.petroMagErr_i, p.petroMagErr_z,\
             p.psfMag_u, p.psfMag_g, p.psfMag_r, p.psfMag_i, p.psfMag_z, \
             p.psfMagErr_u, p.psfMagErr_g, p.psfMagErr_r, p.psfMagErr_i, p.psfMagErr_z, \
             p.petroR90_u, p.petroR90_g, p.petroR90_r, p.petroR90_i, p.petroR90_z, \
             p.petroR90Err_u, p.petroR90Err_g, p.petroR90Err_r, p.petroR90Err_i, p.petroR90Err_z, \
             p.petroR50_u, p.petroR50_g, p.petroR50_r, p.petroR50_i, p.petroR50_z, \
             p.petroR50Err_u, p.petroR50Err_g, p.petroR50Err_r, p.petroR50Err_i, p.petroR50Err_z, \
             s.h_alpha_flux, s.h_alpha_flux_err, s.h_alpha_eqw, s.h_alpha_eqw_err,  \
             s.h_beta_flux, s.h_beta_flux_err, s.h_beta_eqw, s.h_beta_eqw_err,  \
             s.oii_3726_flux, s.oii_3726_flux_err, s.oii_3726_eqw, s.oii_3726_eqw_err, \
             s.neiii_3869_flux, s.neiii_3869_flux_err, s.neiii_3869_eqw, s.neiii_3869_eqw_err, \
             s.oiii_4959_flux, s.oiii_4959_flux_err, s.oiii_4959_eqw, s.oiii_4959_eqw_err, \
             s.oiii_5007_flux, s.oiii_5007_flux_err, s.oiii_5007_eqw, s.oiii_5007_eqw_err, \
             s.nii_6548_flux, s.nii_6548_flux_err, s.nii_6548_eqw, s.nii_6548_eqw_err, \
             s.nii_6584_flux, s.nii_6584_flux_err, s.nii_6584_eqw, s.nii_6584_eqw_err \
             from Galaxy as p, galSpecLine as s \
             WHERE p.specobjid = s.specobjid and {0:>s}".format(idlist)

    lines = sdss.query(query).readlines()

    fh = open('dr8data.txt', 'a')
    for line in lines:
        fh.write(line)
    fh.close()


if __name__ == '__main__':
    log_filename = 'SDSSqueryscriptDR8.log'
    log = lg.setUpLogger(log_filename)
    log.info('Starting script')

    ids = getIds('dr8specobjid')
    log.info('DR8 IDs recovered from the RESOLVE database')

    #need to split
    spl = chunks(ids, 300)
    for id in spl:
        buildQuery(id)
    log.info('data recovered from the DR8 SDSS database')
