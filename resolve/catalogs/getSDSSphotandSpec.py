"""
Downloads SDSS DR7 photometric and spectroscopic information.

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

#    tquery = "SELECT s.specobjid, p.objid, s.speclineid,\
#              p.petroMag_u, p.petroMag_r, p.petroMag_i, p.petroR50_u, \
#              p.petroR50_g, p.petroR50_r, \
#              p.petroR90_u, p.petroR90_g, p.petroR90_r, p.petroRad_r, s.ew, s.ewErr, s.ewMin \
#              from Galaxy as p join SpecLineAll s on p.specobjid = s.specobjid \
#              WHERE s.lineID = dbo.fSpecLineNames('Ha_6565') and s.ewMin > 0 and\
#              s.specobjid in (159257667892674560, 335181438846500864)"


    query = "SELECT s.specobjid, p.objid, s.speclineid,\
              p.petroMag_u, p.petroMag_g, p.petroMag_r, p.petroMag_i, p.petroMag_z, \
              p.petroMagErr_u, p.petroMagErr_g, p.petroMagErr_r, p.petroMagErr_i, p.petroMagErr_z,\
              p.psfMag_u, p.psfMag_g, p.psfMag_r, p.psfMag_i, p.psfMag_z, \
              p.psfMagErr_u, p.psfMagErr_g, p.psfMagErr_r, p.psfMagErr_i, p.psfMagErr_z, \
              p.petroR90_u, p.petroR90_g, p.petroR90_r, p.petroR90_i, p.petroR90_z, \
              p.petroR90Err_u, p.petroR90Err_g, p.petroR90Err_r, p.petroR90Err_i, p.petroR90Err_z, \
              p.petroR50_u, p.petroR50_g, p.petroR50_r, p.petroR50_i, p.petroR50_z, \
              p.petroR50Err_u, p.petroR50Err_g, p.petroR50Err_r, p.petroR50Err_i, p.petroR50Err_z, \
              s.ew, s.ewErr, s.ewMin, s.sigma, s.sigmaErr, s.height, s.heightErr \
              from Galaxy as p join SpecLineAll s on p.specobjid = s.specobjid \
              WHERE s.lineID = dbo.fSpecLineNames('Ha_6565') and s.ewMin > 0 and {0:>s}".format(idlist)

    #fh = open('query.sql', 'w')
    #for x in query.split():
    #    fh.write(x+'\n')
    #fh.close()

    lines = sdss.query(query).readlines()

    fh = open('query_result.txt', 'a')
    for line in lines:
        fh.write(line)
    fh.close()


if __name__ == '__main__':
    log_filename = 'SDSSqueryscript.log'
    log = lg.setUpLogger(log_filename)
    log.info('Starting script')

    ids = getIds('dr7specobjid')
    log.info('IDs recovered from the RESOLVE database')

    #need to split
    spl = chunks(ids, 300)
    for id in spl:
        buildQuery(id)
    log.info('data recovered from the SDSS database')
