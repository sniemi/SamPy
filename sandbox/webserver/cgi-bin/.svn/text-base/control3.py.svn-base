#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()
import os, sys
import string, time, datetime
import pages
sys.stderr = sys.stdout
response = cgi.FieldStorage()

print "Content-type: text/html\n\n"

date = response.getvalue('Date')
output = response.getvalue('Output')
camera = response.getvalue('Camera')
year = response.getvalue('Year')
   
try: #Check date format
    if output == 'Model': (m,d) = date.split('/')
    else: (m,d,y) = date.split('/')
    if (1 <= int(m) <= 12) and (1<= int(d) <= 31):
        dateOK = True
    else:
        print "Numerical date error"
        dateOK = False    
except ValueError:
    dateOK = False
    print "Date format error <br>"
               
if dateOK and output == 'Model':
    start = response.getvalue('Start')
    stop = response.getvalue('Stop')

# Check times
    hm = start.split(':')
    if len(hm) == 2:
        (h1,m1) = hm
        if (0 <= int(h1) < 24) and (0 <= int(m1) < 60) :
            startOK = True
        else:
            print "Numerical Error in Start time<br>"
            startOK = False
    else: 
        print "Start time format error <br>"
        startOK = False           

    hm = stop.split(':')
    if len(hm) == 2:
        (h2,m2) = hm
        if (0 <= int(h2) < 24) and (0 <= int(m2) < 60) :
            stopOK = True
        else: 
            print "Numerical Error in Stop time<br>"
            stopOK = False 
    else: 
        print "Stop time format error <br>"
        stopOK = False                            

    if startOK and stopOK:
        minute1 = 60*int(h1) + int(m1)
        minute2 = 60*int(h2) + int(m2)
        if minute1 > minute2:
            print "Stop time must be later than Start time <br>"
            stopOK = False 
                    
if dateOK:
    if output == 'Measure' or output == 'Compare' or ( startOK and stopOK) :
        if output == 'Measure'or output == 'Compare': pages.MeasurePlot(camera, year, date, output)
        if output == 'Model' : pages.ModelPlot(camera, year, date, output, start, stop)
    else: 
        pages.page2(output,year,camera,response) # Go back to page 2
else: 
    print "Not Ready <br>"
    pages.page2(output,year,camera,response) # Go back to page 2

