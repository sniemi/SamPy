import sqlite3
import glob as g
#Sami's repo
import smnIO.sextutils as su
import log.Logger as lg
import db.sqlite

def generateSQLiteDBfromSAMTables(output = 'sams.db',
                                  fileidentifier = '*.dat'):
    '''
    This little function can be used to generate an
    SQLite3 database from Rachel's GF output.
    
    The script will make a table out from each ascii 
    output file. The halo_id and gal_id columns of
    each table are indexed for faster table joining.
    Each index is names as table_id, albeit there
    should be no need to know the name of the index.

    @param output: name of the output file
    @param fileidentifier: string how to identify input data  
    '''
    #find all files
    files = g.glob(fileidentifier)

    #create a Connection object that represents the database
    #to a file
    conn = sqlite3.connect(output)
    #to memory
    #conn = sqlite3.connect(':memory:')

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
                ins += '?,'
            ins = ins[:-1] + ')'
        if 'galphot.dat' in file:
            start = 'create table galphot '
            ins = 'insert into galphot values ('
            for x in range(len(formats)):
                ins += '?,'
            ins = ins[:-1] + ')'
        if 'galphotdust.dat' in file:
            start = 'create table galphotdust '
            ins = 'insert into galphotdust values ('
            for x in range(len(formats)):
                ins += '?,'
            ins = ins[:-1] + ')'
        if 'halos.dat' in file:
            start = 'create table halos '
            ins = 'insert into halos values ('
            for x in range(len(formats)):
                ins += '?,'
            ins = ins[:-1] + ')'
        if 'totals.dat' in file:
            start = 'create table totals '
            ins = 'insert into totals values ('
            for x in range(len(formats)):
                ins += '?,'
            ins = ins[:-1] + ')'
        if 'FIR.dat' in file:
            start = 'create table FIR '
            ins = 'insert into FIR values ('
            for x in range(len(formats)):
                ins += '?,'
            ins = ins[:-1] + ')'
        if 'galpropz.dat' in file:
            start = 'create table galpropz '
            ins = 'insert into galpropz values ('
            for x in range(len(formats)):
                ins += '?,'
            ins = ins[:-1] + ')'
     
        #generate an SQL table creation string
        sql_create_string = db.sqlite.generateSQLString(columns,
                                                        formats,
                                                        start)
        
        #create a cursor instance
        c = conn.cursor()

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
        
    log.info('All done, DB file is %s', output)


if __name__ == '__main__':
    log_filename = 'insertSAMTablesToSQLite.log' 
    log = lg.setUpLogger(log_filename)

    generateSQLiteDBfromSAMTables()

