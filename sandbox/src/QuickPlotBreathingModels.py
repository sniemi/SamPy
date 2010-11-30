'''
Created on Dec 30, 2009

@author: Sami-Matias Niemi (niemi@stsci.edu)
'''
import matplotlib
matplotlib.rc('xtick', labelsize=8)
import matplotlib.dates
import pylab as P
import numpy as N
import glob as G

def readData(file):
    JD = []
    focus = []
    for line in open(file).readlines():
        if 'Julian' in line:
            continue
        tmp = line.strip().split()
        JD.append(float(tmp[0]))
        focus.append(float(tmp[-1]))
        
    return JD, focus, file

def fromJulian(j):
    '''
    Converts Modified Julian days to human readable format
    @return: human readable date and time
    '''
    import datetime, time
    days = j - 40587 # From Jan 1 1900
    sec = days*86400.0
    return datetime.datetime(*time.gmtime(sec)[:7])

def plotData(JD, focus, filename):  
    fig = P.figure()
    ax = fig.gca()
    P.title(filename)
    time = [fromJulian(x) for x in JD]
    ax.plot_date(time, focus, 'bo', ls = '-', label = 'Flat Model value')
    try:
        P.legend(shadow = True, fancybox = True)
    except:
        P.legend()
    ax.set_ylabel('Flat Model')
   
    #Set major x ticks on Mondays.
    #ax.xaxis.set_major_locator(matplotlib.dates.WeekdayLocator(byweekday=matplotlib.dates.MO))
    ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%H:%M\n%a %d\n%b %y'))
    
    P.savefig(filename[:-4] + '.pdf')
    P.close()

for file in G.glob('plotdata*txt*'): plotData(*readData(file))

    


