import matplotlib
matplotlib.rc('text', usetex = True)
matplotlib.rc('xtick', labelsize = 9)
matplotlib.rc('ytick', labelsize = 9)
matplotlib.rc('axes', linewidth=0.8)
matplotlib.rcParams['legend.fontsize'] = 11
import idlsave, time
import pylab as P
import numpy as N
import datetime as D
from matplotlib.ticker import MultipleLocator

def mylinearregression(x, y, confidence_level = 95, show_plots = False, report = False):
    """
    function to calculate simple linear regression
    inputs: x,y-data pairs and a confidence level (in percent)
    outputs: slope = b1, intercept = b0 its confidence intervals
    and R (+squared)
    """
    #Basic statistics
    x_average = N.mean(x)
    x_stdev = N.std(x)
    y_average = N.mean(y)
    y_stdev = N.std(y)
    n = len(x)

    if n == 2:
        #print 'Only 2 degrees of freedom, cannot calculate errors...'
        return 0,0,0

    # calculate linear regression coefficients
    b1 = N.sum((x-x_average)*(y-y_average))/N.sum((x-x_average)**2)  
    b0 = y_average - b1 * x_average

    # calculate residuals (observed - predicted)
    TotSS = N.sum((y-y_average)**2)   # Total Sum of Squares
    y_hat = b1 * x + b0               # fitted values
    ResSS = N.sum((y-y_hat)**2)       # Residual Sum of Squares

    # calculate standard deviations of fit params
    b1_stdev = N.sqrt((ResSS/(n-2))/N.sum((x-x_average)**2))        
    b0_stdev = b1_stdev*N.sqrt(N.sum(x**2)/n)
    
    # compute the mean square error (variance) and standard error (root of var), R2 and R
    mserr = ResSS/(n-2)
    sterr = N.sqrt(mserr)
    R2 = 1 - ResSS/TotSS
    R = N.sqrt(R2)

    ## calculate confidence interval
    alpha = 1.-(confidence_level*1./100.)
    # degrees of freedom (2 lost by estimates of slope and intercept)
    DF = n-2
    # critical value (from t table)
    cv = 2.01
    # Margin of error = Critical value x Standard error of the statistic 
    moe_b1 = cv * b1_stdev 
    moe_b0 = cv * b0_stdev
    lower_b1 = b1 - moe_b1
    upper_b1 = b1 + moe_b1
    lower_b0 = b0 - moe_b0
    upper_b0 = b0 + moe_b0

    if report:
        print 'Report of linear regression:'
        print N.polyfit(x,y,1)
        print 'Slope = %.6f +/- %.4f, Intercept = %.4f +/- %.4f' %(b1, moe_b1, b0, moe_b0)
        print '%g percent confidence interval for slope: %.4f to %.4f' %(confidence_level, lower_b1, upper_b1)
        print '%g percent confidence interval for intercept: %.4f to %.4f' %(confidence_level, lower_b0, upper_b0)
   
    # compute confidence lines for plot
    lower = upper_b1 * x + lower_b0
    upper = lower_b1 * x + upper_b0
    
    if show_plots:
        P.figure(1000)
        P.title('My Linear Regression')
        P.xlabel('x')
        P.ylabel('y')
        P.grid()
        P.plot(x,y,'bo', label='data')
        P.plot(x,y_hat,'r.-', label='linear fit')
        P.plot(x,lower,'c-')
        P.plot(x,upper,'c-')
        P.legend(loc='best',numpoints=3)
        # are the residuals normally distributed?
        P.figure(1001)
        P.title('Residuals of fit')
        P.xlabel('x')
        P.ylabel('Residuals')
        P.grid()
        P.plot(x,y-y_hat,'mo')
        P.show()
    return b1,moe_b1,b0,lower_b1,upper_b1,lower_b0,upper_b0,R2,R

def findDifferentRatios(dict):
    result = {}
    rats = set(x[3] for x in dict.values())
    for x in rats:
        for _t in dict:
            if x == dict[_t][3]:
                if result.has_key(x):
                    result[x].append(dict[_t])
                else:
                    result[x] = [dict[_t],]
    return result

def fromJulian(j):
    '''
    Converts Julian Date to human readable format
    @return: human readable date and time
    '''
    days = j - 2440587.5
    sec = days*86400.0
    return time.gmtime(sec)

data = idlsave.read('nes_all.dat')

exclude_first = True
legend = False

#titles = ['G185M / G225M @ 2100\AA',
#          'G185M / G225M @ 2130\AA',
#          'G225M / G285M @ 2490\AA',
#          'G225M / G285M @ 2510\AA',
#          'G185M / G230L @ 2130\AA',
#          'G225M / G230L @ 2130\AA',
#          'G285M / G230L @ 2490\AA',
#          'G285M / G230L @ 2510\AA',       
#          'G285M / G230L @ 2620\AA',
#          'G285M / G230L @ 2750\AA',       
#          'G230L / G230L @ 2490\AA',
#          'G225M / G230L @ 2490\AA']

sang = '\AA'
titles = ['G185M (1986'+sang+') / G225M (2186'+sang+') @ 2100'+sang,
          'G185M (2010'+sang+') / G225M (2217'+sang+') @ 2130'+sang,
          'G225M (2390'+sang+') / G285M (2617'+sang+') @ 2490'+sang,
          'G225M (2410'+sang+') / G285M (2637'+sang+') @ 2510'+sang,
          'G185M (2010'+sang+') / G230L (3360'+sang+') @ 2130'+sang,
          'G225M (2217'+sang+') / G230L (3360'+sang+') @ 2130'+sang,
          'G285M (2617'+sang+') / G230L (2635'+sang+') @ 2490'+sang,
          'G285M (2637'+sang+') / G230L (2635'+sang+') @ 2510'+sang,
          'G285M (2617'+sang+') / G230L (2635'+sang+') @ 2620'+sang,
          'G285M (2637'+sang+') / G230L (2635'+sang+') @ 2750'+sang,
          'G230L (2635'+sang+') / G230L (3360'+sang+') @ 2490'+sang+' / 2130'+sang,
          'G225M (2390'+sang+') / G230L (2635'+sang+') @ 2490'+sang]


c = 1
fig = P.figure(0)

#ran = range(4,8)
ran = range(12)

extra_ratio_name = 'G225M (2410\AA) / G230L (2635\AA) @ 2510\AA'
#extra_ratio = (data.f_irats[:, 3] / N.mean(data.f_irats[:,3]))* (data.f_irats[:, 7] / N.mean(data.f_irats[:,7]))
extra_ratio = data.f_irats[:, 3]* data.f_irats[:, 7]

print data.f_irats[:, 3], N.mean(data.f_irats[:, 3])
print
print data.f_irats[:, 7], N.mean(data.f_irats[:, 7])

titles[10] = extra_ratio_name
data.f_irats[:,10] = extra_ratio
data.f_ierats[:,10] = N.sqrt(data.f_ierats[:,3]**2 + data.f_ierats[:,7]**2)

summary = {}
for i in ran:
    print
    print titles[i]
    if exclude_first:
        start = 1
        print 'All below fits exclude the first point shown in the plots as it was measured under different conditions'
    else:
        start = 0

    #normalization of plots
    #average and dates
    #avg_r = N.mean(data.f_irats[start:,i])
    #avg_r = N.mean(data.f_irats[:,i])
    avg_r = data.f_irats[0,i]

    all_mjd = data.jdates
    mjd = data.jdates[start:]

#    if i == 10:
#        avg_r = N.mean(extra_ratio)


    #plot
    ax = fig.add_subplot(6,2,c)
    ax.set_title(titles[i], fontsize = 8, va = 'center')

    #all data points with errorbars
    P.errorbar(all_mjd, data.f_irats[:,i]/avg_r, yerr = data.f_ierats[:,i]/avg_r, marker = 'o', ms = 4)
    P.axhline(y = 1, c = 'k', ls = ':')
    
    #linear fit, whole data
    fit = N.polyfit(mjd, data.f_irats[start:,i]/avg_r, 1)
    p = N.poly1d(fit)
#    P.plot(all_mjd, p(all_mjd), 'r--', label = 'lin fit, no first point')
    tmp = mylinearregression(mjd, data.f_irats[start:,i]/avg_r)
    print 'Plot %i, change %f +/- %f per cent per year, all data. Not plotted.' % (c, fit[0]*356.*100., tmp[1]*356.*100.)

    #linear fit to on orbit data
    msk = all_mjd > 2454970.0
    fit2 = N.polyfit(all_mjd[msk], data.f_irats[msk,i]/avg_r, 1)
    p2 = N.poly1d(fit2)
    P.plot(all_mjd, p2(all_mjd), 'g:', lw  = 3, label = 'lin fit, on orbit data')
    tmp = mylinearregression(all_mjd[msk], data.f_irats[msk,i]/avg_r)
    print 'Plot %i, change %f +/- %f per cent per year, only on orbit data (%i points). Green dotted line.' % (c, fit2[0]*356.*100., tmp[1]*356.*100., len(all_mjd[msk]))

    #fit without the two outliers
    mask = (all_mjd < 2454679.0) | (all_mjd > 2454904.0)
    fit3 = N.polyfit(all_mjd[mask], data.f_irats[mask,i]/avg_r, 1)
    p3 = N.poly1d(fit3)
    P.plot(all_mjd[mask], p3(all_mjd[mask]), 'm-.', label = 'lin fit, no outliers')
    tmp = mylinearregression(all_mjd[mask], data.f_irats[mask,i]/avg_r)
    print 'Plot %i, change %f +/- %f per cent per year, all data excluding the two outliers. Magenta dot-dashed.' % (c, fit3[0]*356.*100., tmp[1]*356.*100.)
    
    #fit to ground data, excluding the two last ground measurements
    mask4 = all_mjd < 2454679.0
    fit4 = N.polyfit(all_mjd[mask4], data.f_irats[mask4,i]/avg_r, 1)
    p4 = N.poly1d(fit4)
    P.plot(all_mjd, p4(all_mjd), 'r--', label = 'lin fit, ground data')
    tmp = mylinearregression(all_mjd[mask4], data.f_irats[mask4,i]/avg_r)
    print 'Plot %i, change %f +/- %f per cent per year, ground data excluding the two clear outliers. Red hatched line.' % (c, fit4[0]*356.*100.,tmp[1]*356.*100.)

    #limit the y axis
    P.ylim(0.50, 1.4)
    P.xlim(N.min(all_mjd)-35, N.max(all_mjd)+55)
    #legend
    if legend: P.legend(shadow = True, fancybox = True)

    #fix labels
    times = []
    if c == 11 or c == 12:
        for m in ax.get_xticks():
            x = D.datetime(*fromJulian(m)[0:6]).strftime('%d %b\n%Y')
            times.append(x)
        ax.set_xticklabels(times)
        #size
        for tl in ax.get_xticklabels(): tl.set_fontsize(8)
    else:
        ax.set_xticklabels(times)

    ax.set_yticks(ax.get_yticks()[::2])

    c += 1

    #Data for the summary plot
    #if i != 10:
    r = titles[i]
    cenw = r[r.find('@')+1:r.rfind('AA')-1].strip()
    tit = r[r.find('G'):5] + '/' + r[r.rfind('G'):r.rfind('G')+5]
    #original
    #summary[i] = [int(cenw), fit3[0]*356.*100., tmp[1]*356.*100., tit]
    #Ground data, excluding three points
    summary[i] = [int(cenw), fit4[0]*356.*100., tmp[1]*356.*100., tit]




P.suptitle('Normalized Relative Efficiency of COS NUV gratings', fontsize = 14)

P.savefig('NUVALLGET.ps')

####################################################################################################
#Summary plot

data = findDifferentRatios(summary)
skeys = sorted(data.keys())

marks = ['D', 'H', 'o', 'p', 's', 'v', 'd', '*']
colors = ['b', 'r', 'g', 'm', 'c', 'y', 'k', 'w']

fig = P.figure(2)
ax = fig.add_subplot(111)
ax.axhline(0, c = 'k', ls ='--')

for i, x in enumerate(skeys):
    for y in data[x]:
        t = ax.errorbar(y[0], y[1], yerr = y[2], marker = marks[i], ms = 13, c = colors[i], label = x)
    #ax.set_label(x) #does not work on old matplotlib

ax.set_ylabel('\% / yr', fontsize = 13)
ax.set_xlabel('Wavelength (\AA)', fontsize = 13)

for tl in ax.get_xticklabels(): tl.set_fontsize(13)
for tl in ax.get_yticklabels(): tl.set_fontsize(13)

P.xlim(2050, 2800)
P.ylim(-10, 10)

ax.yaxis.set_minor_locator(MultipleLocator(1))

#super ungly fix for the legend
r = []
rr = []
handles, labels = ax.get_legend_handles_labels()
for x in set(labels):
    for a, b in zip(handles, labels):
        if x == b:
            r.append(a)
            rr.append(b)
            break
#sort
import operator
hl = sorted(zip(r, rr), key=operator.itemgetter(1))
handles2, labels2 = zip(*hl)

leg = P.legend(handles2, labels2, shadow = True, fancybox = True, numpoints = 1)
#leg = P.legend(shadow = True, fancybox = True, numpoints = 1, ncol=3)

P.savefig('NUVGETsummary.ps')
