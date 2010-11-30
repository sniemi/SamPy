# This tool will plot the HST ground tracks

from mpl_toolkits.basemap import Basemap
from pylab import *
from matplotlib.font_manager import FontProperties

import sys, glob, os.path
import string, math
import ephem
import time_util
import spst_getopt

def get_tle_file(request_time, tle_files):
    """This function will find the appropriate hst tle file
       for the input request_time.
    """

    import time_util
    
    tle_keys = tle_files.keys()
    tle_keys.sort()
    sm4_time = time_util.spss_time("2009.139:00:00:00")
    time_of_interest = time_util.spss_time(request_time)
    
    if (time_of_interest < sm4_time):
        min_index = 0
        max_index = tle_keys.index("2010.055:00:00:00")
    else:
        min_index = tle_keys.index("2010.055:00:00:00")
        max_index = len(tle_keys)
    # end if
    
    tle_file = tle_files[tle_keys[min_index]][0]
    for i in tle_keys[min_index:max_index]:
        if (time_of_interest >= tle_files[i][1]):
            tle_file = tle_files[i][0]
        # end if
    # end for i
    
    return tle_file
# end def get_tle_file

saa_switch_time = time_util.spss_time('2010.151:00:00:00')

# Deal with the input parameters
# 1st parm should be the start time for the HST ground track
# 2nd parm should be the end time for the HST ground track
# Both are required and in YYYY.JJJ:HH:MM:SS format
# Optional switch to label the HST ground track with HH:MM
labelhst = 0
allowed_options = ['labelhst']
options, parms = spst_getopt.spst_getopt(tuple(sys.argv[1:]), allowed_options)
if (options.has_key('-labelhst')):
  labelhst = 1
# end if

arg1 = time_util.spss_time(parms[0])
arg2 = time_util.spss_time(parms[1])
# Note: The +1s is necessary due to the ephem.Date losing 1s somewhere
targ1 = arg1 + 1
targ2 = arg2 + 1
hst_start = ephem.Date(targ1.strftime("%Y/%m/%d %H:%M:%S"))
hst_stop  = ephem.Date(targ2.strftime("%Y/%m/%d %H:%M:%S"))
num_points = int((hst_stop - hst_start)/ephem.minute)

# Get all the Two-Line ephemeris files
#name_list = glob.glob('/Users/niemi/Desktop/Misc/*.tle') 
#tle_files = {}
#for tle in name_list:
#    temp_base = string.split(os.path.splitext(os.path.split(tle)[1])[0],"_")
#    print temp_base
#    if (len(temp_base) != 2):
#        continue
    # end if
#    ephem_date_string = "20" + temp_base[1][0:2] + "." + temp_base[1][2:] + ":00:00:00"
#    tle_files[ephem_date_string] = [tle,time_util.spss_time(ephem_date_string)]
# end for tle

# Read in the HST Two-Line ephemeris                                                                             
#SMN suggestions                                                                                                 
import urllib2                                                                                                  
hand = urllib2.urlopen('http://celestrak.com/NORAD/elements/science.txt')                                          
data = hand.readlines()                                                                                         
hand.close()                                                                                                    
HST = [[data[val], data[val+1], data[val+2]] for val, line in enumerate(data) if 'HST' in line]                             
hst = ephem.readtle(string.strip(HST[0][0]), string.strip(HST[0][1]), string.strip(HST[0][2]))    


# Read in the HST Two-Line ephemeris
#hst_tle = get_tle_file(arg1, tle_files)
#temp = open(hst_tle,"r").readlines()
#hst = ephem.readtle(string.strip(temp[0]), \
#                    string.strip(temp[1]), \
#                    string.strip(temp[2]))
                    
cur_time = hst_start

hst_longs = []
hst_lats  = []
hst_text  = []

for i in range(0,num_points):
    #print ephem.date(cur_time)
    hst.compute(cur_time)
    hst_longs.append(hst.sublong.znorm*180.0/math.pi)
    hst_lats.append(hst.sublat*180.0/math.pi)
    ctime_text = "%02.2i:%02.2i" % (ephem.Date(cur_time).tuple()[3],ephem.Date(cur_time).tuple()[4])
    hst_text.append(ctime_text)
    cur_time = cur_time + ephem.minute
# end for i
#print "hst_longs = ", hst_longs
#print "hst_lats  = ", hst_lats 
#print "hst_text  = ", hst_text  

lon_0 = 330
lat_0 = -20
llcrnrlat = -60
llcrnrlon = -100
urcrnrlat = 20
urcrnrlon = 60

# use these values to setup Basemap instance.
width  = 14000000
height = 10000000
#m = Basemap(width=width,height=height,\
#            resolution='c',projection='aeqd',\
#            lat_0=lat_0,lon_0=lon_0)
#m = Basemap(resolution='c',projection='aeqd',lat_0=lat_0,lon_0=lon_0)
#m = Basemap(width=width,height=height,\
#            resolution='c',projection='aea',\
#            lat_0=lat_0,lon_0=lon_0)
m = Basemap(resolution='c',projection='mbtfpq',lon_0=lon_0)
#m = Basemap(resolution='c',projection='moll',lon_0=lon_0)
#m = Basemap(resolution='c',projection='ortho',lon_0=lon_0,lat_0=lat_0)
#m = Basemap(resolution='c',projection='cyl',llcrnrlat=llcrnrlat,llcrnrlon=llcrnrlon,urcrnrlat=urcrnrlat,urcrnrlon=urcrnrlon)

p = FontProperties()
font1 = p.copy()
font1.set_size('small')

# draw coasts and fill continents.
m.drawcoastlines(linewidth=0.5)
#m.fillcontinents()
m.drawparallels(arange(-80,81,10),labels=[1,1,0,0],fontproperties=font1,labelstyle="+/-")
m.drawmeridians(arange(-180,180,20),labels=[0,0,0,1],fontproperties=font1,labelstyle="+/-")
m.drawmapboundary()

m.bluemarble()
m.drawmapboundary()

if (arg1 < saa_switch_time):
    # Use the previous definitions
    # SAA 02
    x2,y2 = m([357.4-360,357.6-360,356.9-360,355.0-360,352.3-360,348.7-360,342.9-360,336.4-360,324.8-360,303.2-360,292.1-360,289.0-360,285.9-360,283.5-360,282.5-360,282.4-360,282.7-360,357.4-360], \
              [-28.3,-26.1,-23.7,-21.2,-18.8,-16.3,-13.0,-10.6, -9.1,-11.9,-14.9,-17.0,-19.1,-21.3,-23.7,-26.0,-28.6,-28.3])
    # SAA 05,23
    x5,y5 = m([300.0-360, 45.0, 40.0, 30.0, 15.0,  0.0,341.0-360,318.0-360,300.0-360,283.0-360,273.0-360,275.0-360,300.0-360], \
              [-50.0,-30.0,-25.0,-21.0,-15.0,-10.2, -2.0,  1.0, -3.0, -8.0,-20.0,-30.0,-50.0])
    # SAA 24,25,28,31,32
    x24,y24=m([ 20.0, 21.0, 19.0,  7.5,347.0-360,336.4-360,324.8-360,303.2-360,292.1-360,285.9-360,283.5-360,282.5-360,282.4-360,282.7-360, 20.0], \
              [-28.3,-27.5,-26.1,-19.8, -9.6, -7.6, -6.0, -7.9,-12.0,-17.1,-20.3,-23.5,-26.0,-28.6,-28.3])
    # SAA 26,27,29,30
    x26,y26=m([ 25.0,  7.0,351.0-360,341.0-360,318.0-360,300.0-360,290.0-360,284.0-360,278.0-360,273.0-360,275.0-360, 25.0], \
              [-28.5,-16.0, -6.5, -2.0,  1.0, -3.0, -7.0,-10.0,-15.0,-20.0,-30.0,-28.5])
else:
    # Use the current definitions
    # SAA 02
    #x2,y2 = m([357.4-360,357.6-360,356.9-360,355.0-360,352.3-360,348.7-360,342.9-360,336.4-360,324.8-360,297.2-360,286.1-360,283.0-360,279.9-360,277.5-360,276.5-360,276.4-360,276.7-360,357.4-360], \
    #          [-28.3,    -26.1,    -23.7,    -21.2,    -18.8,    -16.3,    -13.0,    -10.6,     -9.1,    -11.9,    -14.9,    -17.0,    -19.1,    -21.3,    -23.7,    -26.0,    -28.6,    -28.3])
    x2,y2 = m([  2.0,  1.0,358.0-360,353.0-360,347.0-360,340.0-360,331.4-360,318.8-360,308.0-360,297.2-360,286.1-360,283.0-360,279.9-360,277.5-360,276.5-360,276.4-360,276.7-360,  2.0], \
              [-29.0,-26.1,-23.0,    -19.3,    -15.6,    -12.0,     -9.9,     -9.1,    -10.0,    -11.9,    -14.9,    -17.0,    -19.1,    -21.3,    -23.7,    -26.0,    -28.6,    -29.0])
    # SAA 05,23
    x5,y5 = m([294.0-360, 39.0, 34.0, 24.0, 9.0,354.0-360,335.0-360,312.0-360,294.0-360,277.0-360,267.0-360,269.0-360,294.0-360], \
              [-50.0,-30.0,-25.0,-21.0,-15.0,-10.2, -2.0,  1.0, -3.0, -8.0,-20.0,-30.0,-50.0])
    # SAA 24,25,28,31,32
    x24,y24=m([ 14.0, 15.0, 13.0,  1.5,341.0-360,330.4-360,318.8-360,297.2-360,286.1-360,279.9-360,277.5-360,276.5-360,276.4-360,276.7-360, 14.0], \
              [-28.3,-27.5,-26.1,-19.8, -9.6, -7.6, -6.0, -7.9,-12.0,-17.1,-20.3,-23.5,-26.0,-28.6,-28.3])
    # SAA 27,29,30
    x26,y26=m([ 19.0,  1.0,345.0-360,335.0-360,312.0-360,294.0-360,284.0-360,278.0-360,272.0-360,267.0-360,269.0-360, 19.0], \
              [-28.5,-16.0, -6.5, -2.0,  1.0, -3.0, -7.0,-10.0,-15.0,-20.0,-30.0,-28.5])
# end if
# HST observation ground track
xhst,yhst = m(hst_longs, hst_lats)

saa02 = m.plot(x2,y2,marker='D',markersize=4.0,markeredgewidth=0.0,color='black',linestyle='-',label='02')
saa05 = m.plot(x5,y5,marker='s',markersize=4.0,markeredgewidth=0.0,color='blue',linestyle='-',label='05')
saa24 = m.plot(x24,y24,marker='x',markersize=4.0,markeredgewidth=1.0,color='green',linestyle='-',label='24') 
saa26 = m.plot(x26,y26,marker='^',markersize=4.0,markeredgewidth=0.0,color='maroon',linestyle='-',label='26')
hst   = m.plot(xhst,yhst,marker='+',markersize=4.0,markeredgewidth=0.5,color='red',linestyle='-',linewidth=0.3,label='hst')
hst_label = 'HST once per minute'
if (labelhst):
    hst_label = hst_label + ' (HH:MM)'
    for j in range(0, num_points):
        text(xhst[j],yhst[j],hst_text[j],fontsize=4,clip_on=True,horizontalalignment='left',verticalalignment='bottom')

font = p.copy()
font.set_size('xx-small')
legend((saa02,saa05,saa24,saa26,hst), \
       ('02 - FGS Guidance/STIS LV', \
        '05/23 - Astrometry/NICMOS', \
        '24/25/31/32 - STIS CCD/STIS MAMA/COS FUV/COS NUV', \
        '27/28/29/30 - ACS CCD/ACS SBC/WFC3 UVIS/WFC3 IR', \
        hst_label), \
       prop=font,numpoints=2,borderpad=0.3,loc='upper center',borderaxespad=0.0,ncol=2)
#figlegend((saa02,saa05,saa24,saa26),('02','05','24','26'),'upper right')
# draw the title.
title('HST from %s to %s' % (str(arg1),str(arg2)))
show()
