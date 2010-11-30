#!/usr/bin/python
import cgi
import cgitb; cgitb.enable()
import sys
import pages

sys.stderr = sys.stdout
response = cgi.FieldStorage()
print "Content-type: text/html\n\n"
        
output = response.getvalue('Output')
year = response.getvalue('Year')
camera = response.getvalue('Camera')
pages.page2(output, year, camera, response)
