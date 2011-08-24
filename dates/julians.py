"""
A simple module to convert dates to (Modified) Julian Dates.

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import time

__author__ = 'Sami-Matias Niemi'
__version__ = '0.1'

def toJulian(year, month, day, hour, minute, timezone='UTC'):
    """
    This function converts a given date to Modified Julian Date.

    :note: The function uses Python's inbuilt time module.

    :param: year: year
    :param: month: month
    :param: day: days
    :param: hour: hours
    :param: minute: minutes
    :param: timezone: Timezone, default is UTC

    :return: Modified Julian Date
    :rtype: float
    """
    dateString = str(year) + ' ' + str(month) + ' ' + str(day) +\
                 ' ' + str(hour) + ' ' + str(minute) + ' ' + timezone
    tup = time.strptime(dateString, '%Y %m %d %H %M %Z')
    sec = time.mktime(tup)
    days = (sec - time.timezone) / 86400.0
    jday = days + 40587 # Julian date of Jan 1 1900
    return jday


def toJulian2(date):
    """
    Converts date and time to Modified Julian Date.
    Uses time functions. Note that date has to be in Python time format.

    :return: Modified Julian Date
    :rtype: float
    """
    sec = time.mktime(date)
    days = (sec - time.timezone) / 86400.0
    jday = days + 40587 # Julian date of Jan 1 1900
    return jday


def fromJulian(j):
    """
    Converts Modified Julian days to human readable format

    :return: human readable date and time
    """
    days = j - 40587 # From Jan 1 1900
    sec = days * 86400.0
    return time.gmtime(sec)


def fromHSTDeployment(julian):
    """
    Returns the number of days that has passed since the
    deployment of the Hubble Space Telescope.

    :return: number of days since HST was deployed (24 Apr 1990)
    """
    julian0 = 48005.0
    return julian - julian0


def HSTdayToRealDate(hstday):
    return fromJulian(hstday + 48005.0)
