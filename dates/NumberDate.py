"""
This simple module can be used to convert a day number to a human readable date.

:note: the file functions also as a standalone script which can be called from the
       command line.

:history: Sep 9 2009; Initial Version 0.1

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu

:version: 0.1
"""
import datetime, sys

__author__ = 'Sami-Matias Niemi'
__version__ = '0.1'

def dayNumber(day, verbose=True):
    """
    This simple function converts a given integer to
    the date of the current year.
    
    :param day: number of the day
    :type day: int

    :param verbose: whether to print or not debug information
    :type verbose: boolean

    :return: date
    :rtype: python datetime
    """
    currentYear = datetime.datetime.today().year
    date = datetime.datetime.strptime(str(currentYear) + day, '%Y%j')

    if verbose:
        print 'Day {0:>s} of year {1:>s} corresponds to {2:>s}.'.format(day, currentYear, date.strftime("%A %d. %B %Y"))

    return date

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print 'Usage:'
        print '\tNumberDate day_number'
        sys.exit(-9)

    if int(sys.argv[1]) > 366 or int(sys.argv[1]) < 1:
        print 'You gave an invalid day number, please use day_number = [1,366]'
        sys.exit(-8)

    dayNumber(sys.argv[1])