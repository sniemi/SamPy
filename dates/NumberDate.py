'''
ABOUT:
         This script converts the day number to a human readable date.

USAGE:   
         NumberDate day_number
         
         E.g NumberDate 250

DEPENDS:
         Python 2.6 (no 3.0 compatible)

EXITSTA:  
          0: No errors
         -8: Invalid day_number
         -9: No day_number given

HISTORY:
         Sep 9 2009: Initial Version 0.1

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu
'''
import datetime, sys

__author__ = 'Sami-Matias Niemi'
__version__ = '0.1'

def print_day_number(day):
    currentYear = datetime.datetime.today().year
    date = datetime.datetime.strptime(str(currentYear) + day, '%Y%j')
    
    print 'Day %s of year %s corresponds to %s.' % (day, currentYear, date.strftime("%A %d. %B %Y"))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage:'
        print '\tNumberDate day_number'
        sys.exit(-9)
    
    if int(sys.argv[1]) > 366 or int(sys.argv[1]) < 1:
        print 'You gave an invalid day number, please use day_number = [1,366]'
        sys.exit(-8)

    day = sys.argv[1]

    print_day_number(day)