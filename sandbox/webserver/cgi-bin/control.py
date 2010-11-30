#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()
import sys
import time
import pages
sys.stderr = sys.stdout
response = cgi.FieldStorage()
print "Content-type: text/html\n\n"
output = 'Model'
camera = 'UVIS1'
year = time.ctime()[-4:] # Default to current year
pages.page1(output, camera, year, response) 
if 'Year' in response.keys():
    year = response.getvalue('Year')
    try:
        iy = int(year)
        firstYear = 2003
        currentYear = time.gmtime()[0] # Get current year   
        if iy < firstYear or iy > currentYear:
            print "not in covered range"
        else:
            output = response.getvalue('Output')
            camera = response.getvalue('Camera')
            pages.page2(output, year, camera, response)  
    except ValueError:
        print "<p>Improper year format</p>"

