#! /usr/bin/env python
#This is just a test program
#It calculates an age at days from input and prints it
#SMN

from datetime import date
import sys

try:
  if (sys.argv[1] == "-h"):
    print """
    First Python program of SMN
    Usage: year month date 
     -h                        Display this usage message
     -v                        Verbose
    """
    sys.exit()
  if (sys.argv[1] == "-v"):
    verbose = 1
    length = len(sys.argv) - 1
    print "\n Verbose on \n"
  else: 
    verbose = 0
    length = len(sys.argv)

  #Saves variables...  
  year = int(sys.argv[1+verbose])
  month = int(sys.argv[2+verbose])
  day = int(sys.argv[3+verbose])
  
  if (length == 4):
    now = date.today() 
    birthday = date(year, month, day)
    age = now - birthday
    print "\n Your age at days: ", age.days
  else:
    print "wrong number of parameters..."
    sys.exit()

except IndexError:
  print """need some values or too many values...
  try running with -h to see help \n"""

except ValueError:
  print "nonsense value or option"
