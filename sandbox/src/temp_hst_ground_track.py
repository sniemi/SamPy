# This tool will plot the HST ground tracks

from mpl_toolkits.basemap import Basemap
from pylab import *
from matplotlib.font_manager import FontProperties

import sys
import string, math
import ephem
import time_util
import spst_getopt

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
hst_start = ephem.Date(arg1.strftime("%Y/%m/%d %H:%M:%S"))
hst_stop  = ephem.Date(arg2.strftime("%Y/%m/%d %H:%M:%S"))
num_points = int((hst_stop - hst_start)/ephem.minute) + 1

# Read in the HST Two-Line ephemeris
#SMN suggestions
#import urllib2
#hand = urllib2.open('http://celestrak.com/NORAD/elements/science.txt')
#data = hand.readlines()
#hand.close()
#HST = [[d[val], d[val+1], d[val+2]] for val, line in enumerate(d) if 'HST' in line]
#hst = ephem.readtle(string.strip(HST[0][0]), string.strip(HST[0][1]), string.strip(HST[0][2]))
temp = open("/Users/niemi/Desktop/Misc/hst_new.tle","r").readlines()
hst = ephem.readtle(string.strip(temp[0]), \
                    string.strip(temp[1]), \
                    string.strip(temp[2]))
                    
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

lon_0 = 335
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
m.fillcontinents()
m.drawparallels(arange(-80,81,10),labels=[1,1,0,0],fontproperties=font1,labelstyle="+/-")
m.drawmeridians(arange(-180,180,20),labels=[0,0,0,1],fontproperties=font1,labelstyle="+/-")
#m.bluemarble()
m.drawmapboundary()

# SAA 02
x2,y2 = m([357.4-360,357.6-360,356.9-360,355.0-360,352.3-360,348.7-360,342.9-360,336.4-360,324.8-360,303.2-360,292.1-360,289.0-360,285.9-360,283.5-360,282.5-360,282.4-360,282.7-360,357.4-360], \
          [-28.3,-26.1,-23.7,-21.2,-18.8,-16.3,-13.0,-10.6, -9.1,-11.9,-14.9,-17.0,-19.1,-21.3,-23.7,-26.0,-28.6,-28.3])
# SAA 03
#x3,y3 = m([294.4-360,301.4-360,350.0-360,358.4-360,335.8-360,304.6-360,295.5-360,279.4-360,282.6-360,294.4-360], \
#          [-41.0,-42.8,-30.0,-20.9,-4.9,-4.9,-7.0,-21.9,-32.7,-41.0])
x3,y3 = m([ 20.0, 21.0, 19.0,  7.5,347.0-360,336.4-360,324.8-360,303.2-360,292.1-360,285.9-360,283.5-360,282.5-360,282.4-360,282.7-360, 20.0], \
          [-28.3,-27.5,-26.1,-19.8, -9.6, -7.6, -6.0, -7.9,-12.0,-17.1,-20.3,-23.5,-26.0,-28.6,-28.3])
# SAA 04
#x4,y4 = m([335.0-360,345.0-360,349.0-360,346.0-360,330.0-360,314.0-360,310.0-360,303.0-360,310.0-360,325.0-360,335.0-360], \
#          [-33.0,-27.0,-24.0,-23.0,-25.0,-30.0,-32.2,-39.0,-40.0,-37.0,-33.0])
x4,y4 = m([ 25.0,  7.0,351.0-360,341.0-360,318.0-360,300.0-360,290.0-360,284.0-360,278.0-360,273.0-360,275.0-360, 25.0], \
          [-28.5,-16.0, -6.5, -2.0,  1.0, -3.0, -7.0,-10.0,-15.0,-20.0,-30.0,-28.5])
# SAA 05,23
x5,y5 = m([300.0-360, 45.0, 40.0, 30.0, 10.0,  0.0,341.0-360,318.0-360,300.0-360,283.0-360,273.0-360,275.0-360,300.0-360], \
          [-50.0,-30.0,-25.0,-21.0,-15.0,-10.2, -2.0,  1.0, -3.0, -8.0,-20.0,-30.0,-50.0])
# SAA 06
#x6,y6 = m([359.0-360,360.0-360,335.4-360,323.0-360,290.0-360,280.0-360,276.0-360,280.0-360,359.0-360], \
#          [-28.0,-20.9,-3.4,-0.0,-7.0,-12.6,-20.9,-30.0,-28.0])
x6,y6 = m([ 20.0, 21.0, 19.0,  7.5,347.0-360,336.4-360,324.8-360,303.2-360,292.1-360,285.9-360,283.5-360,282.5-360,282.4-360,282.7-360, 20.0], \
          [-28.3,-27.5,-26.1,-19.8, -9.6, -7.6, -6.0, -7.9,-12.0,-17.1,-20.3,-23.5,-26.0,-28.6,-28.3])
# SAA 07
x7,y7 = m([300.0-360,359.0-360,5.0,341.0-360,318.0-360,300.0-360,283.0-360,273.0-360,275.0-360,300.0-360], \
          [-50.0,-41.0,-23.0,-2.0,1.0,-3.0,-8.0,-20.0,-30.0,-50.0])
# SAA 24,25,28,31,32
x24,y24=m([ 20.0, 21.0, 19.0,  7.5,347.0-360,336.4-360,324.8-360,303.2-360,292.1-360,285.9-360,283.5-360,282.5-360,282.4-360,282.7-360, 20.0], \
          [-28.3,-27.5,-26.1,-19.8, -9.6, -7.6, -6.0, -7.9,-12.0,-17.1,-20.3,-23.5,-26.0,-28.6,-28.3])
# SAA 26,27,29,30
x26,y26=m([ 25.0,  7.0,351.0-360,341.0-360,318.0-360,300.0-360,290.0-360,284.0-360,278.0-360,273.0-360,275.0-360, 25.0], \
          [-28.5,-16.0, -6.5, -2.0,  1.0, -3.0, -7.0,-10.0,-15.0,-20.0,-30.0,-28.5])
# HST observation ground track
xhst,yhst = m(hst_longs, hst_lats)

saa02 = m.plot(x2,y2,marker='D',markersize=4.0,markeredgewidth=0.0,color='red',linestyle='-',label='02')
saa03 = m.plot(x3,y3,marker='v',markersize=4.0,markeredgewidth=0.0,color='darkorchid',linestyle='-',label='03')
saa04 = m.plot(x4,y4,marker='^',markersize=4.0,markeredgewidth=0.0,color='maroon',linestyle='-',label='04')
saa05 = m.plot(x5,y5,marker='s',markersize=4.0,markeredgewidth=0.0,color='blue',linestyle='-',label='05')
saa06 = m.plot(x6,y6,marker='x',markersize=4.0,markeredgewidth=1.0,color='green',linestyle='-',label='06')
#saa07 = m.plot(x7,y7,marker='>',markersize=4.0,markeredgewidth=0.0,color='darkorchid',linestyle='-',label='07')
#saa24 = m.plot(x24,y24,marker='x',markersize=4.0,markeredgewidth=1.0,color='green',linestyle='-',label='24') 
#saa26 = m.plot(x26,y26,marker='^',markersize=4.0,markeredgewidth=0.0,color='maroon',linestyle='-',label='26')
hst   = m.plot(xhst,yhst,marker='+',markersize=4.0,markeredgewidth=0.5,color='black',linestyle='-',linewidth=0.3,label='hst')
hst_label = 'HST once per minute'
if (labelhst):
    hst_label = hst_label + ' (HH:MM)'
    for j in range(0, num_points):
        text(xhst[j],yhst[j],hst_text[j],fontsize=4,clip_on=True,horizontalalignment='left',verticalalignment='bottom')
    # end for j
# end if

font = p.copy()
font.set_size('xx-small')
leg=legend((saa02,saa03,saa04,saa05,saa06,hst), \
       ('PASS SAA Level 1 - FGS Guidance & STIS LV', \
        'PASS SAA Level 2 - STIS', \
        'PASS SAA Level 3 - ACS & WFC3', \
        'PASS SAA Level 4 - Astrometry & NICMOS', \
        'PASS SAA Level 5 - COS', \
        #'07 - GHRS', \
        #'24/25/31/32 - STIS CCD/STIS MAMA/COS FUV/COS NUV', \
        #'26/27/28/29/30 - WFPC2/ACS CCD/ACS SBC/WFC3 UVIS/WFC3 IR', \
        hst_label), \
       prop=font,numpoints=2,borderpad=0.3,loc='upper center',borderaxespad=0.0,ncol=2)
leg.get_frame().set_alpha(0.7)
#figlegend((saa02,saa05,saa24,saa26),('02','05','24','26'),'upper right')
# draw the title.
title('HST from %s to %s' % (str(arg1),str(arg2)))
show()
