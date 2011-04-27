'''
DESCRIPTION:
Creates few different plots from the focus data.

USAGE:
python focusPlots.py

HISTORY:
Created on Sep 10, 2009
Added to the repository on Dec 3, 2010

:author: Sami-Matias Niemi

:todo:
1) change focus trend since mirror move to two x axis mode (one with date)
2) Create a new plot: all focus data since last mirror move, fit functions

'''
import matplotlib
matplotlib.rc('text', usetex = True)
matplotlib.rc('xtick', labelsize=9) 
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rc('lines', markeredgewidth=2.0)
matplotlib.rcParams['lines.linewidth'] = 2.5
matplotlib.rcParams['legend.fontsize'] = 10
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
matplotlib.rcParams['legend.shadow'] = True
matplotlib.rcParams['legend.fancybox'] = True
matplotlib.rcParams['legend.numpoints'] = 1
matplotlib.use('PDF')
from matplotlib.ticker import MultipleLocator, FormatStrFormatter, NullFormatter
from matplotlib.dates import YearLocator, MonthLocator, DateFormatter 
import pylab as P
import numpy as N
import scipy as S
import datetime as D
import time
import scipy
import scipy.optimize
import numpy.core.defchararray as npstr
#From Sami's repository
import dates.julians as j
import focus.HSTfocus as h
import fitting.fits as f
    

__author__ = 'Sami-Matias Niemi'
__version__ = '1.9'

def findMaxAndPair(data):
    maxa = data[0][0]
    corb = data[0][1]
    for a, b in data:
        if a > maxa:
            maxa = a
            corb = b
    return maxa, corb

def FocusTrendNoBreathing(xmin, xmax, title, type, 
                          input_folder, output_folder,
                          output = 'FocusTrend'):
    '''
    Plots Focus trend since given minimum J-L date (mxin).
    Uses data that has not been breathing corrected.
    xmax is used to limit the fit.
    '''
    data = N.loadtxt(input_folder + 'AllData.txt', skiprows=1,
                     dtype={'names': ('Obs', 'Date', 'MJDate', 'Focus', 'Error'),
                            'formats':('S12','S12','i4','f4','f4')})

    #mirror movements
    mirrorM = h.MirrorMovesInHSTTime()

    #manipulatges the date
    shiftdate = data['MJDate'] - 48005.0
    focus = data['Focus']
    err = data['Error']
    
    #last mirror move date
    lastdate = -999999999

    #creates the step function and fixes the focus by each step
    cfocus = focus + 95.*(shiftdate < 1348)
    step = 95.*(shiftdate < 1353)
    for date, movement in mirrorM:
        #does not use the latest!
        if movement != 2.97:
            step += movement*(shiftdate < date)
            cfocus += movement*(shiftdate < date)
        else:
            lastdate = date  

    #double exponential fitting
    #desorpdays = N.arange(0, endday, 1)
    #SMdesorp = -6.0434 + 56.2568*N.exp(-desorpdays/364.5247)+106.2362*N.exp(-desorpdays/2237.2268) # RvdM
    #SMdesorp2 = -8.3914 + 52.9418 *N.exp(-desorpdays*0.002505)+97.6542*N.exp(-desorpdays*0.000395) # CC
    #p = [-6.05, 56.0, 365., 100., 2240.]
    #expo, params = FitDoubleExponent(shiftdate, cfocus, p)
    #expoExt = params[0] + params[1]*N.exp(-desorpdays/params[2]) + params[3]*N.exp(-desorpdays/params[4])
    
    x = shiftdate[(shiftdate > xmin) & (shiftdate < xmax)]
    y = cfocus[(shiftdate > xmin) & (shiftdate < xmax)]

    maxvalue = int(N.max(shiftdate))
    
    #fit line
    fitted, error = f.PolyFit(y, x)
    
    #fit exponential fitexp = -6.16 + 201.64*exp(-days*0.000570)
    p = [-6.16, 201.64, 0.000570]
    expo, params = f.FitExponent(x, y, p)

    #calculate the zero crossing
    #WFCnom = 1.3
    #ytmp = (params[0] + params[1]*S.exp(-7100*params[2]))
    #print ytmp, params[0]
    #tmp = -WFCnom - 2.97 + ytmp
    #zeroc = N.log((tmp - params[0])/params[1])/params[2]
    #print 'Zero crossing in %f days after 7100 day' % -zeroc

    #make the plot
    ax = P.subplot(111)
    P.title(title)

    #zero focus line
    ax.axhline(y = 0, ls='--', lw = 1., c = 'k')

    #mirror moves
    mirrorM = h.MirrorMovesInHSTTime()
    for time, movement in mirrorM:
        ax.axvline(x = time, ymin = -10, ymax = 3, lw = 1.1, ls=':', c = 'k')
        ax.annotate(s = str(movement) + '$\mu m$', xy= (time+40, min(y)-1.5),
                    rotation = 90, horizontalalignment='center',
                    verticalalignment='center', size = 'small')  
    ax.axvline(x = mirrorM[-1][0], ymin = -10, ymax = 3, lw = 1.1, ls=':',
               c = 'k', label='Mirror Movement')
    
    #plot data
    ax.errorbar(shiftdate, cfocus, yerr = err, marker = 'o', color = 'blue',
                ms = 4, ls = 'None', ecolor = None, mew = 0.4,
                label='No Breathing correction (other SIs)',
                capsize = 2, elinewidth = 0.8, zorder = 10)
    tmp1 = [a for a, b in zip(shiftdate, data['Obs']) if b.startswith('i')]
    tmp2 = [a for a, b in zip(cfocus, data['Obs']) if b.startswith('i')]
    tmp3 = [a for a, b in zip(err, data['Obs']) if b.startswith('i')]
    ax.errorbar(tmp1, tmp2, yerr = tmp3, marker = 'D', color = 'magenta',
                ms = 4.1, ls = 'None', ecolor = None, mew = 0.4,
                label='No Breathing correction (WFC3 UVIS)',
                capsize = 2, elinewidth = 0.8, zorder = 10)
    
    # plot fits
    a = (fitted[2] - fitted[1]) / (x[2] - x[1])
    k = N.arange(xmin, maxvalue)*a
    interp = fitted[-1] - x[-1]*a
    ax.plot(N.arange(xmin, maxvalue)[(N.arange(xmin, maxvalue) <= lastdate)], 
            k[N.arange(xmin, maxvalue) <= lastdate] + interp, lw = 1,
            label='Linear Regression', c = 'g')
    #ax.plot(shiftdate, params[0] + params[1]*S.exp(-shiftdate*params[2]), lw = 1, label='Exponent Fit', c = 'r')
    
    #discontinued xrange
    newxrange = 1 + lastdate + N.arange(maxvalue - lastdate + 150)
    ax.plot(x, expo, lw = 2, label='Exponent Fit', c = 'r')
    ax.plot(newxrange, 2.97 + params[0] + params[1]*S.exp(-newxrange*params[2]),
            'r--', lw = 2, label='Exponent Fit Cont.', zorder = 11)

    ax.set_xlabel('Days since HST deployment')
    ax.set_ylabel('Accumulated Defocus $[SM \mu m]$')  
    
    #minor ticks
    xmajorLocator = MultipleLocator(500)
    xminorLocator = MultipleLocator(100)
    xmajorFormattor = FormatStrFormatter('%i')
    xminorFormattor = NullFormatter()
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.xaxis.set_major_formatter(xmajorFormattor)
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    #y
    ymajorLocator = MultipleLocator(5)
    yminorLocator = MultipleLocator(1)
    ymajorFormattor = FormatStrFormatter('%i')
    yminorFormattor = NullFormatter()
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_major_formatter(ymajorFormattor)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)

    ax.set_xlim(xmin - 10, N.max(newxrange) + 80)
    ax.set_ylim(min(y)-3, max(y)+2)
    
    try:
        P.legend(scatterpoints = 1, numpoints = 1)
    except:
        P.legend()
    
    P.savefig(output_folder + output + type)
    P.close()

def FocusTrend(xmin, xmax, title, type, 
               input_folder, output_folder,
               output = 'FocusTrend'):
    '''
    Plots Focus trend since given minimum J-L date (mxin).
    xmax is used to limit the fit.
    '''
    file = 'BreathingCorrectedData.txt'
    
    data = N.loadtxt(input_folder + file, skiprows=1,
                     dtype={'names': ('Julian', 'J-L', 'Focus', 'Error', 'Camera'),
                            'formats':('i4','i4','f4','f4','S8')})    
    sorted = N.sort(data, order=['J-L', 'Focus'])

    limited = sorted[(sorted['J-L'] > xmin) & (sorted['J-L'] < xmax)]
    x = limited['J-L']
    y = limited['Focus']
    
    maxvalue = N.max(data['J-L'])
    
    #fit line
    fitted, error = f.PolyFit(y, x)
    
    #fit exponential fitexp = -6.16 + 201.64*exp(-days*0.000570)
    p = [-6.16, 201.64, 0.000570]
    expo, params = f.FitExponent(x, y, p)
#    print 'Breathing corrected signle exponent of form (y = A + B*exp(-days*C):'
#    print params

    ax = P.subplot(111)
    P.title(title)

#    P.annotate('y = %f + %f*exp(-days*%f)' % (params[0], params[1], params[2]),
#                   xy = (0.5, 0.01),
#                   horizontalalignment='center',
#                   verticalalignment='center',
#                   xycoords='figure fraction')

    #zero focus line
    ax.axhline(y = 0, ls='--', lw = 1., c = 'k')

    #mirror moves
    mirrorM = h.MirrorMovesInHSTTime()
    for time, movement in mirrorM:
        ax.axvline(x = time, ymin = -10, ymax = 3, lw = 1.1, ls=':', c = 'k')
        ax.annotate(s = str(movement) + '$\mu$m', xy= (time+40, min(y)-1.5),
                    rotation = 90,
                    horizontalalignment='center', verticalalignment='center',
                    size = 'small')  
    ax.axvline(x = mirrorM[-1][0], ymin = -10, ymax = 3, lw = 1.1, ls=':',
               c = 'k', label='Mirror Movement')
    
    #plot data
    ax.errorbar(data['J-L'], data['Focus'], yerr = data['Error'], marker = 'o',
                color = 'blue', ms = 4, ls = 'None',
                ecolor = None, mew = 0.4, label='Breathing corrected (other SIs)',
                capsize = 2, elinewidth = 0.8, zorder = 10)
    ax.errorbar(data['J-L'][data['Camera'] == 'WFC3'],
                data['Focus'][data['Camera'] == 'WFC3'], 
                yerr = data['Error'][data['Camera'] == 'WFC3'],
                marker = 'D', color = 'magenta', ms = 4, ls = 'None',
                ecolor = None, mew = 0.4, label='Breathing corrected  (WFC3 UVIS)',
                capsize = 2.1, elinewidth = 0.8, zorder = 10)
    # plot fits
    a = (fitted[2] - fitted[1]) / (x[2] - x[1])
    k = N.arange(xmin, maxvalue)*a
    interp = fitted[-1] - x[-1]*a
    
    #discontinued xrange
    newxrange = 2 + N.max(limited['J-L']) + N.arange(N.abs(N.max(sorted['J-L']) - N.max(limited['J-L'])) + 200)
    
    #ax.plot(range(xmin, maxvalue), k + interp, lw = 1, label='Linear Regression', c = 'g')
    #ax.plot(sorted['J-L'], params[0] + params[1]*S.exp(-sorted['J-L']*params[2]), lw = 1, label='Exponent Fit', c = 'r')
    ax.plot(x, fitted, lw = 1, label='Linear Regression', c = 'g')
    ax.plot(limited['J-L'], expo, lw = 2, label='Exponent Fit', c = 'r')
    ax.plot(newxrange, 2.97 + params[0] + params[1]*S.exp(-newxrange*params[2]),
            'r--', lw = 2, label='Exponent Fit Cont.')

    ax.set_xlabel('Days since HST deployment')
    ax.set_ylabel('Accumulated defocus in SM microns')  
    
    #minor ticks
    xmajorLocator = MultipleLocator(500)
    xminorLocator = MultipleLocator(100)
    xmajorFormattor = FormatStrFormatter('%i')
    xminorFormattor = NullFormatter()
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.xaxis.set_major_formatter(xmajorFormattor)
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    #y
    ymajorLocator = MultipleLocator(5)
    yminorLocator = MultipleLocator(1)
    ymajorFormattor = FormatStrFormatter('%i')
    yminorFormattor = NullFormatter()
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_major_formatter(ymajorFormattor)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)

    ax.set_xlim(xmin - 10, N.max(newxrange) + 60)
    ax.set_ylim(min(y)-3, max(y)+2)
    
    try:
        P.legend(scatterpoints = 1, numpoints  = 1)
    except:
        P.legend()
    
    P.savefig(output_folder + output + type)
    P.close()

def FocusTrendRemoveLatestMovement(xmin, xmax, title, type,
                                   input_folder, output_folder,
                                   output = 'FocusTrendUptoDate'):
    '''
    @param xmin: minimum Modified Julian Date to be plotted
    @param xmax: maximum Modified Julian Date to be used for the fits
    @param title: title of the plot
    @param output: name of the output file
       
    Plots Focus trend since xmin while taking into account the last mirror move.
    The latest mirror move is subtracted from all the previous data.
    Straight line and an exponential are fitted to the all data since xmin.
    '''
    file = 'BreathingCorrectedData.txt'    
    data = N.loadtxt(input_folder + file, skiprows=1,
                     dtype={'names': ('Julian', 'J-L', 'Focus', 'Error', 'Camera'),
                            'formats':('i4','i4','f4', 'f4', 'S6')})    
    sorted = N.sort(data, order=['J-L', 'Focus'])

    #latest date
    maxvalue = N.max(data['J-L'])

    #latest mirror movement
    mirrorM = h.MirrorMovesInHSTTime()
    last, add = findMaxAndPair(mirrorM)
   
    #all data that is older than the latest mirror move
    ally = N.array([b + add for a, b in zip(sorted['J-L'], sorted['Focus']) if a < last])
    allx = N.array([a for a, b in zip(sorted['J-L'], sorted['Focus']) if a < last])   
    alle = N.array([c for a, b, c in zip(sorted['J-L'], sorted['Focus'], sorted['Error']) if a < last])
    #all data after the latest mirrormove
    ayy = N.array([b for a, b in zip(sorted['J-L'], sorted['Focus']) if a > last])
    axx = N.array([a for a, b in zip(sorted['J-L'], sorted['Focus']) if a > last])   
    aee = N.array([b for a, b in zip(sorted['J-L'], sorted['Error']) if a > last])
    
    #limit data for fitting
    limited = sorted[(sorted['J-L'] > xmin) & (sorted['J-L'] < xmax)]
    x = limited['J-L']
    y = limited['Focus']
    err = limited['Error']
    
    #add the last mirror move to the trailing focus values
    y1 = [b + add for a, b in zip(x, y) if a < last]
    x1 = [a for a, b in zip(x, y) if a < last]
    addy = [b for a, b in zip(x, y) if a > last]
    addx = [a for a in x if a > last]
    y = N.array(y1 + addy)
    x = N.array(x1 + addx)
    #fit polynomial
    fitted, error = f.PolyFit(y, x)
    
    #fit exponential: fitexp = -6.16 + 201.64*exp(-days*0.000570)
    p = [-6.16, 201.64, 0.000570]
    expo, params = f.FitExponent(x, y, p)
    print 'Single exponential (y = A + B*exp(-days*C)) fit between %i and %i days since HST launch (Breathing Corrected):' % (xmin, xmax)
    print params

    #calculate the zero focus day
#    day = 7206 # Jan 15th, 2010
#    daydate = D.datetime(*j.HSTdayToRealDate(day)[0:6]).strftime('%B-%d-%Y')
#    force = 0.5
#    sh = force - (params[0] + params[1]*N.exp(-day*params[2]))
    sh = - 0.5
    zf =  D.datetime(*j.HSTdayToRealDate(f.FindZeroSingleExp(params, 7600))[0:6]).strftime('%A %d, %B, %Y (at %H:%M%Z)')
    zfshift =  D.datetime(*j.HSTdayToRealDate(f.FindZeroSingleExp(params, 7600, sh))[0:6]).strftime('%A %d, %B, %Y (at %H:%M%Z)')
    print 'The predicted zero focus date from breathing corrected focus data that have been derived since Dec 2002 in ACS WFC frame using single exponent fit is:'
    print zf
    print 'and in WFC3 frame (%3.2f microns shift) :\n%s' % (sh, zfshift)

    #create the figure
    ax = P.subplot(111)
    P.title(title)

    P.annotate('y = %.4e + %.4e*exp(-days*%.4e)' % (params[0], params[1], params[2]),
               xy = (0.5, 0.02),
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction',
               size = 'small')

    #plot zero focus line
    ax.axhline(y = 0, ls='--', lw = 1., c = 'k')

    #plot mirror moves
    for time, movement in mirrorM:
        ax.axvline(x = time, ymin = -10, ymax = 1, lw = 1.0, ls=':', c = 'k')
        ax.annotate(s = str(movement) + '$\mu$m', xy= (time+40, min(y)-3), rotation = 90,
                    horizontalalignment='center', verticalalignment='center', size = 'small')   
    #last one with label
    ax.axvline(x = mirrorM[-1][0], ymin = -10, ymax = 1, lw = 1.0, ls=':', c = 'k', label='Mirror Movement')
    
    #plots
    ax.errorbar(allx, ally, yerr = alle, marker = 'o', color = 'blue',
                ms = 4, ls = 'None', ecolor = None, mew = 0.4,
                label='Breathing corrected (other SIs)', capsize = 2, elinewidth = 0.8)
    ax.errorbar(axx, ayy, yerr = aee, marker = 'o', color = 'blue', ms = 4, ls = 'None',
                ecolor = None, mew = 0.4, capsize = 2, elinewidth = 0.8)
    #WFC3 with magenta
    ayyW = N.array([b for a, b, c in zip(sorted['J-L'], sorted['Focus'], sorted['Camera']) if a > last and c == 'WFC3'])
    axxW = N.array([a for a, b, c in zip(sorted['J-L'], sorted['Focus'], sorted['Camera']) if a > last and c == 'WFC3'])   
    aeeW = N.array([b for a, b, c in zip(sorted['J-L'], sorted['Error'], sorted['Camera']) if a > last and c == 'WFC3'])
    ax.errorbar(axxW, ayyW, yerr = aeeW, marker = 'D', color = 'magenta',
                ms = 4, ls = 'None', ecolor = None, mew = 0.4, capsize = 2,
                elinewidth = 0.8, label='Breathing corrected (WFC3 UVIS)')   
    
    #plot fits
    ax.plot(x, fitted, lw = 1, label='Linear Regression', c = 'g')
    ax.plot(x, expo, lw = 1, label='Exponent Fit', c = 'r')
    
    ax.set_xlabel('Days since HST deployment')
    ax.set_ylabel('Accumulated Defocus [SM $\mu$m]')  
    
    #minor ticks
    xmajorLocator = MultipleLocator(500)
    xminorLocator = MultipleLocator(100)
    xmajorFormattor = FormatStrFormatter('%i')
    xminorFormattor = NullFormatter()
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.xaxis.set_major_formatter(xmajorFormattor)
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    #y
    ymajorLocator = MultipleLocator(5)
    yminorLocator = MultipleLocator(1)
    ymajorFormattor = FormatStrFormatter('%i')
    yminorFormattor = NullFormatter()
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_major_formatter(ymajorFormattor)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)

    ax.set_xlim(xmin + 5, maxvalue + 80)
    ax.set_ylim(min(y)-5, max(y)+2)
    try:
        P.legend(scatterpoints = 1, numpoints = 1)
    except:
        P.legend()
    
    P.savefig(output_folder + output + type)
    P.close()


def FocusTrendRemoveLatestMovementOffset(xmin, xmax, title, type,
                                         input_folder, output_folder,
                                         output = 'FocusTrendUptoDateOffset',
                                         WFC3offset = 0.5):
    '''
    @param xmin: minimum Modified Julian Date to be plotted
    @param xmax: maximum Modified Julian Date to be used for the fits
    @param title: title of the plot
    @param output: name of the output file
       
    Plots Focus trend since xmin while taking into account the last mirror move.
    The latest mirror move is subtracted from all the previous data.
    Straight line and an exponential are fitted to the all data since xmin.
    '''
    file = 'BreathingCorrectedData.txt'    
    data = N.loadtxt(input_folder + file, skiprows=1,
                     dtype={'names': ('Julian', 'J-L', 'Focus', 'Error', 'Camera'),
                            'formats':('i4','i4','f4', 'f4', 'S6')})    
    
    mask = (data['Camera'] == 'WFC3')
    print data[mask]['Focus']
    data['Focus'][mask] = data['Focus'][mask] + WFC3offset
    print data[mask]['Focus']
    
    print 'WFC3offset of %f applied' % WFC3offset   
    sorted = N.sort(data, order=['J-L', 'Focus'])

    #latest date
    maxvalue = N.max(data['J-L'])

    #latest mirror movement
    mirrorM = h.MirrorMovesInHSTTime()
    last, add = findMaxAndPair(mirrorM)
   
    #all data that is older than the latest mirror move
    ally = N.array([b + add for a, b in zip(sorted['J-L'], sorted['Focus']) if a < last])
    allx = N.array([a for a, b in zip(sorted['J-L'], sorted['Focus']) if a < last])   
    alle = N.array([c for a, b, c in zip(sorted['J-L'], sorted['Focus'], sorted['Error']) if a < last])
    #all data after the latest mirrormove
    ayy = N.array([b for a, b in zip(sorted['J-L'], sorted['Focus']) if a > last])
    axx = N.array([a for a, b in zip(sorted['J-L'], sorted['Focus']) if a > last])   
    aee = N.array([b for a, b in zip(sorted['J-L'], sorted['Error']) if a > last])
    
    #limit data for fitting
    limited = sorted[(sorted['J-L'] > xmin) & (sorted['J-L'] < xmax)]
    x = limited['J-L']
    y = limited['Focus']
    err = limited['Error']
    #add the last mirror move to the trailing focus values
    y1 = [b + add for a, b in zip(x, y) if a < last]
    x1 = [a for a, b in zip(x, y) if a < last]
    addy = [b for a, b in zip(x, y) if a > last]
    addx = [a for a in x if a > last]
    y = N.array(y1 + addy)
    x = N.array(x1 + addx)
    #fit polynomial
    fitted, error = f.PolyFit(y, x)
    
    #fit exponential: fitexp = -6.16 + 201.64*exp(-days*0.000570)
    p = [-6.16, 201.64, 0.000570]
    expo, params = f.FitExponent(x, y, p)
    print 'Single exponential (y = A + B*exp(-days*C)) fit between %i and %i days since HST launch (Breathing Corrected):' % (xmin, xmax)
    print params

    #calculate the zero focus day
#    day = 7206 # Jan 15th, 2010
#    daydate = D.datetime(*j.HSTdayToRealDate(day)[0:6]).strftime('%B-%d-%Y')
#    force = 1.3
#    sh = force - (params[0] + params[1]*N.exp(-day*params[2]))
    sh = -0.5
    zf =  D.datetime(*j.HSTdayToRealDate(f.FindZeroSingleExp(params, 7600))[0:6]).strftime('%A %d, %B, %Y (at %H:%M%Z)')
    zfshift =  D.datetime(*j.HSTdayToRealDate(f.FindZeroSingleExp(params, 7600, sh))[0:6]).strftime('%A %d, %B, %Y (at %H:%M%Z)')
    print 'The predicted zero focus date from breathing corrected focus data that have been derived since Dec 2002 using single exponent fit is:'
    print zf
    print 'and in WFC3 frame (%3.2f microns shift):\n%s' % (sh, zfshift)

    #create the figure
    ax = P.subplot(111)
    P.title(title)

    P.annotate('y = %.4e + %.4e*exp(-days*%.4e)' % (params[0], params[1], params[2]),
               xy = (0.5, 0.02),
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction',
               size = 'small')

    #plot zero focus line
    ax.axhline(y = 0, ls='--', lw = 1., c = 'k')

    #plot mirror moves
    for time, movement in mirrorM:
        ax.axvline(x = time, ymin = -10, ymax = 1, lw = 1.0, ls=':', c = 'k')
        ax.annotate(s = str(movement) + '$\mu$m', xy= (time+40, min(y)-3),
                    rotation = 90, horizontalalignment='center',
                    verticalalignment='center', size = 'small')   
    #last one with label
    ax.axvline(x = mirrorM[-1][0], ymin = -10, ymax = 1, lw = 1.0,
               ls=':', c = 'k', label='Mirror Movement')
    
    #plots
    ax.errorbar(allx, ally, yerr = alle, marker = 'o', color = 'blue',
                ms = 4, ls = 'None', ecolor = None, mew = 0.4,
                label='Breathing corrected (other SIs)',
                capsize = 2, elinewidth = 0.8)
    ax.errorbar(axx, ayy, yerr = aee, marker = 'o', color = 'blue', ms = 4, ls = 'None',
                ecolor = None, mew = 0.4, capsize = 2, elinewidth = 0.8)
    #WFC3 with magenta
    ayyW = N.array([b for a, b, c in zip(sorted['J-L'], sorted['Focus'], sorted['Camera']) if a > last and c == 'WFC3'])
    axxW = N.array([a for a, b, c in zip(sorted['J-L'], sorted['Focus'], sorted['Camera']) if a > last and c == 'WFC3'])   
    aeeW = N.array([b for a, b, c in zip(sorted['J-L'], sorted['Error'], sorted['Camera']) if a > last and c == 'WFC3'])
    ax.errorbar(axxW, ayyW, yerr = aeeW, marker = 'D', color = 'magenta',
                ms = 4, ls = 'None', ecolor = None, mew = 0.4, capsize = 2,
                elinewidth = 0.8, label='Breathing corrected (WFC3 UVIS)')   
    
    #plot fits
    ax.plot(x, fitted, lw = 1, label='Linear Regression', c = 'g')
    ax.plot(x, expo, lw = 1, label='Exponent Fit', c = 'r')
    
    ax.set_xlabel('Days since HST deployment')
    ax.set_ylabel('Accumulated Defocus [SM $\mu$m]')  
    
    #minor ticks
    xmajorLocator = MultipleLocator(500)
    xminorLocator = MultipleLocator(100)
    xmajorFormattor = FormatStrFormatter('%i')
    xminorFormattor = NullFormatter()
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.xaxis.set_major_formatter(xmajorFormattor)
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    #y
    ymajorLocator = MultipleLocator(5)
    yminorLocator = MultipleLocator(1)
    ymajorFormattor = FormatStrFormatter('%i')
    yminorFormattor = NullFormatter()
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_major_formatter(ymajorFormattor)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)

    ax.set_xlim(xmin + 5, maxvalue + 80)
    ax.set_ylim(min(y)-5, max(y)+2)
    try:
        P.legend(scatterpoints = 1, numpoints = 1)
    except:
        P.legend()
    
    P.savefig(output_folder + output + type)
    P.close()

def FocusTrendRemoveLatestMovementNoBreathing(xmin, xmax,
                                              title, type,
                                              input_folder, output_folder,
                                              output = 'FocusTrendUptoDateNoBreathing'):
    '''
    @param xmin: minimum Modified Julian Date to be plotted
    @param xmax: maximum Modified Julian Date to be used for the fits
    @param title: title of the plot
    @param output: name of the output file
       
    Plots Focus trend since xmin while taking into account the last mirror move.
    The latest mirror move is subtracted from all the previous data.
    Straight line and an exponential are fitted to the all data since xmin.
    '''

    data = N.loadtxt(input_folder + 'AllData.txt', skiprows=1,
				    dtype={'names': ('Obs', 'Date', 'Julian', 'Focus', 'Error'),
					   'formats':('S12','S12','i4','f4','f4')})

    #take a away from Julian the J-L
    data['Julian'] =  j.fromHSTDeployment(data['Julian'])

    #latest date
    maxvalue = N.max(data['Julian'])

    #latest mirror movement
    mirrorM = h.MirrorMovesInHSTTime()
    last, add = findMaxAndPair(mirrorM)

    #this whole thing is very stupidly written, and should be fixed
    #when time...
    #cumulative adding of focus values
    shiftdate = data['Julian']
    focus = data['Focus']
    cfocus = focus + 95.*(shiftdate < 1348)
    step = 95.*(shiftdate < 1353)
    for date, movement in mirrorM:
        #does not use the latest!
        if movement != 2.97:
            step += movement*(shiftdate < date)
            cfocus += movement*(shiftdate < date)

    data['Focus'] = cfocus
    sorted = N.sort(data, order=['Julian', 'Focus'])

    #all data that is older than the latest mirror move
    ally = N.array([b + add for a, b in zip(sorted['Julian'], sorted['Focus']) if a < last])
    allx = N.array([a for a, b in zip(sorted['Julian'], sorted['Focus']) if a < last])   
    alle = N.array([c for a, b, c in zip(sorted['Julian'], sorted['Focus'], sorted['Error']) if a < last])
    #all data after the latest mirrormove
    ayy = N.array([b for a, b in zip(sorted['Julian'], sorted['Focus']) if a > last])
    axx = N.array([a for a, b in zip(sorted['Julian'], sorted['Focus']) if a > last])   
    aee = N.array([b for a, b in zip(sorted['Julian'], sorted['Error']) if a > last])
    
    #limit data for fitting
    limited = sorted[(sorted['Julian'] > xmin) & (sorted['Julian'] < xmax)]
    x = limited['Julian']
    y = limited['Focus']
    err = limited['Error']
    #add the last mirror move to the trailing focus values
    y1 = [b + add for a, b in zip(x, y) if a < last]
    x1 = [a for a, b in zip(x, y) if a < last]
    addy = [b for a, b in zip(x, y) if a > last]
    addx = [a for a in x if a > last]
    y = N.array(y1 + addy)
    x = N.array(x1 + addx)
    #fit polynomial
    fitted, error = f.PolyFit(y, x)
    
    #fit exponential: fitexp = -6.16 + 201.64*exp(-days*0.000570)
    p = [-6.16, 201.64, 0.000570]
    expo, params = f.FitExponent(x, y, p)
    print 'Single exponential (y = A + B*exp(-days*C)) fit between %i and %i days since HST launch for (No Breathing Correction):' % (xmin, xmax)
    print params

    #calculate the zero focus day
#    day = 7206 # Jan 15th, 2010
#    daydate = D.datetime(*j.HSTdayToRealDate(day)[0:6]).strftime('%B-%d-%Y')
#    force = 1.3
#    sh = force - (params[0] + params[1]*N.exp(-day*params[2]))
    sh = -0.5
    zf =  D.datetime(*j.HSTdayToRealDate(f.FindZeroSingleExp(params, 7600))[0:6]).strftime('%A %d, %B, %Y (at %H:%M%Z)')
    zfshift =  D.datetime(*j.HSTdayToRealDate(f.FindZeroSingleExp(params, 7600, sh))[0:6]).strftime('%A %d, %B, %Y (at %H:%M%Z)')
    print 'The predicted zero focus date from focus data (no breathing correction) that have been derived since Dec 2002 using single exponent fit is:'
    print zf
    print 'and in WFC3 frame (%3.2f microns shift):\n%s' % (sh, zfshift)

    #create the figure
    ax = P.subplot(111)
    P.title(title)

    P.annotate('y = %.4e + %.4e*exp(-days*%.4e)' % (params[0], params[1], params[2]),
               xy = (0.5, 0.02),
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction',
               size = 'small')

    #plot zero focus line
    ax.axhline(y = 0, ls='--', lw = 1., c = 'k')

    #plot mirror moves
    for time, movement in mirrorM:
        ax.axvline(x = time, ymin = -10, ymax = 1, lw = 1.0, ls=':', c = 'k')
        ax.annotate(s = str(movement) + '$\mu$m', xy= (time+40, min(y)-3),
                    rotation = 90, horizontalalignment='center',
                    verticalalignment='center', size = 'small')   
    #last one with label
    ax.axvline(x = mirrorM[-1][0], ymin = -10, ymax = 1, lw = 1.0, ls=':', c = 'k', label='Mirror Movement')
    
    #plots
    ax.errorbar(allx, ally, yerr = alle, marker = 'o', color = 'blue',
                ms = 4, ls = 'None', ecolor = None, mew = 0.4,
                label='No Breathing Correction (other SIs)', capsize = 2,
                elinewidth = 0.8)
    ax.errorbar(axx, ayy, yerr = aee, marker = 'o', color = 'blue', ms = 4, ls = 'None',
                ecolor = None, mew = 0.4, capsize = 2, elinewidth = 0.8)
    #WFC3 with magenta
    ayyW = N.array([b for a, b, c in zip(sorted['Julian'], sorted['Focus'], sorted['Obs']) if a > last and c.startswith('i')])
    axxW = N.array([a for a, b, c in zip(sorted['Julian'], sorted['Focus'], sorted['Obs']) if a > last and c.startswith('i')])   
    aeeW = N.array([b for a, b, c in zip(sorted['Julian'], sorted['Error'], sorted['Obs']) if a > last and c.startswith('i')])
    ax.errorbar(axxW, ayyW, yerr = aeeW, marker = 'D', color = 'magenta',
                ms = 4, ls = 'None', ecolor = None, mew = 0.4, capsize = 2,
                elinewidth = 0.8, label='No Breathing Correction (WFC3 UVIS)')   
    
    #plot fits
    ax.plot(x, fitted, lw = 1, label='Linear Regression', c = 'g')
    ax.plot(x, expo, lw = 1, label='Exponent Fit', c = 'r')
    
    ax.set_xlabel('Days since HST deployment')
    ax.set_ylabel('Accumulated Defocus [SM $\mu$m]')  
    
    #minor ticks
    xmajorLocator = MultipleLocator(500)
    xminorLocator = MultipleLocator(100)
    xmajorFormattor = FormatStrFormatter('%i')
    xminorFormattor = NullFormatter()
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.xaxis.set_major_formatter(xmajorFormattor)
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    #y
    ymajorLocator = MultipleLocator(5)
    yminorLocator = MultipleLocator(1)
    ymajorFormattor = FormatStrFormatter('%i')
    yminorFormattor = NullFormatter()
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_major_formatter(ymajorFormattor)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)

    ax.set_xlim(xmin + 5, maxvalue + 80)
    ax.set_ylim(min(y)-5, max(y)+2)
    try:
        P.legend(scatterpoints = 1, numpoints = 1)
    except:
        P.legend()
    
    P.savefig(output_folder + output + type)
    P.close()

def FocusTrendRemoveLatestMovementNoBreathingOffset(xmin, xmax,
                                                    title, type,
                                                    input_folder, output_folder,
                                                    output = 'FocusTrendUptoDateNoBreathingOffset'):
    '''
    @param xmin: minimum Modified Julian Date to be plotted
    @param xmax: maximum Modified Julian Date to be used for the fits
    @param title: title of the plot
    @param output: name of the output file
       
    Plots Focus trend since xmin while taking into account the last mirror move.
    The latest mirror move is subtracted from all the previous data.
    Straight line and an exponential are fitted to the all data since xmin.
    '''
    WFC3offset = 0.5

    data = N.loadtxt(input_folder + 'AllData.txt', skiprows=1,
                    dtype={'names': ('Obs', 'Date', 'Julian', 'Focus', 'Error'),
                       'formats':('S12','S12','i4','f4','f4')})

    #take a away from Julian the J-L
    data['Julian'] =  j.fromHSTDeployment(data['Julian'])

    #offsetting
    #numpy.core.defchararray.startswith(a, prefix, start=0, end=None)
    mask = npstr.startswith(data['Obs'], 'i')
    #print data['Focus'][mask]
    data['Focus'][mask] = data['Focus'][mask] + WFC3offset
    #print data['Focus'][mask]
    
    print 'WFC3offset of %f applied' % WFC3offset   

    #latest date
    maxvalue = N.max(data['Julian'])

    #latest mirror movement
    mirrorM = h.MirrorMovesInHSTTime()
    last, add = findMaxAndPair(mirrorM)

    #this whole thing is very stupidly written, and should be fixed
    #when time...
    #cumulative adding of focus values
    shiftdate = data['Julian']
    focus = data['Focus']
    cfocus = focus + 95.*(shiftdate < 1348)
    step = 95.*(shiftdate < 1353)
    for date, movement in mirrorM:
        #does not use the latest!
        if movement != 2.97:
            step += movement*(shiftdate < date)
            cfocus += movement*(shiftdate < date)

    data['Focus'] = cfocus
    sorted = N.sort(data, order=['Julian', 'Focus'])

    #all data that is older than the latest mirror move
    ally = N.array([b + add for a, b in zip(sorted['Julian'], sorted['Focus']) if a < last])
    allx = N.array([a for a, b in zip(sorted['Julian'], sorted['Focus']) if a < last])   
    alle = N.array([c for a, b, c in zip(sorted['Julian'], sorted['Focus'], sorted['Error']) if a < last])
    #all data after the latest mirrormove
    ayy = N.array([b for a, b in zip(sorted['Julian'], sorted['Focus']) if a > last])
    axx = N.array([a for a, b in zip(sorted['Julian'], sorted['Focus']) if a > last])   
    aee = N.array([b for a, b in zip(sorted['Julian'], sorted['Error']) if a > last])
    
    #limit data for fitting
    limited = sorted[(sorted['Julian'] > xmin) & (sorted['Julian'] < xmax)]
    x = limited['Julian']
    y = limited['Focus']
    err = limited['Error']
    #add the last mirror move to the trailing focus values
    y1 = [b + add for a, b in zip(x, y) if a < last]
    x1 = [a for a, b in zip(x, y) if a < last]
    addy = [b for a, b in zip(x, y) if a > last]
    addx = [a for a in x if a > last]
    y = N.array(y1 + addy)
    x = N.array(x1 + addx)
    #fit polynomial
    fitted, error = f.PolyFit(y, x)
    
    #fit exponential: fitexp = -6.16 + 201.64*exp(-days*0.000570)
    p = [-6.16, 201.64, 0.000570]
    expo, params = f.FitExponent(x, y, p)
    print 'Single exponential (y = A + B*exp(-days*C)) fit between %i and %i days since HST launch for (No Breathing Correction):' % (xmin, xmax)
    print params

    #calculate the zero focus day
    day = 7206 # Jan 15th, 2010
    daydate = D.datetime(*j.HSTdayToRealDate(day)[0:6]).strftime('%B-%d-%Y')
    force = 1.3
    sh = force - (params[0] + params[1]*N.exp(-day*params[2]))
    zf =  D.datetime(*j.HSTdayToRealDate(f.FindZeroSingleExp(params, 7600))[0:6]).strftime('%A %d, %B, %Y (at %H:%M%Z)')
    zfshift =  D.datetime(*j.HSTdayToRealDate(f.FindZeroSingleExp(params, 7600, sh))[0:6]).strftime('%A %d, %B, %Y (at %H:%M%Z)')
    print 'The predicted zero focus date from focus data (no breathing correction) that have been derived since Dec 2002 using single exponent fit is:'
    print zf
#    print 'and with %3.2f microns shift [forced: (date, focus) = (%s, %3.2f)]:\n%s' % (sh, daydate, force, zfshift)

    #create the figure
    ax = P.subplot(111)
    P.title(title)

    P.annotate('y = %.4e + %.4e*exp(-days*%.4e)' % (params[0], params[1], params[2]),
               xy = (0.5, 0.02),
               horizontalalignment='center',
               verticalalignment='center',
               xycoords='figure fraction',
               size = 'small')

    #plot zero focus line
    ax.axhline(y = 0, ls='--', lw = 1., c = 'k')

    #plot mirror moves
    for time, movement in mirrorM:
        ax.axvline(x = time, ymin = -10, ymax = 1, lw = 1.0, ls=':', c = 'k')
        ax.annotate(s = str(movement) + '$\mu$m', xy= (time+40, min(y)-3),
                    rotation = 90, horizontalalignment='center',
                    verticalalignment='center', size = 'small')   
    #last one with label
    ax.axvline(x = mirrorM[-1][0], ymin = -10, ymax = 1, lw = 1.0, ls=':', c = 'k', label='Mirror Movement')
    
    #plots
    ax.errorbar(allx, ally, yerr = alle, marker = 'o', color = 'blue',
                ms = 4, ls = 'None', ecolor = None, mew = 0.4,
                label='No Breathing Correction (other SIs)', capsize = 2,
                elinewidth = 0.8)
    ax.errorbar(axx, ayy, yerr = aee, marker = 'o', color = 'blue',
                ms = 4, ls = 'None', ecolor = None, mew = 0.4, capsize = 2,
                elinewidth = 0.8)
    #WFC3 with magenta
    ayyW = N.array([b for a, b, c in zip(sorted['Julian'], sorted['Focus'], sorted['Obs']) if a > last and c.startswith('i')])
    axxW = N.array([a for a, b, c in zip(sorted['Julian'], sorted['Focus'], sorted['Obs']) if a > last and c.startswith('i')])   
    aeeW = N.array([b for a, b, c in zip(sorted['Julian'], sorted['Error'], sorted['Obs']) if a > last and c.startswith('i')])
    ax.errorbar(axxW, ayyW, yerr = aeeW, marker = 'D', color = 'magenta',
                ms = 4, ls = 'None', ecolor = None, mew = 0.4, capsize = 2,
                elinewidth = 0.8, label='No Breathing Correction (WFC3 UVIS)')   
    
    #plot fits
    ax.plot(x, fitted, lw = 1, label='Linear Regression', c = 'g')
    ax.plot(x, expo, lw = 1, label='Exponent Fit', c = 'r')
    
    ax.set_xlabel('Days since HST deployment')
    ax.set_ylabel('Accumulated Defocus [SM $\mu$m]')  
    
    #minor ticks
    xmajorLocator = MultipleLocator(500)
    xminorLocator = MultipleLocator(100)
    xmajorFormattor = FormatStrFormatter('%i')
    xminorFormattor = NullFormatter()
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.xaxis.set_major_formatter(xmajorFormattor)
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    #y
    ymajorLocator = MultipleLocator(5)
    yminorLocator = MultipleLocator(1)
    ymajorFormattor = FormatStrFormatter('%i')
    yminorFormattor = NullFormatter()
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_major_formatter(ymajorFormattor)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)

    ax.set_xlim(xmin + 5, maxvalue + 80)
    ax.set_ylim(min(y)-5, max(y)+2)
    try:
        P.legend(scatterpoints = 1, numpoints = 1)
    except:
        P.legend()
    
    P.savefig(output_folder + output + type)
    P.close()

def FocusTrendSinceDayZero(title, output,
                           input_folder, output_folder,
                           stepFunction = False,
                           filename = 'AllData.txt',
                           endday = 8100):
    '''
    '''
    
    data = N.loadtxt(input_folder+ filename, skiprows=1,
                     dtype={'names': ('Obs', 'Date', 'MJDate', 'Focus', 'Error'),
                            'formats':('S12','S12','i4','f4','f4')})

    #mirror movements
    mirrorM = MirrorMovesInHSTTime()

    #manipulatges the date
    shiftdate = data['MJDate'] - 48005.0
    focus = data['Focus']
  
    #from SM
    #corrfocus = focus + 5.34*(shiftdate<5947) + 4.16*(shiftdate<5361.97)
    #corrfocus = corrfocus + 3.6*(shiftdate<4610.87) + 3.6*(shiftdate<3710.81)
    #corrfocus = corrfocus + 4.2*(shiftdate<3552.74) + 3.0*(shiftdate<3436.65) 
    #corrfocus = corrfocus - 15.2*(shiftdate<2992.73) + 16.6*(shiftdate<2968.04) 
    #corrfocus = corrfocus - 18.6*(shiftdate<2845.69) + 21.0*(shiftdate<2825.05)
    #corrfocus = corrfocus - 2.4*(shiftdate<2525.95)+ 5.0*(shiftdate<2386.74)
    #corrfocus = corrfocus + 6.0*(shiftdate<2156.78) + 6.5*(shiftdate<1957.63) 
    #corrfocus = corrfocus + 5.0*(shiftdate<1732) + 5.0*(shiftdate<1532) + 95*(shiftdate<1353)
    #creates the step function and fixes the focus by each step
    cfocus = focus + 95.*(shiftdate < 1348)
    step = 95.*(shiftdate < 1353)
    for date, movement in mirrorM:
        #print date, movement
        step += movement*(shiftdate < date)
        cfocus += movement*(shiftdate < date)   

    #double exponential fitting
    desorpdays = N.arange(0, endday, 1)
    SMdesorp = -6.0434 + 56.2568*N.exp(-desorpdays/364.5247)+106.2362*N.exp(-desorpdays/2237.2268) # RvdM
    #SMdesorp2 = -8.3914 + 52.9418 *N.exp(-desorpdays*0.002505)+97.6542*N.exp(-desorpdays*0.000395) # CC

    p = [-6.05, 56.0, 365., 100., 2240.]
    expo, params = FitDoubleExponent(shiftdate, cfocus, p)
    expoExt = params[0] + params[1]*N.exp(-desorpdays/params[2]) + params[3]*N.exp(-desorpdays/params[4])
    
    #create the figure
    ax = P.subplot(111)
    P.title(title)

    ax.scatter(shiftdate, cfocus, s = 7, label = 'No breathing correction')
    if stepFunction: ax.plot(shiftdate, step, c='y', lw = 0.8, label = 'Step Function')
    ax.plot(desorpdays, expoExt, lw = 1.1, c = 'r', label = 'Double Exponent Fit')
    #ax.plot(desorpdays, SMdesorp, lw =1.1, c = 'g', ls='--', label = 'Old Fit')

    ax.set_xlim(0, max(shiftdate) + 100)
    ax.set_ylim(-20, 150)
    
    ax.set_xlabel('Days since HST Deployment, April 1990')
    ax.set_ylabel('Accumulated OTA shrinkage [SM $\mu$m]')

    #minor ticks
    xmajorLocator = MultipleLocator(1000)
    xminorLocator = MultipleLocator(200)
    xmajorFormattor = FormatStrFormatter('%i')
    xminorFormattor = NullFormatter()
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.xaxis.set_major_formatter(xmajorFormattor)
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    #y
    ymajorLocator = MultipleLocator(50)
    yminorLocator = MultipleLocator(10)
    ymajorFormattor = FormatStrFormatter('%i')
    yminorFormattor = NullFormatter()
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_major_formatter(ymajorFormattor)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)

    P.legend(scatterpoints = 1, numpoints = 1)
    P.savefig(output_folder + output)
    P.close()    

def FocusTrendSinceDayZeroDates(title, output,
                                input_folder, output_folder,
                                stepFunction = False,
                                filename = 'AllData.txt'):
    '''
    '''
   
    #mondays = WeekdayLocator(MONDAY)
    months = MonthLocator(range(1,13,4), bymonthday=1)
    year = YearLocator(1, month=1, day=1)
    monthsFmt = DateFormatter("%d\n%b\n%Y")
    
    data = N.loadtxt(input_folder + filename, skiprows=1,
                     dtype={'names': ('Obs', 'Date', 'MJDate', 'Focus', 'Error'),
                            'formats':('S12','S12','i4','f4','f4')})


    #mirror movements
    mirrorM = MirrorMovesInHSTTime()

    #manipulatges the date
    shiftdate = data['MJDate'] - 48005.0
    focus = data['Focus']
  
    cfocus = focus + 95.*(shiftdate < 1348)
    step = 95.*(shiftdate < 1353)
    for date, movement in mirrorM:
        step += movement*(shiftdate < date)
        cfocus += movement*(shiftdate < date)   

    #double exponential fitting
    p = [-6.05, 56.0, 365., 100., 2240.]
    expo, params = FitDoubleExponent(shiftdate, cfocus, p)
    
    #create the figure
    fig = P.figure()
    ax = fig.add_subplot(111)
    #P.title(title)

    ax.plot_date([D.datetime(*fromJulian(x)[:6]) for x in data['MJDate']], cfocus,
                 label = 'No breathing correction', ms = 3)
    ax.plot_date([D.datetime(*fromJulian(x)[:6]) for x in data['MJDate']], expo, ls='-', 
            lw = 1.1, c = 'r', label = 'Double Exponent Fit', marker = 'None')

    min, max = ax.get_xlim()  
    ax.set_xlim(min - 20, max + 140)
    ax.set_ylim(-50, 152)
    
    ax2 = ax.twiny()
    ax2.plot(shiftdate, cfocus, visible = False)
    ax2.plot(shiftdate, expo, visible = False)
    
    ax2.set_xlabel('Days since HST Deployment')
    ax.set_ylabel('Accumulated OTA shrinkage [SM $\mu$m]')

    #time axis
    ax.xaxis.set_major_locator(year)
    ax.xaxis.set_major_formatter(monthsFmt)
    ax.xaxis.set_minor_locator(months)
    #minor ticks
    ymajorLocator = MultipleLocator(50)
    yminorLocator = MultipleLocator(10)
    ymajorFormattor = FormatStrFormatter('%i')
    yminorFormattor = NullFormatter()
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_major_formatter(ymajorFormattor)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)

    for tl in ax.get_xticklabels():
        tl.set_fontsize(8)
        #tl.set_rotation(40)

    ax.legend()  
    P.savefig(output_folder + output)
    P.close()


def FocusTrendSinceDayZeroDates2(output,
                                 input_folder, output_folder,
                                 filename = 'AllData.txt'):    
    '''
    Plots the overall focus trend since the HST launch. Will not plot errors as they
    are smaller or similar size to the markers.
    '''
    data = N.loadtxt(input_folder + filename, skiprows=1,
                     dtype={'names': ('Obs', 'Date', 'MJDate', 'Focus', 'Error'),
                            'formats':('S12','S12','i4','f4','f4')})

    #mirror movements
    mirrorM = h.MirrorMovesInHSTTime()

    #manipulatges the date
    shiftdate = data['MJDate'] - 48005.0
    focus = data['Focus']
  
    cfocus = focus + 95.*(shiftdate < 1348)
    step = 95.*(shiftdate < 1353)
    for date, movement in mirrorM:
        step += movement*(shiftdate < date)
        cfocus += movement*(shiftdate < date)   

    #double exponential fitting
    p = [-6.05, 56.0, 365., 100., 2240.]
    expo, params = f.FitDoubleExponent(shiftdate, cfocus, p)

    #calculate the zero focus day
#    day = 7206 # Jan 15th, 2010
#    daydate = D.datetime(*j.HSTdayToRealDate(day)[0:6]).strftime('%B-%d-%Y')
#    force = 1.3
#    sh = force - (params[0] + params[1]*N.exp(-day/params[2]) + params[3]*N.exp(-day/params[4]))
    sh = -0.5
    zf =  D.datetime(*j.HSTdayToRealDate(f.FindZeroDoubleExp(params, 7600))[0:6]).strftime('%A %d, %B, %Y (at %H:%M%Z)')
    zfshift =  D.datetime(*j.HSTdayToRealDate(f.FindZeroDoubleExp(params, 7600, sh))[0:6]).strftime('%A %d, %B, %Y (at %H:%M%Z)')

    print 'The predicted zero focus date from all focus data using double exponent fit (No Breathing Correction) is:'
    print zf 
    print 'and in WFC3 frame (%3.2f microns shift):\n%s' % (sh, zfshift)
    
    #create the figure
    fig = P.figure()
    ax = fig.add_subplot(111)

    #P.title('HST Focus Measurements (PC \& HRC)')

    #TODO delete these
    weird = True
    weirdtop = 7800
    if weird:
        xdel = N.arange(0, weirdtop)
        ax.plot(xdel, params[0] + params[1]*N.exp(-xdel/params[2]) + params[3]*N.exp(-xdel/params[4]), c = 'r', lw = 1.1)
        #ax.plot(xdel, sh + params[0] + params[1]*N.exp(-xdel/params[2]) + params[3]*N.exp(-xdel/params[4]), c = 'g', lw = 1.1)

    pl = ax.plot(shiftdate, expo, c = 'r', label = 'Double Exponent Fit', lw = 1.2)
    sc = ax.scatter(shiftdate, cfocus, c = 'b', s = 7, label = 'No breathing correction')
    #ax.errorbar(shiftdate, cfocus, yerr = data['Error'], marker = 'o', color = 'blue', ms = 2.2, ls = 'None',
    #            ecolor = None, mew = 0.4, label='No breathing corrected', capsize = 1.4, elinewidth = 0.9)

    ax2 = ax.twiny()
    ax2.plot(shiftdate, expo, c = 'r', visible = False)
    ax2.scatter(shiftdate, cfocus, visible = False)
    #ax.errorbar(shiftdate, cfocus, yerr = data['Error'], marker = 'o', color = 'blue', ms = 2.2, ls = 'None',
    #            ecolor = None, mew = 0.4, capsize = 1.4, elinewidth = 0.9, visible = False)
    
    #minor ticks
    ymajorLocator = MultipleLocator(50)
    yminorLocator = MultipleLocator(10)
    ymajorFormattor = FormatStrFormatter('%i')
    yminorFormattor = NullFormatter()
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_major_formatter(ymajorFormattor)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)
    
    xmajorLocator = MultipleLocator(1000)
    xminorLocator = MultipleLocator(200)
    xmajorFormattor = FormatStrFormatter('%i')
    xminorFormattor = NullFormatter()
    ax2.xaxis.set_major_locator(xmajorLocator)
    ax2.xaxis.set_major_formatter(xmajorFormattor)
    ax2.xaxis.set_minor_locator(xminorLocator)
    ax2.xaxis.set_minor_formatter(xminorFormattor)
  
    ax.set_xlim(0, max(shiftdate) + 100)
    ax2.set_xlim(0, max(shiftdate) + 100)
    ax.set_ylim(-10, 152)
    
    ax.set_ylabel('Accumulated OTA shrinkage $[SM \mu m]$')
    ax2.set_xlabel('Days since HST Deployment')
  
    #for tl in ax.get_xticklabels(): tl.set_rotation(40)
    
    ax.set_xticks(range(0,int(max(shiftdate))+125, 450))
    times = []
    for m in ax.get_xticks():
        x = D.datetime(*j.fromJulian(m + 48005.0)[0:6]).strftime('%d\n%b\n%Y')
        times.append(x)
    ax.set_xticklabels(times)

    if weird:
        ax.set_xlim(0, weirdtop + 100)
        ax2.set_xlim(0, weirdtop + 100)
        ax.axhline(y = 0, lw = 0.7, color='g')
        ax2.axhline(y = 0, lw = 0.7, color='g')
        ax.set_xticks(range(0,weirdtop + 125, 600))
        times = []
        for m in ax.get_xticks():
            x = D.datetime(*j.fromJulian(m + 48005.0)[0:6]).strftime('%d\n%b\n%Y')
            times.append(x)
        ax.set_xticklabels(times)

    ax.legend([pl, sc], ['Double Exponent Fit', 'No Breathing Correction (all SIs)'],
              scatterpoints = 1)
    
    P.savefig(output_folder + output)
    P.close()

def FocusTrendSinceDayZeroOLD(title, output,
                              input_folder, output_folder,
                              filename = 'comp2009allfocus.txt'):
    '''
    @deprecated: This function is no longer used. Please see the other two functions.
    '''
    
    data = N.loadtxt(filename, skiprows=1,
                     dtype={'names': ('Obs', 'Date', 'MJDate', 'Focus'), 'formats':('S12','S12','i4','f4')})

    #double exponentials
    desorpdays = N.arange(0,8000,1)
    SMdesorp = -6.0434 + 56.2568*N.exp(-desorpdays/364.5247)+106.2362*N.exp(-desorpdays/2237.2268) # RvdM
    SMdesorp2 = -8.3914 + 52.9418 *N.exp(-desorpdays*0.002505)+97.6542*N.exp(-desorpdays*0.000395) # CC

    shiftdate = data['MJDate'] - 48005.0
    focus = data['Focus']
  
    #from SM
    corrfocus = focus + 5.34*(shiftdate<5947) + 4.16*(shiftdate<5361.97)
    corrfocus = corrfocus + 3.6*(shiftdate<4610.87) + 3.6*(shiftdate<3710.81)
    corrfocus = corrfocus + 4.2*(shiftdate<3552.74) + 3.0*(shiftdate<3436.65) 
    corrfocus = corrfocus - 15.2*(shiftdate<2992.73) + 16.6*(shiftdate<2968.04) 
    corrfocus = corrfocus - 18.6*(shiftdate<2845.69) + 21.0*(shiftdate<2825.05)
    corrfocus = corrfocus - 2.4*(shiftdate<2525.95)+ 5.0*(shiftdate<2386.74)
    corrfocus = corrfocus + 6.0*(shiftdate<2156.78) + 6.5*(shiftdate<1957.63) 
    corrfocus = corrfocus + 5.0*(shiftdate<1732) + 5.0*(shiftdate<1532) + 95*(shiftdate<1353)
   
    #create the figure
    ax = P.subplot(111)
    P.title(title)

    ax.scatter(shiftdate, corrfocus, s = 6,
               label = 'No breathing correction')
    ax.plot(desorpdays, SMdesorp, lw = 1.3, c = 'r',
            label = 'Double Exponent RvdM')
    ax.plot(desorpdays, SMdesorp2, lw = 1.3, c = 'g', ls='--',
            label = 'Double Exponent CC')

    ax.set_xlim(0, max(shiftdate)+100)
    ax.set_ylim(-20, 150)
    
    ax.set_xlabel('Days since HST Deployment, April 1990')
    ax.set_ylabel('Accumulated OTA shrinkage in SM microns')

    #minor ticks
    xmajorLocator = MultipleLocator(1000)
    xminorLocator = MultipleLocator(200)
    xmajorFormattor = FormatStrFormatter('%i')
    xminorFormattor = NullFormatter()
    ax.xaxis.set_major_locator(xmajorLocator)
    ax.xaxis.set_major_formatter(xmajorFormattor)
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)
    #y
    ymajorLocator = MultipleLocator(50)
    yminorLocator = MultipleLocator(10)
    ymajorFormattor = FormatStrFormatter('%i')
    yminorFormattor = NullFormatter()
    ax.yaxis.set_major_locator(ymajorLocator)
    ax.yaxis.set_major_formatter(ymajorFormattor)
    ax.yaxis.set_minor_locator(yminorLocator)
    ax.yaxis.set_minor_formatter(yminorFormattor)

    P.legend()
    P.savefig(output_folder+output)
    P.close()
    
def confocality(type, input_folder, output_folder):
    '''
    Creates a plot where WFC3 UVIS focus is compared to ACS WFC.
    '''
    file = 'BreathingCorrectedData.txt'    
    data = N.loadtxt(input_folder + file, skiprows=1,
                     dtype={'names': ('Julian', 'J-L', 'Focus', 'Error', 'Camera'),
                            'formats':('i4','i4','f4', 'f4', 'S6')})    
    
    newdata = data[data['J-L'] > 7040]
    
    acsdata = newdata[newdata['Camera'] == 'ACS']
    wfcdata = newdata[newdata['Camera'] == 'WFC3']
    
    delta = acsdata['Focus'] - wfcdata['Focus']
    
    #add errors in quadrature
    errs = N.sqrt(acsdata['Error']**2 + wfcdata['Error']**2)
    
    print '\nACS-WFC3 focus, mean \pm error, and std', delta.mean(), delta.std()/N.sqrt(len(delta)), delta.std()

    fig = P.figure()
    ax = fig.add_subplot(111)
    ax.errorbar(wfcdata['J-L'], delta, yerr=errs, fmt = 'bo', label ='Confocality')
    ax.axhline(0, color = 'g', lw = 1.0)
    ax.axhline(N.mean(delta), color = 'r', ls = '--', label = 'Mean')
    ax.axhline(N.median(delta), color = 'magenta', ls = '-.', label = 'Median')
    
    str = 'Mean: %.3f\n$\sigma$: %.3f\nMedian: %.3f' % (N.mean(delta), N.std(delta), N.median(delta))
    ax.annotate(str, xy = (0.8, 0.2),
                xycoords = 'axes fraction',
                verticalalignment='center')

    times = []
    for m in ax.get_xticks():
        x = D.datetime(*j.fromJulian(m + 48005.0)[0:6]).strftime('%d\n%b\n%Y')
        times.append(x)
    ax.set_xticklabels(times) 
    ax.set_ylabel('$\Delta$Focus (ACS - WFC3) [$\mu$m]')
    ax.set_ylim(-3, 3)
    P.legend(scatterpoints = 1, numpoints = 1, loc = 'upper left')
    P.savefig(output_folder + 'Confocality' + type)

if __name__ == '__main__':  
    #input data
    input_folder = '/Users/niemi/Desktop/Focus/plots/'
    output_folder = '/Users/niemi/Desktop/Focus/plots/'
    #type of the output files
    type = '.pdf'
    
    #creates plots
    FocusTrend(4600, 7040, 'Focus Trend Since Dec 2002 Mirror Move', type,
               input_folder, output_folder)
    FocusTrendNoBreathing(4600, 7040, 'Focus Trend Since Dec 2002 Mirror Move',
                          type, input_folder, output_folder,
                          output = 'FocusTrendNoBreathing')
    FocusTrend(5300, 7040, 'Focus Trend Since Dec 2004 Mirror Move',
               type, input_folder, output_folder,
               output = 'FocusTrend2')
    print '\n\nFocus Trend Since Dec 2002 Mirror Move (Breathing Correction):'
    FocusTrendRemoveLatestMovement(4700, 8500, 'Focus Trend Since Dec 2002 Mirror Move',
                                   type, input_folder, output_folder)  
    print '\n\nFocus Trend Since Dec 2002 Mirror Move (No Breathing Correction):'
    FocusTrendRemoveLatestMovementNoBreathing(4700, 8500,
                                              'Focus Trend Since Dec 2002 Mirror Move',
                                              type, input_folder, output_folder)      
    print '\n\nFocus Trend Since Launch (No Breathing Correction):'
    FocusTrendSinceDayZeroDates2('TotalFocusDates' + type,
                                 input_folder, output_folder)

    print '\n\nFocus Trend Since Dec 2002 Mirror Move (Breathing Correction):'
    FocusTrendRemoveLatestMovementOffset(4700, 8500,
                                         'Focus Trend Since Dec 2002 Mirror Move',
                                         type,
                                         input_folder, output_folder)  

#    print '\nFocus Trend Since Dec 2002 Mirror Move (No Breathing Correction, but Offset applied):'
#    FocusTrendRemoveLatestMovementNoBreathingOffset(4700, 8500,
#                                                    'Focus Trend Since Dec 2002 Mirror Move',
#                                                    type,
#                                                    input_folder, output_folder)      

    confocality(type, input_folder, output_folder)

    #old and obsolete plots
    #FocusTrendSinceDayZero(title = 'HST Focus Measurements (PC \& HRC)', output = 'TotalFocusStep.pdf', stepFunction = True)
    #FocusTrendSinceDayZeroDates(title = 'HST Focus Measurements (PC \& HRC)', output = 'TotalFocusDates2.pdf')    
    #FocusTrendSinceDayZero(title = 'HST Focus Measurements (PC \& HRC)', output = 'TotalFocus.pdf')    
    #FocusTrendSinceDayZeroOLD(title = 'HST Focus Measurements (PC \& HRC)', output = 'TotalFocusOLD.pdf')
