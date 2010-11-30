#
#MODULE time_util
#
#*******************************************************************
"""

   **PURPOSE** --
   A module for dealing with SPSS times and related things.

   **DEFINITIONS** --
   
   - SOGS seconds:  the number of seconds since 1980.001:00:00:00
   - SOGS character time:  a string representation of the time in the form yyyy.ddd:hh:mm:ss.sss
 
   **DEVELOPER** --
   Don Chance

   **MODIFICATION HISTORY** --
   Initial implementation 11/10/99
   Fixed spss_time.get_weekid() DRC 2/15/00
   Update delta_time constructor to enable string input in delta time format. drc 9/18/00
   Added get_honcho function to weekid class  drc 10/18/00
   Added get_sms_time fuction to spss_time class  drc 10/19/00
   changed set_sogs_character_time to except other input formats gww 11/01/00
   Assume years < 80 are in 2000 and 99 >= years >= 80 are in 1900.  drc 4/09/01
   Added a function to set syssec in spss_time.  drc 04/13/01
   Added EPHEM_ADJUST_SECS constant.  drc 5/30/01
   Added window.complement, window_list.complement and changed window.intersection 
   so that it no longer allows a zero second intersection. wmw 07/10/01 
   Slight enhancement to window.complement and window_list.complement to make code more
   efficient. wmw 8/06/01
   Added strptime function to spss_time class.  drc 9/27/01
   Enhanced delta_time to accept times like 2D11H20M45.345S  mdr 1/14/02
   strptime now returns self.  drc 1/15/02
   Use GUI_AVAILABLE instead of try block around tkinter code. gww 1/15/02
   Added orbit_relative_time class.  drc 1/16/02
   Fix bugs delta_time.__add__ and in window.__init__.  drc 2/12/02
   Modify how week_id determines the week id given a ccl object.  drc 7/30/02
   Extend spss_time constructor to accept a list to allow passing of time 
   reference argument. wmw 10/02/02
   Fix orbit relative time regular expressions.  drc 2/25/03
   Modified __add__ in window_list class to behave like addition for lists.
   drc 3/6/03
   Added __abs__ function for delta_time.  drc 6/11/03
   Add set_time function to Time_Entry. drc 7/1/03
   Added get_localtime function to spss_time.  gww 9/11/03
   Added set_begin_time and set_end_time to window class. drc 2/2/04
   Fix bug in window_list.union. drc 6/3/04
   Change window_list to a new-style class. 8/25/04
   Add __eq__ and __ne__ functions to window_list class. drc 3/28/05
   Add __eq__ and __ne__ functions to window class. drc 3/29/05
   Add window.contains function. 4/20/05
   Add earliest_start and latest_end functions to window_list. drc 4/28/05
   Add localtime class.  drc  5/24/06
   Change spss_time constructor to accept mx.DateTime objects as input. drc 6/14/06
   Make having mx.DateTime optional. drc 6/22/06
   add new fuctions to window_list class. drc 8/22/06
   enhance contains function to work with times as well as time windows.  drc 7/17/07
   fix __cmp__ in spss_time.  drc 4/14/08
   Improve parsing of PASS delta times.  drc 6/11/09
   More improvements to delta time parsing. drc 6/15/09
   Change to support addition with localtime. drc 9/14/09
   Fix julian day calculation. drc 9/23/09
   Fix strptime when timezone is not GMT. drc 9/24/09
"""
#*******************************************************************
# Constants
LEAP_YEAR_SECONDS   = 31622400  # the number of seconds in a leap year
NORMAL_YEAR_SECONDS = 31536000  # the number of seconds in a normal year
JD_1_1_1970         = 2440587.5 # Julian day of 1970.001:00:00:00
SECONDS_IN_A_WEEK   = 604800.0  # the number of seconds in a week
SYS_TO_SOGSSEC      = 315532800 # the number of seconds between 1970 and 1980
EPHEM_ADJUST_SECS   = 157852800 # the number of seconds between 1980 and 1985 
LOCAL_TIMEZONE      = "US/Eastern"

__version__ = "9/24/09"


import time, math, string, types, re
import exceptions
from boolean import *
try:
    # versions of python <2.3 do not have datetime built-in
    import datetime
    HAS_DATETIME = True
except ImportError:
    HAS_DATETIME = False

try:
    import mx.DateTime
    HAS_MX = True
except ImportError:
    HAS_MX = False

class delta_time:
    """A class for delta times."""

    def __init__(self,diff=0):
        """The delta_time constructor.
        
        ARGUMENTS:
        
         diff --  may be an integer, float, string or another delta_time.
         Defaults to 0.  If a string, it assumes the time is in delta time
         format (days:hours:minutes:seconds or ddDhhHmmMss.sssS)

        **Raises** -- TypeError - Raised when the input is something
        other than an integer, float, or delta_time
        """
        if (isinstance(diff,types.IntType) 
            or isinstance(diff,types.FloatType)):
            self.delta = diff
        elif isinstance(diff, types.StringType):
            if re.findall(r'\d+[:]', diff):
                ldiff = string.split(string.strip(diff), ':')
                if (ldiff[-1] == ''):
                    del ldiff[-1]
                if ldiff[0][0] == '-':
                    sign = -1
                    # remove the sign since we don't need it embedded here
                    ldiff[0] = ldiff[0][1:]
                else:
                    sign = 1

                # if the length of the list is less than 4 then we need to
                # default the early units in the string (ie, right justify
                # what was passed in)
                while ((len(ldiff) < 4) and (len(ldiff) >= 1)):
                    ldiff.insert(0, '0')

                self.set_list([sign, abs(float(ldiff[0]))] + map(float, ldiff[1:]))
            else:
                try:
                    # First, just try converting it to a number.  If that works,
                    # then we'll assume thats just the delta time in seconds.
                    self.delta = float(diff)
                except:
                    # Parse a PASS ASCII delta time type string
                    if string.strip(diff)[0] == '-':
                        sign = -1
                    else:
                        sign = 1
                    self.delta = 0
                    fseconds = re.findall(r'\d+\.\d*[Ss]', diff)
                    seconds = re.findall(r'\d+[Ss]', diff)
                    if fseconds:
                        self.delta += float(fseconds[0][:-1])
                    elif seconds:
                        self.delta += int(seconds[0][:-1])
                    minutes = re.findall(r'\d+[Mm]', diff)
                    if minutes:
                        self.delta += int(minutes[0][:-1])*60
                    hours = re.findall(r'\d+[Hh]', diff)
                    if hours:
                        self.delta += int(hours[0][:-1])*3600
                    days = re.findall(r'\d+[Dd]', diff)
                    if days:
                        self.delta += int(days[0][:-1])*86400
                    self.delta = sign * self.delta
                
        elif isinstance(diff,delta_time):
            self.delta = diff.delta
        else:
            DeltaTimeError = """delta_time constructor requires an
            integer, float, or another delta_time"""
            raise TypeError(DeltaTimeError)

		
    def __float__(self):
        """The delta_time is returned as a float.
        """
        return float(self.delta)

		
    def __int__(self):
        """The delta_time is returned as an int.
        """
        return int(self.delta)


    def __repr__(self):
        """The string representation of a delta_time.

        **Returns** -- The delta_time will be
        expressed as a string in the form
        days:hours:minutes:seconds.
        """
        l = self.get_list()
        d = "%i:%02i:%02i:%06.3f" % (l[1],l[2],l[3],l[4])
        if l[0] == -1:
            d = "-" + d
        return d

    def __cmp__(self, other):
        """Operator overloading for cmp.

        Allows the comparision operators (==, !=, >, >=, <, <=)
        to work in an appropriate manner for delta_times.

        **Raises** -- TypeError - Raised when a comparing with
        something other than an int, float, long, or
        another delta_time.
        """
        if (isinstance(other,types.IntType) 
            or isinstance(other,types.FloatType)
            or isinstance(other,types.LongType)):
            return cmp(self.delta, other)
        elif isinstance(other,delta_time):
            return cmp(self.delta, other.delta)
        else:
            DeltaTimeError = """delta_times may only be compared
            with floats, ints, longs, and other delta_times"""
            raise TypeError(DeltaTimeError)

    def __sub__(self, other):
        """Operator overloading for subtraction.

        **Returns** -- If an int, float or a delta_time is
        subracted from a delta_time, another
        delta_time is returned.

        **Raises** -- TypeError - Raised when something
        other than an int, float, or another
        delta_time is subtracted from a delta_time.
        """
        if (isinstance(other,types.IntType) 
            or isinstance(other,types.FloatType)):
            return delta_time(self.delta - other)
        elif isinstance(other, delta_time):
            return delta_time(self.delta - other.delta)
        else:
            DeltaTimeError = """Only ints, floats, and other
            delta_times may be subtracted from a delta_time."""
            raise TypeError(DeltaTimeError)

    def __add__(self, other):
        """Operator overloading for addition.

        **Raises** -- TypeError - Raised when something other
        than an int, float, spss_time or another
        delta_time is added to a delta_time.
        """
        if (isinstance(other,types.IntType) 
            or isinstance(other,types.FloatType)):
            return delta_time(self.delta + other)
        elif isinstance(other, delta_time):
            return delta_time(self.delta + other.delta)
        elif isinstance(other,spss_time):
            return other.__class__(self.delta + other.get_sogsseconds())
        else:
            DeltaTimeError = """delta_times may only be added to
            ints, floats, other delta_times, and spss_times"""
            raise TypeError(DeltaTimeError)


    def __mul__(self, other):
        """Operator overloading for multiplication (self * other).

        **Raises** -- TypeError - Raised when something other
        than an int or float is multiplied by a delta_time.
        """
        if (isinstance(other,types.IntType) 
            or isinstance(other,types.FloatType)):
            return delta_time(self.delta * other)
        else:
            DeltaTimeError = """delta_times may only be multiplied by
            ints or floats."""
            raise TypeError(DeltaTimeError)

    def __rmul__(self, other):
        """More operator overloading for multiplication (other * self).

        **Raises** -- TypeError - Raised when something other
        than an int or float is multiplied by a delta_time.
        """
        return self.__mul__(other)


    def __div__(self, other):
        """Operator overloading for division (self / other).

        **Raises** -- TypeError - Raised when something other
        than an int or float is divided into a delta_time.
        """
        if (isinstance(other,types.IntType) 
            or isinstance(other,types.FloatType)):
            return delta_time(self.delta / other)
        else:
            DeltaTimeError = """delta_times may only be divided by
            ints or floats."""
            raise TypeError(DeltaTimeError)

    def __abs__(self):
        """The absolute value operation.
        """
        return delta_time(abs(self.delta))

    def set_sec(self, sec):
        """Set the delta_time to the input (int or float)."""
        self.delta = sec
        
    def get_sec(self):
        """Return the delta_time in seconds (int or float)."""
        return self.delta

    def get_list(self):
        """Returns a list containing the delta_time components.  

        **Returns** -- A list

         o Item [0] = sign (+1 or -1)
         o Item [1] = days
         o Item [2] = hours
         o Item [3] = minutes
         o Item [4] = seconds
        """
        if self.delta < 0:
            sign = -1
        else:
            sign = 1
        d = abs(self.delta)
        days = math.floor(d/86400.0)                              
        hours = math.floor((d - days*86400.0)/3600.0) 
        minutes = math.floor((d - days*86400.0 - hours
                              *3600.0)/60.0) 
        seconds = (d - days*86400.0 - hours
                   *3600.0 - minutes*60.0) 
        return [sign, days, hours, minutes, seconds]
    
    def to_pass_delta_time(self):
        """Output a string in the PASS ASCII delta time format.
        """
        sign, days, hours, minutes, seconds = self.get_list()
        if sign == -1:
            outstring = '-'
        else:
            outstring = ''
        if days:
            outstring += str(int(days)) + 'D'
        if days or hours:
            outstring += '%02iH' % hours
        if days or hours or minutes:
            outstring += '%02iM' % minutes
        return outstring + '%02iS' % int(seconds + 0.5)
        
    def set_list(self, L):
        """Accepts a list in the same format as 'get_list' produces.

        Sets delta_time using this list.
        """
        self.delta = L[0]*(L[1]*86400.0 + L[2]*3600.0 + L[3]*60.0 +
                           L[4])


class spss_time:
    """A class for dealing with times in spss."""
    sct_format  = "%Y.%j:%H:%M:%S"
    sms_format  = "%yY%jD%HH%MM%SS"
    pass_format = "%YY%jD%HH%MM%SS" #time format for PASS.
    def __init__(self, t = None):
        """The spss_time constructor.

        Arguments:

        t -- If a number, it is assumed to be SOGS seconds.  If  
        a string, it is assumed to be a SOGS character time.  The
        default will set the time to the current system time.

        **Returns** -- an spss_time object with the time 
        set to the current time.

        **Raises** -- TypeError - Raised when the input is something
        other than an int, float, string, or another spss_time.
        """
	SpssTimeError = """spss_time constructor requires an
	int, float, string, another spss_time, or a list of [<time>, <format>]."""
        if t is None:
            self.syssec = time.time()
        elif (isinstance(t,types.IntType) 
              or isinstance(t,types.FloatType)):
            self.syssec = t + SYS_TO_SOGSSEC
        elif isinstance(t,types.StringType):
            spss_time.set_sogs_character_time(self, t)
        elif isinstance(t,spss_time):
            self.syssec = t.syssec
	elif isinstance(t, types.ListType):
	    if len(t) == 2:
		if t[1] == 'systemtime':
		    self.syssec = t[0]
		else:
		    SpssTimeError = """Unsupported Input time reference '%s'""" % t[1]
		    raise TypeError(SpssTimeError)
	    else:
		SpssTimeError = """List Input time requires 2 elements got %s""" % len(t)
		raise TypeError(SpssTimeError)
        elif HAS_DATETIME and isinstance(t, datetime.datetime):
            spss_time.set_sogs_character_time(self, t.strftime(self.sct_format))
        elif HAS_MX and type(t) == type(mx.DateTime.DateTime(2001)):
            self.syssec = t.ticks()
        else:
            raise TypeError(SpssTimeError)



    def __repr__(self):
        """The string representation of an spss_time.

        **Returns** --  The SOGS character time 
        will be printed.
        """
        return time.strftime(self.sct_format,time.gmtime(self.syssec))

		
    def __float__(self):
        """The SOGS seconds representation of the time is returned
        as a float.
        """
        return float(self.get_sogsseconds())

		
    def __int__(self):
        """The SOGS seconds representation of the time is returned
        as an int.
        """
        return int(self.get_sogsseconds())


    def __cmp__(self, other):
        """Operator overloading for cmp.
        
        SOGS times may be compared with the '>','>=','<','<=','==', 
        and '!=' operators.
        """
        if hasattr(other, 'syssec'):
            return cmp(self.syssec, other.syssec)
        elif type(other) == type(0) or type(other) == type(0.0):
            return cmp(self.syssec, other)
        elif type(other) == type(None):
            return cmp(self.syssec, 0)
        else:
            raise TypeError("Cannot compare an spss_time with %s" % type(other))
	
    def __sub__(self, other):
        """Operator overloading for subraction.

        **Returns** -- A delta_time when two spss_times are subtracted.  
        Subracting a float, int, or delta_time from a spss_time
        returns an spss_time.
        """
        if isinstance(other,spss_time):
            return delta_time(self.syssec - other.syssec)
        elif isinstance(other,delta_time):
            return self.__class__(self.syssec - other.delta - SYS_TO_SOGSSEC)
        elif (isinstance(other,types.IntType) 
              or isinstance(other,types.FloatType)):
            return self.__class__(self.syssec - other - SYS_TO_SOGSSEC)
        else:
            SpssTimeError = """Only ints, floats, delta_times,
            and other spss_times may be subtracted from an
            spss_time."""
            raise TypeError(SpssTimeError)

    def __add__(self, other):
        """Operator overloading for addition.
        
        **Returns** -- When an spss_time and a delta, int, or float
        are added, an spss_time object will be returned.
        """
        if isinstance(other,delta_time):
            return self.__class__(self.syssec + other.delta - SYS_TO_SOGSSEC)
        elif (isinstance(other,types.IntType) 
              or isinstance(other,types.FloatType)):
            return self.__class__(self.syssec + other - SYS_TO_SOGSSEC)
        else:
            SpssTimeError = """Only ints, floats, and delta_times
            may be added to an spss_time."""
            raise TypeError(SpssTimeError)
        
    def get_sogsseconds(self):
        """Returns the time of the spss_time object expressed in SOGS seconds."""
        return self.syssec - SYS_TO_SOGSSEC

    def set_sogsseconds(self, ss):
        """Sets the spss_time to 'ss' SOGS seconds.
        
        Arguments:

        ss -- must be in SOGS seconds. Sets spss_time object to that
        number of SOGS seconds.
        
        **Raises** -- TypeError - Raised when the input parameter is
        something other than an int, float, or string.
        """
        if (isinstance(ss,types.IntType) 
            or isinstance(ss,types.FloatType)):
            self.syssec = ss + SYS_TO_SOGSSEC
        elif isinstance(ss,types.StringType):
            self.syssec = int(ss) + SYS_TO_SOGSSEC
        else:
            raise TypeError('set_sogsseconds requires an int, float, or string')
                    
                
    def get_system_seconds(self):
        """Returns the time of the spss_time object expressed in system seconds
        (seconds since Jan. 1, 1970).
        """
        return self.syssec

    def set_system_seconds(self, ss):
        """Sets the spss_time to 'ss' system seconds.
        
        Arguments:

        ss -- must be seconds since Jan. 1, 1970. Sets spss_time object to that
        number of system seconds.
        
        **Raises** -- TypeError - Raised when the input parameter is
        something other than an int, float, or string.
        """
        if (isinstance(ss,types.IntType) 
            or isinstance(ss,types.FloatType)):
            self.syssec = ss
        elif isinstance(ss,types.StringType):
            self.syssec = int(ss)
        else:
            raise TypeError('set_system_seconds requires an int, float, or string')
                                    
    def get_sogs_character_time(self):
        """Returns the time of the spss_time object expressed as a SOGS character time."""
        return time.strftime(self.sct_format,time.gmtime(self.syssec))

    def set_sogs_character_time(self, sct):
        """Sets spss_time object to 'sct'. 

        Input parameter is expressed in SOGS character time format."""
        #I parse the sogs character time string myself rather than 
        # using strptime because strptime does not parse 
        # fractional seconds.
        sct = string.strip(sct)
        time_list = re.split('[YDHMSydhms\.:\s]',sct)
        # remove any empty strings at the end of the list
        while time_list[-1] == '':
            del time_list[-1]
        year = int(time_list[0])
        if 80 <= year <= 99:
            # Default century to 1900 for years between 80 and 99.
            year = year + 1900
        elif year < 80:
            year = year + 2000
            
        day = int(time_list[1])

        if len(time_list) > 2:
            hour = int(time_list[2])
        else:
            hour = 0
        if len(time_list) > 3:
            minute = int(time_list[3])
        else:
            minute = 0
        if len(time_list) > 4:
            second = int(time_list[4])
        else:
            second = 0
        if len(time_list) > 5:
            if time_list[5]:
                second = second + \
                    float('0.%s' % time_list[5])
        self.syssec = second + 60*minute + 3600*hour + 86400*(day-1)
        leapyears = math.floor((year - 1969)/4)
        normalyears = year - 1970 - leapyears
        self.syssec = (self.syssec + LEAP_YEAR_SECONDS * leapyears 
                       + NORMAL_YEAR_SECONDS * normalyears)
		
    def get_sms_time(self):
        """Returns the time of the spss_time object expressed in SMS time format.
        """
        return time.strftime(self.sms_format,time.gmtime(self.syssec))

    def get_pass_time(self):
        """Returns the time of the spss_time object expressed in PASS time format.
        """
        return time.strftime(self.pass_format,time.gmtime(self.syssec))

    def set_julian_day(self, jd):
        """Sets the spss_time object to the entered Julian Day."""
        self.syssec = (jd - JD_1_1_1970)*86400.

    def get_julian_day(self):
        """Returns the time in Julian Day format."""
        return float(self.syssec)/86400. + JD_1_1_1970

    def get_localtime(self):
        """returns time based upon time.tztime local time zone defined for
           the current system. returns identical spss_time object
           on GMT systems.
        """
        return localtime(int(self))

    def strftime(self,format):
        """Returns the spss_time in format 'format'.  Possible formats include:

        o %a - abbreviated weekday name
        o %A - full name of the weekday
        o %b - abbreviated month name
        o %B - full month name
        o %d - day of the month (1-31)
        o %H - hour of the day (0-23); 24-hour clock basis
        o %I - hour of the day (1-12); 12-hour clock basis
        o %j - day of the year (1-366)
        o %m - month of the year (1-12)
        o %M - minute (0-59)
        o %S - seconds (0-59)
        o %U - week number of the year (0-53) with Sunday as the first day of the week
        o %w - weekday (Sunday=0,...,Saturday=6)
        o %W - week number of the year (0-53) with Monday as the first day of the week
        o %y - two-digit year representation (00-99)
        o %Y - year with century (for example, 1998)

        See 'time.strftime' for more possible formats."""
        return time.strftime(format,time.gmtime(self.syssec))

    def strptime(self, time_string, format):
        """Parse a string representing a time and set the spss_time object to that time.

        Returns the spss_time object.
        
        Formats are the same as in strftime.
        """
        self.syssec = time.mktime(time.strptime(time_string, format))
        if time.daylight:
            self.syssec = self.syssec - time.altzone
        else:
            self.syssec = self.syssec - time.timezone
            
        return self

    def get_weekid(self):
        """Finds the previous Monday.

        Returns a weekid object constructed from that time."""
        weekday_number = int(self.strftime('%w'))
        if weekday_number == 0:
            monday = spss_time(self.get_sogsseconds() - 6*86400)
        else:
            monday = spss_time(self.get_sogsseconds() -
                               (weekday_number - 1)*86400)
        return weekid(monday)


class localtime(spss_time):
    """A class for dealing with local times.
    """
    def __init__(self, t=None, timezone=None):
        if timezone:
            self.timezone = timezone
        else:
            self.timezone = LOCAL_TIMEZONE

        spss_time.__init__(self, t)

    def __repr__(self):
        return self.strftime('%X %x %Z')

    def set_timezone(self, tz):
        self.timezone = tz

    def get_timezone(self):
        return self.timezone

    def strftime(self, format):
        import os
        old_tz = self.timezone
        if os.environ.has_key('TZ'):
            old_tz = os.environ['TZ']
        os.environ['TZ'] = self.timezone
        time.tzset()
        lt = time.strftime(format, time.localtime(self.syssec))
        os.environ['TZ'] = old_tz
        return lt

    def strptime(self, time_string, format):
        """Parse a string representing a time and set the spss_time object to that time.

        Returns the spss_time object.
        
        Formats are the same as in strftime.
        """
        import os
        old_tz = self.timezone
        if os.environ.has_key('TZ'):
            old_tz = os.environ['TZ']
        os.environ['TZ'] = self.timezone
        time.tzset()
        self.syssec = time.mktime(time.strptime(time_string, format))
        os.environ['TZ'] = old_tz
        return self

    
class orbit_relative_time:
    """A class for orbit relative times."""
    def __init__(self, t=None):
        """The orbit relative time constructor.

        The input parameter must be an orbit relative time object or a
        string containing an orbit relative time.
        """
        if isinstance(t, orbit_relative_time):
            self.__dict__ = t.__dict__
            return

        if type(t) == type(""):
            if string.find(t, "MFSYNC") != -1:
                # A major frame sync time
                orbtime = re.findall("ORB,(\d+),(\w+),(.+?),MFSYNC,([^S]+)S",t)[0]

                self.mfsync    = 1
                self.mf_delta  = delta_time(orbtime[3])
            else:
                # Not a MF sync time
                orbtime = re.findall("ORB,(\d+),(\w+),([^S]+)S",t)[0]

                self.mfsync    = 0

            self.orbit         = int(orbtime[0])
            self.orbital_event = orbtime[1]
            self.delta         = delta_time(orbtime[2])


    def __repr__(self):
        """The string representation of an orbit relative time."""
        if self.mfsync:
            return "(ORB,%i,%s,%s,MFSYNC,%s)" % (self.orbit,
                                                 self.orbital_event,
                                                 self.delta,
                                                 self.mf_delta)
        else:
            return "(ORB,%i,%s,%s)" % (self.orbit,
                                       self.orbital_event,
                                       self.delta)
            


    def __sub__(self, other):
        """Operator overloading for subraction.
        
        If other is an orbit_relative_time, the orbit number and event must be
        the same for non-major frame sync times.  If other is a MFSYNC time, self
        must be one as well. The delta times must also be the same for MFSYNC times.

        **Returns** -- A delta_time when two orbit_relative_times are subtracted.  
        Subracting a float, int, or delta_time from a orbit_relative_time
        returns an orbit_relative_time.
        """
        if isinstance(other,orbit_relative_time):
            if self.orbit != other.orbit:
                raise ValueError("""Currently only orbit relative times with the
                same orbit number may be subtracted.""")

            if self.orbital_event != other.orbital_event:
                raise ValueError("""Currently only orbit relative times referenced to
                the same orbital event may be subtracted.""")

            if self.mfsync and other.mfsync:
                if self.delta != other.delta:
                    raise ValueError("""Currently only MFSYNC times with the same delta
                    may be subtracted.""")
                return self.mf_delta - other.mf_delta

            elif not self.mfsync and not other.mfsync:
                return self.delta - other.delta

            else:
                raise ValueError("""Cannot subract two orbit relative times
                unless they are both MFSYNC or both not MFSYNC.""")

        elif (isinstance(other,delta_time)
              or isinstance(other,types.IntType) 
              or isinstance(other,types.FloatType)):
            if self.mfsync:
                return orbit_relative_time("(ORB,%i,%s,%s,MFSYNC,%s)"
                                           % (self.orbit,
                                              self.orbital_event,
                                              self.delta,
                                              self.mf_delta - other))
            else:
                return orbit_relative_time("(ORB,%i,%s,%s)"
                                           % (self.orbit,
                                              self.orbital_event,
                                              self.delta - other))
        else:
            OrbTimeError = """Only ints, floats, delta_times,
            and other orbit_relative_times may be subtracted from an
            orbit_relative_time."""
            raise TypeError(OrbTimeError)


    def __add__(self, other):
        """Operator overloading for addition.

        **Raises** -- TypeError - Raised when 'other' is not
        an int, float, or delta_time.

        **Returns** -- An orbit relative time.
        """
        if (isinstance(other,types.IntType) 
            or isinstance(other,types.FloatType)
            or isinstance(other, delta_time)):
            if self.mfsync:
                return orbit_relative_time("(ORB,%i,%s,%s,MFSYNC,%s)"
                                           % (self.orbit,
                                              self.orbital_event,
                                              self.delta,
                                              self.mf_delta + other))
            else:
                return orbit_relative_time("(ORB,%i,%s,%s)"
                                           % (self.orbit,
                                              self.orbital_event,
                                              self.delta + other))
        else:
            OrbTimeError = """orbit_relative_times may only be added to
            ints, floats, or delta_times."""
            raise TypeError(OrbTimeError)
        

class window:
    """A class for time windows."""
    def __init__(self, t1, t2=None):
        """The window constructor.

        The constructor requires a pair of spss_times
        with the second time the same or after the first
        or another window object.  If the first parameter
        is set to the string INFINITE, an INFINITE window
        is created.

        **Raises** -- WindowError - Raised when the second time
        (t2) is before the first time (t1).
        """
        WinError = """Window constructor requires a pair of
        spss_time objects"""
        if (isinstance(t1, types.StringType) and
            string.upper(t1) == "INFINITE"):
	    t1 = INFINITE_WINDOW.start
            t2 = INFINITE_WINDOW.end
        elif isinstance(t1, window):
            t2 = t1.end
            t1 = t1.start
            
        if isinstance(t1, spss_time):
            self.start = t1
        else:
            raise TypeError(WinError)
        
        if isinstance(t2, spss_time):
            self.end = t2
        else:
            raise TypeError(WinError)
        if t2 < t1:
            WinError = """Second spss_time in a window cannot
            be earlier than first spss_time, t1= %s, t2= %s""" % (
                t1.get_sogs_character_time(),
                t2.get_sogs_character_time())
            raise WindowError(WinError)
                
    def __repr__(self):
        """The string representation of a window.

        Returned string will appear similar to '1999.200:12:00:00 - 1999.300:12:00:00'"""
        return (self.start.get_sogs_character_time() + " - "
                + self.end.get_sogs_character_time())
    
    def __eq__(self, other):
        """Test for equality.
        """
        if not isinstance(other, window):
            return False
        if self.start == other.start and self.end == other.end:
            return True
        else:
            return False

    def __ne__(self, other):
        """Test for inequality.
        """
        if not isinstance(other, window):
            return True
        if self.start != other.start or self.end != other.end:
            return True
        else:
            return False

    def check_other(self, other, func):
        """Checks that 'other' is a window.

        **Raises** -- TypeError - Raised if other is not a window object."""
        if isinstance(other, window):
            return
        else:
            WindowError = """Function, %s, requires a window as a
            parameter""" % func
            raise TypeError(WindowError)

    def union(self, other):
        """Finds the union of two windows.

        Returns a window_list object."""
        if other is None:
            return window_list(self)
        self.check_other(other, "union")
        if ((self.start <= other.start <= self.end) or
            (self.start <= other.end <= self.end or
             (other.start <= self.start <= other.end))):
            return window_list(self.__class__(min(self.start, other.start),
                                              max(self.end, other.end)))
        else:
            return window_list([self, other])


    def intersection(self, other):
        """Finds the intersection of two windows.  Argument 'other' must be a window.

        Returns a window or 'None' if 'self' and 'other' do not intersect."""
        if other is None:
            return None
        self.check_other(other, "intersection")
        if ((self.start  <= other.start < self.end) or
            (self.start  <  other.end  <= self.end) or
            (other.start <= self.start  < other.end)):
            return self.__class__(max(self.start, other.start),
                                  min(self.end, other.end))
        else:
            return None


    # The following function 'complement' finds the complement of two windows.
    # It returns immediately if 'other' is not a window, if the windows do not 
    # intersect, or if the windows are identical. 
    #    other:     *-------------------* 
    #    self:  |---*-------------------*-----|   no complement in this case
    #    self:      |-------------------*-----|   no complement in this case
    #    self:  |---*-------------------|         no complement in this case
    #    self:      |-------------------|         no complement in this case
    #    self:      *    |--------------|
    #    self:      *    |----------|   *
    #    self:      |---------------|   *
    #    return     *----|  and/or  |---*    

    def complement(self,other=None):
        """Finds the complement of two windows.  Argument 'other' must be a window.
        'other' is assumed to be the window which defines the interval of interest.
        'self' is assumed to be the window that intersects the interval of interest. 
        If 'other' is None, INFINITE_WINDOW is used to define the interval of interest.
        Returns a window or list of windows, or 'None' if 'other' and 'self' are 
        identical. 
        Raises a TypeError if 'other' is not a window."""

	if other is None:
	    other = INFINITE_WINDOW
	else:
	    self.check_other(other, "complement")                          
        if self.compare(other) == 0:                  # other and self are identical          
            return None
	else:
	    cmplist = window_list()                                      
	    left_intersection  = other.intersection(window(INFINITE_WINDOW.start, self.start))
	    right_intersection = other.intersection(window(self.end, INFINITE_WINDOW.end))
	    if left_intersection:
		cmplist.append(left_intersection)
	    if right_intersection:
		cmplist.append(right_intersection)
	    return cmplist

    def first_start(self, other):
        """Returns the window with the earliest start - 'self' or 'other'.

        If the starts are the same, it will retrun 'self'."""
        self.check_other(other, "first_start")
        if self.start <= other.start:
            return self
        else:
            return other

    def last_start(self, other):
        """Returns the window with the latest start - 'self' or 'other'.

        If the starts are the same, it will return 'other'."""
        self.check_other(other, "last_start")
        if self.start > other.start:
            return self
        else:
            return other

    def first_end(self, other):
        """Returns the window with the earliest end - 'self' or 'other'.

        If the ends are the same, it will return 'self'."""
        self.check_other(other, "first_end")
        if self.end <= other.end:
            return self
        else:
            return other

    def last_end(self, other):
        """Returns the window with the latest end - 'self' or 'other'.

        If the ends are the same, it will return 'other'."""
        self.check_other(other, "last_end")
        if self.end > other.end:
            return self
        else:
            return other

    def set_begin_time(self, t):
        """Set the start time.
        """
        self.start = spss_time(t)

    def set_end_time(self, t):
        """Set the end time.
        """
        self.end = spss_time(t)
    
    def starttime(self):
        """Returns the spss_time object for the window start."""
        return self.start
    
    def endtime(self):
        """Returns the spss_time object for the window end."""
        return self.end

    def size(self):
        """Returns the difference between the start and end times of the window as a delta time."""
        return self.end - self.start
    
    def compare(self, other):
        """Compare window 'self' with window 'other'.

        - Returns 0 if the two windows have the same start and end.
        - Returns -1 if 'self' begins before 'other' or ends before
        other if the starts are the same.
        - Returns 1 if 'self' begins after 'other' or ends after
        'other' if the starts are the same.
        """
        if self.start == other.start and self.end == other.end:
            return 0
        elif self.start < other.start:
            return -1
        elif self.start == other.start and self.end < other.end:
            return -1
        elif self.start > other.start:
            return 1
        else:
            # self.start == other.start and self.end > other.end
            return 1

    def overlaps(self, other):
        """Does window 'self' overlap window 'other'?

        Returns true if self and other overlap, otherwise returns false."""
        if self.start >= other.end or other.start >= self.end:
            return 0
        else:
            return 1

    def contains(self, other):
        """Returns True if the start of 'other' is greater than or
        equal to that of 'self' and the end of 'other' is less
        that or equal to the endtime of 'self'.
        """
        if isinstance(other, spss_time):
            if self.start <= other <= self.end:
                return 1
            else:
                return 0
        elif isinstance(other, window): 
            if self.start <= other.start and self.end >= other.end:
                return 1
            else:
                return 0
        else:
            raise ValueError("Input to contains function must be an spss_time or a window.")
        
class WindowError(exceptions.EnvironmentError):
    """Raised by class time_util.window_list.

    Raised when the first time in the window is
    after the second."""
    pass
        
#More constants...
INFINITE_WINDOW = window(spss_time("1980.001:00:00:00"),
			 spss_time("2030.001:00:00:00"))

class window_list(list):
    """A class for lists of windows."""
    def __init__(self, l=None):
        """The window_list constructor.

        The constructor requires a list of windows or a single window.
        The default constructor produces an empty window_list.

        **Raises** -- TypeError - Raised if the input is something other
        than a window, list, or another window_list."""
        WindowListError = """Window_list constructor requires a list of
        windows as input, a single window, or another window_list."""
        if l is None:
            list.__init__(self, [])
        elif isinstance(l, window):
            list.__init__(self, [l])
        elif isinstance(l, types.ListType):
            for w in l:
                if not isinstance(w, window):
                    raise TypeError(WindowListError)           
            list.__init__(self, l)
        else:
            raise TypeError(WindowListError)

    def __repr__(self):
        """The string representation of a window list.

        Returns a string containing each
        pair of times for each window in the list."""
        s = ""
        for win in self:
            s = s + str(win) + '\n'
        return s[:-1]

    def __eq__(self, other):
        """Equals comparison.
        """
        # Lists must be sorted.
        self.sort()
        other.sort()
        if len(self) != len(other):
            return False
        for i in range(len(self)):
            if self[i] != other[i]:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __add__(self, other):
        return window_list(list.__add__(self, other))

    def earliest_start(self):
        """Return the earliest window start time.
        """
        if len(self):
            earliest_start = self[0].starttime()
            for win in self[1:]:
                if win.starttime() < earliest_start:
                    earliest_start = win.starttime()
            return earliest_start
        else:
            return None

    def latest_end(self):
        """Return the lastest window end time.
        """
        if len(self):
            latest_end = self[0].endtime()
            for win in self[1:]:
                if win.endtime() > latest_end:
                    latest_end = win.endtime()
            return latest_end
        else:
            return None

    def intersection(self, other):
        """Finds the intersection between two window_lists.

        Input parameter 'other' must be a window_list.
        Raises a TypeError if 'other' is not a window_list."""
        new_windowlist = window_list()
        if not isinstance(other, window_list):
            WindowListError = """Intersection requires a
            window_list object as the parameter"""
            raise TypeError(WindowListError)
        for s_win in self:
            for o_win in other:
                new_win = s_win.intersection(o_win)
                if new_win is not None:
                    new_windowlist.append(new_win)
        return new_windowlist

    def sort(self, cmpfunc=window.compare):
        """Sort this window_list based on the input 'cmpfunc'.

        Default sorts are done with the 'window.compare' function."""
        list.sort(self, cmpfunc)
        return

    def union(self):
        """Returns the union of the current set of windows."""

        # Sort the windows first since this algorithm only works
        # with sorted windows, however, we first copy the input
        # list since the sort method does the sort in place
        inplist = window_list(self[:])
        inplist.sort()
        
        unioned_windows = window_list()
        
        if inplist:
            temp_window = inplist[0]
            for cur_win in inplist:
                temp_unioned = temp_window.union(cur_win)
                # The result will either be 1 or 2 windows.
                # If it's 2 windows, then store the 1st one
                if (len(temp_unioned) == 2):
                    unioned_windows.append(temp_unioned[0])
                # Save away the last window for use in the next iteration
                temp_window = temp_unioned[-1]
            # Write out the final unioned window from the buffer
            unioned_windows.append(temp_unioned[-1])

        return unioned_windows

    def complement(self, interval=INFINITE_WINDOW):
        """Returns the complement of a set of windows over 'interval'.
	   Interval defaults to infinity as defined by the constant
	   INFINITE_WINDOW.
           If there is no complement, None is returned."""

	# -- TypeError - Raised if interval is not a window object.      
	if not isinstance(interval, window):
	    WinError = """window_list.complement function requires a window argument"""
	    raise WindowError(WinError)
        complist = window_list(interval)
        # First let's make a clean unioned list to complement since this
        # makes complement significantly faster
        unioned_list = self.union()
        for wnd in unioned_list:
            tmplist = wnd.complement(interval)
            if tmplist is not None:
                complist = complist.intersection(tmplist)            
	    else:
		return None
	return complist
    
    def get_windowlette_sum(self):
	"""Gets the sum of the delta times for all windowlettes in the plan 
	window.
	"""
	sum = delta_time()
	for windowlette in self:
	    sum = sum + windowlette.size()
	return sum

    def get_total_duration(self):
	"""Gets the delta time between earliest windowlette start and latest 
	windowlette end for the plan window.
	"""
	if len(self):
	    total_pw = window(self.earliest_start(), self.latest_end())
	    return total_pw.size()
	else:
	    return 0

    def contains(self, other):
        """Returns True if other is total contained within self.
        Otherwise returns False.
        """
        if isinstance(other, window_list):
            for w1 in self:
                ww = 0
                for w2 in other:
                    if w1.contains(w2):
                        ww = 1
                        break
                if not ww:
                    return 0
            return 1
        elif isinstance(other, window) or isinstance(other, spss_time):
            for w1 in self:
                if w1.contains(other):
                    return 1
            return 0
        else:
            raise ValueError("contains input must be a window_list, a window or an spss_time")

        
class weekid:
    """A class for weekids.

    A week id is a two digit year followed by a three digit day number."""
    import exceptions
    def __init__(self, intime):
        """The weekid constructor.

        Contructs a weekid from a string, spss_time, or ccl.
        Raises a TypeError if called with something other than
        one of these.""" 
        import ccl_util
        if isinstance(intime, types.StringType):
            self.from_string(intime)
        elif isinstance(intime, spss_time):
            self.year  = int(intime.strftime('%Y'))
            self.day   = int(intime.strftime('%j'))
            self.yyddd = intime.strftime('%y%j')
        elif isinstance(intime, ccl_util.ccl):
            self.year  = int(intime.get_begin_time().strftime('%Y'))
            self.day   = int(intime.get_begin_time().strftime('%j'))
            self.yyddd = intime.get_begin_time().strftime('%y%j')            
        else:
            raise TypeError("""weekid constructor requires a
            string, spss_time, or ccl.""")

    def __repr__(self):
        """The string representation of a weekid object.

        Returns a string 'yyddd' as the string representation of a
        weekid."""
        return self.yyddd
    
    def __cmp__(self, other):
        """Compare two weekids.

        'other' must be a weekid object.

        The comparison is done is done on the ASCII representaion
        of the weekids."""
        return cmp(self.guess_starttime(), other.guess_starttime())

    def from_string(self, s):
        """Extract the weekid attributes from an input string.

        Assumes the first two characters are the two digit year and
        the next three characters are the day number.""" 
        
        s = string.strip(s)
        if s == "":
           raise WeekIdError("Input is null")
        if re.search("^[0-9]{5,5}", s) is None:
           raise WeekIdError('First 5 chars of week ID must be numeric.')
        y = int(s[:2])
        if y < 80:
            self.year = 2000 + y
        else:
            self.year = 1900 + y
        self.day = int(s[2:5])
        max_days_in_year = 365
        if (self.year % 4) == 0:
            max_days_in_year = 366
        if not (0 < self.day <= max_days_in_year):
            raise WeekIdError('%i is an invalid day number' % self.day)
        self.yyddd = s[:5]

    def get_year(self):
        """Returns four digit year as an integer."""
        return self.year
    
    def get_yyyy(self):
        """Returns four digit year as a string."""
        return str(self.year)

    def get_yy(self):
        """Returns two digit year as a string."""
        if self.year > 1999:
            return "%02i" % (self.year - 2000)
        else:
            return "%02i" % (self.year - 1900)
        
    def get_day(self):
        """Returns day as an integer."""
        return self.day
    
    def get_ddd(self):
        """Returns day as a string left padded with zeros."""
        return "%03i" % self.day
    
    def get_yyddd(self):
        """Returns week id 'yyddd'."""
        return self.yyddd
    
    def guess_starttime(self):
        """Guess the start time from the week_id.

        Returns an spss_time."""
        return spss_time(str(self.year) + ".%03i" % self.day +
                         ":00:00:00")

    def guess_endtime(self):
        """Guess the end time.

        Returns the start time plus one week as an spss_time."""
        return (self.guess_starttime() + SECONDS_IN_A_WEEK)
            
    def is_monday(self):
        """Checks that weekid corresponds to a Monday.

        Returns true if weekid is a Monday, false otherwise."""
        start = self.guess_starttime()
        if int(start.strftime('%w')) == 1:
            return 1
        else:
            return 0

    def get_honcho(self):
        """Gets the SMS honcho for this weekid.

        Returns a tuple containing the week id (as a string), the SMS honcho's
        name, his phone number, and his email address.  When this weekid cannot
        be matched with any weekid in the sms-honcho.dat file, None is returned.
        """
        import spss_sys_util
        honcho_file = spss_sys_util.resolver("PE_DAT", "sms-honcho.dat")
        if not honcho_file:
            raise WeekIdError("Can't find sms-honcho.dat in PE_DAT")
        hlines = open(honcho_file, "r").readlines()

        # The following regular expression matches a 5 digit weekid followed
        # by a | followed by a name (non-white space, some white space, non-white
        # space) followed by some white space followed a phone number followed
        # by some white space followed by an email address.
        r = re.compile("(\d{5,5})\|(\S+\s+\S+)\s+(\S+)\s+(\S+)")
        for hline in hlines:
            match = r.findall(hline)
            if not match:
                continue
            if match[0][0] == self.yyddd:
                return match[0]
        return None
        

class WeekIdError(exceptions.Exception):
    """The error raised when a bad weekid is detected."""
    pass
    


#
# Test to see if GUI is available because VMS does not
# support Tkinter at the moment.
#
from spss_tk_util import *
if GUI_AVAILABLE:
    from Tkinter import *
    #
    # class Time_entry has inherited fuctionality from Frame.
    #
    class Time_Entry(Frame):
        """ Entry widget class for entering spss_time 

        **USAGE** --
            demo_widget = Time_entry(<main "master" window instance>,
                value = <spss_time object>
                bg_error=<background color for error in field>
                background = <normal background color>) """

        def __init__(self,master,
            value               = None,
            max_time            = None,
            min_time            = None,
            bg_error            = 'green',
            background          = 'lightgrey',
            foreground          = 'black',
            highlightbackground = '#d9d9d9',
            highlightcolor      = 'Black',
            justify             = 'left',
            insertbackground    = 'Black',
            state               = 'normal'
            ):

            #initialize from Frame. 
            Frame.__init__(self,master)

            # set the min time for error checking.
            if min_time is not None:
                self.min_time     = spss_time(min_time)
            else:
                self.min_time     = None

            # set the max time for error checking.
            if max_time is not None:
                self.max_time     = spss_time(max_time)
            else:
                self.max_time     = None

            self.error        = false        #error state of all entry fields.
            self.bg_error     = bg_error     #color of background for
                                             #error in input.
            self.bg_default   = background   #default NO error background

            #define default time values for each input field.
            def_time = spss_time(value)
            self.default_year = def_time.strftime("%Y")
            self.default_day  = def_time.strftime("%j")
            self.default_hour = def_time.strftime("%H")
            self.default_min  = def_time.strftime("%M")
            self.default_sec  = def_time.strftime("%S")
            self.value = def_time

            #create year entry box and bindings to validations.
            #arguments not included in Frame class must be
            #explicitly defined for call to Entry object.

            self.year_entry =       IntEntry(self,
                value               = int(self.default_year),
                format              = '%04i',
                max_value           = 3000,
                min_value           = 1900,
                name_value          = "Year",
                background          = background,
                foreground          = foreground,
                justify             = justify,
                insertbackground    = insertbackground,
                state               = state)
            self.year_entry.pack(side=LEFT)

            Label(self,text=".",width=1).pack(side=LEFT)

            self.day_entry =       IntEntry(self,
                value               = int(self.default_day),
                format              = '%03i',
                max_value           = 366,
                min_value           = 1,
                name_value          = "Day",
                background          = background,
                foreground          = foreground,
                justify             = justify,
                insertbackground    = insertbackground,
                state               = state)
            self.day_entry.pack(side=LEFT)

            Label(self,text=":",width=1).pack(side=LEFT)

            self.hour_entry =       IntEntry(self,
                value               = int(self.default_hour),
                format              = '%02i',
                max_value           = 23,
                min_value           = 0,
                name_value          = "Hour",
                background          = background,
                foreground          = foreground,
                justify             = justify,
                insertbackground    = insertbackground,
                state               = state)
            self.hour_entry.pack(side=LEFT)

            Label(self,text=":",width=1).pack(side=LEFT)

            self.min_entry =       IntEntry(self,
                value               = int(self.default_min),
                format              = '%02i',
                max_value           = 59,
                min_value           = 0,
                name_value          = "Minute",
                background          = background,
                foreground          = foreground,
                justify             = justify,
                insertbackground    = insertbackground,
                state               = state)
            self.min_entry.pack(side=LEFT)

            Label(self,text=":",width=1).pack(side=LEFT)

            self.sec_entry =       IntEntry(self,
                value               = int(self.default_sec),
                format              = '%02i',
                max_value           = 59,
                min_value           = 0,
                name_value          = "Second",
                background          = background,
                foreground          = foreground,
                justify             = justify,
                insertbackground    = insertbackground,
                state               = state)
            self.sec_entry.pack(side=LEFT)

            #set binding to validate time upon mouse pointer leaving field.
            self.bind("<Leave>",self.validate)

            #set bindings to alow Control-R to reset time value for entire widget.
            self.year_entry.bind("<Control-R>",self.reset)
            self.day_entry.bind("<Control-R>",self.reset)
            self.hour_entry.bind("<Control-R>",self.reset)
            self.min_entry.bind("<Control-R>",self.reset)
            self.sec_entry.bind("<Control-R>",self.reset)

        def get_pass_time(self):
            """returns pass formated time string"""

            time_string = "%04dY%03dD%02dH%02dM%02dS" % \
                (self.year_entry.get(),self.day_entry.get(),
                 self.hour_entry.get(),self.min_entry.get(),
                 self.sec_entry.get())
            return time_string

        def get(self,event=None):
            """time retrieval function. returns spss_time object."""

            if self.get_error_state():
                    self.value = None
                    return self.value
            time_string = "%04d.%03d:%02d:%02d:%02d" % \
                (self.year_entry.get(),self.day_entry.get(),
                 self.hour_entry.get(),self.min_entry.get(),
                 self.sec_entry.get())
            self.value = spss_time(time_string)
            return self.value

        def reset(self,event=None):
            """reset all fields to default values
            """
            self.year_entry.reset()
            self.day_entry.reset()
            self.hour_entry.reset()
            self.min_entry.reset()
            self.sec_entry.reset()
            self.set_error_state(false)
 
        def validate(self,event=None):
            """validates time in widget"""
            self.get()
            #check for correct day entry - ie. leap year problems like day 366 in 2002
            if self.value is not None:
                if int(self.value.strftime("%j")) != self.day_entry.get():
                    error = "Check day value!"
                    error_message = Error_Window(self,error)
                    self.day_entry.set_error_state(true)

                if self.max_time is not None:
                    if self.value > self.max_time:
                        self.set_error_state(true)
                        error = "Time must be before max time:  %s\n" % self.max_time
                        error_message = Error_Window(self,error)

                if self.min_time is not None:
                    if self.value < self.min_time:
                        self.set_error_state(true)
                        error = "Time must be after min time:  %s\n" % self.min_time
                        error_message = Error_Window(self,error)

        def get_error_state(self):
            """returns true/false for error in entry widget """

            if self.year_entry.get_error_state() or\
               self.day_entry.get_error_state() or\
               self.hour_entry.get_error_state() or\
               self.min_entry.get_error_state() or\
               self.sec_entry.get_error_state():
                self.error = true
            else:
                self.error = false
            return self.error

        def set_error_state(self,on):
            """ on = true  - set background color to self.bg_error
                on = false - set background color to self.bg_default
            """
            self.year_entry.set_error_state(on)
            self.day_entry.set_error_state(on)
            self.hour_entry.set_error_state(on)
            self.min_entry.set_error_state(on)
            self.sec_entry.set_error_state(on)

        def set_time(self, time):
            """Set the time in the entry boxes to the input value.
            """
            time = spss_time(time)
            self.year_entry.delete(0,END)
            self.year_entry.insert(0, time.strftime("%Y"))
            self.year_entry.set_value()
            self.day_entry.delete(0,END)
            self.day_entry.insert(0, time.strftime("%j"))
            self.day_entry.set_value()
            self.hour_entry.delete(0,END)
            self.hour_entry.insert(0, time.strftime("%H"))
            self.hour_entry.set_value()
            self.min_entry.delete(0,END)
            self.min_entry.insert(0, time.strftime("%M"))
            self.min_entry.set_value()
            self.sec_entry.delete(0,END)
            self.sec_entry.insert(0, time.strftime("%S"))
            self.sec_entry.set_value()

        def get_time(self):
            """Synonym of get.  Return the input time.
            """
            return self.get()
