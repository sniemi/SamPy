"""
Connects to the localhost MySQL db.

:author: Sami-Matias Niemi
:version: 0.1
"""
import sys
import MySQLdb as M


class MySQLdbSMN():
    def __init__(self, sql, database):
        """
        Class constructor
        """
        self.user = 'sammy'
        self.passwd = 'Asd1Zxc8'
        self.address = 'localhost'
        self.sql = sql
        self.database = database


    def fetchdata(self):
        #Connect to database and get cursor
        try:
            DB = M.connect(host=self.address, user=self.user, passwd=self.passwd, db=self.database, )
        except M.Error, e:
            print '\n Error while connecting to the MySQL database! \n'
            print 'Error %d: %s' % (e.args[0], e.args[1])
            print 'Will exit with status -99...'
            sys.exit(-99)

        #Reads the data from the database
        try:
            cursor = M.cursors.Cursor(DB)
            cursor.execute(self.sql)
            result = cursor.fetchall()
        except M.Error, e:
            print '\n Error while reading the MySQL database! \n'
            print 'Error %d: %s' % (e.args[0], e.args[1])
            print 'Will exit with status -99...'
            sys.exit(-99)
            #Closes the cursor and the connection
        cursor.close()
        DB.close()
        #returns 2D-array
        return result
