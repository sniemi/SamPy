'''HTML Pages'''

import os, sys, glob
import time, datetime
import matplotlib
from matplotlib import dates as MD
from matplotlib import ticker as MT
matplotlib.use('Agg')
import numpy as N
import pylab as P
from math import *

def page1(output, camera, year, response):
    # Introduction
    print "<html>"
    print "<head><center><b>HST Focus Model</b></center></head>"
    print "<body style='background-color:Moccasin;''>"
    print "<p> Calculations of the HST focus model and measurements of the HST focus are presented."
    print " Model results can be obtained for any time range at 5 minute intervals beginning on March 9th 2003. </p> "
    print "<p> Measured values are available for about one hour each month."
    print "Each camera has its own operational time period listed below during which focus measurements were made" 
    print" A comparison between measurements and the model may be chosen for the measurement time periods. </p>"

    # Radio buttons for display type
    print "<br><b> Display </b><br>"
    print "<form method='POST' action = 'control2.py'>"
    if output == 'Model': print "<input type='radio' name='Output' value='Model' checked/> Model <br>"
    else: print "<input type='radio' name='Output' value='Model'/> Model <br>"
    if output == 'Measure': print "<input type='radio' name='Output' value='Measure' checked /> Measurement <br>"
    else: print "<input type='radio' name='Output' value='Measure' /> Measurement <br>"
    if output == 'Compare': print "<input type='radio' name='Output' value='Compare' checked /> Comparison <br>"
    else: print "<input type='radio' name='Output' value='Compare' /> Comparison <br>"
    
    # Radio buttons for camera
    print "<br><b> Camera </b><br>"
    if camera ==  'HRC':print "<input type='radio' name='Camera' value='HRC' /> ACS / HRC January 22nd 2003 to January 21st 2007 <br>"
    else: print "<input type='radio' name='Camera' value='HRC' /> ACS / HRC January 22nd 2003 to January 21st 2007 <br>"
    if camera == 'PC': print "<input type='radio' name='Camera' value='PC' checked/> WFC2 / PC January 22nd 2003 to May 7th 2009 <br>"
    else: print "<input type='radio' name='Camera' value='PC' checked/> WFC2 / PC January 22nd 2003 to May 7th 2009 <br>"
    if camera == 'WFC1': print "<input type='radio' name='Camera' value='WFC1' checked /> ACS / WFC1 August 2009 to present <br>"
    else: print "<input type='radio' name='Camera' value='WFC1' /> ACS / WFC1 August 2009 to present <br>"
    if camera == 'WFC2': print "<input type='radio' name='Camera' value='WFC2' checked /> ACS / WFC2 <br>"
    else: print "<input type='radio' name='Camera' value='WFC2' /> ACS / WFC2  <br>"
    if camera == 'UVIS1': print "<input type='radio' name='Camera' value='UVIS1' checked /> WFC3 / UVIS1 August 2009 to present  <br>"
    else: print "<input type='radio' name='Camera' value='UVIS1' /> WFC3 / UVIS1 August 2009 to present  <br>"
    if camera == 'UVIS2': print "<input type='radio' name='Camera' value='UVIS2' checked /> WFC3 / UVIS2 <br>"
    else: print "<input type='radio' name='Camera' value='UVIS2' /> WFC3 / UVIS2 <br>"
    # Select year
    #year = time.ctime()[-4:] # Default to current year
    print "<br>"
    print "Year: <input type='text' name='Year' size = '4' value = '%s'/> Years 2003 to present <br>" %year

    # Submit reponses and move to next page
    print "<br>"
    print "<input type='submit' value='Select Time Period' />"
    print "<br>"

    print "</form>"
    print "</body>"

def page2(output, year, camera, response):
    print "<html>"
    print "<head> <center> <b>Modelling Time Period</b> </center></head> "
    print "<body style='background-color:Moccasin;''>"
    print "<p> %s %s in %s </p>" %(output, camera, year)
    print "<form action = 'control3.py' method='POST'>"    
    # Transmit information from first web page
    print "<input type='hidden' name='Output' value= '%s' >" %output
    print "<input type='hidden' name='Year' value= '%s' >" %year
    print "<input type='hidden' name='Camera' value= '%s' >"%camera

    if output == 'Model': #Arbitrary time period
        print "<br/>"
        print "Date: <input type='text' name='Date' size = '5'/> in form mm/dd <br>"
        print "Start Time: <input type='text' name='Start' size = '5'/> Use 24-hour clock times <br>"
        print " Stop Time: <input type='text' name='Stop' size = '5'/> in format hh:mm <br>"

    else: # Select from times when focus measurements were taken
        yy = int(year[-2:]) # Last two digits
        direct = '/grp/hst/OTA/focus/source/FocusModel/'
        if not os.path.exists(direct): direct = '/Users/cox/Documents/OTA/focus/' # Use local
        measure = open(direct + camera + 'FocusHistory.txt','r')
        focusData = measure.readlines()
        measure.close()
        dates = []
        for line in focusData[1:]: # Skip first title line
            bits = line.split()
            dateString = bits[2]
            (m,d,y) = dateString.split('/')            
            if int(y) == yy:
                if len(dates) == 0 or dateString != dates[-1]: dates.append(dateString)
        if len(dates) > 0:
            print "<p><b>Select from list of available dates </b></p>" 
            print "<select name = 'Date'>"
            for d in dates:
                print "<option value = '%s' > '%s' </option>" %(d,d)
            print "</select>"
            print "<br/>"
        else: print "<p><b>No measurements for ", camera, " in ", year, "</b></p>"
        
    print "<br/>"
    print "<input type='submit' value='Make Focus Plot' />"

    print "</form>"
    print "</body>"

def MeasurePlot(camera, year, date, output):
    direct = '/grp/hst/OTA/focus/source/FocusModel/'
    if not os.path.exists(direct): 
        print "Central Storage path not available"
        direct = '/Users/cox/Documents/OTA/focus/' # Use local
        
    measure = open(direct + camera + 'FocusHistory.txt','r')
    focusData = measure.readlines()
    measure.close()

    # Prepare to collect requested focus measurements    
    tod = []
    focus = []
    timeAxis2 = []
    for line in focusData: #Skip first title line
        part = line.split()
        if part[2] == date:
            jdate = float(part[3])
            tod.append(24.0*(jdate - floor(jdate)))
            timeAxis2.append(jdate - 40587.0)
            focus.append(float(part[4]))
    
    #for ltemp in range(len(tod)) : print ltemp+1, tod[ltemp], focus[ltemp], "<br>"
    
    P.plot(timeAxis2,focus,'ro-')
    P.xlabel('Time of day')
    P.ylabel('Focus position in microns')
    ax = P.gca()
    period = 24.0*(timeAxis2[-1]-timeAxis2[0])
    stepSize = int(period/6)+1
    hrs = MD.HourLocator(interval=stepSize)
    ax.xaxis.set_major_locator(hrs)
    hrFormat = MD.DateFormatter('%H:00')
    ax.xaxis.set_major_formatter(hrFormat)
    mins = MD.MinuteLocator(range(0,60,10))
    ax.xaxis.set_minor_locator(mins)
    if period < 1.0: # if period less than 1 hour label each 10 minutes
        if period < 0.25: mins = MD.MinuteLocator(range(0,60,5)) # If less than 15 min,label every 5 min
        if period < 0.09: mins = MD.MinuteLocator(range(60)) # Less than 5 min label every minute
        ax.xaxis.set_minor_locator(mins)
        minFormat = MD.DateFormatter('%H:%M')
        ax.xaxis.set_minor_formatter(minFormat)
    else: ax.xaxis.set_minor_formatter(MT.NullFormatter())
    P.title('Measured Focus for ' + camera + ' ' + date)
    P.grid(True)
    
    if output == 'Compare' :
        # Express times for input to Model plot
        t1 = tod[0]
        t2 = tod[-1]
        h1 = int(t1)
        m1 = int(60*(t1-h1))
        h2 = int(t2)
        m2 = int(60*(t2-h2))
        start = '%02d:%02d' %(h1,m1)
        stop = '%02d:%02d' %(h2,m2)
        if t2-t1 < 0.17: print "Time range too short to model <br>" #if less than 10 minutes
        else:
            # Strip year from date
            (m,d,y) = date.split('/')
            date = m + '/' + d
            ModelPlot(camera,year,date,output,start,stop)
            P.title('Comparison of Measurement and Model for ' + camera + ' ' + date + '/' + year)
            P.legend(('Measured', 'Model'), loc = 'best', shadow = True)
    P.savefig('focusplot.png')
    print "<p><img src='../focusplot.png'/></p>"

def ModelPlot(camera, year, date, output, startTime, stopTime):
    if os.path.exists('/Volumes/grp'): thermal = "/Volumes/grp/hst/OTA/thermal/" # Mac access
    elif os.path.exists('/grp'): thermal = "/grp/hst/OTA/thermal/"               # Sun access
    else : thermal = "./breathing/"   # Temporary for use when Central Storage is not accessible 
    
    # Focus model offsets
    camConst = {'PC': 261.1, 'HRC': 261.0, 'WFC1': 259.7, 'WFC2': 260.35, 'UVIS1': 259.39, 'UVIS2': 259.39}
    secMove = {'2004.12.22':4.16, '2006.07.31':5.34, '2009.07.20':2.97}

    # Define data lists
    julian = []
    temp1 = []
    temp2 = []
    temp3 = []
    temp4 = []
    temp5 = []
    temp6 = []
    hours = []
    focusDate = time.strptime(date, '%m/%d')
    timeAxis = []
    timeAxis2 =[]
    year = int(year)
    month = focusDate[1]
    day = focusDate[2]

    # Get date-dependent focus adjustment
    focusShift = 0.0
    dateStamp = '%4d.%02d.%02d' %(year,month,day)
    for k in secMove.keys():
        if dateStamp > k:
            focusShift = focusShift + secMove[k]
    #print 'Secondary mirror move ', focusShift, " microns <br>"

    dayOfYear = focusDate[7]
    dayString = "%03d" % dayOfYear
    yearString = str(year)
    start = startTime.split(':')
    stop = stopTime.split(':')
    startHour = int(start[0])
    startMinute = int(start[1])
    stopHour = int(stop[0])
    stopMinute = int(stop[1])
    jday = toJulian(year,month,day)
    jstart = jday +(startHour+startMinute/60.0)/24.0 - 40.0/(60.0*24.0)  # 40 minute backtrack
    jstop = jday + (stopHour + stopMinute/60.0)/24.0
    fileName =  'thermalData' + yearString + '.dat' 
    if not(os.access(thermal + fileName, os.F_OK)): print filename, " File not found <br>"
    f=open(thermal + fileName, 'r')    
    while f: 
        line = f.readline()
        if line == '' : break
        columns = line.split()
        timeStamp = columns[0]
        jul = float(columns[1])

        if jstart <= jul <= jstop :
            julian.append(jul)
            tup = fromJulian(jul)
            hr = tup[3]+ (tup[4]+tup[5]/60.0)/60.0 # Extract hours
            hours.append(hr)
            tobj = datetime.datetime(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5])
            timeAxis.append(tobj)
            timeAxis2.append(jul-40587.0) # Days since 1900-01-01
            temp1.append(float(columns[2]))
            temp2.append(float(columns[3])) 
            temp3.append(float(columns[4]))
            temp4.append(float(columns[5]))
            temp5.append(float(columns[6]))
            temp6.append(float(columns[7]))
            if day > dayOfYear : break
    f.close()
    if  len(temp1) == 0: # No temperature data in time range
            print 'No matching thermal data <br>'
            return
            
    jtime = N.array(julian)
    aftLS = N.array(temp1)
    trussAxial = N.array(temp2)
    trussDiam = N.array(temp3)
    aftShroud = N.array(temp4)
    fwdShell = N.array(temp5)
    lightShield = N.array(temp6)
    #tBreath is value of light shield temp  minus average of previous eight values
    tBreath = lightShield.copy() # Make a real copy
    l = N.size(tBreath)
    if l < 1:
        print 'No temperature data <br>'
        return

    r1 = range(8)
    tBreath[r1] = 0.0 # Set first 8 points to zero
    r2 = range(8,l)   # Calculate 9th and onward
    for r in r2:
        tBreath[r] = 0.7*(lightShield[r]-sum(lightShield[r-8:r])/8.0)
    focusModel = camConst[camera] + focusShift \
    - 0.0052*jtime + 0.48*aftLS + 0.81*trussAxial - 0.28*aftShroud + 0.18*fwdShell + 0.55*tBreath
    print "Average model %10.2f microns <br>" % (N.mean(focusModel[8:]))
    # Just the Bely term
    Bely = 0.55*tBreath
    bShift = N.mean(focusModel)- N.mean(Bely)
    Bely = Bely +bShift

    # Time independent Focus model with mean zero offset
    flatModel= camConst[camera] + focusShift \
    + 0.48*aftLS + 0.81*trussAxial - 0.28*aftShroud + 0.18*fwdShell + 0.55*tBreath - 281.64
    #print "Flat model %10.2f microns <br>" % (N.mean(flatModel[8:]))
    if l > 9:
        P.plot(timeAxis2[8:],focusModel[8:], '-bo')
        #P.plot(hours[8:], Bely[8:], '-g+')
        P.title(camera + ' Model ' + date + '/' + yearString)
        P.xlabel('Time of day')
        P.ylabel('Focus position in microns')
        P.grid(True)
        ax = P.gca()
        period = hours[-1]-hours[8]
        stepSize = int(period/6)+1
        hrs = MD.HourLocator(interval=stepSize)
        ax.xaxis.set_major_locator(hrs)
        hrFormat = MD.DateFormatter('%H:00')
        ax.xaxis.set_major_formatter(hrFormat)
        mins = MD.MinuteLocator(range(0,60,10))
        if period < 0.33: mins = MD.MinuteLocator(range(0,60,5)) # if less than 20 minutes mark each 5-minute
        ax.xaxis.set_minor_locator(mins)
        if period < 1.0: # if period less than 1 hour label each 10 minutes
            minFormat = MD.DateFormatter('%H:%M')
            ax.xaxis.set_minor_formatter(minFormat)
            firstMinute = 60*startHour + 10.0*floor(startMinute/10.0) # Round down to earlier 10-minute
            lastMinute = 60*stopHour + 10.0*ceil(stopMinute/10.0)   # Round up to next 10-minute
            firstTime = int(julian[8])-40587 + firstMinute/1440.0
            lastTime = int(julian[-1])-40587 + lastMinute/1440.0
            P.xlim(firstTime,lastTime)
        
        else: 
            ax.xaxis.set_minor_formatter(MT.NullFormatter())
            firstTime = int(julian[8])-40587 + startHour/24.0
            lastTime = int(julian[-1])-40587 + (stopHour+1)/24.0
            P.xlim(firstTime,lastTime)
        
        if output == 'Model' :
            P.savefig('focusplot.png')
            print "<p><img src='../focusplot.png'/></p>"

        # Make up an output file
        outfile = './plotdata' + dateStamp + '.txt'
        op = open(outfile,'w')
        op.write('Julian Date     Date       Time    Model  Flat Model\n')
        for r in range(8,l):
            dataString1 = '%12.6f' %jtime[r]       
            dataString2 = timeAxis[r].strftime(' %b %d %Y %H:%M:%S')
            dataString3 = '%8.4f %8.4f \n'% (focusModel[r], flatModel[r])
            op.write(dataString1 + dataString2 + dataString3)
            t = timeAxis[r]
        op.close()
    
        #print "Plot file may be found at <a href = '../focusplot.png'> Plot </a> <br>"    
        #print "Data file may be found at <a href = '../%s'> Output </a> <br>" %outfile
    
    return

def toJulian(year,month,day) :
    '''Use time functions'''
    dateString = str(year) + ' ' + str(month) + ' ' + str(day) + ' UTC'
    tup = time.strptime(dateString, '%Y %m %d %Z')
    sec = time.mktime(tup)
    days = (sec-time.timezone)/86400.0  # Cancel time zone correction
    jday = days + 40587 # Julian date of Jan 1 1900
    return jday

def fromJulian(j):
    days = j-40587 # From Jan 1 1900
    sec = days*86400.0
    tup = time.gmtime(sec)
    return tup

   