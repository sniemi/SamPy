#!/sw/bin/python

import sys
import os

def striplist(list):
    return([x.strip() for x in list])

temp = os.popen3('ls *.eps')
files = striplist(temp[1].readlines())

for file in files:
    remove = '''rm ~/Documents/workspace/Field\ Ellipticals\ paper/''' + file
    link = '''ln %s ~/Documents/workspace/Field\ Ellipticals\ paper/''' % file
    os.popen(remove)
    os.popen(link)
    print 'link to file %s has been updated...' % file

print 'All .eps files have been updated...'

sys.exit
