'''
A file containing SQLite3 related functions.

@note: The following is the orinal note:
This little script can be used to generate an
SQLite3 database from Rachel's GF output.

The script will make a table out from each ascii 
output file. The halo_id and gal_id columns of
each table are indexed for faster table joining.
Each index is names as table_id, albeit there
should be no need to know the name of the index.

output file, by default, is names as sams.db, 
however, this is easy to change as the name
is stored to output variable.
'''

import sqlite3
import glob as g
import io.sextutils as su
import numpy as N

def toPowerTen(value):
    '''
    10**value
    @note: This function can be passed on to slite3 connection
    @param value: can either be a number or a numpy array 
    '''
    return N.power(10, value)

def get_data_sqlitePowerTen(path, db, query):
    '''
    Run the SQL query.
    '''
    conn = sqlite3.connect(path + db)
#    conn.create_function('janskyToMagnitude', 1, janskyToMagnitude)
    conn.create_function('Pow10', 1, toPowerTen)
    c = conn.cursor()
    c.execute(query)
    data = c.fetchall()
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
    data = c.fetchall()
    c.close()
    return N.array(data)

def parse_column_names(filename, commentchar = '#', colnumber = 2):
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

def make_sql_string(columns, format, start):
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

if __name__ == '__main__':
    #name of the output database
    output = 'sams.db'

    #find all files
    files = g.glob('*.dat')

    #create a Connection object that represents the database
    #to a file
    conn = sqlite3.connect(output)
    #to memory
    #conn = sqlite3.connect(':memory:')

    for file in files:
        print 'Processing file %s' % file
        columns = parse_column_names(file)
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
            
        sql_create_string = make_sql_string(columns, formats, start)

        c = conn.cursor()

        #Create table
        c.execute(sql_create_string)

        #insert data
        fh = open(file, 'r')
        while True:
            try:
                line = fh.next().strip()
            except:
                break
            if not line.startswith('#'):
                c.execute(ins, line.split())
        
        #create index to make searching faster
        if 'halos.dat' in file:
            c.execute('''CREATE UNIQUE INDEX %s_ids on %s (halo_id)''' % (file[:-4], file[:-4]))
        else:
            c.execute('''CREATE UNIQUE INDEX %s_ids on %s (halo_id, gal_id)''' % (file[:-4], file[:-4]))

        # Save (commit) the changes
        conn.commit()
        # We can also close the cursor if we are done with it
        c.close()
        

    print 'All done, DB file is %s' % output
