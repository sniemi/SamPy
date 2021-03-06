#!/usr/bin/env python
# -*- encoding: utf-8 -*-
#MySQLdbSMN class has been designed to make the localhost MySQL db connection easier.
#

class MySQLdbSMN():
    def __init__(self, sql, database):
        self.user = 'sami'
        self.passwd = 'llepsnoom'
        self.address = 'localhost'
        self.sql = sql
        self.database = database
    
    def fetchdata(self):
        import sys
        import MySQLdb as M
        
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

if __name__ == '__main__':
    '''Just to test the module'''
    import sys

    SMNmods = '/Users/Sammy/Python/'
    sys.path.append(SMNmods)
    
    import sami.MySQLdbSMN as DB
    
    sql = 'select mvir, np from FieldEllipticals where type = 0 order by galaxyId'
    db = DB.MySQLdbSMN(sql, 'FieldEllipticalStudy')
    dt = db.fetchdata()
    
    import numpy as N
    data = N.array(dt)
    
    print data[:,0]
