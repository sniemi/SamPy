# Linear regression example
# including confidence intervals for params
from scipy import linspace, polyval, polyfit, sqrt, stats, randn
from pylab import figure, plot, title, show , legend, xlabel, ylabel, grid
from numpy import arange, linspace, mean, std, zeros, ones
from numpy import loadtxt, array
import scipy.interpolate

## definition
def mylinearregression(x,y,confidence_level):
    """
    function to calculate simple linear regression
    inputs: x,y-data pairs and a confidence level (in percent)
    outputs: slope = b1, intercept = b0 its confidence intervals
    and R (+squared)
    """
    show_plots = 'on'        # 'on' to show data, fit and conf interval
    x_average = mean(x)
    x_stdev = std(x)
    y_average = mean(y)
    y_stdev = std(y)
    n = len(x)
    # calculate linear regression coefficients
    b1 = sum((x-x_average)*(y-y_average))/sum((x-x_average)**2)  
    b0 = y_average - b1 * x_average
    #sample_correlation = b1*x_stdev/y_stdev
    # calculate residuals (observed - predicted)
    TotSS = sum((y-y_average)**2)   # Total Sum of Squares
    y_hat = b1 * x + b0             # fitted values
    ResSS = sum((y-y_hat)**2)       # Residual Sum of Squares
    # calculate standard deviations of fit params
    b1_stdev = sqrt((ResSS/(n-2))/sum((x-x_average)**2))        
    b0_stdev = b1_stdev*sqrt(sum(x**2)/n)    
    # compute the mean square error (variance) and standard error (root of var), R2 and R
    mserr = ResSS/n-2
    sterr = sqrt(mserr)
    R2 = 1 - ResSS/TotSS
    R = sqrt(R2)
    # Pearson's r (this is the same as sample_correlation)  
    #pearsonsr = (sum(x*y)-(sum(x)*sum(y))/n)/sqrt((sum(x**2)-sum(x)**2/n)*(sum(y**2)-sum(y)**2/n))
    #print 'Pearsons r = %.3f ' %(pearsonsr)

    ## calculate confidence interval
    # alpha
    alpha = 1.-(confidence_level*1./100.)
    # degrees of freedom (2 lost by estimates of slope and intercept)
    DF = n-2
    # critical value (look up in t table)
    cv = 2.01
    # Margin of error = Critical value x Standard error of the statistic 
    moe_b1 = cv * b1_stdev 
    moe_b0 = cv * b0_stdev
    lower_b1 = b1-moe_b1
    upper_b1 = b1+moe_b1
    lower_b0 = b0-moe_b0
    upper_b0 = b0+moe_b0
    print ' Report of linear regression:'
    print ' Slope = %.4f +/- %.4f, Intercept = %.4f +/- %.4f' %(b1, moe_b1, b0, moe_b0)
    print ' %g percent confidence interval for slope: %.4f to %.4f' %(confidence_level, lower_b1, upper_b1)
    print ' %g percent confidence interval for intercept: %.4f to %.4f' %(confidence_level, lower_b0, upper_b0)
    # compute confidence lines for plot
    lower = upper_b1 * x + lower_b0
    upper = lower_b1 * x + upper_b0
    
    if show_plots == 'on':
        figure(1000)
        title('My Linear Regression')
        xlabel('x')
        ylabel('y')
        grid()
        plot(x,y,'bo', label='data')
        plot(x,y_hat,'r.-', label='linear fit')
        plot(x,lower,'c-')
        plot(x,upper,'c-')
        legend(loc='best',numpoints=3)
        # are the residuals normally distributed?
        figure(1001)
        title('Residuals of fit')
        xlabel('x')
        ylabel('Residuals')
        grid()
        plot(x,y-y_hat,'mo')
    return b1,b0,lower_b1,upper_b1,lower_b0,upper_b0,R2,R

### program start: choose wiki data or random data
## WIKIPEDIA DATA
## http://en.wikipedia.org/wiki/Simple_linear_regression
x = [1.47,1.50,1.52,1.55,1.57,1.60,1.63,1.65,1.68,1.70,1.73,1.75,1.78,1.80,1.83]
y = [52.21,53.12,54.48,55.84,57.20,58.57,59.93,61.29,63.11,64.47,66.28,68.10,69.92,72.19,74.46]
x = array(x)
y = array(y)
## Random Sample data creation
n=50
x=linspace(-5,5,n)
#parameters
a=0.7; b=-4
y=polyval([a,b],x)
#add some noise
y=y+randn(n)
print ' Run simple linear regression:'
b1,b0,lower_b1,upper_b1,lower_b0,upper_b0,R2,R = mylinearregression(x, y, 95)
show()
