'''
Adapted from Merle Reinhard's HST script.

http://stevendkay.wordpress.com/2009/10/12/scatter-plots-with-basemap-and-matplotlib/
'''
from mpl_toolkits.basemap import Basemap
from pylab import *
from matplotlib.font_manager import FontProperties
from matplotlib.collections import LineCollection
from matplotlib import cm
import sys
import string, math
import ephem
import time_util
import spst_getopt
import numpy as N
import pylab as P
import datetime as D

def toJulian(data):
    '''
    Converts to Modified Julian Date.
    '''
    return ephem.julian_date(data) - 2400000.5

def fromJulian(j):
    '''
    Converts Modified Julian days to human readable format
    @return: human readable date and time
    '''
    import time
    days = j - 40587 # From Jan 1 1900
    sec = days*86400.0
    return time.gmtime(sec)   
   
def padData(Data, hst_startMJD, hst_stopMJD):
    '''
    Resamples telemetry data to every second.
    Pads missing time stamps with the previous value
    if necessary.
    @todo: Remove unnecessary use of Python list that cosumes memory
    @return: 2-d NumPy array
    '''
    result = []

    delta = int((hst_stopMJD - hst_startMJD) * 24 * 60 * 60) #in seconds
    newtime = N.arange(delta + 1) / (24 * 60 * 60.) + hst_startMJD
    
    if hst_startMJD == Data['MJD'][0]:
        one_before = 0
    else:
        one_before = Data[Data['MJD'] <= hst_startMJD].shape[0] - 1
    
    if hst_stopMJD == Data['MJD'][-1]:
        one_after = -1
    else:
        one_after = Data[Data['MJD'] <= hst_stopMJD].shape[0] + 1
  
    before = Data['COUNTS'][one_before]
    after = Data['COUNTS'][one_after]

    limited = Data[(Data['MJD'] <= hst_stopMJD) & (Data['MJD'] >= hst_startMJD)]
  
    length = limited.shape[0]
    i = 0
    for x in newtime:
        if  i < length and i == 0 and x < limited['MJD'][i]:
            result.append((x, before))
        elif i < length and i > 0 and x < limited['MJD'][i]:
            result.append((x, limited['COUNTS'][i-1]))
        elif i == length:
            result.append((x, after))
        else:
            result.append((x, limited['COUNTS'][i]))
            i += 1
            
    return N.array(result, dtype = [('MJD', N.float64), ('COUNTS', N.float32)])
    
def plotCounts(FUVAevents, FUVBevents, FUVAhv, FUVBhv, MAMAevents, MAMAhv, hst_startMJD, hst_stopMJD):
    '''
    Changes the HV signs.
    '''
    fig = P.figure()
    left, width, height = 0.1, 0.8, 0.3
    rect1 = [left, 0.7, width, height]
    rect2 = [left, 0.4, width, height]
    rect3 = [left, 0.1, width, height]
    ax1 = fig.add_axes(rect1)  #left, bottom, width, height
    ax2 = fig.add_axes(rect2)
    ax3 = fig.add_axes(rect3)
    #FUVA subplot
#    ax1.plot(FUVAevents['MJD'], FUVAevents['COUNTS'],  ls = 'steps-', lw = 2, label = 'EVENTS')
#    ax1.plot(FUVAhv['MJD'], -FUVAhv['COUNTS'], ls = 'steps-', lw = 2, label = 'High Voltage')
    ax1.plot(FUVAevents['MJD'], FUVAevents['COUNTS'], ls = '-', lw = 2, label = 'EVENTS')
    ax1.plot(FUVAhv['MJD'], -FUVAhv['COUNTS'], ls = '-', lw = 2, label = 'High Voltage')

    #FUVB subplot
#    ax2.plot(FUVBevents['MJD'], FUVBevents['COUNTS'],  ls = 'steps-', lw = 2, label = 'EVENTS')
#    ax2.plot(FUVBhv['MJD'], -FUVBhv['COUNTS'], ls = 'steps-', lw = 2, label = 'High Voltage')
    ax2.plot(FUVBevents['MJD'], FUVBevents['COUNTS'], ls = '-', lw = 2, label = 'EVENTS')
    ax2.plot(FUVBhv['MJD'], -FUVBhv['COUNTS'], ls = '-', lw = 2, label = 'High Voltage')

    #MAM subplot
#    ax3.plot(MAMAevents['MJD'], MAMAevents['COUNTS'],  ls = 'steps-', lw = 2, label = 'EVENTS')
#    ax3.plot(MAMAhv['MJD'], -MAMAhv['COUNTS'], ls = 'steps-', lw = 2, label = 'High Voltage')
    ax3.plot(MAMAevents['MJD'], MAMAevents['COUNTS'], ls = '-', lw = 2, label = 'EVENTS')
    ax3.plot(MAMAhv['MJD'], -MAMAhv['COUNTS'], ls = '-', lw = 2, label = 'High Voltage')

    ax1.annotate('FUVA', xy = (0.1,0.8), xycoords='axes fraction', horizontalalignment='center', verticalalignment='center')
    ax2.annotate('FUVB', xy = (0.1,0.8), xycoords='axes fraction', horizontalalignment='center', verticalalignment='center')
    ax3.annotate('NUV', xy = (0.1,0.8), xycoords='axes fraction', horizontalalignment='center', verticalalignment='center')
    
    ax1.set_xticklabels([])
    ax2.set_xticklabels([])
        
    ax1.set_yscale('log')
    ax2.set_yscale('log')
    ax3.set_yscale('log')
    
    ax1.set_yticks(ax1.get_yticks()[1:-1])
    ax2.set_yticks(ax2.get_yticks()[1:-1])
    ax3.set_yticks(ax3.get_yticks()[1:-1])
    
    ax1.set_ylabel('COUNTS')
    ax2.set_ylabel('COUNTS')
    ax3.set_ylabel('COUNTS')
    ax1.set_xlabel('MJD')

    ax1.set_xlim(hst_startMJD, hst_stopMJD)
    ax2.set_xlim(hst_startMJD, hst_stopMJD)
    ax3.set_xlim(hst_startMJD, hst_stopMJD)
    
    ax3.set_ylim(5, 6000)
    
    #P.legend(shadow = True, fancybox = True)
    P.show()
    
def plotHSTtrack(hst_start, hst_stop, tlefile, ephemerisOnline = False):
    num_points = int((hst_stop - hst_start)/ephem.minute) + 1
    
    # Read in the HST Two-Line ephemeris
    if ephemerisOnline:
        import urllib2
        hand = urllib2.open('http://celestrak.com/NORAD/elements/science.txt')
        data = hand.readlines()
        hand.close()
        HST = [[d[val], d[val+1], d[val+2]] for val, line in enumerate(d) if 'HST' in line]
        hst = ephem.readtle(string.strip(HST[0][0]), string.strip(HST[0][1]), string.strip(HST[0][2]))
    else:
        temp = open(tlefile, 'r').readlines()
        hst = ephem.readtle(string.strip(temp[0]), string.strip(temp[1]), string.strip(temp[2]))
                        
    cur_time = hst_start
    
    hst_longs = []
    hst_lats  = []
    for i in range(0,num_points):
        hst.compute(cur_time)
        hst_longs.append(hst.sublong.znorm*180.0/math.pi)
        hst_lats.append(hst.sublat*180.0/math.pi)
        cur_time = cur_time + ephem.minute
    
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
    m = Basemap(resolution='c', projection='mbtfpq', lon_0=lon_0)
    #m = Basemap(resolution='c',projection='moll',lon_0=lon_0)
    #m = Basemap(resolution='c',projection='ortho',lon_0=lon_0,lat_0=lat_0)
    #m = Basemap(resolution='c',projection='cyl',llcrnrlat=llcrnrlat,llcrnrlon=llcrnrlon,urcrnrlat=urcrnrlat,urcrnrlon=urcrnrlon)
    
    p = FontProperties()
    font1 = p.copy()
    font1.set_size('small')
    
    # draw coasts and fill continents.
    m.drawcoastlines(linewidth = 0.5)
    #m.fillcontinents()
    
    m.drawparallels(arange(-80,81,10),labels=[1,1,0,0],fontproperties=font1,labelstyle="+/-")
    m.drawmeridians(arange(-180,180,20),labels=[0,0,0,1],fontproperties=font1,labelstyle="+/-")
    
    m.bluemarble()
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
    
    saa02 = m.plot(x2,y2,marker='D',markersize=4.0,markeredgewidth=0.0,color='turquoise',linestyle='-',label='02')
    saa03 = m.plot(x3,y3,marker='v',markersize=4.0,markeredgewidth=0.0,color='white',linestyle='-',label='03')
    saa04 = m.plot(x4,y4,marker='^',markersize=4.0,markeredgewidth=0.0,color='orange',linestyle='-',label='04')
    saa05 = m.plot(x5,y5,marker='s',markersize=4.0,markeredgewidth=0.0,color='green',linestyle='-',label='05')
    saa06 = m.plot(x6,y6,marker='x',markersize=4.0,markeredgewidth=1.0,color='magenta',linestyle='-',label='06')
    #saa07 = m.plot(x7,y7,marker='>',markersize=4.0,markeredgewidth=0.0,color='darkorchid',linestyle='-',label='07')
    #saa24 = m.plot(x24,y24,marker='x',markersize=4.0,markeredgewidth=1.0,color='green',linestyle='-',label='24') 
    #saa26 = m.plot(x26,y26,marker='^',markersize=4.0,markeredgewidth=0.0,color='maroon',linestyle='-',label='26')
    
    hst = m.plot(xhst,yhst,marker='+',markersize=4.0,markeredgewidth=1.0,color='red',linestyle='-',linewidth=0.7,label='hst')
    #SMN:
    #cnts must be sampled similar as xhst and yhst!
    #cs = m.contour(xhst,yhst,cnts,15,linewidths=1.5)
    
    hst_label = 'HST once per minute'
    
    font = p.copy()
    #font.set_size('xx-small')
    font.set_size('small')
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

def plotContoursOverHSTTrack(data, hst_start, hst_stop, tlefile, ephemerisOnline = False, SAA_zoomed = False, hold_on = False):
    num_points = int((hst_stop - hst_start)/ephem.minute) + 1
    
    # Read in the HST Two-Line ephemeris
    if ephemerisOnline:
        import urllib2
        hand = urllib2.open('http://celestrak.com/NORAD/elements/science.txt')
        data = hand.readlines()
        hand.close()
        HST = [[d[val], d[val+1], d[val+2]] for val, line in enumerate(d) if 'HST' in line]
        hst = ephem.readtle(string.strip(HST[0][0]), string.strip(HST[0][1]), string.strip(HST[0][2]))
    else:
        temp = open(tlefile, 'r').readlines()
        hst = ephem.readtle(string.strip(temp[0]), string.strip(temp[1]), string.strip(temp[2]))
                        
    cur_time = hst_start
    
    hst_longs = []
    hst_lats  = []
    for i in range(0,num_points):
        hst.compute(cur_time)
        hst_longs.append(hst.sublong.znorm*180.0/math.pi)
        hst_lats.append(hst.sublat*180.0/math.pi)
        cur_time = cur_time + ephem.minute
        
    hst_longs = N.array(hst_longs)
    hst_lats = N.array(hst_lats)
    
    #projection
    lon_0 = 335
    lat_0 = -20
    llcrnrlat = -60
    llcrnrlon = -100
    urcrnrlat = 20
    urcrnrlon = 60
    # use these values to setup Basemap instance.
    width  = 14000000
    height = 10000000
    
    #SAA
    if SAA_zoomed:
        m = Basemap(width = width, height = height, resolution = 'c', projection = 'aeqd', lat_0 = lat_0, lon_0 = lon_0)
        sz = 100
    else:
        m = Basemap(resolution='c', projection='mbtfpq', lon_0 = lon_0)
        sz = 35
    #OTHER PROJECTIONS    
    # crashed?
    #m = Basemap(resolution='c', projection='aeqd', lat_0 = lat_0, lon_0 = lon_0)
    # Full map, good
    #m = Basemap(resolution='c', projection='mbtfpq', lon_0 = lon_0)
    # Full map, diff projection
    #m = Basemap(resolution='c', projection='moll', lon_0 = lon_0)
    # Globe, SAA well presented
    #m = Basemap(resolution='c', projection='ortho', lon_0 = lon_0, lat_0 = lat_0)
    # Square, SAA well presented.
    #m = Basemap(resolution='c',projection='cyl',llcrnrlat=llcrnrlat,llcrnrlon=llcrnrlon,urcrnrlat=urcrnrlat,urcrnrlon=urcrnrlon)
    
    p = FontProperties()
    font1 = p.copy()
    font1.set_size('small')
    
    # draw coasts and fill continents.
    m.drawcoastlines(linewidth = 0.5)
    #m.fillcontinents()
    
    m.drawparallels(arange(-80,81,10),labels=[1,1,0,0],fontproperties=font1,labelstyle="+/-")
    m.drawmeridians(arange(-180,180,20),labels=[0,0,0,1],fontproperties=font1,labelstyle="+/-")
    
    m.bluemarble()
    m.drawmapboundary()
    
    # SAA 02
    x2,y2 = m([357.4-360,357.6-360,356.9-360,355.0-360,352.3-360,348.7-360,342.9-360,336.4-360,324.8-360,303.2-360,292.1-360,289.0-360,285.9-360,283.5-360,282.5-360,282.4-360,282.7-360,357.4-360], \
              [-28.3,-26.1,-23.7,-21.2,-18.8,-16.3,-13.0,-10.6, -9.1,-11.9,-14.9,-17.0,-19.1,-21.3,-23.7,-26.0,-28.6,-28.3])
    # SAA 03
    x3,y3 = m([ 20.0, 21.0, 19.0, 7.5,347.0-360,336.4-360,324.8-360,303.2-360,292.1-360,285.9-360,283.5-360,282.5-360,282.4-360,282.7-360, 20.0], \
              [-28.3,-27.5,-26.1,-19.8, -9.6, -7.6, -6.0, -7.9,-12.0,-17.1,-20.3,-23.5,-26.0,-28.6,-28.3])
    # SAA 04
    x4,y4 = m([ 25.0,  7.0,351.0-360,341.0-360,318.0-360,300.0-360,290.0-360,284.0-360,278.0-360,273.0-360,275.0-360, 25.0], \
              [-28.5,-16.0, -6.5, -2.0,  1.0, -3.0, -7.0,-10.0,-15.0,-20.0,-30.0,-28.5])
    # SAA 05,23
    x5,y5 = m([300.0-360, 45.0, 40.0, 30.0, 10.0, 0.0,341.0-360,318.0-360,300.0-360,283.0-360,273.0-360,275.0-360,300.0-360], \
              [-50.0,-30.0,-25.0,-21.0,-15.0,-10.2, -2.0,  1.0, -3.0, -8.0,-20.0,-30.0,-50.0])
    # SAA 06
    x6,y6 = m([ 20.0, 21.0, 19.0, 7.5,347.0-360,336.4-360,324.8-360,303.2-360,292.1-360,285.9-360,283.5-360,282.5-360,282.4-360,282.7-360, 20.0], \
              [-28.3,-27.5,-26.1,-19.8, -9.6, -7.6, -6.0, -7.9,-12.0,-17.1,-20.3,-23.5,-26.0,-28.6,-28.3])

    #SAA
    saa02 = m.plot(x2,y2,marker='D',markersize=4.0,markeredgewidth=0.0,color='turquoise',linestyle='-',label='02')
    saa03 = m.plot(x3,y3,marker='v',markersize=4.0,markeredgewidth=0.0,color='white',linestyle='-',label='03')
    saa04 = m.plot(x4,y4,marker='^',markersize=4.0,markeredgewidth=0.0,color='orange',linestyle='-',label='04')
    saa05 = m.plot(x5,y5,marker='s',markersize=4.0,markeredgewidth=0.0,color='green',linestyle='-',label='05')
    saa06 = m.plot(x6,y6,marker='x',markersize=4.0,markeredgewidth=1.0,color='magenta',linestyle='-',label='06')
    
    # HST observation ground track
    xhst, yhst = m(hst_longs, hst_lats)    
    #hst = m.plot(xhst,yhst,marker='+',markersize=4.0,markeredgewidth=1.0,color='red',linestyle='-',linewidth=0.7,label='hst')
    
    #scatter plot
    if hold_on:
        scatter = m.scatter(xhst[:-1], yhst[:-1], s = sz, c = data, cmap = cm.jet, linestyle = 'solid', zorder = 11, hold = 'on')
    else:
        fig = P.figure(1)
        points = N.array([xhst, yhst]).T.reshape(-1, 1, 2)
        segments = N.concatenate([points[:-1], points[1:]], axis=1)
        ax = P.axes()
        lc = LineCollection(segments, cmap = P.get_cmap('jet'), norm = P.Normalize(0, 10000))
        lc.set_array(data)
        lc.set_linewidth(5)
        
        ax.add_collection(lc)
        
        axcb = fig.colorbar(lc)
        axcb.set_label('EVENTS')

    #contour plot
    #cs = m.contour(xhst, yhst, data, 15, linewidths = 1.5)    
    #mx = N.max(data)
    #cbar = map.colorbar(s, ticks=[N.max(data), mx//2., mx], orientation='vertical')
    
    hst_label = 'HST once per minute'
    
    font = p.copy()
    #font.set_size('xx-small')
    font.set_size('small')
    leg=legend((saa02,saa03,saa04,saa05,saa06,hst), \
           ('PASS SAA Level 1 - FGS Guidance & STIS LV', \
            'PASS SAA Level 2 - STIS', \
            'PASS SAA Level 3 - ACS & WFC3', \
            'PASS SAA Level 4 - Astrometry & NICMOS', \
            'PASS SAA Level 5 - COS', \
            hst_label), \
           prop=font,numpoints=2,borderpad=0.3,loc='upper center',borderaxespad=0.0,ncol=2)
    leg.get_frame().set_alpha(0.7)
    # draw the title.
    P.title('HST from %s to %s' % (str(arg1),str(arg2)))
    
    if hold_on == False: P.show()
    
def countEvents(eventsData, hvData, hvlow, hvhigh, sampling):
    '''
    Counts EVENTS. Will prioritize eventsData over hvData ie
    time stamps in eventsData have more weight compared to
    time stamps in hvData. Sampling is not taken into account
    at this point. Should be added to be used for NUV data correctly.
    
    The algorithm is a little flacky and should be maybe rewritten
    as it is not the fastest.
    '''
    results = 0

    #Check the MJD interval common for both, but selects
    #the earlier time .
    if eventsData['MJD'][0] < hvData['MJD'][0]:
        minMJD = eventsData['MJD'][0]
    else:
        minMJD = hvData['MJD'][0]
        
    if eventsData['MJD'][-1] > hvData['MJD'][-1]:
        maxMJD = hvData['MJD'][-1]
    else:
        maxMJD = eventsData['MJD'][-1]
        
    #newtime vector has a timestamp for each second
    delta = int((maxMJD - minMJD) * 24 * 60 * 60) #in seconds
    newtime = N.arange(delta + 1) / (24 * 60 * 60.) + minMJD
 
    i = 0
    j = 0
    length_i = eventsData['MJD'].shape[0]
    length_j = hvData['MJD'].shape[0]

    #algorithm to count EVENTS from unevenly spaced data
    for x in newtime:
        if  i == 0 and x < eventsData['MJD'][0]:
            if j == 0 and x < hvData['MJD'][0]:
                if hvData['COUNTS'][0] > hvlow and hvData['COUNTS'][0] < hvhigh:
                    results += eventsData['COUNTS'][0]
            elif x < hvData['MJD'][j] and j > 0:
                if hvData['COUNTS'][j-1] > hvlow and hvData['COUNTS'][j-1] < hvhigh:
                    results += eventsData['COUNTS'][0]
            elif x == hvData['MJD'][j]:
                if hvData['COUNTS'][j] > hvlow and hvData['COUNTS'][j] < hvhigh:
                    results += eventsData['COUNTS'][0]
                j += 1
            else:
                j += 1
                if j < length_j:
                    if hvData['COUNTS'][j] > hvlow and hvData['COUNTS'][j] < hvhigh:
                        results += eventsData['COUNTS'][0]
                else:
                    if hvData['COUNTS'][-1] > hvlow and hvData['COUNTS'][-1] < hvhigh:
                        results += eventsData['COUNTS'][0]
        elif i < length_i and x < eventsData['MJD'][i]:
            if j == 0 and x < hvData['MJD'][0]:
                if hvData['COUNTS'][0] > hvlow and hvData['COUNTS'][0] < hvhigh:
                    results += eventsData['COUNTS'][i-1]
            elif x < hvData['MJD'][j] and j > 0:
                if hvData['COUNTS'][j-1] > hvlow and hvData['COUNTS'][j-1] < hvhigh:
                    results += eventsData['COUNTS'][i-1]
            elif x == hvData['MJD'][j]:
                if hvData['COUNTS'][j] > hvlow and hvData['COUNTS'][j] < hvhigh:
                    results += eventsData['COUNTS'][i-1]
                j += 1
            else:
                j += 1
                if j < length_j:
                    if hvData['COUNTS'][j] > hvlow and hvData['COUNTS'][j] < hvhigh:
                        results += eventsData['COUNTS'][i-1]
                else:
                    if hvData['COUNTS'][-1] > hvlow and hvData['COUNTS'][-1] < hvhigh:
                        results += eventsData['COUNTS'][i-1]
        elif i < length_i and x == eventsData['MJD'][i]:
            if j == 0 and x < hvData['MJD'][0]:
                if hvData['COUNTS'][0] > hvlow and hvData['COUNTS'][0] < hvhigh:
                    results += eventsData['COUNTS'][i]
            elif x < hvData['MJD'][j] and j > 0:
                if hvData['COUNTS'][j-1] > hvlow and hvData['COUNTS'][j-1] < hvhigh:
                    results += eventsData['COUNTS'][i]
            elif x == hvData['MJD'][j]:
                if hvData['COUNTS'][j] > hvlow and hvData['COUNTS'][j] < hvhigh:
                    results += eventsData['COUNTS'][i]
                j += 1
            else:
                j += 1
                if j < length_j:
                    if hvData['COUNTS'][j] > hvlow and hvData['COUNTS'][j] < hvhigh:
                        results += eventsData['COUNTS'][i]
                else:
                    if hvData['COUNTS'][-1] > hvlow and hvData['COUNTS'][-1] < hvhigh:
                        results += eventsData['COUNTS'][i]
            i += 1
        else:
            if j == 0 and x < hvData['MJD'][0]:
                if hvData['COUNTS'][0] > hvlow and hvData['COUNTS'][0] < hvhigh:
                    results += eventsData['COUNTS'][i]
            elif x < hvData['MJD'][j] and j > 0:
                if hvData['COUNTS'][j-1] > hvlow and hvData['COUNTS'][j-1] < hvhigh:
                    results += eventsData['COUNTS'][i]
            elif x == hvData['MJD'][j]:
                if hvData['COUNTS'][j] > hvlow and hvData['COUNTS'][j] < hvhigh:
                    results += eventsData['COUNTS'][i]
                j += 1
            else:
                j += 1
                if j < length_j:
                    if hvData['COUNTS'][j] > hvlow and hvData['COUNTS'][j] < hvhigh:
                        results += eventsData['COUNTS'][i]
                else:
                    if hvData['COUNTS'][-1] > hvlow and hvData['COUNTS'][-1] < hvhigh:
                        results += eventsData['COUNTS'][i]
            i += 1
                  
    return results

    
def Bin(data, column, to_sample):
    result = []
    a = 0

    max = len(data[column])
    ran = max / to_sample
    
    for i in range(ran):
        if (i+1)*to_sample < max:
            result.append(N.sum(data[column][a:(i+1)*to_sample]))
            a = (i+1)*to_sample
        else:
            result.append(N.sum(data[column][a:-1]))
    
    return N.array(result)

if __name__ == '__main__':
    FUVsize = 16384*1024.
    MAMAsize = 1024*1024.
    FUVhvlow = -4135
    FUVhvhigh = -3985
    MAMAhvlow = -1825
    MAMAhvhigh = -1675
    
    TotalEvents = False #True
    calculateEvents = False #True
    
    #hard coded values and names
    startdate = '2010.178:01:30:00' 
    stopdate = '2010.178:04:00:00'
    telepath = '/smov/cos/housekeeping/Telemetry/'  # PATH
    FUVAevents = 'LDCEFECA'                         # FUVA
    FUVBevents = 'LDCEFECB'                         # FUVB
    events = 'LMEVENTS'                             # MAMA
    FUVAhv = 'LDCHVMNA'
    FUVBhv = 'LDCHVMNB'
    cmpv = 'LMMCPV'
    tlefile = '/Users/niemi/Desktop/Misc/hst_new.tle'
    ephemerisOnline = True
    
    #telemetry data files
    #FUV
    FUVAcountsfile = telepath + FUVAevents
    FUVBcountsfile = telepath + FUVBevents
    FUVAhvfile = telepath + FUVAhv
    FUVBhvfile = telepath + FUVBhv
    #MAMA
    lmeventsfile = telepath + events #EVENTS
    lmmcpvfile = telepath + cmpv     #HV
    
    #Time manipulations
    arg1 = time_util.spss_time(startdate)
    arg2 = time_util.spss_time(stopdate)
    hst_start = ephem.Date(arg1.strftime("%Y/%m/%d %H:%M:%S"))
    hst_stop  = ephem.Date(arg2.strftime("%Y/%m/%d %H:%M:%S"))
    hst_startMJD = toJulian(hst_start)
    hst_stopMJD = toJulian(hst_stop)        
    #read the telemetry data in
    #FUV
    FUVAeventsData = N.loadtxt(FUVAcountsfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8','f4')})
    FUVBeventsData = N.loadtxt(FUVBcountsfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8','f4')})
    FUVAhvData = N.loadtxt(FUVAhvfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8', 'f4')})
    FUVBhvData = N.loadtxt(FUVBhvfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8', 'f4')})
    #MAMA
    MAMAeventsData = N.loadtxt(lmeventsfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8','f4')})
    MAMAhvData = N.loadtxt(lmmcpvfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8', 'f4')})
    
    if calculateEvents:        
        FUVA = countEvents(FUVAeventsData, FUVAhvData, FUVhvlow, FUVhvhigh, 10)
        print '\nThe total number of events at HV-LOW (%0.f <= HV <= %0.f) for FUVA:' % (FUVhvlow, FUVhvhigh)
        print '%.0f' % FUVA
        print 'and per pixel'
        print '%.0f' % (FUVA / FUVsize)
        
        FUVB = countEvents(FUVBeventsData, FUVBhvData, FUVhvlow, FUVhvhigh, 10)
        print '\nThe total number of events at HV-LOW (%0.f <= HV <= %0.f) for FUVB:' % (FUVhvlow, FUVhvhigh)
        print '%.0f' % FUVB
        print 'and per pixel'
        print '%.0f' % (FUVB / FUVsize)
        
        MAMA = countEvents(MAMAeventsData, MAMAhvData, MAMAhvlow, MAMAhvhigh, 60)
        print '\nThe total number of events at HV-LOW (%0.f <= HV <= %0.f) for MAMA:' % (MAMAhvlow, MAMAhvhigh)
        print '%.0f' % MAMA
        print 'and per pixel'
        print '%.0f' % (MAMA / FUVsize)
        
        #with other limits
        FUVhvlow = -14135
        FUVhvhigh = -985
        MAMAhvlow = -11825
        MAMAhvhigh = -675
        
        FUVA = countEvents(FUVAeventsData, FUVAhvData, FUVhvlow, FUVhvhigh, 10)
        print '\nThe total number of events at %0.f <= HV <= %0.f for FUVA:' % (FUVhvlow, FUVhvhigh)
        print '%.0f' % FUVA
        print 'and per pixel'
        print '%.0f' % (FUVA / FUVsize)
        
        FUVB = countEvents(FUVBeventsData, FUVBhvData, FUVhvlow, FUVhvhigh, 10)
        print '\nThe total number of events at %0.f <= HV <= %0.f for FUVB:' % (FUVhvlow, FUVhvhigh)
        print '%.0f' % FUVB
        print 'and per pixel'
        print '%.0f' % (FUVB / FUVsize)
        
        MAMA = countEvents(MAMAeventsData, MAMAhvData, MAMAhvlow, MAMAhvhigh, 60)
        print '\nThe total number of events at %0.f <= HV <= %0.f for MAMA:' % (MAMAhvlow, MAMAhvhigh)
        print '%.0f' % MAMA
        print 'and per pixel'
        print '%.0f' % (MAMA / FUVsize)

    if TotalEvents:        
        print '\nThe total number of telemetry measurements (only changes count) for'
        print 'FUVA %0.f' % FUVAeventsData.shape[0]
        print 'FUVB %0.f' % FUVBeventsData.shape[0]
        print 'MAMA %0.f' % MAMAeventsData.shape[0]
        
        #Total counts
        minFUVAMJD = N.min(FUVAeventsData['MJD'])
        maxFUVAMJD = N.max(FUVAeventsData['MJD'])
        paddedFUVAevents = padData(FUVAeventsData, minFUVAMJD, maxFUVAMJD)
        sumFUVAevents = N.sum(paddedFUVAevents['COUNTS'])
        print '\nThe total event counts in the FUVA telemetry data (between %f and %f MJD)' % (minFUVAMJD, maxFUVAMJD)
        print 'between %s and %s' % (D.datetime(*fromJulian(minFUVAMJD)[0:6]).strftime('%A %d, %B, %Y (%H:%M%Z)'),
                                           D.datetime(*fromJulian(maxFUVAMJD)[0:6]).strftime('%A %d, %B, %Y (%H:%M%Z)'))
        print '%.0f' % sumFUVAevents
        print 'and per pixel'
        print  '%.0f' % (sumFUVAevents / FUVsize)
        
        minFUVBMJD = N.min(FUVBeventsData['MJD'])
        maxFUVBMJD = N.max(FUVBeventsData['MJD'])
        paddedFUVBevents = padData(FUVBeventsData, minFUVBMJD, maxFUVBMJD)
        sumFUVBevents = N.sum(paddedFUVBevents['COUNTS'])
        print '\nThe total event counts in the FUVB telemetry data (between %f and %f MJD)' % (minFUVBMJD, maxFUVBMJD)
        print 'between %s and %s' % (D.datetime(*fromJulian(minFUVBMJD)[0:6]).strftime('%A %d, %B, %Y (%H:%M%Z)'),
                                           D.datetime(*fromJulian(maxFUVBMJD)[0:6]).strftime('%A %d, %B, %Y (%H:%M%Z)'))
        print '%.0f' % sumFUVBevents
        print 'and per pixel'
        print  '%.0f' % (sumFUVBevents / FUVsize)
        
        minMAMAMJD = N.min(MAMAeventsData['MJD'])
        maxMAMAMJD = N.max(MAMAeventsData['MJD'])
        paddedMAMAevents = padData(MAMAeventsData, minMAMAMJD, maxMAMAMJD)
        sumMAMAevents = N.sum(paddedMAMAevents['COUNTS'])
        print '\nThe total event counts in the MAMA telemetry data (between %f and %f MJD)' % (minMAMAMJD, maxMAMAMJD)
        print 'between %s and %s' % (D.datetime(*fromJulian(minMAMAMJD)[0:6]).strftime('%A %d, %B, %Y (%H:%M%Z)'),
                                           D.datetime(*fromJulian(maxMAMAMJD)[0:6]).strftime('%A %d, %B, %Y (%H:%M%Z)'))
        print '%.0f' % sumMAMAevents
        print 'and per pixel'
        print  '%.0f' % (sumMAMAevents / MAMAsize)
    

    #telemetry between the plotted dates
    #FUV
    print '\nStart and Stop MJDs:', hst_startMJD, hst_stopMJD 
    FUVAevents = padData(FUVAeventsData, hst_startMJD, hst_stopMJD)  
    FUVBevents = padData(FUVBeventsData, hst_startMJD, hst_stopMJD)
    FUVAhv = padData(FUVAhvData, hst_startMJD, hst_stopMJD)
    FUVBhv = padData(FUVBhvData, hst_startMJD, hst_stopMJD)
    print 'Number of FUV Telemetry points measured:', FUVAevents.shape[0]
    #MAMA
    MAMAevents = padData(MAMAeventsData, hst_startMJD, hst_stopMJD)
    MAMAhv = padData(MAMAhvData, hst_startMJD, hst_stopMJD)
    print 'Number of MAMA Telemetry points measured:', MAMAevents.shape[0]
    
    #plot counts vs. time
    plotCounts(FUVAevents, FUVBevents, FUVAhv, FUVBhv, MAMAevents, MAMAhv, hst_startMJD, hst_stopMJD)
    
    #Bin data to 60 second bins
    FUVA60cnts = Bin(FUVAevents, 'COUNTS', 60)
    FUVB60cnts = Bin(FUVBevents, 'COUNTS', 60)
    MAMA60cnts = Bin(MAMAevents, 'COUNTS', 60)
    
    print 'Total counts for FUVA, B, and MAMA:'
    print N.sum(FUVA60cnts), N.sum(FUVB60cnts), N.sum(MAMA60cnts)

    #make HST track plot
    #print 'Will plot HST ground tracks'
    #plotHSTtrack(hst_start, hst_stop, tlefile)
    
    #Overplot counts
    print 'Will plot FUV counts'
    plotContoursOverHSTTrack(FUVA60cnts+FUVB60cnts, hst_start, hst_stop, tlefile, ephemerisOnline, SAA_zoomed = True)
    plotContoursOverHSTTrack(FUVA60cnts+FUVB60cnts, hst_start, hst_stop, tlefile, ephemerisOnline)

    print 'Will plot MAMA counts'
    plotContoursOverHSTTrack(MAMA60cnts, hst_start, hst_stop, tlefile, ephemerisOnline, SAA_zoomed = True)
    plotContoursOverHSTTrack(MAMA60cnts, hst_start, hst_stop, tlefile, ephemerisOnline)
    
    #plot many tracks:
    for i in range(11,30):
        startdate = '2010.0%i:00:00:00' % i
        #stopdate = '2010.0%i:23:59:59' % i
        stopdate = '2010.0%i:06:00:0' % i
    
        arg1 = time_util.spss_time(startdate)
        arg2 = time_util.spss_time(stopdate)
        hst_start = ephem.Date(arg1.strftime("%Y/%m/%d %H:%M:%S"))
        hst_stop  = ephem.Date(arg2.strftime("%Y/%m/%d %H:%M:%S"))
        hst_startMJD = toJulian(hst_start)
        hst_stopMJD = toJulian(hst_stop)
        print 'Start and Stop MJDs:', hst_startMJD, hst_stopMJD 
            
        #read the telemetry data in
        #FUV
        FUVAeventsData = N.loadtxt(FUVAcountsfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8','f4')})
        FUVBeventsData = N.loadtxt(FUVBcountsfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8','f4')})
        FUVAhvData = N.loadtxt(FUVAhvfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8', 'f4')})
        FUVBhvData = N.loadtxt(FUVBhvfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8', 'f4')})
        #MAMA
        MAMAeventsData = N.loadtxt(lmeventsfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8','f4')})
        MAMAhvData = N.loadtxt(lmmcpvfile, dtype={'names': ('MJD', 'COUNTS'), 'formats' : ('f8', 'f4')})
    
        #telemetry between the plotted dates
        #FUV
        FUVAevents = padData(FUVAeventsData, hst_startMJD, hst_stopMJD)  
        FUVBevents = padData(FUVBeventsData, hst_startMJD, hst_stopMJD)
        FUVAhv = padData(FUVAhvData, hst_startMJD, hst_stopMJD)
        FUVBhv = padData(FUVBhvData, hst_startMJD, hst_stopMJD)
        print 'Number of FUV Telemetry points measured:', FUVAevents.shape[0]
        #MAMA
        MAMAevents = padData(MAMAeventsData, hst_startMJD, hst_stopMJD)
        MAMAhv = padData(MAMAhvData, hst_startMJD, hst_stopMJD)
        print 'Number of MAMA Telemetry points measured:', MAMAevents.shape[0]
        
        #plot counts vs time
        #plotCounts(FUVAevents, FUVBevents, FUVAhv, FUVBhv, MAMAevents, MAMAhv, hst_startMJD, hst_stopMJD)
        
        FUVA60cnts = Bin(FUVAevents, 'COUNTS', 60)
        FUVB60cnts = Bin(FUVBevents, 'COUNTS', 60)
        MAMA60cnts = Bin(MAMAevents, 'COUNTS', 60)
        
        print 'Total counts for FUVA, B, and MAMA:'
        print N.sum(FUVA60cnts), N.sum(FUVB60cnts), N.sum(MAMA60cnts)
    
        plotContoursOverHSTTrack(FUVA60cnts+FUVB60cnts, hst_start, hst_stop, tlefile, ephemerisOnline, hold_on = True)
    
    P.show()
