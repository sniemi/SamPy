###################################################################
# ABOUT:
#    This Python script gets data from the Pipeline-database and
#    produces plots and correlations of selected variables.
#    The purpose is to study how seeing with ALFOSC
#    is related to various variables e.g. wind and temperature.
#
# NOTE:
#    This is horrible programming. The script is quickly modified
#    from the old al_focpyr_test.py script...
#
# DEPENDS:
#    numpy, scipy, matplotlib (pylab) and SMNpca
#
# AUTHOR:
#    Sami-Matias Niemi, for Nordic Optical Telescope (NOT)
#
# HISTORY:
#    19/09/08 Modified for Pipeline DB
#    14/11/08 Added PCA analysis
#
##################################################################

__author__ = 'Sami-Matias Niemi'
__version__ = '0.1'

class Logger(object):
    def __init__(self, filename, verbose = False):
        self.file = open(filename, 'w')
        self.verbose = verbose
    
    def write(self, text):
        print >> self.file, text
        if self.verbose: print text

#Function for command line arguments
def process_args():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Verbose mode on.")
    parser.add_option("-s", "--show", action="store_true", dest="show",
                      help="Shows plots in X-windows.")
    return parser.parse_args()

#Function for fetching the data
def getdata():
    import MySQLdb
    import sys
    
    #Connect to the QC database and get cursor
    try:
        db = MySQLdb.connect(host="eeva", user="select_user", passwd="select_pass", db="Pipeline", )
        #OLD DATABASE
        #db = MySQLdb.connect(host="eeva", user="select_user", passwd="select_pass", db="QC", )
    except MySQLdb.Error, e:
        print "\n Error while connecting to the MySQL database! \n"
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    
    #Reads the data from the database
    try:    
        cursor = MySQLdb.cursors.Cursor(db)
        #Actual execution command
        cursor.execute("""SELECT medianFWHMcor, meanFWHMcor, stdevFWHM, AltitudePosDeg, WindSpeedMS, WindDirectionDeg, DateTimeUT,TempInAirDegC,TempAtBoxDegC, HumidityPercent, s239, s240, EXPTIME, PressureHPA, AzimuthPosDeg
                  FROM SeeingALdat
                  WHERE EXPTIME > 9.
                  AND N > 4
                  AND medianFWHMcor < 4.0
                  AND stdevFWHM < 0.15
                  AND TELFOCUS > 23350
                  AND TELFOCUS < 23450
                  AND ALAPRTNM = 'Open'
                  AND ALGRNM = 'Open (Lyot)'
                  AND ALFOCUS = 1810
                  AND AltitudePosDeg Not Null
                  AND WindSpeedMS Not Null
                  AND WindDirectionDeg Not Null
                  AND HumidityPercent Not Null
                  AND TempInAirDegC Not Null
                  AND PressureHPA Not Null
                  AND AzimuthPosDeg Not Null""")
        
#        #OLD DATABASE
#        cursor.execute("""SELECT medianFWHMcor, meanFWHMcor, stdevFWHM, AltitudePosDeg, WindSpeedMS, WindDirectionDeg, dateobs, TempInAirDegC,TempAtBoxDegC,HumidityPercent, s239, s240, EXPTIME, PressureHPA
#                  FROM Seeing
#                  WHERE exptime > 1.
#                  AND N > 2
#                  AND instrume = 'alfosc'
#                  AND medianFWHMcor is not NULL
#                  AND telfocus > 23300
#                  AND telfocus < 23500
#                  AND apertur = 'Open'
#                  AND alfocus = 1810""")
    
        #data are saved
        result = cursor.fetchall()
    except MySQLdb.Error, e:
        print "\n Error while reading the MySQL database! \n"
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
        
    #Closes the cursor and the connection
    cursor.close()
    db.close()
    #returns 2D-array
    return result

def basicStatistics(data):
    import numpy as N
    return N.median(data), N.max(data), N.min(data), N.mean(data), N.std(data)

#Function for adding two vectors together
def addVectors(vector1, vector2):
    result = []
    for i in range(0,len(vector1)):
        result.append(vector1[i] + vector2[i])
    return result

def subVectors(vector1, vector2):
    result = []
    for i in range(0,len(vector1)):
        result.append(vector1[i] - vector2[i])
    return result

#Function for getting time
def getTime(data):
    result = []
    for i in range(0,len(data)):
        unixt=mktime(strptime(str(data[i]), "%Y-%m-%d %H:%M:%S"))
        result.append(int(unixt-1154386801.)/(24*60*60))
    return result

def getColumn(vector, column):
    result = []
    for i in range(0,len(data)):
        result.append(vector[i][column])
    return result

#Main program begins!
if __name__ == '__main__':
    from pylab import *
    from time import *
    from scipy.stats.stats import spearmanr, linregress, skewtest, mode
    import numpy as N
    import SMNpca
    
    #Fetch the data
    data = getdata()

    #Checks if verbose was selected
    (opts, args) = process_args()
    if opts.verbose == True: 
        print "\nVerbose mode.\n"
        print "%d rows were returned" % len(data)
        print

    #lets do PCA
    indices = (0,3,5,7,9,12,13,14)
    limdata = N.array(data)[:,indices]
    PCA = SMNpca.SMNpca(N.transpose(limdata), stdnorm = False)
    newdata = PCA.doPCA()
    if opts.verbose == True:
        PCA.DisplayCov()
        PCA.DisplayEigenvalues()
        PCA.DisplayEigenvectors()
        PCA.DisplayFeatureMatrix()
    PCA.VisualisePCAtoFileIn2D(newdata, 'PCA2d')
    PCA.VisualisePCAtoFileIn3D(newdata, 'PCA3d')

    #this would be completely obsolete with:
    #data = N.array(data)
    #medianFWHM = data[:,0]
    #etc
    #Only could also write an dictionary for columns...
    #saves data to specified vectors
    medianFWHM = getColumn(data,0)
    meanFWHM = getColumn(data,1)
    stdevFWHM = getColumn(data,2)
    AltitudePosDeg = getColumn(data,3)
    WindSpeedMS = getColumn(data,4)
    WindDirectionDeg = getColumn(data,5)
    DateTimeUT = getColumn(data,6)
    TempInAirDegC = getColumn(data,7)
    TempAtBoxDegC = getColumn(data,8)
    HumidityPercent = getColumn(data,9)
    temp239 = getColumn(data,10)
    temp240 = getColumn(data,11)
    exptime = getColumn(data,12)
    PressureHPA = getColumn(data,13)
        
    #A special column
    #This would be obsolete with:
    #from matplotlib.dates import MONDAY, MonthLocator, WeekdayLocator, DateFormatter
    time = getTime(DateTimeUT)
    
    #Just an empty class
    class Dummy(object): pass
    
    #Lets get some statistics
    tdfst = Dummy()
    tdfStat = []
    
    tdfst.name, tdfst.median, tdfst.max, tdfst.min, tdfst.mean, tdfst.stdev = \
    "Seeing", median(medianFWHM), max(medianFWHM), min(medianFWHM), mean(medianFWHM), std(medianFWHM)
    
    tdfst.mode = mode(medianFWHM)
 
    tdfStat.append(tdfst)
    
    if opts.verbose == True:
        print
        print ("%5s" + "%11s"*6) % ("Name", "Median", "Max", "Min", "Mean", "Stdev", "Mode")
        frmt = "%5s" + "%11.2f"*6
        print frmt % (tdfst.name, tdfst.median, tdfst.max, tdfst.min, tdfst.mean, tdfst.stdev, tdfst.mode[0])
        print
    
    #Calculates some 2D correlations
    WDCorr = spearmanr(medianFWHM, WindDirectionDeg)
    Humidity = spearmanr(medianFWHM, HumidityPercent)
    Pressure = spearmanr(medianFWHM, PressureHPA)

    #Calculates skewness test
    #Tests whether the skew is significantly different from a normal distribution.
    tfdskew = skewtest(medianFWHM)
    
    if opts.verbose == True:
        print "\nSpearman Rank correlation between WindDirection and medianFWHM: ", WDCorr
        print "Skewness of medianFWHM (Z-score, Z-prob.): ", tfdskew
        print "\nSpearman Rank correlation between air humidity and medianFWHM: ", Humidity
        print "\nSpearman Rank correlation between pressure and medianFWHM: ", Pressure
        print
        
    y2007 = mktime(strptime("2007-01-01 00:00:01","%Y-%m-%d %H:%M:%S"))-1154386801.
    y2008 = mktime(strptime("2008-01-01 00:00:01","%Y-%m-%d %H:%M:%S"))-1154386801.
    y2007 = y2007/(24*60*60)
    y2008 = y2008/(24*60*60)
    
    #Figure1
    figure(1)
    #subimage for Fig1    
    subplot(211)
    title('ALFOSC Seeing data')
    errorbar(time, medianFWHM, yerr=stdevFWHM, fmt='bo')
    axhline(tdfst.median)
    axvline(y2007)
    axvline(y2008)
    limits=[200.,880.,0,5]
    axis(limits)
    text(90,23225,'2006')
    text(300,23225,'2007')
    text(550,23225,'2008')
    legend()
    ylabel('Seeing (arc sec)')

    #subimage for Fig1
    subplot(212)
    plot(time, TempInAirDegC,'ro')
    axhline(0.)
    axvline(y2007)
    axvline(y2008)
    limits=[200.,880.,-3.,21]
    axis(limits)
    ylabel('Temperature In Air (DegC)')
    xlabel('day since 01-01-2006')
    savefig('seeing_time.png')
        
    #Figure 2
    figure(2)
    plot(TempInAirDegC, medianFWHM, 'bo')
    axhline(tdfst.median, color='r')
    xlabel('Temperature In Air (DegC)')
    ylabel('Median FWHM')
    savefig('seeingtemp.png')
       
    #Histogram
    figure(4)
    xlabel('Seeing (arc sec)')
    histogram = hist(medianFWHM, bins=20, log=True)
    axvline(tdfst.median, linewidth=2.5, color='r', label='Median value')
    savefig('seeinghistogram.png', facecolor='w', edgecolor='w', orientation='portrait')
    
    figure(5)
    plot(HumidityPercent, medianFWHM,'bo')
    axhline(tdfst.median, color='r')
    xlabel('Humidity (per cent)')
    ylabel('Seeing (arc sec)')
    savefig('humidity.png')
    
    figure(7)
    plot(temp239, medianFWHM, 'bo')
    axhline(tdfst.median, color='r')
    xlabel('Temperature s239 (DegC)')
    ylabel('Seeing (arc sec)')
    savefig('temp239.png')
    
    figure(8)
    plot(temp240, medianFWHM,'bo')
    axhline(tdfst.median, color='r')
    xlabel('Temperature s240 (DegC)')
    ylabel('Seeing (arc sec)')
    savefig('temp240.png')
    
    figure(9)
    xlabel('Standard deviation of Seeing')
    histogram = hist(stdevFWHM, bins=15, log=True)
    savefig('stdev_histog.png', facecolor='w', edgecolor='w', orientation='portrait')

    figure(10)
    plot(medianFWHM, meanFWHM,'bo')
    plot([0,9],[0,9], 'r-')
    axis([0,5,0,5])
    xlabel('Mediancor FWHM')
    ylabel('Meancor FWHM')
    savefig('fwhm.png')
    
    figure(11)
    plot(log(exptime),medianFWHM,'bo')
    axhline(tdfst.median, color='r')
    xlabel('Log (Exposure time (sec))')
    ylabel('Seeing (arc sec)')
    savefig('exptime.png')
    
    figure(12)
    plot(WindDirectionDeg,medianFWHM,'bo')
    axhline(tdfst.median, color='r')
    xlabel('Wind Direction (Deg)')
    ylabel('Seeing (arc sec)')
    savefig('windDirection.png')
    
    figure(13)
    plot(PressureHPA,medianFWHM,'bo')
    axhline(tdfst.median, color='r')
    xlabel('Pressure (HPa)')
    ylabel('Seeing (arc sec)')
    savefig('pressure.png')
    
    figure(14)
    plot(WindSpeedMS,medianFWHM,'bo')
    axhline(tdfst.median, color='r')
    xlabel('Wind Speed (m/s)')
    ylabel('Seeing (arc sec)')
    savefig('windspeed.png')
    
    figure(15)
    scatter(WindDirectionDeg, WindSpeedMS, s=20, c='b', marker='o')
    xlabel('Wind Direction (Deg)')
    ylabel('Wind Speed (m/s)')
    savefig('wind')
    
    #Show all the figures!
    if opts.show == True: show() 
    
    if opts.verbose == True: print "\nProgram exits...\n"
    sys.exit()
    