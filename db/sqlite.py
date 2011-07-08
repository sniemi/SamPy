'''
This file contains SQLite3 related functions.

:requires: NumPy

:author: Sami-Matias Niemi
:version: 0.1
'''
import sqlite3
import numpy as N
#Sami's repository
import astronomy.conversions as conv


def toPowerTen(value):
    '''
    @note: This function can be passed on to slite3 connection
    @param value: can either be a number or a NumPy array
    @return: 10**value
    '''
    return N.power(10, value)


def toLogTen(value):
    '''
    @note: This function can be passed on to slite3 connection
    @param value: can either be a number or a NumPy array 
    @return: Log_10(value)
    '''
    return N.Log10(value)


def SSFR(mstardot, mstar):
    '''
    Log_10(value1 / 10**value2)
    @note: This function can be passed on to slite3 connection
    @param mstardot: star formation rate
    @param mstar: stellar mass in log10(M_solar)
    @return: specific star formation rate in Gyr**-1
    '''
    return N.log10(mstardot / 10 ** mstar)


def get_data_sqlitePowerTen(path, db, query):
    '''
    Run an SQL query to a database with a custom
    made function "toPowerTen".
    @param path: path to the SQLite3 database
    @param db: name of the SQLite3 database
    @param query: valid SQL query
    @return: all data in a NumPy array   
    '''
    conn = sqlite3.connect(path + db)
    conn.create_function('Pow10', 1, toPowerTen)
    c = conn.cursor()
    c.execute(query)
    data = N.array(c.fetchall())
    c.close()
    return data


def get_data_sqliteSMNfunctions(path, db, query):
    '''
    Run an SQL query to a database with custom
    made functions "toPowerTen" and "janskyToMagnitude".
    @param path: path to the SQLite3 database
    @param db: name of the SQLite3 database
    @param query: valid SQL query
    @return: all data in a NumPy array
    '''
    conn = sqlite3.connect(path + db)
    conn.create_function('janskyToMagnitude', 1, conv.janskyToMagnitude)
    conn.create_function('Pow10', 1, toPowerTen)
    conn.create_function('Log10', 1, toLogTen)
    conn.create_function('SSFR', 2, SSFR)
    c = conn.cursor()
    c.execute(query)
    data = N.array(c.fetchall())
    c.close()
    return data


def get_data_sqlite(path, db, query):
    '''
    This function can be used to pull out data
    from an slite3 database. Output is given as
    a numpy array for ease of further processing.
    @param path: path to the db file, should end with /
    @param db: name of the database file
    @param query: query to be performed
    @return: numpy array of data 
    '''
    conn = sqlite3.connect(path + db)
    c = conn.cursor()
    c.execute(query)
    data = N.array(c.fetchall())
    c.close()
    return data


def parseColumnNamesSAMTables(filename,
                              commentchar='#',
                              colnumber=2):
    '''
    Parse column names from a text file that follows
    SExtractor format, i.e., columns are specified in
    the beginning of the file. Each column are specified
    in a single line that starts with a comment charachter.
    The line assumed to follow the following format:
    # number name
    For example:
    # 1 the_first_column.
    In the case of the example, the function would return
    a list ['the_first_column',].
    '''
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
                    splitChar=' '):
    '''
    Parse a single line ascii information
    '''
    firstLine = open(filename).readline()
    splitted = firstLine.split(splitChar)
    cols = [x for x in splitted]
    return cols


def generateSQLString(columns, format, start):
    '''
    Generates an SQL string from two vectors that
    describe the name of the column and the format.
    Can be used to assist when generating a string
    to create a new table.
    '''
    start += '('
    for a, b in zip(columns, format):
        start += '%s %s, ' % (a, b)

    start = start[:-2] + ')'
    return start

