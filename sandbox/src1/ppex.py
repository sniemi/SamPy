#!/usr/bin/python
import os
import pp
 
 
def calculate(i, j):
    print os.popen("ps").read()
    return i*j
 
 
n = 2
#start ppsmp server with n processes
ppservers = ()
job_server = pp.Server(n, ppservers=ppservers)
 
f = []
 
N = 3
 
for i in range(0,N):
  for j in range(0,N):
      #it might be a little bit more complex if 'calculate' depends on
      f.append(job_server.submit(calculate, (i,j), (), ("os",)))
 
for i in range(0,N):
  for j in range(0,N):
     print i, "*", j, "=", f.pop(0)()
