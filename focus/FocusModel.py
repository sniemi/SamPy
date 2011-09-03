"""
User Interface for Focus Monitor
"""
import glob
import string, time, datetime
from math import *
from matplotlib import dates
from matplotlib.dates import MinuteLocator, DateFormatter
from Tkinter import *
import tkMessageBox
import numpy as N
import pylab as P


def modelled(camera, date, startTime, stopTime):
    """
    Date in form of a string: month day  year. Times as 15:33 - 24 hour clock
    """
    print 'Modelled', camera, date, startTime, stopTime
    thermal = "/Users/niemi/Desktop/temp/hst/OTA/thermal/"

    # Focus model offsets
    camConst = {'PC': 261.1, 'HRC': 261.0, 'WFC1': 259.7, 'WFC2': 260.35}
    secMove = {'2004.12.22': 4.16, '2006.07.31': 5.34}

    # Define data lists
    julian = []
    temp1 = []
    temp2 = []
    temp3 = []
    temp4 = []
    temp5 = []
    temp6 = []
    hours = []
    focusDate = time.strptime(date, '%m/%d/%Y')
    timeAxis = []
    year = focusDate[0]
    month = focusDate[1]
    day = focusDate[2]

    # Get date-dependent focus adjustment
    focusShift = 0.0
    dateStamp = '%4d.%02d.%02d' % (year, month, day)
    for k in secMove.keys():
        if dateStamp > k:
            focusShift = focusShift + secMove[k]
    print 'Secondary mirror move ', focusShift

    dayOfYear = focusDate[7]
    dayString = "%03d" % dayOfYear
    yearString = str(year)
    start = string.split(startTime, ':')
    stop = string.split(stopTime, ':')
    startHour = int(start[0])
    startMinute = int(start[1])
    stopHour = int(stop[0])
    stopMinute = int(stop[1])
    jday = toJulian(year, month, day)
    jstart = jday + (startHour + startMinute / 60.0) / 24.0 - 40.0 / (60.0 * 24.0)  # 40 minute backtrack
    jstop = jday + (stopHour + stopMinute / 60.0) / 24.0
    fileName = 'thermalData' + yearString + '.dat'
    #if not(os.access(thermal + fileName, os.F_OK)): # then check Chris Long's file
    f = open(thermal + fileName, 'r')
    while f:
        line = f.readline()
        if line == '': break
        columns = string.split(line)
        timeStamp = columns[0]
        jul = float(columns[1])

        if jstart <= jul <= jstop:
            julian.append(jul)
            tup = fromJulian(jul)
            hr = tup[3] + (tup[4] + tup[5] / 60.0) / 60.0 # Extract hours
            hours.append(hr)
            tobj = datetime.datetime(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5])
            timeAxis.append(tobj)
            num = dates.date2num(tobj)
            temp1.append(float(columns[2]))
            temp2.append(float(columns[3]))
            temp3.append(float(columns[4]))
            temp4.append(float(columns[5]))
            temp5.append(float(columns[6]))
            temp6.append(float(columns[7]))
            if day > dayOfYear: break
    f.close()

    if  len(temp1) == 0: # No temperature data in time range - Check Chris Long file
        longFile = glob.glob(thermal + '/breathing2009/BreathingData' + '*') # will produce a list
        if  len(longFile) > 0:
            longFile.sort()
            print 'Using ', longFile[-1] # Use latest version
            f = open(longFile[-1], 'r')
            while f:
                line = f.readline()
                if line == '': break
                columns = string.split(line)
                timeStamp = columns[0]
                jul = float(columns[1])

                if jstart <= jul <= jstop:
                    julian.append(jul)
                    tup = fromJulian(jul)
                    hr = tup[3] + (tup[4] + tup[5] / 60.0) / 60.0 # Extract hours
                    hours.append(hr)
                    tobj = datetime.datetime(tup[0], tup[1], tup[2], tup[3], tup[4], tup[5])
                    timeAxis.append(tobj)
                    num = dates.date2num(tobj)
                    temp1.append(float(columns[2]))
                    temp2.append(float(columns[3]))
                    temp3.append(float(columns[4]))
                    temp4.append(float(columns[5]))
                    temp5.append(float(columns[6]))
                    temp6.append(float(columns[7]))
                    if day > dayOfYear: break
            f.close()
        else:
            print 'Did not find Chris Long file'
            print 'No matching thermal data file'
            gui.statusBar.config(text='No matching thermal data file')
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
    if l < 10:
        print 'No temperature data'
        gui.statusBar.config(text='No temperature data')
        return

    r1 = range(8)
    tBreath[r1] = 0.0
    r2 = range(8, l)
    for r in r2:
        tBreath[r] = 0.7 * (lightShield[r] - sum(lightShield[r - 8:r]) / 8.0)

    focusModel = camConst[camera] + focusShift\
                 - 0.0052 * jtime + 0.48 * aftLS + 0.81 * trussAxial - 0.28 * aftShroud + 0.18 * fwdShell + 0.55 * tBreath
    print 'Average model%10.2f' % (N.mean(focusModel[8:]))
    # Just the Bely term
    Bely = 0.55 * tBreath
    bShift = N.mean(focusModel) - N.mean(Bely)
    Bely = Bely + bShift

    # Time independent Focus model with mean zero offset
    flatModel = camConst[camera] + focusShift\
                + 0.48 * aftLS + 0.81 * trussAxial - 0.28 * aftShroud + 0.18 * fwdShell + 0.55 * tBreath - 281.64
    print 'Flat model%10.2f' % (N.mean(flatModel[8:]))



    # Make up an output file

    op = open('plotdata' + dateStamp + '.txt', 'w')
    op.write('Julian Date     Date       Time    Model  Flat Model\n')
    for r in range(8, l):
        dataString1 = '%12.6f' % jtime[r]
        dataString2 = timeAxis[r].strftime(' %b %d %Y %H:%M:%S')
        dataString3 = '%8.4f %8.4f \n' %\
                      (focusModel[r], flatModel[r])
        op.write(dataString1 + dataString2 + dataString3)
        t = timeAxis[r]
        #print t.strftime('%b %d %Y %H:%M:%S')
    op.close()

    # Set up for plots        
    P.figure(1)
    P.clf()
    P.subplot(211)
    P.ylabel('Degrees C')
    P.title('Temperatures ' + date)
    P.plot(dates.date2num(timeAxis), temp3)
    P.plot(dates.date2num(timeAxis), temp4)
    P.plot(dates.date2num(timeAxis), temp5)
    ax = P.gca()
    ax.xaxis.set_major_locator(MinuteLocator((0, 20, 40)))
    ax.xaxis.set_major_formatter((DateFormatter('%H:%M')))
    P.legend(('Truss Dia', 'Aft Shr', 'Fwd Sh'), loc='upper left')
    P.grid(True)
    P.subplot(212)
    P.plot(dates.date2num(timeAxis), temp1)
    P.plot(dates.date2num(timeAxis), temp6)
    P.legend(('Aft LS', 'Light Sh'))
    P.xlabel('Time')
    P.ylabel('Degrees C')
    ax2 = P.gca()
    ax2.xaxis.set_major_locator(MinuteLocator((0, 20, 40)))
    ax2.xaxis.set_major_formatter((DateFormatter('%H:%M')))
    P.grid(True)

    P.figure(2)
    #P.clf()
    P.plot(hours[8:], focusModel[8:], '-ro')
    #P.plot(hours[8:], Bely[8:], '-g+')
    P.title('Model ' + date)
    P.xlabel('Time')
    P.ylabel('microns')
    #print gui.display
    if gui.display == 'Comparison': P.legend(('Measured', 'Model'), loc='upper right')
    P.grid(True)
    P.draw()
    return


def measured(camera, testDate):
    """
    Extract focus measurements
    """
    print 'MEASURED'
    fDate = []
    fJulian = []
    fActual = []
    dateList = []

    measure = open(camera + 'FocusHistory.txt', 'r')
    focusData = measure.readlines()
    measure.close()
    for k in range(10): print focusData[k] #Temporary test
    count = len(focusData)
    print count, 'lines in History file'
    for l in range(2, count):
        pieces = string.split(focusData[l])
        if len(pieces) > 0:
            dataSet = pieces[0]
            if dataSet != '0':
                fDate.append(pieces[2])
                fJulian.append(pieces[3])
                fActual.append(pieces[4])
    entries = len(fDate)
    print entries, ' entries'

    plotJulian = []
    plotTime = []
    plotFocus = []
    for e in range(entries):
        if fDate[e] == testDate:
            t = float(fJulian[e])
            h = 24.0 * (t - floor(t))
            plotJulian.append(t)
            plotTime.append(h)
            plotFocus.append(float(fActual[e]))
    meanF = sum(plotFocus) / len(plotFocus)
    print 'Average measurement%10.2f' % (meanF)
    # Reformat date
    pDate = time.strptime(testDate, '%m/%d/%y')
    dateText = time.asctime(pDate)
    datePieces = string.split(dateText)
    plotDate = datePieces[1] + ' ' + datePieces[2] + ' ' + datePieces[4]

    P.figure(2)
    P.clf()
    P.plot(plotTime, plotFocus, '-bo')
    P.grid(True)
    P.title(camera + ' Focus measurement ' + plotDate)
    P.xlabel('Time')
    P.ylabel('Microns')
    P.draw()
    return (plotJulian[0], plotJulian[-1])


def toJulian(year, month, day):
    """
    Use time functions
    """
    dateString = str(year) + ' ' + str(month) + ' ' + str(day) + ' UTC'
    tup = time.strptime(dateString, '%Y %m %d %Z')
    sec = time.mktime(tup)
    days = (sec - time.timezone) / 86400.0  # Cancel time zone correction
    jday = days + 40587 # Julian date of Jan 1 1900
    return jday


def fromJulian(j):
    days = j - 40587 # From Jan 1 1900
    sec = days * 86400.0
    tup = time.gmtime(sec)
    return tup


def comparison(camera, date):
    monthName = ['blank', 'January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
    times = measured(camera, date) # times now contains start and end Julian times
    t0 = times[0]
    tp0 = fromJulian(t0)
    h0 = 24.0 * (t0 - int(t0))
    ih0 = int(h0)
    m0 = int(60 * (h0 - int(h0)))
    t1 = times[1]
    tp1 = fromJulian(t1)
    h1 = 24.0 * (t1 - int(t1))
    ih1 = int(h1)
    m1 = int(60 * (h1 - int(h1)))
    dateString = '%2d/%2d/%4d' % (tp1[1], tp1[2], tp1[0])
    dateString = string.lstrip(dateString) # clean up leading blanks
    startTime = '%02d:%02d' % (h0, m0)
    stopTime = '%02d:%02d' % (h1, m1)
    modelled(camera, dateString, startTime, stopTime)


class FocusMenu(object):
    def __init__(self):
        self.root = None


    def CreateForm(self):
        self.root = Tk()
        self.root.title('HST Focus Monitor')
        self.disp = StringVar()
        self.disp.set('Modelled')
        self.cam = StringVar()
        self.cam.set('PC')
        self.year = IntVar()

        Label(self.root, text='Display').grid(row=1, column=2)
        Label(self.root, text='Camera').grid(row=1, column=0, sticky=W)

        # Camera choice
        self.rc1 = Radiobutton(self.root, text='PC', variable=self.cam, value='PC')
        self.rc1.grid(row=3, column=0, sticky=W)
        self.rc2 = Radiobutton(self.root, text='HRC', variable=self.cam, value='HRC')
        self.rc2.grid(row=4, column=0, sticky=W)

        #Display choice
        self.rd1 = Radiobutton(self.root, text='Modelled', variable=self.disp, value='Modelled')
        self.rd1.grid(row=3, column=2, sticky=W)
        self.rd2 = Radiobutton(self.root, text='Measured', variable=self.disp, value='Measured')
        self.rd2.grid(row=4, column=2, sticky=W)
        self.rd3 = Radiobutton(self.root, text='Comparison', variable=self.disp, value='Comparison')
        self.rd3.grid(row=5, column=2, sticky=W)

        # Year of model or measurement
        Label(self.root, text='Year to display').grid(row=6, column=0, sticky=W)
        self.yearEntry = Entry(self.root)
        self.yearEntry.grid(row=6, column=1)

        self.b1 = Button(self.root, text='Proceed', command=self.GetDate)
        self.b1.grid(row=13, column=1)

        self.b2 = Button(self.root, text='Exit', command=self.Finish)
        self.b2.grid(row=13, column=2)

        self.statusBar = Label(self.root, text='', foreground='blue')
        self.statusBar.grid(row=11, sticky=S)

    def Show(self):
        self.root.mainloop()


    def GetDate(self):
    # Validate year and date input
        firstYear = 2003
        lastYear = time.gmtime()[0] # Get current year
        self.display = self.disp.get()
        self.camera = self.cam.get()
        self.year = self.yearEntry.get()
        goodyear = False
        try:
            iy = int(self.year)
            if iy < firstYear or iy > lastYear:
                self.statusBar.config(text='Year must be between 2003 and current year')
            else:
                goodyear = True
        except ValueError:
            self.statusBar.config(text='Bad format for Year')
            msg.grid(row=7, column=0)

        if goodyear: # Show selection for exact date
            if self.display == 'Measured' or self.display == 'Comparison':
                #print 'Display', self.display
                focusFile = self.camera + 'FocusHistory.txt'
                print 'Focus File', focusFile # Temporary
                measure = open(focusFile, 'r')
                focusData = measure.readlines()
                lf = len(focusData)
                measure.close()

                self.dateList = [] # Prepare to collect measurement dates from one year
                for l in range(1, lf): #Skip first  line
                    pieces = string.split(focusData[l])
                    if len(pieces) > 1 and pieces[0] != "0": # Skip blank and meaningless lines
                        [m, d, y] = string.split(pieces[2], '/')
                        if int(y) == iy % 100: # Match last two digits of year
                            dateStamp = pieces[2] # If this is different from previous date, add to list
                            if len(self.dateList) == 0 or self.dateList[-1] != dateStamp: self.dateList.append(
                                dateStamp)

                # Now make up listbox with dateList             
                ly = len(self.dateList)
                if ly == 0:
                    nodata = 'No data for ' + self.camera + ' in ' + self.year
                    self.statusBar.config(text=nodata)
                    goodyear = False
                    return

                Label(self.root, text='Choose date of measurement').grid(row=7, column=0, sticky=NW)
                self.measureDates = Listbox(self.root, height=ly, selectmode=SINGLE)
                self.measureDates.grid(row=7, column=1)
                self.dateChoice = None # until chosen
                for i in range(ly): self.measureDates.insert(END, self.dateList[i])
                self.measureDates.bind("<Button1-ButtonRelease>", self.ChooseDate)
                self.b1.grid_forget()  # Remove PROCEED button
                self.rc1.config(state=DISABLED) # Turn off camera and display choices
                self.rc2.config(state=DISABLED)
                self.rd1.config(state=DISABLED)
                self.rd2.config(state=DISABLED)
                self.rd3.config(state=DISABLED)
                self.yearEntry.config(state=DISABLED)
                self.statusBar.config(text='')

                Button(self.root, text='Display', command=self.StartGraph).grid(row=8, column=1)

            elif self.display == 'Modelled': # Select arbitrary dates and times
                #print 'Display',self.display
                self.b1.grid_forget()  # Remove PROCEED button
                self.rc1.config(state=DISABLED) # Turn off camera and display choices
                self.rc2.config(state=DISABLED)
                self.rd1.config(state=DISABLED)
                self.rd2.config(state=DISABLED)
                self.rd3.config(state=DISABLED)
                self.yearEntry.config(state=DISABLED)
                self.statusBar.config(text='')

                Label(self.root, text='Date e.g. 11/23').grid(row=8, column=0, sticky=W)
                self.dayEntry = Entry(self.root)
                self.dayEntry.grid(row=8, column=1)
                Label(self.root, text='Start time in form 12:23').grid(row=9, column=0, sticky=W)
                self.time1Entry = Entry(self.root)
                self.time1Entry.grid(row=9, column=1)
                self.time2Entry = Entry(self.root)
                self.time2Entry.grid(row=10, column=1)
                Label(self.root, text='Use 24 hour clock').grid(row=9, column=2)
                Label(self.root, text='Stop time').grid(row=10, column=0, sticky=W)
                Button(self.root, text='Display', command=self.GetTimes).grid(row=11, column=1)

    def GetTimes(self):
        self.day = self.dayEntry.get()
        try:
            (m, d) = string.split(self.day, '/')
            if (1 <= int(m) <= 12) and (1 <= int(d) <= 31):
                goodday = True
            else:
                self.statusBar.config(text='Numerical error in date')
                goodday = False
        except ValueError:
            self.statusBar.config(text='Date to be in form mm/dd')
            goodday = False

        self.time1 = self.time1Entry.get()
        try:
            (hour1, minute1) = string.split(self.time1, ':')
            if (0 <= int(hour1) <= 23) and (0 <= int(minute1) <= 59):
                goodstart = True
            else:
                self.statusBar.config(text='Numerical error in start time')
                goodstart = False
        except ValueError:
            self.statusBar.config(text='Start time to be in form hh:mm')
            goodstart = False

        if goodstart: print 'h1m1', hour1, minute1

        self.time2 = self.time2Entry.get()
        try:
            (hour2, minute2) = string.split(self.time2, ':')
            if (0 <= int(hour2) <= 23) and (0 <= int(minute2) <= 59):
                goodstop = True
            else:
                self.statusBar.config(text='Numerical error in stop time')
                goodstop = True
        except ValueError:
            self.statusBar.config(text='Stop time to be in form hh:mm')
            goodstop = False

        if goodstop: print 'h2m2', hour2, minute2

        # Final check
        if goodstart and goodstop:
            t1 = int(hour1) + int(minute1) / 60.0
            t2 = int(hour2) + int(minute2) / 60.0
            if t1 > t2:
                goodstop = False
                self.statusBar.config(text='Start time is later than stop time').grid(row=11, column=0)
            else:
                goodstop = True

        if goodday and goodstart and goodstop:
            self.statusBar.config(text='Generating graphs')
            graph() # Start display

        return

    def ChooseDate(self, event):
        item = self.measureDates.curselection()
        self.dateChoice = self.dateList[int(item[0])]

    def StartGraph(self):
        if self.dateChoice: # Proceed only if date choice has been made
            self.statusBar.config(text='Generating graphs')
            graph()
            #self.statusBar.config(text = 'Finished')
        else: self.statusBar.config(text='Choose a date')

    def Finish(self):
        self.root.destroy()
        P.close('all')


def graph():
    monthName = ['blank', 'January', 'February', 'March', 'April', 'May', 'June',
                 'July', 'August', 'September', 'October', 'November', 'December']
    print 'Create display'
    print 'Camera', gui.camera
    print 'Display ', gui.display
    if gui.display == 'Modelled':
        #print gui.day, gui.year, gui.time1, gui.time2        
        fulldate = "%5s/%4s" % (gui.day, gui.year)
        fulldate = string.lstrip(fulldate)
        modelled(gui.camera, fulldate, gui.time1, gui.time2)

    elif gui.display == 'Measured':
        #print 'Date ', gui.dateChoice
        times = measured(gui.camera, gui.dateChoice)

    elif gui.display == "Comparison":
        #print gui.camera, gui.dateChoice
        comparison(gui.camera, gui.dateChoice)

    print 'Finished'
    #gui.statusBar.config(text = 'Finished')
    return

if __name__ == '__main__':
    gui = FocusMenu()   # Creates an instance of FocusMenu
    gui.CreateForm()    # Builds the form
    gui.Show()          # Starts the loop

        
