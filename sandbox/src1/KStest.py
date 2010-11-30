
import numpy as N
import scipy.stats as S

file1 = "sigv_uzc.hist"
file2 = "sigv_hg82.hist"
column1 = 4
column2 = 4

data1 = N.loadtxt(file1)
data2 = N.loadtxt(file2)

x = data1[:,column1]
y = data2[:,column2]

print x
print 
print y

KS = S.stats.ks_2samp(x,y)

print "Results of the KS-test"
print "D = %f\np = %e" % (KS[0], KS[1])

