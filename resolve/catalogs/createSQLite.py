"""
This module contains a function that can be used to generate an SQLite3 database from ascii files.

:requires: SamPy

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.2
"""
import sqlite3
import glob as g
import SamPy.log.Logger as lg
import SamPy.db.sqlite


def generateSQLiteDBfromASCII(output='catalogs.db',
                              fileidentifier='*.txt'):
    """
    Generates a database, each ascii file will be a separate table.

    The first line of the ascii file will be used to identify
    column names. This line should start with # so that it will
    be ignored. Each column name should be separated by a white space.

    :param output: name of the output file
    :param fileidentifier: string how to identify input data

    :type output: string
    :type fileidentifier: string
    """

    #find all files matching the file identifier
    files = g.glob(fileidentifier)
    #create a connection object to output that represents the database
    conn = sqlite3.connect(output)

    for file in files:
        log.info('Processing file %s', file)

        #process columns
        columns = SamPy.db.sqlite.parseASCIITitle(file)
        formats = []
        for col in columns:
            if 'name' in col.lower() or\
               'tel' in col.lower() or\
               'flags' in col.lower() or\
               'istherespec' in col.lower() or\
               'data' in col.lower() or\
               'setup' in col.lower() or\
               'frontend' in col.lower() or\
               'obsshift' in col.lower():
                formats.append('TEXT')
            elif 'flag' in col.lower():
                formats.append('INT')
            elif 'id' in col.lower():
                formats.append('BIGINT')
            else:
                formats.append('DOUBLE')

        #name of the table
        table = file.split('.')[0]

        start = 'create table %s ' % table
        ins = 'insert into %s values (' % table
        for x in range(len(formats)):
            ins += '?,'
        ins = ins[:-1] + ')'

        #generate an SQL table creation string
        sql_create_string = SamPy.db.sqlite.generateSQLString(columns,
                                                              formats,
                                                              start)

        log.info(sql_create_string)

        #create a cursor instance
        c = conn.cursor()

        #Create table
        c.execute(sql_create_string)

        log.info('Created table, will start inserting data to %s' % table)

        #insert data, line-by-line to save memory
        fh = open(file, 'r')
        while True:
            try:
                line = fh.next().strip()
            except:
                break
            if not line.startswith('#'):
                c.execute(ins, line.split())

        log.info('Finished inserting data to %s' % table)

        #create index on the first column to make searching faster
        if 'galex' in table:
            indexString = 'CREATE UNIQUE INDEX %sids on %s (%s, %s)' % (table, table, columns[0], 'sdssid')
        elif 'kindata' in table:
            indexString = 'CREATE INDEX %sids on %s (%s)' % (table, table, columns[0])
        else:
            indexString = 'CREATE UNIQUE INDEX %sids on %s (%s)' % (table, table, columns[0])

        log.info('Creating index: %s' % indexString)
        c.execute(indexString)

        log.info('Will commit all changes to %s' % table)
        # Save (commit) the changes
        conn.commit()
        # We can also close the cursor when we are done with it
        c.close()

    log.info('All done, DB file is %s', output)


if __name__ == '__main__':
    log_filename = 'insertSAMTablesToSQLite.log'
    log = lg.setUpLogger(log_filename)

    generateSQLiteDBfromASCII()
  