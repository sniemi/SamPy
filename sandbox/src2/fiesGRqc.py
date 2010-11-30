#!/usr/bin/python

# The FIES Gain/Ron measurement is written in the last line of the
# database, by the data-reduction script 'fiesgainron.py' .
#
# This is a script that performs Quality Control on this latest
# measurement that was added to the FIES Gain/Ron database.
#
# This script reads the latest line of database 'fiesgainron.database',
# and then extracts all other entries with the same amplifier, gain, and
# binning settings.
#
# All data, except the latest measurement(!), are least-squares fitted
# with a straight-line y(x) = A + Bx, and a single clipping iteration
# is performed to discard the outliers from the fit.  A new fit is
# done on the remaining accepted data, again without the latest entry.
#
# Then, the latest entry is compared against the second fit
# and a warning email is sent if an offlying value is found.
#
# JHT, Jan 2006

verbose=True
#verbose=False

# Set data clipping value: previous data that is off by more than
# cut*RMS will be discarded in the fits.  If the new point is off by
# more than cut*RMS, this script will send a warning email.
# Note: RMS = root of mean squares
cut=2.5

database='/home/qc-user/fies/gainron/fiesgainron.database'
emailaddress='jht@not.iac.es'



def timeday2007(datestr):
   # Convert FITS header DATE-OBS string to a (float) time in days wrt 2007-01-01T00:00:00
 
   from time import mktime

   #print datestr[0:4], datestr[5:7], datestr[8:10], datestr[11:13], datestr[14:16], datestr[17:19]
   timesec=mktime((int(datestr[0:4]), int(datestr[5:7]), int(datestr[8:10]), int(datestr[11:13]), \
                   int(datestr[14:16]), int(datestr[17:19]), 0, 0, 0))
   timeday = timesec/86400 - 13514
   #print datestr, timesec, timesec/86400 - 13514

   return (timeday)



def leastSQs(x,y,s):
   # Least-squares fit of straight line  y(x) = A + Bx
   # Input: data arrays X and Y,  and the clipping parameter s.
   # Returns: A, B, rms, and array indexes of data that lies s*RMS from the fit.

   from math import sqrt

   # Do summations
   i=0
   xsum=0.0
   ysum=0.0
   xxsum=0.0
   xysum=0.0
   while i<len(x):
     xsum =xsum  + x[i]
     ysum =ysum  + y[i]
     xxsum=xxsum + x[i]*x[i]
     xysum=xysum + x[i]*y[i]
     i=i+1

   # Solve least squares fit
   B = (xysum-xsum*ysum/i) / (xxsum-xsum*xsum/i)
   A = (ysum-B*xsum)/i

   # Find RMS around fit
   i=0
   rms=0.0
   while i<len(x):
     rms=rms+(y[i] - A - B*x[i])**2
     i=i+1
   rms=sqrt(rms/i)

   # Find outliers: fill 'outliers' array with indexes
   i=0
   outliers = []
   while i<len(x):
     flag = 0
     if abs(y[i]-A-B*x[i])>s*rms: 
        outliers.append(i)
        flag = 1
     if verbose: print "%d %10.5f %10.3f %10.3f %10.3f %10.3f %d" % \
                       (i, x[i], y[i], A+B*x[i], y[i]-A-B*x[i], (y[i]-A-B*x[i])/rms, flag)
     i=i+1

   return(A,B,rms,outliers)



def fitAndCheck (x,y,cutlevel,xc,yc):
   # Fits straight line to X,Y array data, with one clipping iteration,
   # and afterwards checks whether the additional point (xc,yc) is within
   # a Y-distance of cutlevel*RMS of the fit.    
   # The additional point (xc,yc) is not taking part in the fits.
   # 
   # Returns 1 if the additional point is an outlier, 0 if it is OK.
 

   # Do the first fit
   if verbose: print "\nFirst fit:"
   (aa,bb,rms,outs) = leastSQs(x, y, cutlevel)

   # Discard the outliers: copy only accepted points to new arrays
   i=0
   newx=[]
   newy=[]
   while i<len(x):
      if outs.count(i)==0:
         newx.append(x[i])
         newy.append(y[i])
      i=i+1

   # Do the second fit
   if verbose: print "Re-Fit on accepted points:"
   (aa,bb,rms,outs) = leastSQs(newx, newy, cutlevel)

   # Check additional data point
   flag = 0
   flagtext = ""
   if abs(yc - aa - bb*xc) > cutlevel*rms:  
      flag=1
      flagtext = "Alarm!"
   if verbose: print "Check additional point\n- %10.5f %10.3f %10.3f %10.3f %10.3f %d %s" % \
                        (xc, yc, aa+bb*xc, yc-aa-bb*xc, (yc-aa-bb*xc)/rms, flag, flagtext)

   if flag==1:  return(1)

   return(0)
  


######## main part starts here ########

# Read all database entries into memory
fd=open(database,'r')
dblines=fd.readlines()
fd.close()

# Read detector settings from last entry
obsdate = dblines[-1].split()[0]
amplm   = dblines[-1].split()[5]
gainm   = dblines[-1].split()[6]
xbin    = dblines[-1].split()[7]
ybin    = dblines[-1].split()[8]
biasfile= dblines[-1].split()[9]

# Initialize arrays
times = []
Lg = []  # left-side gain
Lr = []  # left-side ron
Lc = []  # left-side count
Lb = []  # left-side bias
Rg = []  # right-side gain
Rr = []  # right-side ron
Rc = []  # right-side count
Rb = []  # right-side bias

# Read database entries into arrays
for line in dblines:
   # Skip commented-out lines
   if (line[0] != '#'):
      a=line.split()[5]
      g=line.split()[6]
      x=line.split()[7]
      y=line.split()[8]
      # Load only entries with same detector settings
      if (a==amplm) & (g==gainm) & (x==xbin) & (y==ybin):
         times.append(timeday2007(line.split()[0]))
         Lg.append(float(line.split()[14]))
         Lr.append(float(line.split()[16]))
         Lc.append(float(line.split()[18]))
         Lb.append(float(line.split()[19]))
         Rg.append(float(line.split()[21]))
         Rr.append(float(line.split()[23]))
         Rc.append(float(line.split()[25]))
         Rb.append(float(line.split()[26]))

# Do the fits and the checks
statusline = biasfile+' outliers:   '
if verbose: print '\n\n',obsdate, amplm, gainm, xbin, ybin, biasfile, 'Lg'
if fitAndCheck(times[:-1],Lg[:-1], cut, times[-1],Lg[-1])==1:  statusline=statusline+'Lg '

if verbose: print '\n\n',obsdate, amplm, gainm, xbin, ybin, biasfile, 'Lr'
if fitAndCheck(times[:-1],Lr[:-1], cut, times[-1],Lr[-1])==1:  statusline=statusline+'Lr '

if verbose: print '\n\n',obsdate, amplm, gainm, xbin, ybin, biasfile, 'Lc'
if fitAndCheck(times[:-1],Lc[:-1], cut, times[-1],Lc[-1])==1:  statusline=statusline+'Lc '

if verbose: print '\n\n',obsdate, amplm, gainm, xbin, ybin, biasfile, 'Lb'
if fitAndCheck(times[:-1],Lb[:-1], cut, times[-1],Lb[-1])==1:  statusline=statusline+'Lb '

if verbose: print '\n\n',obsdate, amplm, gainm, xbin, ybin, biasfile, 'Rg'
if fitAndCheck(times[:-1],Rg[:-1], cut, times[-1],Rg[-1])==1:  statusline=statusline+'Rg '

if verbose: print '\n\n',obsdate, amplm, gainm, xbin, ybin, biasfile, 'Rr'
if fitAndCheck(times[:-1],Rr[:-1], cut, times[-1],Rr[-1])==1:  statusline=statusline+'Rr '

if verbose: print '\n\n',obsdate, amplm, gainm, xbin, ybin, biasfile, 'Rc'
if fitAndCheck(times[:-1],Rc[:-1], cut, times[-1],Rc[-1])==1:  statusline=statusline+'Rc '

if verbose: print '\n\n',obsdate, amplm, gainm, xbin, ybin, biasfile, 'Rb'
if fitAndCheck(times[:-1],Rb[:-1], cut, times[-1],Rb[-1])==1:  statusline=statusline+'Rb '

# Report result of check
if statusline!=biasfile+' outliers:   ':
    from os import system
    system ('echo fiesGRqc   ' + statusline + \
            ' | /usr/bin/mail -s "FIES gainron QC Warning" ' + emailaddress)
    print statusline
else:
    print "All OK!"
