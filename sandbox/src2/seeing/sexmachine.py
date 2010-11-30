import tempfile
import os

class Sextractor:

  def __init__(self):
    
    self.sexpath     = '/usr/local/bin/sex '
    self.configpath  = '/home/postprocess/seeing_mon/src.v2/config/'
    self.conf_file   = self.configpath + 'default.sex'
    self.param_file  = self.configpath + 'default.param' 	
    self.nnw_file    = self.configpath + 'default.nnw'		
    self.filter_file = self.configpath + 'default.conv'	
    self.output_file = tempfile.mkstemp()[1]	


  def dosex(self, fits_file, output, 
		SATUR_LEVEL='58000', 
		MAG_ZEROPOINT='21', 
		GAIN='0.7', 
		PIXEL_SCALE='0.2',
		SEEING_FWHM='1.0'):

    """
	Execute the sextractor binary
    """			

    import os	
    	
    # Calculate the minimum detection threshold in pixels to be passed 
    # as input paramter to sextractor. This depends on pixel scale. 
    # We choose a threshold of 0.76 arcsec^2
    DETECT_MINAREA = str(int((0.76/float(PIXEL_SCALE))**2))

    command = self.sexpath + fits_file + ' -c ' + self.conf_file + \
		' -PARAMETERS_NAME ' + self.param_file + \
		' -FILTER_NAME ' + self.filter_file + \
		' -CATALOG_NAME ' + self.output_file + \
		' -STARNNW_NAME ' + self.nnw_file + \
		' -VERBOSE_TYPE FULL ' + \
		' -SATUR_LEVEL ' + SATUR_LEVEL + \
		' -MAG_ZEROPOINT ' + MAG_ZEROPOINT + \
		' -GAIN ' + GAIN + \
		' -PIXEL_SCALE ' + PIXEL_SCALE + \
		' -DETECT_MINAREA ' + DETECT_MINAREA + \
		' -SEEING_FWHM ' + SEEING_FWHM

    # Execute command and catch output. We use popen3 to catch and discard
    # stderr output from sextractor
    cin, cout, cerr = os.popen3(command)
    res = ''.join(cout.readlines())

    # Write to logfile
    logfile = open(output, 'a')
    logfile.write('Executing command:\n' + command)    
    logfile.write(res)
    logfile.close()

  def readsex(self,output):

    """
	Read the source catalog into a list 	
	Return list
    """

    # Define the list to hold sources	
    objects = []

    # Read in a list of sources from sextractor output file 
    # Remove trailing '\n', using splitlines()

    fh = open(self.output_file)	    	
    sources = fh.read().splitlines()
    fh.close()

    # Remove the temporary sextractor output file
    os.remove(self.output_file)    

    # Run split on each object and store data in list
    # We thus have a list of lists 
    for s in sources:
	objects.append(s.split())

    # Write to logfile
    logfile = open(output, 'a')
    loghead = "====== Sextractor Output: length=%s ======\n" % len(objects)
    logfile.write(loghead)    
    for o in objects:
       logfile.write('\t'.join(o) + '\n')
    logfile.close()

    # Return the list of lists
    return objects


  def filtersex(self, objects, output, **kw):

    """
	Remove bad data from a list of sources 	
	Return list
    """	
       
    #  0: NUMBER
    #  1: X_IMAGE
    #  2: Y_IMAGE
    #  3: A_IMAGE
    #  4: B_IMAGE
    #  5: THETA_IMAGE
    #  6: ELLIPTICITY
    #  7: FWHM_IMAGE
    #  8: FLAGS
    #  9: CLASS_STAR
    # 10: MAG_AUTO
    # 11: FLUX_MAX	
    # 12: BACKGROUND	

    if 'ErrorFlag' in kw:
       # Remove sources for which sextractor has raised an error flag
       objects = [obj for obj in objects if int(obj[8]) == kw['ErrorFlag']]	
    
    if 'MinAxisRMS' in kw:
       # Remove sources with an semi major/minor axis rms less than a number. Typically 1 pixel.
       MinRMS = kw['MinAxisRMS']
       objects = [obj for obj in objects
 		if float(obj[3]) > MinRMS and float(obj[4]) > MinRMS]

    if 'MinFWHM' in kw:
       # Remove sources with FWHM less than a number. Typically 2pixels (undersampling)
       objects = [obj for obj in objects if float(obj[7]) > kw['MinFWHM']]	

    if 'StellaLike' in kw:
       # Remove sources based on the stellar-like parameter 
       objects = [obj for obj in objects if float(obj[9]) > kw['StellaLike']]	

    if 'EdgeObj' in kw:
       # Remove sources close to the CCD edge
       TheEdge = kw['EdgeObj']	
       objects = [obj for obj in objects
 		if int(obj[1]) < TheEdge and int(obj[2]) < TheEdge]

    if 'SigmaClip' in kw:
	# Sigmaclip also requieres Mean and StdDev to be passed
	#  to the filtersex method in order to be valid.
	clipLowLimit  =  float(kw['Mean']) - float(kw['SigmaClip']) * float(kw['Stdev'])
	clipHighLimit =  float(kw['Mean']) + float(kw['SigmaClip']) * float(kw['Stdev'])
	if __debug__ : print "Low Clip Limit: " + str(clipLowLimit)
	if __debug__ : print "High Clip Limit: " + str(clipHighLimit)
	objects = [obj for obj in objects
		if float(obj[7]) <= clipHighLimit and float(obj[7]) >= clipLowLimit ]	


    # Write to logfile
    logfile = open(output, 'a')
    cmdpar = ",".join(["%s=%s" % (k,v) for k,v in kw.items()])
    loghead = "====== Filtered Output: %s,length=%s ======\n" % (cmdpar,len(objects))
    logfile.write(loghead)    
    for o in objects:
       logfile.write('\t'.join(o) + '\n')
    logfile.close()

    return objects


  def statsex(self, objects):

    """
	Do some statistics on a source list
	Return dictionary
    """

    import stats, pstat
    
    # Return if we have no objects
    if len(objects) == 0:
      return 0	 

    # Define dictionary to hold statistics	
    stat = {}

    # Get number of objects
    stat['N'] = str(len(objects))

    # Define list (float) of FWHM values
    fwhm = [ float(obj[7]) for obj in objects ]
 
    # Define list (float) of ELLIPTICITY values
    el = [ float(obj[6]) for obj in objects ]

    # Define list (float) of THETA_IMAGE values
    pa = [ float(obj[5]) for obj in objects ]

    # Define list (float) of 'Stella-like' values
    stella = [ float(obj[9]) for obj in objects ]	

    # Create a histogram of FWHM values of binsize 1 pixel
    hfwhm = stats.histogram(fwhm,40,[0,40])[0]
    
    stat['medianFWHM'] = "%.2f" % stats.median(fwhm)
    stat['meanFWHM']   = "%.2f" % stats.mean(fwhm)
    stat['modeFWHM']   = "%.2f" % float(hfwhm.index(max(hfwhm))+0.5)

    try:	
       stat['stdevFWHM']  = "%.2f" % stats.stdev(fwhm)
    except ZeroDivisionError:
       stat['stdevFWHM'] = '0.00';

    stat['medianEL'] = "%.2f" % stats.median(el)
    stat['meanEL']   = "%.2f" % stats.mean(el)

    try:
      stat['stdevEL']  = "%.2f" % stats.stdev(el)
    except ZeroDivisionError:
      stat['stdevEL']  = '0.00' 

    # Histogram of Ellipticity PA (-180 to 180, bins of 45 deg)
    #stat['histoTHETA'] = stats.histogram(pa,8,[-180,180])[0]

    # Histogram of Stellarity (0 to 1, bins of 0.05)
    #stat['histoStella']  = stats.histogram(stella,20,[0,1.01])[0]   

    return stat


  def WriteDS9Regions(self,objects,ds9_nm) :

    """ Find brightest objects and write ds9 colour regions file """
    
    ds9file = open(ds9_nm, 'w')
    
    for obj in filter(lambda x: (float(x[11]) + float(x[12])) > 60000., objects):
       ds9file.write("image;circle(%.2f,%.2f,30) # color=red width=2 \n"  % (float(obj[1]),float(obj[2])))
    ds9file.close()

#   colorobjects = [obj for obj in objects if float(obj[11]) > 10000.]
#	peak = float(obj[11]) + float(obj[12]) 
#        if (peak > 60000.) :
#            ds9file.write("image;circle(%.2f,%.2f,30) # color=red width=2 \n"  % (float(obj[1]),float(obj[2])))
#        if (peak > 50000.) :
#            ds9file.write("image;circle(%.2f,%.2f,30) # color=magenta width=2 \n"  % (float(obj[1]),float(obj[2])))
#        if (peak > 40000.) and (peak <= 50000.):
#            ds9file.write("image;circle(%.2f,%.2f,30) # color=green width=2 \n"  % (float(obj[1]),float(obj[2])))
#        if (peak > 30000.) and (peak <= 40000.):
#            ds9file.write("image;circle(%.2f,%.2f,30) # color=yellow width=2 \n"  % (float(obj[1]),float(obj[2])))
#        if (peak > 10000.) and (peak <= 30000.):
#            ds9file.write("image;circle(%.2f,%.2f,30) # color=blue width=2 \n"  % (float(obj[1]),float(obj[2])))
#        if (peak > 1000.) and (peak <= 20000.):
#            ds9file.write("image;circle(%.2f,%.2f,30) # color=blue width=2 \n"  % (float(obj[1]),float(obj[2])))
#    ds9file.close()



  def WriteDS9Stats(self,filename,s,ds9_nm): 

    """ Append image statistics to a ds9 input file """ 

    ds9file = open(ds9_nm, 'a')
    ds9file.write("global color=green font=\"helvetica 12 normal\" select=1 highlite=1 edit=1 move=1 delete=1 include=1 fixed=0 \n")
    #ds9file.write("# text(0,300) text={File: %s} color=green \n" % filename)
    ds9file.write("# text(300,150) text={Seeing: %1.2f''} color=green \n" % float(s['meanFWHM']) )
    ds9file.write("# text(300,50) text={Elong: %.2f} color=green \n" %  float(s['meanEL']) )
    ds9file.close()