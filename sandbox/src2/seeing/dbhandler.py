import MySQLdb
import sys

class DBException(Exception):
  pass

class MySQLhandler:

    """ A set of methods to deal with database connectivity """

    def __init__(self):

        """ Create a MySQL database connection """

	try:
          self.__cnx1 = MySQLdb.connect(host='eeva',user='postprocess',passwd='postprocess',db='Pipeline')
        except MySQLdb.Error, e:
          raise DBException("Error %d: %s" % (e.args[0], e.args[1]))


    def close(self):

        """ Close database connections and Commit transaction """

        if self.__cnx1 is not None:

	    self.__cnx1.commit() 
            self.__cnx1.close()
            self.__cnx1 = None



    def getFitsHeader(self,tbl,filename):
       
	""" Return Primary and 1'st Extended HDU """

        if self.__cnx1 is not None:		
	 		
            prihdu = tbl + 'prihdu'
	    exthdu = tbl + 'exthdu'
	    idprihdu = 'id' + prihdu
            fk_constraint = "%s.%s = %s.%s_%s" % (prihdu,idprihdu,exthdu,prihdu,idprihdu)
   	    cursor = self.__cnx1.cursor(MySQLdb.cursors.DictCursor)
	    	
	    if tbl == 'NC':
	        sql = """SELECT %s.*,%s.CD1_1,%s.CD1_2,%s.CCDSUM,%s.GAIN1 AS GAIN 
		     FROM FitsHeader.%s, FitsHeader.%s 
		     WHERE %s.`file` = '%s' AND %s LIMIT 1""" % \
		(prihdu,exthdu,exthdu,exthdu,prihdu,prihdu,exthdu,prihdu,filename,fk_constraint)
	    else:
	        sql = """SELECT %s.*,%s.CD1_1,%s.CD1_2,%s.CCDSUM,%s.GAIN 
		     FROM FitsHeader.%s, FitsHeader.%s 
		     WHERE %s.`file` = '%s' AND %s LIMIT 1""" % \
		(prihdu,exthdu,exthdu,exthdu,exthdu,prihdu,exthdu,prihdu,filename,fk_constraint)

	    try:
	      cursor.execute(sql)
              return cursor.fetchone()

            except MySQLdb.Error, e: 
              raise DBException ("Error: %s (%s)" % (str(e.__class__), str(e)))


    def getFilterCenwave(self,id):

        """ Return central wavelength for a given filter ID """

        if self.__cnx1 is not None:		

   	    cursor = self.__cnx1.cursor()
            sql = "SELECT cenwave FROM Operations.FilterData WHERE `filterid` = '%s'" % id
	    try:
	      cursor.execute(sql)
              return cursor.fetchone()

            except MySQLdb.Error, e: 
              raise DBException ("Error: %s (%s)" % (str(e.__class__), str(e)))

    def insertDataDB(self,tbl,id,stat,objects):

        """ Insert Header and Statistcs Data for a Frame """
 

	if self.__cnx1 is not None:

            cursor = self.__cnx1.cursor()


	    # ------------------------- #
	    # Insert into *sexdat table #
	    # -------------------------	#


            # Create SQL string for statistics keywords 
            sql_stat =  ",".join(["%s='%s'" % (k,v) for k,v in stat.items()]) 

	    # Create full SQL insert statement
            sql = "INSERT INTO %ssexdat SET id_Header=%d,%s" % (tbl,id,sql_stat)
	    
 	    # Execute SQL statement
	    try:	
              cursor.execute(sql)

	      # Get the last autonumbering ID inserted. Needed as FK constraint
              # when inserting the individual objects
	      last_id = self.__cnx1.insert_id()

	    except  MySQLdb.Error, e:
              self.__cnx1.rollback()
              raise DBException("Error %d: %s" % (e.args[0], e.args[1]))


	    # ------------------------- #
	    # Insert into *sexobj table #
	    # -------------------------	#

	    for obj in objects:	

	      # SQL Foreign key constraint
              fk_constraint = "%ssexdat_id%ssexdat='%d'" % (tbl,tbl,last_id)

	      sql_str = """x_image='%s',y_image='%s',a_image='%s',b_image='%s',theta='%s',
			 el='%s',fwhm='%s',stella='%s',mag_auto='%s',flux_max='%s',background='%s'""" % \
			(obj[1],obj[2],obj[3],obj[4],obj[5],obj[6],obj[7],obj[9],obj[10],obj[11],obj[12])	

	      sql = "INSERT IGNORE INTO %ssexobj SET %s,%s" % (tbl,fk_constraint,sql_str)

	      try:	
                cursor.execute(sql)
	      except  MySQLdb.Error, e:
                self.__cnx1.rollback()
                raise DBException("Error %d: %s" % (e.args[0], e.args[1]))



    def deleteDataDB(self,tbl,id):

        """ Delete Header and Statistcs Data for a Frame """
 

	if self.__cnx1 is not None:

            cursor = self.__cnx1.cursor()

            sql = "DELETE FROM %ssexdat WHERE id_Header = '%s' LIMIT 1" % (tbl,id)
	   
	    try:	
              cursor.execute(sql)
	      self.__cnx1.commit()
	    except  MySQLdb.Error, e:
              raise DBException("Error %d: %s" % (e.args[0], e.args[1]))
              self.__cnx1.rollback()


    def getSeeingData(self,tbl):

        """ Return all seeing entries where TCS system key is NULL """ 

        if self.__cnx1 is not None:		

   	    cursor = self.__cnx1.cursor(MySQLdb.cursors.DictCursor)

	    tblsex   = tbl+"sexdat"
	    idtblsex = "id"+tblsex	
            tblhdu   = tbl+"prihdu"
	    idtblhdu = "id"+tblhdu 	    	

# 	    if tbl == 'NC':
#	    	sql = """
#		  SELECT NCsexdat.idNCsexdat as id,
#	 	  NCprihdu.DateTimeUT,
#	          NCexthdu.EXPTIME
#		  FROM FitsHeader.NCprihdu, FitsHeader.NCexthdu, Pipeline.NCsexdat 
#		  WHERE NCprihdu.DateTimeUT > DATE_SUB(NOW(), INTERVAL %s DAY)
#		  AND NCsexdat.id_Header = NCprihdu.idNCprihdu
#		  AND NCexthdu.IMAGEID = 1 
#		  AND NCexthdu.NCprihdu_idNCprihdu = NCprihdu.idNCprihdu
#                """ 
#	    else:
#		sql = """SELECT %s.%s as id,
#	 	  %s.DateTimeUT,
#	          %s.EXPTIME
#		  FROM FitsHeader.%s, Pipeline.%s 
#		  WHERE %s.DateTimeUT > DATE_SUB(NOW(), INTERVAL %s DAY)
#		  AND %s.id_Header = %s.%s""" % (tblsex,idtblsex,tblhdu,tblhdu,tblhdu,tblsex,tblhdu,interval,tblsex,tblhdu,idtblhdu)

 	    if tbl == 'NC':
	    	sql = """
		  SELECT NCsexdat.idNCsexdat as id,
	 	  NCprihdu.DateTimeUT,
	          NCexthdu.EXPTIME
		  FROM FitsHeader.NCprihdu, FitsHeader.NCexthdu, Pipeline.NCsexdat 
		  WHERE NCsexdat.id_TCS IS NULL
		  AND NCsexdat.id_Header = NCprihdu.idNCprihdu
		  AND NCexthdu.IMAGEID = 1 
		  AND NCexthdu.NCprihdu_idNCprihdu = NCprihdu.idNCprihdu
                """ 
	    else:
		sql = """
		  SELECT %s.%s as id,
	 	  %s.DateTimeUT,
	          %s.EXPTIME
		  FROM FitsHeader.%s, Pipeline.%s 
		  WHERE %s.id_TCS IS NULL
		  AND %s.id_Header = %s.%s
                """ % (tblsex,idtblsex,tblhdu,tblhdu,tblhdu,tblsex,tblsex,tblsex,tblhdu,idtblhdu)

	    try:
	      cursor.execute(sql)
              return cursor.fetchall()

            except MySQLdb.Error, e: 
              raise DBException ("Error: %s (%s)" % (str(e.__class__), str(e)))


    def getSystemIDs(self,date,exptime):

        """ Get System IDs at midpoint of exposure """ 

        if self.__cnx1 is not None:		

   	    cursor = self.__cnx1.cursor(MySQLdb.cursors.DictCursor)

	    sql = """SELECT id_TCS,id_TMS,id_MET,id_DUST,DateTimeUT
                     FROM Operations.SystemStatus
                     WHERE DateTimeUT
                     BETWEEN DATE_SUB(DATE_ADD('%s', INTERVAL %s SECOND), INTERVAL 30 SECOND) AND
                             DATE_ADD(DATE_ADD('%s', INTERVAL %s SECOND), INTERVAL 30 SECOND)
                     LIMIT 1""" % (date,exptime/2,date,exptime/2)

	    try:
	      cursor.execute(sql)
              return cursor.fetchone()

            except MySQLdb.Error, e: 
              raise DBException ("Error: %s (%s)" % (str(e.__class__), str(e)))



    def getDIMMData(self,date,t1,t2):

        """ Get averaged DIMM Data over an interval  """ 

        if self.__cnx1 is not None:		

   	    cursor = self.__cnx1.cursor(MySQLdb.cursors.DictCursor)

	    sql = """SELECT  AVG((fwhmhorl+fwhmvert+fwhmverl)/3) as meanDIMM, 
                             STD((fwhmhorl+fwhmvert+fwhmverl)/3) as stdevDIMM,
                             COUNT(*) as NumDIMM 
                     FROM SiteData.RoboDimmING
                     WHERE DateTimeUT 
                     BETWEEN DATE_SUB('%s', INTERVAL %s SECOND) AND
                             DATE_ADD('%s', INTERVAL %s SECOND)
                   """ % (date,t1,date,t2)

	    try:
	      cursor.execute(sql)
              return cursor.fetchone()

            except MySQLdb.Error, e: 
              raise DBException ("Error: %s (%s)" % (str(e.__class__), str(e)))


    def updateSeeingData(self,tbl,id,sys,dimm):

        """ Update Seeing table with SystemStatus IDs and DIMM measurements """
 

	if self.__cnx1 is not None:

            cursor = self.__cnx1.cursor()

	    # Create full SQL insert statement
            sql = "UPDATE %ssexdat" % tbl + """ 
		     SET id_TCS  = %s,
			 id_TMS  = %s,
			 id_MET  = %s,
			 id_DUST = %s,
			 meanDIMM = %s,
			 stdevDIMM = %s,
		         NumDIMM =  %s """ + \
		   "WHERE id%ssexdat = %s" % (tbl,id)
	     
	    try:	
              cursor.execute(sql, (sys['id_TCS'],sys['id_TMS'],sys['id_MET'],sys['id_DUST'],
			dimm['meanDIMM'],dimm['stdevDIMM'],dimm['NumDIMM']) )

	    except  MySQLdb.Error, e:
              self.__cnx1.rollback()
              raise DBException("Error %d: %s" % (e.args[0], e.args[1]))