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


    def insertDataDB(self,head,stat):

        """ Insert Header and Statistcs Data for a Frame """
 

	if self.__cnx1 is not None:

            cursor = self.__cnx1.cursor()

            # Create SQL string for header keywords 
            sql_head =  ",".join(["%s='%s'" % (k,v) for k,v in head.items()]) 


            # Create SQL string for statistics keywords 
            sql_stat =  ",".join(["%s='%s'" % (k,v) for k,v in stat.items()]) 

	    # Now create full SQL insert statement
            sql = "INSERT INTO SeeingMonitorData SET " + sql_head + "," + sql_stat
	    
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

            sql = "DELETE FROM SeeingMonitorData WHERE filename = '%s' LIMIT 1" % filenm
	   
	    try:	
              cursor.execute(sql)
	      self.__cnx1.commit()
	      #print "Number of rows deleted: %d" % cursor.rowcount
	    except  MySQLdb.Error, e:
     	      print "Error %d: %s" % (e.args[0], e.args[1])
     	      sys.exit (1)
	      #pass	


    def insertObjectsDB(self,head,objects):

        """ Insert Object Data """
 
	if self.__cnx1 is not None:

            cursor = self.__cnx1.cursor()

            # Create and execute SQL statement

	    for obj in objects:	

  	    	obj[3]  = str("%.3f" % (float(obj[3])*float(head['pscale'])))
     		obj[4]  = str("%.3f" % (float(obj[4])*float(head['pscale'])))
     		obj[7]  = str("%.2f" % (float(obj[7])*float(head['pscale'])))

	      	sql = """INSERT INTO SeeingMonitorObjects SET filename='%s',x_image='%s',y_image='%s',
			a_image='%s',b_image='%s',theta='%s',el='%s',fwhm='%s',stella='%s',mag_auto='%s'""" % \
			(head['filename'],obj[1],obj[2],obj[3],obj[4],obj[5],obj[6],obj[7],obj[9],obj[10])	
			
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

            sql = "DELETE FROM SeeingMonitorObjects WHERE filename = '%s'" % filenm

	    try:	
              cursor.execute(sql)
	      self.__cnx1.commit()
	      #print "Number of rows deleted: %d" % cursor.rowcount
	    except  MySQLdb.Error, e:
     	      print "Error %d: %s" % (e.args[0], e.args[1])
     	      sys.exit (1)
	      #pass	