#!/usr/bin/env python
# Parallel Python Software: http://www.parallelpython.com

import math, sys
import pp

def isprime(n):
    """Returns True if n is prime and False otherwise"""
    if not isinstance(n, int):
        raise TypeError("argument passed to is_prime is not of 'int' type")
    if n < 2:
        return False
    if n == 2:
        return True
    max = int(math.ceil(math.sqrt(n)))
    i = 2
    while i <= max:
        if n % i == 0:
            return False
        i += 1
    return True

print """Usage: python sum_primes.py [ncpus]
    [ncpus] - the number of workers to run in parallel, 
    if omitted it will be set to the number of processors in the system
"""

# tuple of all parallel python servers to connect with
#ppservers = ("*",) # auto-discover
#ppservers = ("10.0.0.1","10.0.0.2") # list of static IPs
ppservers = ()

if len(sys.argv) > 1:
    ncpus = int(sys.argv[1])
    # Creates jobserver with ncpus workers
    job_server = pp.Server(ncpus, ppservers=ppservers)
else:
    # Creates jobserver with automatically detected number of workers
    job_server = pp.Server(ppservers=ppservers)

print "Starting pp with", job_server.get_ncpus(), "workers"

# Submit a job of calulating sum_primes(100) for execution. 
# sum_primes - the function
# (100,) - tuple with arguments for sum_primes
# (isprime,) - tuple with functions on which function sum_primes depends
# ("math",) - tuple with module names which must be imported 
#             before sum_primes execution
# Execution starts as soon as one of the workers will become available
#job1 = job_server.submit(sum_primes, (10,), (isprime,), ("math",), callback=callback)

# Retrieves the result calculated by job1
# The value of job1() is the same as sum_primes(100)
# If the job has not been finished yet, 
# execution will wait here until result is available
#result = job1()

#print "Sum of primes below 10 is", result

inputs = range(10000000,10100000)

ajo = pp.Template(job_server, isprime, (), ("math",))

jobs = [(input, ajo.submit(input)) for input in inputs]

for input, job in jobs:
    if (job() == True):
        print "Number %i is a prime number" % input

print "Run done with ", job_server.get_ncpus(), "workers"
job_server.print_stats()

# Parallel Python Software: http://www.parallelpython.com
