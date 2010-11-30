from matplotlib.matlab import *

x = randn(10000) # some gaussian noise

subplot(211) # a subplot
hist(x, 100) # make a histogram
grid(True) # make an axes grid
ylabel('histogram')

# now do the regression...
x = arange(0.0, 2.0, 0.05)
y = 2+ 3*x + 0.2*randn(len(x)) # y is a linear function of x + nse

# the bestfit line from polyfit
m,b = polyfit(x,y,1) # a line is 1st order polynomial...

# plot the data with blue circles and the best fit with a thick
# solid black line
subplot(212)
plot(x, y, 'bo', x, m*x+b, '-k', linewidth=2)
ylabel('regression')
grid(True) 

# save the image to hardcopy
savefig('demo')
show()
