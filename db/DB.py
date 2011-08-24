"""
This file contains a wrapper class to fetch data from a Sybase or MySQL database.

:author: Sami-Matias Niemi (niemi@stsci.edu) for STScI.
"""

__author__ = 'Sami-Matias Niemi'
__version__ = '1.0'

class DBSMN():
    """
    Wrapper class to fetch data from a database. Separate functions
    for Sybase and MySQL database. A new class instance must be
    initialised for every server/database combination.
    """
    
    def __init__(self, sql, user, password, database, address):
        """
        Init
        """
        import sys

        self.sql = sql
        self.user = user
        self.password = password
        self.database = database
        self.address = address

    def fetchSybaseData(self):
        """
        Function to fetch data from Sybase database.
        Fetches all data from the database given in the class constructor.
        Returns the fetched data as an array.
        """
        import Sybase as S

        #creates the connection
        try:
            DB = S.connect(self.address, self.user, self.password, self.database)
        except S.Error, e:
            print '\nError while connecting to the Sybase database %s at %s' % (self.database, self.address)
            print 'Error %s' % e.args
            print 'Will exit with status -99...'
            sys.exit(-99)

        #reads the data from the database
        try:
            cursor = DB.cursor()
            cursor.execute(self.sql)
            result = cursor.fetchall()
        except:
            DB.close()
            print '\nError while reading the Sybase database\n'
            print 'Will exit with status -99...'
            sys.exit(-99)

        cursor.close()
        DB.close()
        return result

    def fetchMySQLData(self):
        """
        Function to fetch data from MySQL database.
        Fetches all data from the database given in the class constructor.
        Returns the fetched data as an array.
        """
        import MySQLdb as M

        #Connects to the database
        try:
            DB = M.connect(host=self.address, user=self.user, passwd=self.passwd, db=self.database, )
        except M.Error, e:
            print '\nError while connecting to the MySQL database! \n'
            print 'Error %d: %s' % (e.args[0], e.args[1])
            print 'Will exit with status -99...'
            sys.exit(-99)

        #Reads the data from the database
        try:
            cursor = M.cursors.Cursor(DB)
            cursor.execute(self.sql)
            result = cursor.fetchall()
        except M.Error, e:
            print '\nError while reading the MySQL database! \n'
            print 'Error %d: %s' % (e.args[0], e.args[1])
            print 'Will exit with status -99...'
            sys.exit(-99)
            #Closes the cursor and the connection
        cursor.close()
        DB.close()
        #returns 2D-array
        return result

if __name__ == '__main__':
    """
    No proper test section written. Do NOT try to execute this file!
    """
    import sys

    sys.exit('Do NOT try to execute this file!')

    import string, Sybase

    db = Sybase.connect('SYBASE', 'sa', '', 'sybsystemprocs')
    c = db.cursor()
    if len(sys.argv) > 1:
        c.execute('select c.text from syscomments c, sysobjects o'
                  ' where o.name = @name and o.type = "P" and c.id = o.id'
                  ' order by c.colid', {'@name': sys.argv[1]})
        print string.join([row[0] for row in c.fetchall()], '')
    else:
        c.execute('select name from sysobjects where type = "P" order by name')
        print string.join([row[0] for row in c.fetchall()], '\n')