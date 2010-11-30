import MySQLdb
import sys

class DBException(Exception):
  pass


class MySQLhandler:

    """ A set of methods to deal with database connectivity """

    def __init__(self):

        """ Create a MySQL database connection """

	try:
          self.__cnx1 = MySQLdb.connect(host='eeva',user='fitsheader_user',passwd='fitsheader_pass',db='FitsHeader')
        except MySQLdb.Error, e:
	  raise DBException("Error %d: %s" % (e.args[0], e.args[1]))

    def close(self):

        """ Close database connections and Commit transaction """

        if self.__cnx1 is not None:

	    self.__cnx1.commit() 
            self.__cnx1.close()
            self.__cnx1 = None


    def insertFitsHeader(self,head,fits_nm):

        """ Insert Header for a Frame """
 
	if self.__cnx1 is not None:

            cursor = self.__cnx1.cursor()

	    # Get table prefix from head[0]
	    tbl = head[0]

            # ----------- #
	    # PRIMARY HDU #
	    # ----------- #	


	    # Make a dictionary out of the fitsheaders (keyword=value) pairs  	
            try:
	      dct = dict(head[1].items())
            except ValueError, e:
      	      self.__cnx1.rollback()
	      raise DBException("Error %s" % e)

	    # Add the (disk) filename to the dictionary
	    dct['file'] = fits_nm

 	    # Add a DateTimeUT to the dictionary which will be a proper
	    # datetime column type  
	    dct['DateTimeUT'] = dct['DATE-OBS']

	    # Convert boolean types into 'T' of 'F', which is the fitsheader value	
	    for k in [x for x in dct if type(dct[x]) is bool]:
              dct[k] = (dct[k] and 'T') or 'F'

	    # Use Python extended format codes (pyformat) for the insert parameter style
	    # Thus we can pass a dictionary as the placeholder when executing the insert statement
            # instead of a tuble. Adds flexibility.	
            sql_str = ",".join(["`%s` = %%(%s)s" % (k,k) for k in dct])
	
            # Add the table specification to the insert statement
	    sql = "INSERT INTO %sprihdu SET %s" % (tbl,sql_str)	

 	    # Execute SQL statement
	    try:
	      # Pass the dictionary containing the column values as placeholder
	      # for the insert statement
              cursor.execute(sql, dct) 

	      # Get the last autonumbering ID inserted. Needed as FK constraint
	      # when inserting the Extended HDUs
	      last_id = self.__cnx1.insert_id()

	    except  MySQLdb.Error, e:
	      self.__cnx1.rollback()
	      raise DBException("Error %d: %s" % (e.args[0], e.args[1]))



            # --------------- #
	    # EXTENDED HDU(S) #
	    # --------------- #	


	    # Create SQL string for Inserting Extented Headers (head[2..n])

	    for hdu in head[2:]:	

	      try: 
                dct = dict(hdu.items())
              except ValueError, e:
	        self.__cnx1.rollback()
                raise DBException("Error %s" % e)
		 
	      for k in [x for x in dct if type(dct[x]) is bool]:
                dct[k] = (dct[k] and 'T') or 'F'

	      # Add the foreign key to the dictionary
	      fk = "%sprihdu_id%sprihdu" % (tbl,tbl)
	      dct[fk] = last_id	      

              sql_str =  ",".join(["`%s`=%%(%s)s" % (k,k) for k in dct]) 

	      sql = "INSERT INTO %sexthdu SET %s" % (tbl,sql_str)	       

	      try:
                cursor.execute(sql, dct)
	      except  MySQLdb.Error, e:
	        self.__cnx1.rollback()
	        raise DBException("Error %d: %s" % (e.args[0], e.args[1]))



    def deleteFitsHeader(self,tbl,filenm):

        """ Delete Header for a Frame """
 

	if self.__cnx1 is not None:

            cursor = self.__cnx1.cursor()

            sql = "DELETE FROM %sprihdu WHERE file = '%s' LIMIT 1" % (tbl,filenm)
	   
	    try:	
              cursor.execute(sql)
	      self.__cnx1.commit()
	    except  MySQLdb.Error, e:
	      raise DBException("Error %d: %s" % (e.args[0], e.args[1]))
	      self.__cnx1.rollback()
