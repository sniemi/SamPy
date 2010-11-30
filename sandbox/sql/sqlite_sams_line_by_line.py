'''
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
import sextutils as su

def parse_column_names(filename):
    cols = []
    next = True
    fh = open(filename)
    while next:
        line = fh.next()
        if not line.startswith('#'):
            next = False
        else:
            tmp = line.split()
            cols.append(tmp[2])
    return cols

def make_sql_string(columns, format, start):
    start += '('
    for a, b in zip(columns, format):
        start += '%s %s, ' % (a, b)
        
    start = start[:-2] + ')'
    return start

if __name__ == '__main__':

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
