"""
SQLite3 database related functions that help to create a new database or to query an old one.

:requires: NumPy
:requires: SamPy

:author: Sami-Matias Niemi
:version: 0.2
"""
import sqlite3
import re
import numpy as np
import SamPy.astronomy.conversions as conv


def toPowerTen(value):
    """
    Raises the given value to a power of ten.

    :note: This function can be passed on to slite3 connection

    :param value: data
    :type value: float or ndarray

    :return: :math:`10^{value}`
    """
    return np.power(10, value)


def toLogTen(value):
    """
    Takes the 10th base logarithm of the given value.

    :note: This function can be passed on to slite3 connection

    :param value: data
    :type value: float or ndarray

    :return: :math: `\\log_{10} (value)`
    """
    return np.Log10(value)


def SSFR(mstardot, mstar):
    """
    Calculates the specific star formation rate from a given (SAM) data.

    .. math::

       \\log_{10} \\left ( \\frac {value1}{10^{value2}} \\right )

    :note: This function can be passed on to slite3 connection

    :param mstardot: star formation rate
    :type mstardot: float or ndarray
    :param mstar: stellar mass in :math:`\\log_{10}(M_{\\mathrm{solar}})`
    :type mstar: float or ndarray

    :return: specific star formation rate in :math:`\\mathrm{Gyr}^{-1}`
    :rtype: float or ndarray
    """
    return np.log10(mstardot / 10 ** mstar)


def get_data_sqlitePowerTen(path, db, query):
    """
    Run an SQL query to a database with a custom made function "toPowerTen".

    :param path: path to the SQLite3 database
    :type path: string
    :param db: name of the SQLite3 database
    :type db: string
    :param query: valid SQL query
    :type query: string

    :return: all requested data
    :rtype: ndarray
    """
    conn = sqlite3.connect(path + db)
    conn.create_function('Pow10', 1, toPowerTen)
    c = conn.cursor()
    c.execute(query)
    data = np.array(c.fetchall())
    c.close()
    return data


def get_data_sqliteSMNfunctions(path, db, query, toNumpy=True):
    """
    Run an SQL query to a database with custom made functions "toPowerTen" and "janskyToMagnitude".

    :param path: path to the SQLite3 database
    :type path: string
    :param db: name of the SQLite3 database
    :type db: string
    :param query: valid SQL query
    :type query: string
    :param toNumPy: whether or not to convert to NumPy ndarray
    :type toNumPy: boolean
    
    :return: all requested data
    :rtype: list or ndarray
    """
    conn = sqlite3.connect(path + db)
    conn.create_function('janskyToMagnitude', 1, conv.janskyToMagnitude)
    conn.create_function('Pow10', 1, toPowerTen)
    conn.create_function('Log10', 1, toLogTen)
    conn.create_function('SSFR', 2, SSFR)
    c = conn.cursor()
    c.execute(query)
    if toNumpy:
        data = np.array(c.fetchall())
    else:
        data = c.fetchall()
    c.close()
    return data


def get_data_sqlite(path, db, query):
    """
    This function can be used to pull out data from an slite3 database.
    Output is given as a numpy array for ease of further processing.

    :param path: path to the SQLite3 database
    :type path: string
    :param db: name of the SQLite3 database
    :type db: string
    :param query: valid SQL query
    :type query: string

    :return: all requested data
    :rtype: ndarray
    """
    conn = sqlite3.connect(path + db)
    c = conn.cursor()
    c.execute(query)
    data = np.array(c.fetchall())
    c.close()
    return data


def parseColumnNamesSAMTables(filename,
                              commentchar='#',
                              colnumber=2):
    """
    Parse column names from a text file that follows SExtractor format, i.e., columns are specified in
    the beginning of the file. Each column are specified in a single line that starts with a comment character.

    The line assumed to follow the following format:
    # number name
    For example:
    # 1 the_first_column.
    In the case of the example, the function would return
    a list ['the_first_column',].
    """
    cols = []
    next = True
    fh = open(filename)
    while next:
        line = fh.next()
        if not line.startswith(commentchar):
            next = False
        else:
            tmp = line.split()
            cols.append(tmp[colnumber])
    return cols


def parseASCIITitle(filename,
                    strip=True,
                    lower=False,
                    split=None):
    """
    Parse a single line ascii information. Assumes that the first line is the header.
    Converts all column names to lower case if lower=True, but by default does not.

    If strip=True then will remove all dots and replace them with empty spaces.

    :param filename: name of the file to processed
    :type filename: string
    :param strip: a flag whether dots should be stripped from the name
    :type strip: boolean
    :param lower: a flag whether the column names should be converted to lower case
    :type lower: boolean
    :param split: character to be used for splitting the header string
    :type split: string

    :return: a list of column names
    :rtype: list
    """
    firstLine = open(filename).readline()
    if strip:
        cols = []
        for x in firstLine.split():
            tmp = re.sub(r'[^\w]', '', x.strip('.'))
            cols.append(tmp.replace('#', '').strip())
    else:
        if lower:
            cols = [x.replace('#', '').strip() for x in firstLine.split(split).lower()]
        else:
            cols = [x.replace('#', '').strip() for x in firstLine.split(split)]
    return cols


def generateSQLString(columns, format, start):
    """
    Generates an SQL string from two vectors that describe the name of the column and the format.

    Can be used to assist when generating a string to create a new table.
    """
    start += '('
    for a, b in zip(columns, format):
        start += '%s %s, ' % (a, b)

    start = start[:-2] + ')'
    return start

