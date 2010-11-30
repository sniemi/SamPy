import MySQLdb
import sys

class MySQLhandler:

    """ A set of methods to deal with database connectivity """

    def __init__(self):

        """ Create a MySQL database connection """

	try:
          self.__cnx1 = MySQLdb.connect(host='eeva',user='qc_user',passwd='qc_pass',db='QC')
        except MySQLdb.Error, e:
     	  print "Error %d: %s" % (e.args[0], e.args[1])
     	  sys.exit (1)
	  #self.__cnx1 = None

    def close(self):

        """ Close database connections and Commit transaction """

        if self.__cnx1 is not None:

	    self.__cnx1.commit() 
            self.__cnx1.close()
            self.__cnx1 = None


    def insertDataDB(self,data):

        """ Insert Header and Statistcs Data for a Frame """
 

	if self.__cnx1 is not None:

            cursor = self.__cnx1.cursor()

            # Create SQL string
            sql_head =  ",".join(["%s='%s'" % (k,v) for k,v in data.items()]) 

	    # Now create full SQL insert statement
            sql = "INSERT INTO FocusDataALFOSC SET " + sql_head
	    
 	    # Execute SQL statement
	    try:	
              cursor.execute(sql)
	      #print "Number of rows inserted: %d" % cursor.rowcount
	    except  MySQLdb.Error, e:
     	      print "Error %d: %s" % (e.args[0], e.args[1])
     	      sys.exit (1)
	      #pass	


    def deleteDataDB(self,filenm):

        """ Delete Header and Statistcs Data for a Frame """
 

	if self.__cnx1 is not None:

            cursor = self.__cnx1.cursor()

            sql = "DELETE FROM FocusDataALFOSC WHERE filename = '%s' LIMIT 1" % filenm
	   
	    try:	
              cursor.execute(sql)
	      self.__cnx1.commit()
	      #print "Number of rows deleted: %d" % cursor.rowcount
	    except  MySQLdb.Error, e:
     	      print "Error %d: %s" % (e.args[0], e.args[1])
     	      sys.exit (1)
	      #pass	


    def insertObjectsDB(self,filename,objects):

        """ Insert Object Data """
 
	if self.__cnx1 is not None:

            cursor = self.__cnx1.cursor()

            # Create and execute SQL statement

	    for obj in objects:	

	      	sql = """INSERT INTO FocusObjectsALFOSC SET filename='%s',offsetfocus='%s',xdist='%s',
			ydist='%s',xccd='%s',yccd='%s',peak='%s'""" % \
			(filename,obj[0],obj[1],obj[2],obj[3],obj[4],obj[5])	
			
	       	try:	
                  cursor.execute(sql)
	          #print "Number of rows inserted: %d" % cursor.rowcount
	       	except  MySQLdb.Error, e:
     	          print "Error %d: %s" % (e.args[0], e.args[1])
     	          sys.exit (1)
	          #pass	


    def deleteObjectsDB(self,filenm):

        """ Delete Objects Data for a Frame """
 
	if self.__cnx1 is not None:

            cursor = self.__cnx1.cursor()

            sql = "DELETE FROM FocusObjectsALFOSC WHERE filename = '%s'" % filenm

	    try:	
              cursor.execute(sql)
	      self.__cnx1.commit()
	      #print "Number of rows deleted: %d" % cursor.rowcount
	    except  MySQLdb.Error, e:
     	      print "Error %d: %s" % (e.args[0], e.args[1])
     	      sys.exit (1)
	      #pass	