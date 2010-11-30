import numpy as N

#Creates a dummy class of a build-in object type
#does not do really anything yet (pass)
class Dummy(object): pass

#Returned value of Dummy class is reference to Dummy object
#lets create statistics which is a an instance of the Dummy class:
statistics = Dummy()

#lets see what Python knows about this instance
print 'statistics:', statistics

#creates random data and prints it out
data =  N.random.rand(10)
print 'data:', data

#We can use statistics as a "data holder"
#Lets assing some attributes to the statistics instance:
statistics.std = N.std(data)
statistics.max = N.max(data)
statistics.min = N.min(data)
statistics.mean = N.mean(data)
#Each assigned element (std, max, etc.) is an attribute of the class

#Lets print out some of the attribute values:
print 'statistics.std & statistics.mean', statistics.std, statistics.mean
#We have now pulled out info from the statistics object

#testing if an object has an attribute:
print 'Attribute std?', hasattr(statistics, 'std')
print 'Attribute median?', hasattr(statistics, 'median')

#And the best part, lets see what we have really done!!
print '\n\n\nWhy-o-why did we really do this?:\n', statistics.__dict__
