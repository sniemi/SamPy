"""
Functions related to HST focus such as mirror move dates.
"""
import dates.julians as j
import time

def MirrorMoves():
    """
    HST Secondary mirror moves and amounts.
    """
    tmp = {'29 Jun 1994    17:36 UTC': +5.0,
           '15 Jan 1995    23:40 UTC': +5.0,
           '28 Aug 1995    15:16 UTC': +6.5,
           '14 Mar 1996    18:47 UTC': +6.0,
           '30 Oct 1996    17:40 UTC': +5.0,
           '18 Mar 1997    22:55 UTC': -2.4,
           '12 Jan 1998    01:15 UTC': +21.0,
           '01 Feb 1998    16:40 UTC': -18.6,
           '04 Jun 1998    01:01 UTC': +16.6,
           '28 Jun 1998    17:26 UTC': -15.2,
           '15 Sep 1999    15:40 UTC': +3.0,
           '09 Jan 2000    17:42 UTC': +4.2,
           '15 Jun 2000    19:38 UTC': +3.6,
           '02 Dec 2002    20:50 UTC': +3.6,
           '22 Dec 2004    23:12 UTC': +4.16,
           '31 Jul 2006    14:35 UTC': +5.34,
           '20 Jul 2009    09:35 UTC': +2.97}
    return tmp


def MirrorMovesInHSTTime():
    """
    Returns HST mirror move times.
    """
    x = MirrorMoves()
    tmp = []
    for key in x:
        julian = j.toJulian2(time.strptime(key.replace(':', ' '), "%d %b %Y %H %M %Z"))
        hstTime = j.fromHSTDeployment(julian)
        tmp.append([hstTime, x[key]])
    return tmp
