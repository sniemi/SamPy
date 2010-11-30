#!/usr/bin/python

# Output file path for log
logpath = '/home/postprocess/seeing_mon/logs' 

pymodules = '/home/postprocess/python_modules'
import sys
sys.path.append(pymodules)
import dbhandler
from postprocess import *

# Open a MySQL connection
dh = dbhandler.MySQLhandler()

tbls = ['AL','MO','NC','ST']

# Loop over every instrument seeing table
for tbl in tbls:

  # Get all seeing data with empty system IDs
  try:
    data = dh.getSeeingData(tbl)
  except dbhandler.DBException, e:
    writeLog(logpath,'Table Update',str(e))
    continue

  # Loop over every seeing measurement and fetch 
  # the IDs from SystemStatus table closest to midpoint of exposure,
  # DIMM measurements and update table 
  for d in data:
  
     try:  
       id_dct = dh.getSystemIDs(d['DateTimeUT'],d['EXPTIME'])	
     except dbhandler.DBException, e:
       writeLog(logpath,str(d['id']),str(e))
       continue
  	  	
     if not id_dct:
       writeLog(logpath,str(d['id']),'Update: No system IDs available')
       continue
       
     # Determine the time interval for which to average DIMM data
     if d['EXPTIME'] > 900:
        t1 = 0
        t2 = d['EXPTIME']
     else:
        t1 = 450 - float(d['EXPTIME'])/2
        t2 = float(d['EXPTIME'])/2 + 450

     try:  
       dimm_dct = dh.getDIMMData(d['DateTimeUT'],t1,t2)	
     except dbhandler.DBException, e:
       writeLog(logpath,str(d['id']),str(e))
       continue

     if dimm_dct['NumDIMM'] > 0:
       dimm_dct['meanDIMM']  = "%.2f" % dimm_dct['meanDIMM']
       dimm_dct['stdevDIMM'] = "%.2f" % dimm_dct['stdevDIMM']

     try:
       dh.updateSeeingData(tbl,d['id'],id_dct,dimm_dct)  	
     except dbhandler.DBException, e:
       writeLog(logpath,str(d['id']),str(e))
       continue

# Close database connection
dh.close()
