import MySQLdb
import re

class DBException(Exception):
  pass

class MySQLhandler:

    """ 
        Wrapper class for retrieving FIES and TCS status values from databases 
    """

    def __init__(self):

        """ 
            Initialize the MySQL connection and define mappings between encoder positions 
            and description of arm, mask and lamp positions 
        """

	try:
	  # Create a persistent database connection 
          self.__cnx = MySQLdb.connect(host='lili',user='select_user',passwd='select_pass',db='Operations')

          #Upon initialization, define mappings from static DB tables    
          cursor = self.__cnx.cursor(MySQLdb.cursors.DictCursor)

          cursor.execute('select humpos AS pos, name from FIESArm')
          self.fibArmDict = self.tuble2dict(cursor)

          cursor.execute('select humpos AS pos, name from FIESMask')
          self.fibMaskDict = self.tuble2dict(cursor)   

          cursor.execute('select position AS pos, name from FIESLamps')
          self.calLampDict = self.tuble2dict(cursor)
          self.calLamps = {1:"lamp1",2:"lamp2",3:"lamp3",4:"lamp4"}

          cursor.execute('select pos, nametxt AS name from FIESFibLamps')
          self.fibLampDict = self.tuble2dict(cursor)
          self.fibLamps = {1:"fiblamp1",2:"fiblamp2"}

          # Define simple mappings for shutters
          self.ccdShutterDict = {0:'Closed',1:'Open'}
          self.calShutterDict = {0:'Closed',1:'Open'}

 	except MySQLdb.Error, e: 
          raise DBException ("Fatal Error: %s (%d)" % (e.args[1], e.args[0]))


    def tuble2dict(self,cursor):

        """
            Convert a tuble of dictionaries into a dictionary
        """

        a = cursor.fetchall()
        dict = {}
        for i in range(len(a)):
            key = a[i]['pos']
            val = a[i]['name']
            dict[key] = val
        return dict

    def close(self):

        """
            Close database connection
        """    

        if self.__cnx is not None:
            self.__cnx.close()
            self.__cnx = None


    def InitFiesStatus(self):

	""" Return an undef dictionary of Fies status values """

	status = {}
	status["fiesfocus"]  	= 'na'
	status["ccdshutter"] 	= 'na'
	status["calshutter"] 	= 'na'
	status["callamps"]	= 'na'
	status["fiberlamps"]	= 'na'
	status["fibermask"]	= 'na'
	status["maskpos"]	= 4
	status["fiberarm"]	= 'na'
	status["armpos"]   	= 0		
	status["calmirror"]	= 'na'	
	return status


    def queryFiesStatus(self):

        """
            Return a dictionary of actual status values of FIES, stored in database
        """
	try:
          status = {}
          cursor = self.__cnx.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute('SELECT focenc,lamp1,lamp2,lamp3,lamp4,lamp5,fiblamp1,fiblamp2,shut_pos,cshut_pos,posenc,maskenc,armenc,counts FROM FIESInst')

          # FIES status is stored in one row, we use fetchone()
          a = cursor.fetchone()
            
          # The FIES focus value is the raw value stored in database
          status["fiesfocus"]  = a['focenc']

          # 'shut_pos' is either '0' or '1' - map it to 'Open', 'Closed' or Unknown
          status["ccdshutter"] = self.ccdShutterDict.get(a['shut_pos'], "<font color='#aa0000'>Unknown</font>")

          # as above for calibration shutter
          status["calshutter"] = self.calShutterDict.get(a['cshut_pos'], "<font color='#aa0000'>Unknown</font>")

          # Create a string of calibration lamps currently turned on
          status["callamps"] = '\n'.join([self.calLampDict[key] for (key,val) in self.calLamps.items() if a[val] == 1])
          if not status["callamps"]:
            status["callamps"] = "Lamps Off"
            
          # Create a string of fiber calibration lamps currently turned on
          status["fiberlamps"] = '\n'.join([self.fibLampDict[key] for (key,val) in self.fibLamps.items() if a[val] == 1])
          if not status["fiberlamps"]:
            status["fiberlamps"] = "Lamps Off"        

          # The Exposure Meter counts is the raw value stored in database
          status["counts"] = a['counts']

          # Get the human readable positions of mask,arm and cal. selector
          cursor.execute('SELECT * FROM FIESHumPos')
          b = cursor.fetchall()
        
          # Get name of Mask position
          if (a['maskenc'] == -99):
            status["fibermask"] = "Moving"
            status["maskpos"]   = 4 #when moving, set mask to closed
          elif (a['maskenc'] == -88):
            status["fibermask"] = "Initialized"
            status["maskpos"]   = 4 #when moving, set mask to closed
          else:
            status["fibermask"] = re.sub(' ','\n',self.fibMaskDict[b[0]['humpos']])
            status["maskpos"]   = b[0]['humpos']
    
          # Get name of Arm position
          if (a['armenc'] == -99):
            status["fiberarm"] = "Moving"
            status["armpos"]   = 0
          elif (a['armenc'] == -88):
            status["fiberarm"] = "Initialized"
            status["armpos"]   = 0
          else:
            tmp = re.split(' ',self.fibArmDict[b[1]['humpos']])
            status['fiberarm'] = '%s %s \n %s' % (tmp[0],tmp[1],tmp[2])
            status["armpos"]   = b[1]['humpos']  
    
          # Get name of Lamp selector position (calmirror)
          if (a['posenc'] == -99):
            status["calmirror"] = "Moving"
          else:
            status["calmirror"] = self.calLampDict[b[2]['humpos']]

          # return the dictionary containing the current FIES status
          return status
	except Exception, e: 
          raise DBException ("Error: %s (%s)" % (str(e.__class__), str(e)))

    

    def InitTCSStatus(self):

	""" Return an undef dictionary of TCS status values """

	status = {}
	status['ut'] 		= 'na'
	status["pickoffmirror"] = 'na'
	status["ccdfilter"]	= 'na'
	status["ccdfiltername"]	= 'na'
	status['vignetting']	= 'na'
	return status

    def queryTcsStatus(self):

        """
            Return a dictionary of TCS status values to be shown in the GUI
        """

	try:
          status = {}
          cursor = self.__cnx.cursor(MySQLdb.cursors.DictCursor)
          cursor.execute('SELECT * FROM TCSStatusNow')
	  self.__cnx.commit()
          a = cursor.fetchone()

	  # Get current UT from TCS
	  status['ut'] = a['DateTimeUT']
	  
	  # Determine status of the pickoff mirror	
          if a['CameraProbeInSplitPos']: 
	    status["pickoffmirror"] = "FIES"
          elif a['CameraProbeInCCDpos']: 
            status["pickoffmirror"] = "StanCam"
          else: # we have a['CameraProbeParked'] 
	    status["pickoffmirror"] = "Park"

	  # StanCam filter position
          status["ccdfilter"]     = str(a.get('CCDfilterNumber',0))
          status["ccdfiltername"] = a.get('CCDfiltName','na')

	  # Check if telescope beam is somehow vignetted
	  vignet = []	

          # guide probe vignetting area.
          if (
            (58000 < a['GuideProbeX'] < 162000) and
            (26000 < a['GuideProbeY'] < 133000)
          ):      	
            vignet.append('Guideprobe')
                
	  # Mirror Covers not opened
	  if not a['MirrorCoversOpened']: vignet.append('MirrorCover') 

	  # Upper Hatch
	  if not a['UpperHatchOpened']: vignet.append('UpperHatch')

	  # Lower Hatch
	  if (
	    (not a['LowerHatchOpened']) and
	    (a['AltitudePosDeg'] < 30)
	  ): 
	     vignet.append('LowerHatch')
	
	  status['vignetting'] = '<font color=red>' + '<br>'.join(vignet) + '</font>'

          return status
    
	except Exception, e: 
          raise DBException ("Error: %s (%s)" % (str(e.__class__), str(e)))

