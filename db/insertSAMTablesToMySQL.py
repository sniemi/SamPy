import MySQLdb as M
#import pymysql as M
import glob as g
#Sami's repo
import log.Logger as lg
import db.sqlite

def addToMySQLDBfromSAMTables(user='sammy',
                              passwd='Asd1Zxc8',
                              host='localhost',
                              database='SAM100GOODS',
                              fileidentifier='*.dat'):
    '''
    This little function can be used to add a table to a
    mySQL database from Rachel's GF output.
    
    The script will make a table out from each ascii 
    output file. The halo_id and gal_id columns of
    each table are indexed for faster table joining.
    Each index is names as table_id, albeit there
    should be no need to know the name of the index.

    :param user: user name to be used
    :param passwd: user password
    :param host: address of the database host
    :param database: name of the database to which insert
    :param fileidentifier: string how to identify input data
    '''
    #find all files
    files = g.glob(fileidentifier)

    #create a Connection object that represents the database
    #to a file
    conn = M.connect(host, user, passwd, db=database)

    for file in files:
        log.info('Processing file %s', file)
        columns = db.sqlite.parseColumnNamesSAMTables(file)
        formats = []
        for col in columns:
            if 'halo_id' in col:
                formats.append('INTEGER')
            elif 'gal_id' in col:
                formats.append('INTEGER')
            elif 'weight' in col or 'ngal' in col:
                formats.append('INTEGER')
            else:
                formats.append('REAL')

        if 'galprop.dat' in file:
            start = 'create table galprop '
            ins = 'insert into galprop values ('
            for x in range(len(formats)):
                ins += '%s,'
            ins = ins[:-1] + ')'
        if 'galphot.dat' in file:
            start = 'create table galphot '
            ins = 'insert into galphot values ('
            for x in range(len(formats)):
                ins += '%s,'
            ins = ins[:-1] + ')'
        if 'galphotdust.dat' in file:
            start = 'create table galphotdust '
            ins = 'insert into galphotdust values ('
            for x in range(len(formats)):
                ins += '%s,'
            ins = ins[:-1] + ')'
        if 'halos.dat' in file:
            start = 'create table halos '
            ins = 'insert into halos values ('
            for x in range(len(formats)):
                ins += '%s,'
            ins = ins[:-1] + ')'
        if 'totals.dat' in file:
            start = 'create table totals '
            ins = 'insert into totals values ('
            for x in range(len(formats)):
                ins += '%s,'
            ins = ins[:-1] + ')'
        if 'FIR.dat' in file:
            start = 'create table FIR '
            ins = 'insert into FIR values ('
            for x in range(len(formats)):
                ins += '%s,'
            ins = ins[:-1] + ')'
        if 'galpropz.dat' in file:
            start = 'create table galpropz '
            ins = 'insert into galpropz values ('
            for x in range(len(formats)):
                ins += '%s,'
            ins = ins[:-1] + ')'

        #generate an SQL table creation string
        sql_create_string = db.sqlite.generateSQLString(columns,
                                                        formats,
                                                        start)

        #create a cursor instance
        c = M.cursors.Cursor(conn)

        #Create table
        c.execute(sql_create_string)

        log.info('Created table, will start inserting data')

        #insert data, line-by-line to save memory
        fh = open(file, 'r')
        while True:
            try:
                line = fh.next().strip()
            except:
                break
            if not line.startswith('#'):
                c.execute(ins, line.split())

        log.info('Finished inserting data')

        #create index to make searching faster
        if file in 'halos.dat':
            indexString = 'CREATE UNIQUE INDEX %s_ids on %s (halo_id)' % (file[:-4], file[:-4])
        elif file in ['galphot.dat', 'galphotdust.dat']:
            indexString = 'CREATE UNIQUE INDEX %s_ids on %s (halo_id, gal_id, z)' % (file[:-4], file[:-4])
        elif file in 'galpropz.dat':
            indexString = 'CREATE UNIQUE INDEX %s_ids on %s (halo_id, gal_id, zgal)' % (file[:-4], file[:-4])
        elif 'totals.dat' in file:
            indexString = 'CREATE UNIQUE INDEX %s_ids on %s (z)' % (file[:-4], file[:-4])
        else:
            indexString = 'CREATE UNIQUE INDEX %s_ids on %s (halo_id, gal_id)' % (file[:-4], file[:-4])

        c.execute(indexString)
        log.info('%s', indexString)

        # Save (commit) the changes
        conn.commit()
        # We can also close the cursor if we are done with it
        c.close()
        #close the connection
        conn.close()

    log.info('All done, check out the DB')


if __name__ == '__main__':
    log_filename = 'insertSAMTablesToSQLite.log'
    log = lg.setUpLogger(log_filename)
    addToMySQLDBfromSAMTables()

