#! /usr/bin/env python
# Make sure that the script "sinfit_mod.py" is in the same directory as the data since it contains the fitting function. 
# The script "multiple.py" is run by the command "python multiple.py datafile.txt". For running all output files from rvel, run the script "runall.py".   

import sys
# from pylab import *
#from scipy import optimize
from scipy import *
from numpy import *
from subprocess import Popen, PIPE
import os

# sinfit_mod contains the fitting function
from sinfit_mod import fit_model

class PartialFile(file):
    def __init__(self, filename, lowerbound, upperbound):
	self.file = open(filename)
        self.lower = lowerbound
        self.upper = upperbound

    def next(self):
        row = self.file.next()
        xvalue = float(row.split()[0])
        while xvalue < self.lower:
            row = self.file.next()
            xvalue = float(row.split()[0])
        if self.upper < xvalue:
            raise StopIteration

        return row

    def __iter__(self):
	return self

plot_sequence1 ="""
set xrange [%(LOWER)f:%(UPPER)f]
set xlabel 'Date [HJD]'
set ylabel 'Radial Velocity [km/s]'
plot '%(DATAFILE)s' using %(xcol)d:%(ycol)d:%(err)d with errorbars 5 title 'err radial velocity [km/s]' lw 3, '%(INITIALPAR)s' title 'guess' with lines, '%(FITPAR)s' title 'fit' with lines
set terminal png size 600,400
set out '%(PLOTFILE)s'
replot
exit"""

plot_sequence2 ="""
set xrange [%(LOWER)f:%(UPPER)f]
set xlabel 'Date [HJD]'
set ylabel 'Radial Velocity [km/s]'
set terminal png size 600,400
set out '%(PLOTFILE)s'
plot '%(DATAFILE)s' using %(xcol)d:%(ycol)d:%(err)d with errorbars 5 title 'err radial velocity [km/s]' lw 3, '%(INITIALPAR)s' title 'guess' with lines, '%(FITPAR)s' title 'fit' with lines
exit"""

class Fitting(object):
    def __init__(self, G, K, PHI_0, P, LOWER, UPPER):
        self.G = G
        self.K = K
        self.PHI_0 = PHI_0
        self.P = P
        self.LOWER = LOWER
        self.UPPER = UPPER

    def fit(self, filename,
            xcol = 1, ycol = 2, errcol = 3, scale = 1.0,
            save_into = None):
        """fit(filename, xcol = 1, ycol = 2, errcol = 3,
            scale = 1, save_into = None)

filename:    Where the data comes from
xcol:        Columns in the files (starting 1) for each data series
ycol
errcol
scale:       Scale factor for the Chi^2 (modifies errors)
save_into:   Dictionary. It's either empty/None or contains two keys,
             "initpar", "fitpar", whose values are the names of the files
             where to write down the result of the fitting.
        
Returns: (G, K, PHI_0), (Gerr, Kerr, PHIerr), simple_Chi^2, reducing_factor"""

        xdata, ydata, err = loadtxt(PartialFile(filename, self.LOWER, self.UPPER),
                                    usecols=[xcol - 1, ycol - 1, errcol - 1],
                                    unpack=True)

        # 3 is the number of independent parameters
        reducing_factor = (len(xdata) - 3)
        print "Fitting the model (G=%f, K=%f, PHI_0=%f)" % (self.G, self.K, self.PHI_0)
        if not save_into:
            updated, chi2, cov = fit_model(xdata, ydata, err * scale,
                                             self.PHI_0, self.G, self.K)
        else:
            scaled_err = err * scale
            updated, chi2, cov = fit_model(xdata, ydata, scaled_err,
                                             self.PHI_0, self.G, self.K,
                                             initpar_file = save_into["initpar"],
                                             fitpar_file = save_into["fitpar"])
            savetxt(save_into["data"], zip(xdata, ydata, scaled_err) )
        rchi2 = chi2 / reducing_factor
        print "    G        K      PHI_0  Chi^2  reduced Chi^2"
        print "%8.2f %8.2f %8.2f %8.6f %8.2f  %8.2f" % (tuple(updated) + (P,  chi2, rchi2))


        print "Iteration 2: Fitting the model (G=%f, K=%f, PHI_0=%f)" % (self.G, self.K, self.PHI_0)
	scale = rchi2**0.5
        if not save_into:
            updated, chi2, cov = fit_model(xdata, ydata, err * scale,
                                             self.PHI_0, self.G, self.K)
        else:
            scaled_err = err * scale
            updated, chi2, cov = fit_model(xdata, ydata, scaled_err,
                                             self.PHI_0, self.G, self.K,
                                             initpar_file = save_into["initpar"],
                                             fitpar_file = save_into["fitpar"])
            savetxt(save_into["data"], zip(xdata, ydata, scaled_err) )
        rchi2 = chi2 / reducing_factor
        print "    G        K      PHI_0  Chi^2  reduced Chi^2"
        print "%8.2f %8.2f %8.2f %8.10f %8.2f  %8.2f" % (tuple(updated) + (P,  chi2, rchi2))
    

        return updated, ((rchi2*cov[0][0])**0.5, (rchi2*cov[1][1])**0.5, (rchi2*cov[2][2])**0.5), chi2, reducing_factor

    def plot(self, template, datafile, initialpar, fitpar, plotfile,
             xcol = 1, ycol = 2, errcol = 3):

        proc = Popen('gnuplot', stdin=PIPE, stdout=PIPE)

        command = template % {
                              'LOWER': self.LOWER,
                              'UPPER': self.UPPER,
                              'xcol': xcol,
                              'ycol': ycol,
                              'err': errcol,
                              'DATAFILE': datafile,
                              'INITIALPAR': initialpar,
                              'FITPAR': fitpar,
                              'PLOTFILE': plotfile,
                            }
        # print command
        proc.communicate(command)
        proc.wait()

# Main program
if __name__ == '__main__':
    if len(sys.argv) not in ( 2, 3 ):
        print "Usage:"
        print " %s [ -n ] datafilename.txt" % sys.argv[0]
        sys.exit(0)

    if sys.argv[1] == '-n':
        filename = sys.argv[2]
        template = plot_sequence2
    else:
        filename = sys.argv[1]
        template = plot_sequence1
    G = -40
    K = 40.0
    P = 0.0762233
    PHI_0 = 349.745

    PHI_0 = 0.745

    INITIALPAR='%s/initialpar.dat'
    FITPAR='%s/fitpar.dat'
    DATAFILE='%s/data.dat'
    PLOTFILE='%s/fitplot.png'
    PARAMETERS='%s/fitplot.png'

    bounds = ( (349.74, 349.82),
               (363.73, 363.81),
               (397.72, 397.81),
               (398.69, 398.77),
               (401.75, 401.83) )

    print "Starting to fit the data"

    parameters_file = open("parameters.txt", "w")
    for order, (lower, upper) in enumerate(bounds):
        dataset = order + 1
        datadir = "dataset%d" % dataset
        if not os.path.isdir(datadir):
            os.mkdir(datadir)
        fitter = Fitting(G, K, PHI_0, P, lower, upper)

        datafile = DATAFILE % datadir
        initialpar = INITIALPAR % datadir
        fitpar = FITPAR % datadir
        result = fitter.fit(filename, save_into = {"initpar": initialpar,
                                                   "fitpar": fitpar,
                                                   "data": datafile})
        fitted_par, par_err, chi2, rf = result

        S_updated = ["%12.10f" % x for x in fitted_par]
        Errors =  ["%20.18f" % x for x in par_err]
        savetxt(PARAMETERS % datadir,
                zip(("G", "K", "PHI_0"),
                     S_updated,
                    ("GErr", "Kerr", "PHIerr"),
                     Errors),
                fmt="%10s")
        parameters_file.write("%3d %14.11f %14.11f %14.11f %20.18f %20.18f %20.18f\n" %
                              (dataset,
                               fitted_par[0], fitted_par[1], fitted_par[2],
                               par_err[0], par_err[1], par_err[2]))
#        savetxt(parameters_file,
#                zip(("G", "K", "PHI_0"),
#                     S_updated,
#                    ("GErr", "Kerr", "PHIerr"),
#                     Errors),
#                fmt="%10s")
        fitter.plot(template, datafile, initialpar, fitpar, PLOTFILE % datadir)
    parameters_file.close()