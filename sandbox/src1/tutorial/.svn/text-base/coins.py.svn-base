from numpy import *
import numpy.random as ra

prob = 0.4 # probablity for heads
n2h = n2t = 0. # number of successes for double heads and tails
trials = 1000000 # number of parallel trials in ensemble
# start with array indicating first toss (0-->tails, 1-->heads)
prev = ra.random(trials) < prob
while trials > 0:
    next = ra.random(trials) < prob
    notdone = next != prev
    # careful with summing boolean arrays!
    n2h += sum(1.*(prev & next)) # two heads in a row
    n2t += sum(1.*logical_not(prev | next)) # two tails
    prev = next[notdone]
    trials = len(prev)
    print trials

print "double heads =", n2h
print "double tails =", n2t

predicted = prob**2*(2.-prob)/(1.-prob*(1.-prob))
print "expected fraction double heads =", predicted    
