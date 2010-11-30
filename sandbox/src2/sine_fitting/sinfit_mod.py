#! /usr/bin/python
# The script contains the sin-fitting funtion for the rvel data and should be used in the program "multiple.py".
# The script "multiple.py" is run by the command "python multiple.py datafile.txt". For running all output files from rvel, run the script "runall.py".   

import sys
from scipy import *
#from scipy import optimize
from numpy import *
from math import pi

P_fixed = 0.0762233

def translate (x, phi_0, period):
   return ((x - phi_0) / period) * (2 * pi)

def residuals_withP(p, y, x):
   err = abs(y - peval_nonfixed(x, p))
   return err

def residuals_withoutP(p, y, x):
   err = abs(y - peval_fixed(x, p))
   return err

def errfunc_withoutP(p, y, x, err):
   err2 = abs((y - peval_fixed(x, p))/err)
   return err2

#function to be fitted

def peval_nonfixed(x, p):
    return p[0] - p[1]*sin(translate(x, p[2], p[3]))

def peval_fixed(x, p):
    return p[0] - p[1]*sin(translate(x, p[2], P_fixed))

def fit_model(xdata, ydata, err, PHI_0, G, K, initpar_file = "", fitpar_file = "", period=None):

   

   if period is None:
       initpars = [G,K, PHI_0]
       residuals = residuals_withoutP
       peval = peval_fixed
   else:
       initpars = [G,K, PHI_0, period]
       residuals = residuals_withP
       peval = peval_nonfixed

   output = optimize.leastsq(errfunc_withoutP, initpars, args=(ydata, xdata,err), full_output = 1)
   ##output = optimize.leastsq(residuals, initpars, args=(ydata, xdata), full_output = 1)
   updated, cov_x, infodict, mesg, ok = output
   
   corr = cov_x*0.
   for i in range(0,2):
      for j in range(0,2):
         corr[i][j]=cov_x[i][j]/(sqrt(cov_x[i][i])*sqrt(cov_x[j][j]))
      
   
   print cov_x
   print corr
  

   if err is not None:
      squared_res = [errfunc_withoutP(updated,y,x,s)**2 for (x,y,s) in zip(xdata, ydata, err)]
      ##squared_res = [(residuals(updated, y, x) / s)**2 for (x,y,s) in zip(xdata, ydata, err)]
      chi2 = sum(squared_res)
   else:
      chi2 = None

   if initpar_file != "":
      savetxt(initpar_file, zip(xdata, peval(xdata, initpars)) )
   if fitpar_file != "":
      if err is not None:
         savetxt(fitpar_file, zip(xdata, peval(xdata, updated), err) )
      else:
         savetxt(fitpar_file, zip(xdata, peval(xdata, updated)) )
   
   return updated, chi2, cov_x