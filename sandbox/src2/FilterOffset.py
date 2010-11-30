#!/usr/bin/env python
# -*- encoding: utf-8 -*-

#This script calculates some linear fits and correlations for filter data.
#It fits first order polynom, calculates the mean square error and plots the data.
#It also calculates Spearman rank-order correlation which can be
#used to define if linear correlation is significant.
#The two tailed probabilities are also given to ease out the pain caused
#by the defining of the significance levels.

#11/06/2008 Sami-Matias Niemi for NOT

if __name__ == '__main__':
    from scipy.stats import *
    import numpy
    from pylab import *
    from scipy import polyval, polyfit, sqrt
    from fit_help import *

    #reads the data
    dataAll = numpy.loadtxt("f.dat", comments='#', skiprows=1)
 
    #marks only the ones which fulfil criterion
    indices = numpy.where(dataAll[:,2] != 999) 

    #now data contains the original table without 999:s
    data = dataAll[indices]
 
    #gets correct column
    lam = data[:,1]
    FWHM = data[:,2]
    thick = data[:,3]
    foff = data[:,4]
 
    #Initial parameter:
    a = Parameter(20.)
    pname = (['slope'])
    #function to be fitted
    def func(x): return a()*x
    #fitting
    afinal = fitSMN(func, [a], foff, thick) 
    fitted = pevalSMN(func, foff)
    
    print "\nLinear fit so that the line will go through (0,0):"
    print "Final parameters:"
    for i in range(len(pname)):
        print "%s = %.4f " % (pname[i], afinal)

    #Another way of fitting using polyfit:
    a=20; b=0
    xdata = thick
    ydata = foff
    x = polyval([a,b],xdata)
    ar, br= polyfit(xdata,ydata,1)
    yfit = polyval([ar, br],xdata)
    #Computes the mean square error:
    err = sqrt(sum((yfit-ydata)**2)/(shape(ydata)[0]))
   
    print("\nLinear regression using polyfit:" )    
    print('Initial values: a=%.2f b=%.2f \nregression: a=%.4f b=%.4f, mean square error= %.5f' % (a,b,ar,br,err))

    #Linear regression will give the fit directly without polyfit and polyval
    Lincorrtf = linregress(thick,foff)
    Lincorrlf = linregress(lam,foff)
    
    #Lets get some statistics:
    Corrtf = spearmanr(thick,foff)
    Corrlf = spearmanr(lam,foff)

    print "\nCorrelations for filter thickness vs. offset"
    print "Spearman rank-order correlation coefficient and the p-value :\n%f and %e" % (Corrtf[0], Corrtf[1])
    print "Linear Correlation (slope, intercept, r, two-tailed prob, stderr-of-the-estimate):\n%f, %f, %f, %e and %f" % (Lincorrtf[0], Lincorrtf[1], Lincorrtf[2], Lincorrtf[3], Lincorrtf[4])
    
    print "\nCorrelations for filter residuals and offset" 
    print "Spearman rank-order correlation coefficient and the p-value :\n%f and %e" % (Corrlf[0], Corrlf[1])
    print "Linear Correlation (slope, intercept, r, two-tailed prob, stderr-of-the-estimate):\n%f, %f, %f, %e and %f" % (Lincorrlf[0], Lincorrlf[1], Lincorrlf[2], Lincorrlf[3], Lincorrlf[4])
    
    #Plots the data:
    figure(1)
    title('Filters thickness vs. offset')
    plot(thick, foff, 'bo')
    plot([0.,11.],[Lincorrtf[1],11.*Lincorrtf[0]+Lincorrtf[1]], 'r-.', linewidth=1.5, label = 'Linear Fit')
    plot([0.,11.],[0,11.*afinal], 'g-', linewidth=1.5, label = 'Linear Fit through (0,0)')
    legend()
    xlabel('Filter thickness [mm]')
    ylabel('Filter offset [telescope units]')
    limitstemp=[3.5,11,0,250]
    axis(limitstemp)
    savefig('thickOffset.eps')
    
    figure(2)
    title('Filter residuals vs. offset')
    plot(lam, foff, 'bo')
    plot([0.,800],[Lincorrlf[1],800.*Lincorrlf[0]+Lincorrlf[1]], 'r.-', linewidth=1.5, label = 'Linear Fit')
    legend()
    xlabel('Residuals')
    ylabel('Filter offset [telescope units]')
    limits=[300,800,55,220]
    axis(limits)
    savefig('residualsOffset.eps')
    
    #Shows the data in X11 windows...
    show()
