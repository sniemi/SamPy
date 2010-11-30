###################################################################
# ABOUT:
#    This Python script gets data from the Pipeline-database and
#    produces plots and can calculates correlations of selected 
#    variables.
#    The purpose is to study how ALFOSC telescope focus is
#    related to various variables e.g. temperature and altitude.
#
# DEPENDS:
#    numpy, scipy and matplotlib (pylab)
#
# AUTHOR:
#    Sami-Matias Niemi, for Nordic Optical Telescope (NOT)
#
# HISTORY:
#    25/04/08 Initial Version
#    07/10/08 Modified for new plots etc.
#    08/10/08 Changed correction from TempInAir to Focus Temp
#
# CURRENT VERSION:
#    0.13a
##################################################################

__author__ = 'Sami-Matias Niemi'
__version__ = "0.13a"

class Logger(object):
    def __init__(self, filename, verbose = False):
        self.file = open(filename, 'w')
        self.verbose = verbose
    
    def write(self, text):
        print >> self.file, text
        if self.verbose: print text

def scatterPlot(x, ycorr, ynocorr, yerr, xlabel, ylabel, name, medianOld, medianNew):
    import pylab as P
    #P.scatter(x, y, s = 15, marker = 'o', c = 'b')
    P.plot(x, ynocorr, 'wo', label = 'UnCorrected', linestyle = 'None')
    P.errorbar(x, ycorr, yerr=yerr, fmt='bo', label = 'Corrected')
    P.axhline(medianOld, color ='b', label = 'Old Median', lw = 1.1, ls = '-')
    P.axhline(medianNew , color ='r', label = 'New Median', lw = 1.1, ls = '--')
    P.ylabel(ylabel)
    P.xlabel(xlabel)
    #P.yscale('log')
    #P.ylim(min(y), max(y))
    #P.xlim(min(x), max(x))
    P.legend(shadow=True, loc = 'best')
    P.savefig(name + '.png')
    P.close()

def histogramPlot(data, xlabel, bins, log, name, median = False):
    import pylab as P
    import numpy as N
    P.xlabel(xlabel)
    P.hist(data, bins=bins, log=log, rwidth = 0.8)
    if median: P.axvline(N.median(data), linewidth=2.5, color='r')
    P.savefig(name)
    P.close()

def process_args():
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Verbose mode on.")
    return parser.parse_args()

def getdata(sql):
    import MySQLdb
    import sys
        
    #Connects to the Pipeline database and gets cursor
    try:
        db = MySQLdb.connect(host="eeva", user="select_user", passwd="select_pass", db="Pipeline", )
    except MySQLdb.Error, e:
        print "\n Error while connecting to the MySQL database! \n"
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)
    
    #Reads the data from the database
    try:    
        cursor = MySQLdb.cursors.Cursor(db)
        cursor.execute(sql)   
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

def extraHistogram():
    import pylab as P
    import numpy as N
    
    
    P.figure()
    bins = 25
    min = 23310.
    max = 23455.
    nu, binsu, patchesu = P.hist(telfocusOld, bins=bins, rwidth=0.9, range = (min, max) , 
           label = 'UnCorrected Data', fc ='b', alpha = 0.4, normed = True)
    n, bins, patches = P.hist(telfocusCorrected, bins=bins, rwidth=0.7, range = (min, max),
           label='Corrected Data', fc = 'r', alpha = 0.6, normed = True)
    #P.axvline(medianNew, label = 'Corrected Median', color = 'r', lw = 1.1)
    #P.axvline(medianOld, label = 'UnCorrected Median', color = 'b', lw = 1.1)
    y1 = P.normpdf(binsu, N.mean(telfocusOld), N.std(telfocusOld))
    y2 = P.normpdf(bins, N.mean(telfocusCorrected), N.std(telfocusCorrected))
    P.plot(binsu, y1, 'b-', linewidth = 2.5, label='Gaussian Fit')
    P.plot(bins, y2, 'r-', linewidth = 3., label='Gaussian Fit')
    P.xlim(min,max)
    P.xlabel('Telescope Focus + median Offset')
    P.ylabel('Normed Values')
    P.legend(shadow=True, loc ='best')
    P.savefig('TelFocusHistogram.png')
    P.close()
 
def oldvsnew():
    import pylab as P
    import numpy as N

    length = len(data[:,dict['stdevOffset']])
    ones = N.ones(length)
    
    size = 100.*ones/data[:,dict['stdevOffset']]
    
    P.figure()
    P.title('Circle size corresponds to stdevOffset$^{-1}$')
    P.scatter(telfocusOld, telfocusCorrected, s = size, alpha = 0.6)
    P.plot([0., 30000.], [0., 30000.], lw = 1.8)
    P.xlabel('Corrected Telescope Focus + Median Offset')
    P.ylabel('Original Telescope Focus + Median Offset')
    P.xlim(23325,23455)
    P.ylim(23325,23455)
    P.savefig('oldvsnew.png')
    P.close()

def extraPlots():
    import datetime
    from matplotlib.dates import MONDAY, MonthLocator, WeekdayLocator, DateFormatter

    #converts dates to format matplotlib understands...
    time = P.date2num(data[:,dict['DateTimeUT']])

    mondays   = WeekdayLocator(MONDAY)
    months    = MonthLocator(range(1,13, 2), bymonthday=2)
    monthsFmt = DateFormatter("%b '%y")
    
    y2007 = datetime.date(2007, 1, 1)
    y2008 = datetime.date(2008, 1, 1)

    y2007plot = P.date2num(y2007)
    y2008plot = P.date2num(y2008)

    widening = 5.

    fig = P.figure()
    P.subplots_adjust(hspace=0.1)
    ax = fig.add_subplot(211)
    P.title('ALFOSC focus pyramid data')
    ax.plot_date(time, telfocusOld, 'wo', xdate = True)
    ax.plot_date(time, telfocusCorrected, 'bo')
    ax.axhline(medianNew, color = 'b', label = 'New Median', lw = 1., ls = '-')
    ax.axhline(medianOld, color = 'r', label ='Old Median', lw = 1., ls = '--')
    ax.axvline(y2007plot, color = 'k')
    ax.axvline(y2008plot, color = 'k')
    ax.legend(shadow = True, loc = 'best')
    P.ylabel('Telescope Focus + Median Offset')
    P.xlim(min(time)-widening, max(time)+widening)
    P.ylim(23300.,23500.)
    ax.xaxis.set_major_locator(months)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(mondays)
    fig.autofmt_xdate()
    
    bx = fig.add_subplot(212)
    bx.plot_date(time, data[:,dict['TempInAirDegC']], fmt='ro', xdate=True)
    bx.axhline(0.)
    bx.axvline(y2007plot, color = 'k')
    bx.axvline(y2008plot, color = 'k')
    bx.xaxis.set_major_locator(months)
    bx.xaxis.set_major_formatter(monthsFmt)
    bx.xaxis.set_minor_locator(mondays)
    P.xlim(min(time)-widening, max(time)+widening)
    P.ylabel('Temperature In Air (DegC)')
    fig.autofmt_xdate()
    fig.savefig('foc-pyr_time.png')
    P.close()
    
def OffsetPlot():
    import pylab as P
    import scipy.stats as S
    
    offsp = S.spearmanr(data[:,dict['medianOffset']], telfocusCorrected)
    offreg = S.linregress(data[:,dict['medianOffset']], telfocusCorrected)
    offreg2 = S.linregress(data[:,dict['medianOffset']], telfocusOld)
    min = -50.
    max = 50.
    
    print '\nOffset Spearman rank-order:', offsp
    print 'Offset fit:', offreg
    print 'and For unCorrected data:', offreg2
    
    P.plot(data[:,dict['medianOffset']], telfocusCorrected, 'bo', label = 'Data')
    P.plot([min,max], [min*offreg[0] + offreg[1], max*offreg[0] + offreg[1]], 
           'r-', label ='Linear Fit (Corrected)', lw = 2.0)
    P.plot([min,max], [min*offreg2[0] + offreg2[1], max*offreg2[0] + offreg2[1]], 
           'g--', label ='Linear Fit (UnCorrected)', lw = 1.5)
    P.axhline(medianNew, color ='b')
    P.xlim(min, max)
    P.xlabel('Median Offset (telescope units)')
    P.ylabel('Temperature Corrected Telescope Focus + Median Offset')
    P.legend(shadow=True)
    P.savefig('offsetCorrelation.png')
    P.close()
    
def focusTempPlot():
    import pylab as P
    
    P.plot([0.,20.],[correction[1],20.*correction[0]+correction[1]], 'r-', linewidth=2.0, label = 'Linear Fit')
    P.errorbar(focustemp, data[:,dict['telfocus']], yerr=data[:,dict['stdevOffset']],
               fmt='bo', label = 'UnCorrected Data')
    P.axhline(medianOld)
    P.xlabel('Focus Temperature (degC)')
    P.ylabel('Telescope Focus + Median Offset')
    P.xlim(2.,20.)
    P.ylim(23300.,23500.)
    P.savefig('FocusTemperature.png')
    P.legend(shadow=True)
    P.close()

def basicStatistics(data):
    import numpy as N
    return N.median(data), N.max(data), N.min(data), N.mean(data), N.std(data)

#Main program begins!
if __name__ == '__main__':
    import pylab as P
    import numpy as N
    import scipy.stats as S

    sql = """SELECT telfocus + medianOffset as telfocus,
    medianOffset,
    telalt,
    DateTimeUT,
    TempInAirDegC,
    TempAtBoxDegC,
    azimuth,
    AirMass,
    HumidityPercent,
    s239,
    s240,
    stdevOffset,
    Airmass,
    exptime,
    PressureHPA,
    s201,
    ActualFieldRotDeg,
    RotatorPosDeg,
    AzimuthPosDeg,
    ObjectRAhours,
    s244
FROM FocusALdat
    WHERE exptime > 5.
    AND N > 2
    AND medianOffset between -45 and 45
    AND telfocus between 23300 and 23500
    AND stdevOffset < 20
    AND stdevOffset != 0.0
    AND ALFLTNM ='Open'
    AND FAFLTNM ='Open'
    AND FBFLTNM ='Open'
    AND ALFOCUS = 1810
    AND FocusDeltaPos = 0
    AND TempInAirDegC > 0.0
    AND s201 Not Null"""

    dict = {'telfocus' : 0,
           'medianOffset' : 1,
           'telalt' : 2,
           'DateTimeUT' : 3,
           'TempInAirDegC' : 4,
           'TempAtBoxDegC' : 5,
           'azimuth' : 6,
           'AirMass' : 7,
           'HumidityPercent' : 8,
           's239' : 9,
           's240' : 10,
           'stdevOffset' : 11,
           'Airmass' : 12,
           'exptime' : 13,
           'PressureHPA' : 14,
           's201' : 15,
           'ActualFieldRotDeg' : 16,
           'RotatorPosDeg' : 17,
           'AzimuthPosDeg' : 18,
           'ObjectRAhours' : 19,
           's244': 20
           }
 
    scatters = {'telfocus' : (0, 'Telescope Focus + Median Offset'),
           'medianOffset' : (1, 'Median Offset'),
           'telalt' : (2, 'Telecsope Altitude'),
           'TempInAirDegC' : (4, 'Temperature In Air (DegC)'),
           'TempAtBoxDegC' : (5,'Temperature At Box (DegC)'),
           'azimuth' : (6, 'Azimuth (Deg)'),
           'AirMass' : (7, 'AirMass'),
           'HumidityPercent' : (8, 'Humidity (%)'),
           's239' : (9, 'Temperature s239 (DegC)'),
           's240' : (10, 'Temperature s240 (DegC)'),
           'stdevOffset' : (11, 'StDev of Offset'),
           'Airmass' : (12, 'Air Mass'),
           'exptime' : (13, 'Exposure Time (s)'),
           'PressureHPA' : (14, 'Air Pressure (HPa)'),
           's201' : (15, 'Temperature s201 (DegC)'),
           'ActualFieldRotDeg' : (16,'Actual Field Rotation (Deg)'),
           'RotatorPosDeg' : (17, 'Rotator Position (Deg)'),
           'AzimuthPosDeg' : (18, 'Azimuth Position (Deg)'),
           'ObjectRAhours' : (19, 'Object RA (hours)'),
           's244' : (20, 'Temperature s244 (DegC)')
           }
    
    hists = {'stdevOffset':
            {'column' : 11, 
            'file' : 'stdev_histogram',
            'bins' : 15,
            'log': False,
            'xlabel': 'StDev of Focus Offset',
            'median': False}
            }
     
    print 'Starting the program!'
     
    temp = getdata(sql)
    data = N.array(temp)
    
    focustemp = 0.375*(data[:,dict['s239']] + data[:,dict['s240']]) + 0.25*data[:,dict['s244']]
    
    #Checks if verbose was selected
    (opts, args) = process_args()
    verbose = opts.verbose
    
    log = Logger('Focus.output', verbose)
    
    log.write('\nThis program can be used to study ALFOSC Focus data!')
    log.write("\n%i rows were returned" % len(data[:,dict['telfocus']]))
    
    #calculates linear regression for the correction
    significance = S.spearmanr(focustemp, data[:,dict['telfocus']])
    correction = S.linregress(focustemp, data[:,dict['telfocus']])
    
    log.write('\nThe Spearman Rank-order correlation between focus temperature and telfocus:')
    log.write(significance)
    if significance[1] < 10.**-4.:
        print '\nSignificant correlation between focus temperature and telfocus:\n', significance
    
    
    log.write('\nCorrection:')
    log.write(correction)
           
    telfocusOld = data[:,dict['telfocus']]
    
    telfocusCorrected = []
    corrs = []
    criticalT = (N.median(data[:,dict['telfocus']]) - correction[1]) / correction[0]
    #criticalT = 10.
    
    log.write('\nCritical Focus Temperature: %6.3f' % criticalT)
    
    for focus, temperature in zip(data[:,dict['telfocus']], data[:,dict['TempInAirDegC']]):
        corr = correction[0]*(criticalT - temperature)
        foc = focus + corr
        telfocusCorrected.append(foc)
        corrs.append(corr)
    
    telfocStat = basicStatistics(telfocusOld)
    telfocnewStat = basicStatistics(telfocusCorrected)
    corrsStat = basicStatistics(corrs)
    medianOld = telfocStat[0]
    medianNew = telfocnewStat[0]

    focusTempPlot()
    extraHistogram()
    extraPlots()
    oldvsnew()
    focusTempPlot()
    OffsetPlot()
    #Plot1()

    frmt = "%13.2f"*5
    log.write('\n')
    log.write(("%17s" + "%13s"*5) % ("Name", "Median", "Max", "Min", "Mean", "Stdev"))
    log.write('Corrected Focus  ' + frmt % telfocnewStat)
    log.write('Uncorrected Focus' + frmt % telfocStat)
    log.write('Correction       ' + frmt % corrsStat)
 
    log.write('\n**************************************************')
    log.write('All following correlations are for corrected data!')
    #Calculates correlations between corrected focus and all variables!
    for key in dict:
        if key != 'DateTimeUT':
            temp1 = S.spearmanr(telfocusCorrected, data[:,dict[key]])
            temp2 = S.linregress(telfocusCorrected, data[:,dict[key]])
            log.write('\nSpearman Rank correlation between corrected telescope focus and %s:' % key)
            log.write(temp1)
            if temp1[1] < 10.**-5.: log.write('This is highly SIGNIFICANT CORRELATION!')
            log.write('While the Linear Regression is:')
            log.write(temp2)
  
    regressions = []
    #Calculates all correlations for the old data!
    log.write('\n******************************************************')
    log.write('All following correlations are for uncorrected data!')
    for key1 in dict:
        for key2 in dict:
            if dict[key1] < dict[key2] and key1 != 'DateTimeUT' and key2 != 'DateTimeUT':
                temp1 = S.spearmanr(data[:,dict[key1]], data[:,dict[key2]])
                temp2 = S.linregress(data[:,dict[key1]], data[:,dict[key2]])
                log.write('\nSpearman Rank correlation between %s and %s:' % (key1, key2))
                log.write(temp1)
                if temp1[1] < 10.**-5.: log.write('This is highly SIGNIFICANT CORRELATION!')
                log.write('While the Linear Regression is:')
                log.write(temp2)
                regressions.append(['%s,%s' % (key1, key2), (temp1, temp2)])

    #Calculates skewness test for the telescope focus data
    skew = S.skew(data[:,dict['telfocus']])
    skewtest = S.skewtest(data[:,dict['telfocus']])
    log.write('\nTest of the Skewness:')
    log.write(skewtest)
    
    for key in scatters:
        if key != 'telfocus':
            scatterPlot(data[:,scatters[key][0]], telfocusCorrected, telfocusOld, 
                        data[:,dict['stdevOffset']], scatters[key][1], scatters['telfocus'][1], 
                        key, medianOld, medianNew)

    for plot in hists:
        column = hists[plot]['column']
        name = hists[plot]['file']
        bins = hists[plot]['bins']
        xlabel = hists[plot]['xlabel']
        log = hists[plot]['log']
        median = hists[plot]['median']
        
        histogramPlot(data[:,column], xlabel, bins, log, name, median)
        
    print 'Program exits successfully...'