#!/usr/bin/env python
#
# fit.py : 	GUI for the module Scientific.Functions.LeastSquares
#		Implementation of the Levenberg-Marquardt algorithm for general
#		non-linear least-squares fits.
#
#  from fit import *
#  root = Tk()
#  data = [(1.,1.),(2.,4.), ...]
#  fitdialog(root,data)
#

from string import *
from Numeric import *
from Scientific.Functions.LeastSquares import *
from Scientific.Functions.FirstDerivatives import *
from pylab import *
from tkSimpleDialog import Dialog
from Tkinter import *
import string,Pmw
from plot2d import message
from plotAscii import readArray,xdisplayfile,transposeA

global FIT
 
def calcfwhm(x,y):
	"""
	calcfwhm(x,y) - with input x,y vector this function calculate fwhm and return (fwhm,xpeak,ymax)
	x - input independent variable
	y - input dependent variable
	fwhm - return full width half maximum
	xpeak - return x value at y = ymax
	"""
	ymin,ymax = min(y),max(y)
	y_hpeak = ymin + .5 *(ymax-ymin)
	x_hpeak = []
	NPT = len(x)
	for i in range(NPT):
		if y[i] >= y_hpeak:
			i1 = i
			break
	for i in range(i1+1,NPT):
		if y[i] <= y_hpeak:
			i2 = i
			break
		if i == NPT-1: i2 = i
	if y[i1] == y_hpeak: x_hpeak_l = x[i1]
	else:
		x_hpeak_l = (y_hpeak-y[i1-1])/(y[i1]-y[i1-1])*(x[i1]-x[i1-1])+x[i1-1]
	if y[i2] == y_hpeak: x_hpeak_r = x[i2]
	else:
		x_hpeak_r = (y_hpeak-y[i2-1])/(y[i2]-y[i2-1])*(x[i2]-x[i2-1])+x[i2-1]
	x_hpeak = [x_hpeak_l,x_hpeak_r]

	fwhm = abs(x_hpeak[1]-x_hpeak[0])
	for i in range(NPT):
		if y[i] == ymax: 
			jmax = i
			break
	xpeak = x[jmax]
	return (fwhm,xpeak,ymax)

def fit_linear(parameters, values):
	a, b = parameters
	x = values
	return (a + b * x)

def fit_cuadratic(parameters, values):
	x = values
	x0, a, b, c = parameters
	return(a *(x-x0)**2 + b*(x-x0) + c )

def fit_gauss(parameters, values):
	a, x0, w, y0 = parameters
	x = values
	return(a * exp(-2*(x-x0)**2/w**2) + y0)

def fit_lorentz(parameters, values):
	a, x0, w = parameters
	x = values
	return( a * w **2 / ((x-x0)**2 + w**2) )

def fit_boltzman(parameters, values):
	x0, a1, a2, dx = parameters
	x = values
	return((a1 - a2)/(1 + exp((x - x0)/dx)) + a2)

def fit_logistic(parameters, values):
	x0, a1, a2, p = parameters
	x = values
	return((a1 - a2)/(1 + (x/x0)**p) + a2)

def fit_expdecay(parameters, values):
	x0, y0, a, t = parameters
	x = values
	return(y0 + a * exp(-(x - x0)/t))

def fit_expgrow(parameters, values):
	x0, y0, a, t = parameters
	x = values
	return(y0 + a * exp((x - x0)/t))

def fit_expassoc(parameters, values):
	y0, a1, t1, a2, t2 = parameters
	x = values
	return(y0 + a1 * (1 + exp(-x/t1)) + a2 * (1 + exp(-x/t2)))

def fit_hyperbl(parameters, values):
	p1, p2 = parameters
	x = values
	return(p1 * x/ (p2 + x))

def fit_pulse(parameters, values):
	x0, y0, a, t1, t2 = parameters
	x = values
	return(y0 + a * (1 + exp(-(x - x0)/t1)) * exp(-(x - x0)/t2))

def fit_rational0(parameters, values):
	a, b, c = parameters
	x = values
	return((b + c*x)/(1 + a*x))

def fit_sine(parameters, values):
	x0, a, w = parameters
	x = values
	return(a * sin(pi*(x - x0)/w))

def fit_gaussamp(parameters, values):
	x = values
	a, x0, w, y0 = parameters
	return( a * exp(-(x - x0)**2/(2*w**2)) + y0)
#	a0, a1, a2, a3, a4, a5 = parameters
#	return(a0 * exp(-(x-a1)**2/a2**2/2) *( a3*x**2 + a4 * x + a5 ))

def fit_allometric(parameters, values):
	a, x0, c = parameters
	x = values
	return(a * (x-x0)**2 + c)



fit_linear_dic = {
	"Doc" : "Linear Function",
	"Exp" : "y = a + b * x",
	"Par" :	("a", "b"),
	"NumPar" : 2,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_linear
}
fit_cuadratic_dic = {
	"Doc" : "Cuadratic Function",
	"Exp" : "y = a *(x-x0)**2 + b*(x-x0) + c ",
	"Par" :	("x0", "a","b", "c"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_cuadratic
}
fit_gauss_dic = {
	"Doc" : "Amplitude version of Gaussian Function",
	"Exp" : "y = a * exp(-2*(x-x0)**2/w**2) + y0",
	"Par" :	("a", "x0", "w", "y0"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_gauss
}
fit_lorentz_dic = {
	"Doc" : "Lorentzian Peak Function",
	"Exp" : "y = a * w**2 / ((x - x0)**2 + w**2)",
	"Par" :	("a", "x0", "w"),
	"NumPar" : 3,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_lorentz
}
fit_boltzman_dic = {
	"Doc" : "Boltzman Function: sigmoidal curve",
	"Exp" : "y = (a1 - a2)/(1 + exp((x - x0)/dx)) + a2",
	"Par" :	("x0", "a1", "a2", "dx"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_boltzman
}
fit_logistic_dic = {
	"Doc" : "Logistic dose/response",
	"Exp" : "y = (a1 - a2)/(1 + (x/x0)**p) + a2",
	"Par" :	("x0", "a1", "a2", "p"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_logistic
}
fit_expdecay_dic = {
	"Doc" : "Exponential Decay",
	"Exp" : "y = y0 + a * exp(-(x - x0)/t)",
	"Par" :	("x0", "y0", "a", "t"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_expdecay
}
fit_expgrow_dic = {
	"Doc" : "Exponential Growth",
	"Exp" : "y = y0 + a * exp((x - x0)/t)",
	"Par" :	("x0", "y0", "a", "t"),
	"NumPar" : 4,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_expgrow
}
fit_expassoc_dic = {
	"Doc" : "Exponential Associate",
	"Exp" : "y = y0 + a1 * (1 + exp(-x/t1)) + a2 * (1 + exp(-x/t2))",
	"Par" :	("y0", "a1", "t1", "a2", "t2"),
	"NumPar" : 5,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_expassoc
}
fit_hyperbl_dic = {
	"Doc" : "Hyperbola Function",
	"Exp" : "y = p1 * x/ (p2 + x)",
	"Par" :	("p1", "p2"),
	"NumPar" : 2,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_hyperbl
}
fit_pulse_dic = {
	"Doc" : "Pulse Function",
	"Exp" : "y = y0 + a * (1 + exp(-(x - x0)/t1)) * exp(-(x - x0)/t2)",
	"Par" :	("x0", "y0", "a", "t1", "t2"),
	"NumPar" : 5,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_pulse
}
fit_rational0_dic = {
	"Doc" : "Rational Function , type 0",
	"Exp" : "y = (b + c*x)/(1 + a*x)",
	"Par" :	("a", "b", "c"),
	"NumPar" : 3,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_rational0
}
fit_sine_dic = {
	"Doc" : "Sine Function",
	"Exp" : "y = a * sin(pi*(x - x0)/w)",
	"Par" :	("x0", "a", "w"),
	"NumPar" : 3,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_sine
}
fit_gaussamp_dic = {
	"Doc" : "Amplitude version of Gaussian Peak Function",
	"Exp" : "y = a * exp(-(x - x0)**2/(2*w**2)) + y0",
	"Par" :	("a", "x0", "w", "y0"),
	"NumPar" : 4,
#	"Exp" : "y = a0 * exp(-(x-a1)**2/a2**2/2)*(a3*x**2 + a4*x + a5)",
#	"Par" : ("a0", "a1", "a2", "a3", "a4", "a5"),
#	"NumPar" : 6,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_gaussamp
}
fit_allometric_dic = {
	"Doc" : "Classical Freundlich Model",
	"Exp" : "y = a * (x-x0)**2 + c",
	"Par" :	("a", "x0", "c"),
	"NumPar" : 3,
	"IVar" : "x",
	"DVar" : "y",
	"Function" : fit_allometric
}


functions = {
	"Linear" : fit_linear_dic,
	"Cuadratic" : fit_cuadratic_dic,
	"Gauss" : fit_gauss_dic,
	"Lorentz" : fit_lorentz_dic,
	"Boltzman" : fit_boltzman_dic,
	"Logistic" : fit_logistic_dic,
	"ExpDecay" : fit_expdecay_dic,
	"ExpGrow" : fit_expgrow_dic,
	"ExpAssoc" : fit_expassoc_dic,
	"Hyperbl" : fit_hyperbl_dic,
	"Pulse" : fit_pulse_dic,
	"Rational0" : fit_rational0_dic,
	"Sine" : fit_sine_dic,
	"GaussAmp" : fit_gaussamp_dic,
	"Allometric" : fit_allometric_dic
}


def fitting(fn,data,parms=None,steps=None):
    """ fitting(fn,data,parms=None,steps=None) -
	This function uses leastSquaresFit to calculate the fitting 
	coefficients with user specified fitting function
	fn    - function name defined in fitting functions directory
	data  - specified the (x,y) data list to be fitted
	steps - maximum number of iteration steps allowed
	parms - returns the fitted parmeters
	errs  - fitting least square  error returned
    """
    try:
	f = functions[fn]
	np = f['NumPar']
	if parms == None:
	    parms=[]
	    for i in range(np):
		s = data[i]
        	parms.append(s[1])
	RETS = leastSquaresFit(f['Function'],parms,data,max_iterations=steps)
	return RETS
    except:
	print 'fitting failed on data'
	return None
	

def plotfitting(f,x,y1,y2,ret,legd=None):
	""" 
	plotfitting(f,x,y1,y2,ret,legd=None) - this function use pylab plot 
routine to do fitted plot
	f - specify the fitted function 
	x - independent x array
	y1 - dependent data arry
	y2 - fitted dependent array
	ret - coeffs and err list returned by the leastSquareFit function
	ledg - indicator whether to record fit function and coefficients on plot
	"""
	np = f['NumPar']
	parms=ret[0]
	print 'coeffs=', parms
	print 'err=',ret[1]
	err = 'err='+str(ret[1])
	figure(1,figsize=(5,4))
	clf()
	plot(x,y1,'b+',linewidth=1)
	plot(x,y2,'k-',linewidth=1)
	connect('button_press_event',closewin)
	title(f['Exp'])
	if legd == 1:
	    xmin,xmax = xlim()
	    dx = (xmax-xmin)*.1	
	    xlim(xmin-dx,xmax+dx)
	    ymin,ymax = ylim()
	    dy = .1*(ymax-ymin)
	    text(0,ymax-.5*dy,err)
	    text(0,ymax-dy,'coeffs='+str(f['Par']))
	    for i in range(np):
		text(0,ymax-1.5*dy-i*.5*dy,str(parms[i]))
	show()

def fittedData(f,x,y1,y2,ret,title=None):
	"""
	fittedData(f,x,y1,y2,ret,title=None) - pop up fitted displaywindow
	f - specify the fitting function struture dictionary used
	x - dependent vector
	y1 - raw y data vector
	y2 - fitted y value vector
	ret - LeastSquares fit returned values
	title - title string used by pop up window
	"""
	parms = ret[0]
	errs = ret[1]
	gdness = sqrt(errs/(len(x)-1))
	np = f['NumPar']
	fo = open('fit_out.txt','w')
	fo.write('# %s\n' % f['Exp'])
	fo.write('# %s\n' % str(f['Par']) )
	for i in range(np):
		fo.write('# %s =  %s\n' % (f['Par'][i],str(parms[i])) )
	fo.write('# Least Square Errors = %f\n# \n' % errs)
	fo.write('# Goodness of Fit = %f\n# \n' % gdness)
	fo.write('# %18s %18s %18s\n' % ('X','Y','Y_FIT'))
	for i in range(len(x)):
		fo.write('%4d  %18.7f %18.7f %18.7f\n' % (i,x[i],y1[i],y2[i]) )
	fo.close()	
	if title != None: title= 'fit_out.txt: ' + title
	else: title = 'fit_out.txt'
	xdisplayfile('fit_out.txt',title=title)

def closewin(event):
	"closewin(event) - if right mouse event close the plot window"
	if event.button == 3: close(1)

# Test for linear fit:
def testfit(self,data=None,fn=None,parms=None,legd=None,steps=None):
 	"""
	testfit(self,data=None,fn=None,parms=None,legd=None,steps=None) -
	this function try to fit the data with user picked function
	self  - specify the pointer for fit structure
	data -  specify the data (x,y) list array to be fitted, it None
		specified the default data will be used
	fn   -  string to specify the fitting function name, default 'Linear'
	parms - return list from leastSquaresFit function
	legd  - indicator whether to write fitted coefficients on plot	
	steps - specify the maximum iteration steps used
	"""
	if data == None:
	    data = [ (0., 0.), (1., 1.1), (2., 1.98), (3., 3.05), (4.,2.) ]
	if fn == None: fn = 'Linear'
	ret = fitting( fn, data, steps=steps)
	if ret != None:
		parms = ret[0]
		errs = ret[1]
		p = str(parms[0])
		for i in range(1,len(parms)):
			p = p + ', ' + str(parms[i])
		self.parms[1].delete(0,200)
		self.parms[1].insert(0,p)
		self.RETS = ret
		x = array(self.x)
		y = array(self.y)
		f = functions[fn]
		self.f = f
		y2 = f['Function'](parms,x)
		fittedData(f,x,y,y2,ret,title=self.Wtitle)
		plotfitting(f,x,y,y2,ret,legd=legd)
	return ret

class FitDialog(Frame):
    def __init__(self,master=None):
	Frame.__init__(self,master,width=700,height=400)

    def createPolyDialog(self,top,title):
	"""
	createPolyDialog(self,top,title) - create polynomial fitting dialog
	top - specify parent widget
	e.g. power 4 polynomial
	A0 * x**4 + a1 * x**3 + a2 * x**2 + a3 * x + a4
	"""

	master = Toplevel()
	master.title('Polynomial '+title)

	self.fm = master
	Label(master,text='Polynomial Fit').grid(row=1,column=0,sticky=W)
	Label(master,text='Polynomial Power #').grid(row=2,column=0,sticky=W)
	self.polVar = IntVar()
	self.polVar = Entry(master,width=5)
	self.polVar.grid(row=2,column=2,sticky=W)
	self.polVar.insert(0,'2')
	Button(master,text='Close',command=self.polydestroy).grid(row=3,column=0,sticky=W)
	Button(master,text='Accept',command=self.runpolyfit).grid(row=3,column=2,sticky=W)
	Label(master,text='Polynomial Coeffs:').grid(row=4,column=0,sticky=W)
	self.coeffsVar = StringVar() 
	self.coeffsVar = Entry(master,width=60)
	self.coeffsVar.grid(row=4,column=2,sticky=W)

	figure(1,figsize=(5,4))
	clf()
	plot(self.x,self.y,'b+')
	connect('button_press_event',closewin)
	show()

    def polydestroy(self):	
	"polydestroy(self) - destory polynomial fit dialog"
	self.fm.destroy()

    def runpolyfit(self):	
	"runpolyfit(self) - accept pow # and perform polynomial fit"
	x = self.x
	y = self.y
	pow = string.atoi(self.polVar.get())
	coeffs = polyfit(x,y,pow)
	z = polyval(coeffs,x)
	figure(1,figsize=(5,4))
	clf()
	plot(x,y,'b+',x,z,'k-',linewidth=1)
	self.coeffsVar.delete(0,300)
	self.coeffsVar.insert(0,str(coeffs))

    def createDialog(self,top):
	"""
	createDialog(self,top) - create multiple fitting functions dialog
	top - specify the parent widget
	"""
	list = functions.keys()
	print list
	x = self.x
	master = Toplevel()
	master.title('Setup Fit Dialog - ' + self.Wtitle)
	self.fm = master
	Label(master,text='FIT ID #').grid(row=1,column=0,sticky=W)
	Label(master,text='FIT NAME').grid(row=1,column=1,sticky=W)
	Label(master,text='FIT EXPRESSION - X'+str([x[0],x[len(x)-1]])).grid(row=1,column=2,sticky=W)
	Label(master,text='COEFFS #').grid(row=1,column=3,sticky=E)
	for i in range(len(list)):
		f= functions[list[i]]
		Label(master,text=str(i)).grid(row=i+2,column=0,sticky=W)
		Label(master,text=list[i]).grid(row=i+2,column=1,sticky=W)
		Label(master,text=f['Exp']).grid(row=i+2,column=2,sticky=W)
		Label(master,text=f['NumPar']).grid(row=i+2,column=3,sticky=E)
	self.id = 0

	i = 16
	self.parms = [StringVar(),StringVar(),StringVar()]
	Label(master,text='Enter').grid(row=i+3,column=0,sticky=W)
	Label(master,text='FIT ID #:').grid(row=i+3,column=1,sticky=W)
	self.parms[0] = Pmw.EntryField(master,labelpos=W,label_text='with <carriage return>',command=self.setfitid)
	self.parms[0].grid(row=i+3,column=2,sticky=W)
	Label(master,text='INIT').grid(row=i+4,column=0,sticky=W)
	Label(master,text='COEFFS:').grid(row=i+4,column=1,sticky=W)
	self.parms[1] = Entry(master,width=60)
	self.parms[1].grid(row=i+4,column=2,sticky=W)
	Label(master,text='Total #').grid(row=i+5,column=0,sticky=W)
	Label(master,text='of Iterations:').grid(row=i+5,column=1,sticky=W)
	self.parms[2] = Entry(master,width=5)
	self.parms[2].grid(row=i+5,column=2,sticky=W)
	btn1 = Button(master,text='Close',command=self.destroy)
	btn1.grid(row=i+15,column=0,sticky=W)
	btn2 = Button(master,text='Fitting...',command=self.apply)
	btn2.grid(row=i+15,column=1,sticky=W)
	self.legdVar = IntVar()
	Checkbutton(master,text='Plot Legend On',state=NORMAL,variable=self.legdVar,command=self.setlegend).grid(row=i+15,column=2,sticky=W)

	self.btn = [btn1,btn2]
#	self.legdVar.set(self.legd)
	self.parms[0].insert(0,str(self.id))
	self.parms[2].insert(0,str(300))
	self.initcoeffs()
	
	figure(1,figsize=(5,4))
	clf()
	plot(self.x,self.y,'b+')
	connect('button_press_event',closewin)
	title('Data To Be Fitted')
	show()

    def destroy(self):
	"destroy(self) - close multiple fitting functions dialog"
	try: self.fm.destroy()
	except: pass

    def setfitid(self):
	"setfitid(self) - set fit function id and initialize fit coeffs"
	self.id = string.atoi(self.parms[0].get())
	self.initcoeffs()
#	self.apply()

    def initcoeffs(self):
	"initcoeffs(self) - initialize fit coeffs according fit function id #"
	list = functions.keys()
	x = self.x
	y = self.y
	(fwhm,xpeak,ypeak) = calcfwhm(x,y)
	npt = len(x)
	id = self.id
	num = functions[list[id]]['NumPar']	
	ymin,ymax = min(y),max(y)
	self.max = ymax
	self.min = ymin
	self.parms[1].delete(0,200)
	import MLab 
	if id == 0:  # Sine
		x0 = 0.5*(x[npt-1]-x[0])
		w = x[npt-1] - x[0]
		a = ymax
		p =  str(x0)+ ', '+ str(a) + ', '+str(w)
	if id == 1: # Rational0
		a = x[0]
		b = y[0]
		c = x[npt-1]
		p =  str(a)+ ', '+ str(b) + ', '+str(c)
	if id ==2: # Linear
		a = y[0]
		b = (y[npt-1]-a)/(x[npt-1]-x[0])
		p =  str(a)+ ', '+ str(b) 
	if id == 3: # Allometric
		a = 1. 
		x0 = x[0]
		c = ymin
		p =  str(a)+ ', '+str(x0) + ', ' + str(c)
	if id == 4: # Cuadratic
		x0 = x[npt/2]
		a = (ymax-ymin)/(x[npt-1]-x[0])
		b = -x[npt/2]
		c = ymin
		p =  str(x0) + ', ' + str(a)+ ', '+ str(b) + ', '+str(c) 
	if id == 5: # Gauss
		y0 =  y[0]
		x0 = x[npt/2]
		a =  (ymax-ymin)
		w = MLab.std(y)  
		w = -(x[npt-1]-x[0])/10
		p =  str(a)+ ', '+ str(x0) + ', '+str(w) +', '+str(y0)
	if id == 6: # Boltzman
		x0 = 0.5*(x[npt-1]+x[0])
		a1 = 2.*y[npt/2]-y[npt-1]+y[0]
		a2 = 2.*y[npt/2]+y[npt-1]-y[0]
		dx = x[npt-1]-x[0]
		p =  str(x0)+ ', '+ str(a1) + ', '+str(a2) +', '+str(dx)
	if id == 7: # ExpGrow
		x0 = x[0]
		y0 = y[0]
		a = (y[npt-1]-y[0])
		t = (x[npt-1]-x[0])
		p =  str(x0)+ ', '+ str(y0) + ', '+str(a) +', '+str(t)
	if id == 8: # Lorentz
		a = ypeak
		x0 = xpeak
		w = fwhm/2
		p =  str(a)+ ', '+str(x0) +', '+str(w)
		print p
	if id == 9: # Expassoc
		y0 = y[0]
		a1 = y[npt/2]*.5
		t1 = x[npt-1]-x[0]
		a2 = y[npt/2]*.5
		t2 = x[npt-1]-x[0]
		p =  str(y0)+ ', '+ str(a1) + ', '+str(t1) +', '+str(a2) +', '+str(t2)
	if id == 10: # Logistic
		x0 = x[npt-1]-x[0]
		p = .5
		a2 = (x[npt-1]/x0)**p*(y[npt-1]/y[npt/2]-(x[npt/2]/x[npt-1])**p)/(1.-y[npt-1]/y[npt/2]) - 1
		a1 = a2+y[npt/2]*(1.+a2+(x[npt/2]/x0)**p)
		p =  str(x0)+ ', '+ str(a1) + ', '+str(a2) +', '+str(p)
	if id == 11: # GaussAmp
		a = ymax-ymin
		w = -(x[npt-1]-x[0])/6
		x0=x[npt/2]
		y0 = y[0]
		p =  str(a)+ ', '+ str(x0) + ', '+str(w) +', '+str(y0)
#		a0 = ymax*.8
#		a1 = .5*(x[npt-1]-x[0])
#		a2 = a1/4.
#		a3 = 1.1
#		a4 = a1*a1 
#		a5 = a1
#		p =  str(a0)+ ', '+ str(a1) + ', '+str(a2) +', '+str(a3) + ', '+str(a4) +', '+str(a5)
	if id == 12: # Pulse
		x0 = x[npt/2]
		y0 = ymin
		a = (ymax-ymin)/2
		t1 = (x[npt-1]-x[0])/2.
		t2 = t1
		p =  str(x0)+ ', '+ str(y0) + ', '+str(a) +', '+str(t1) +', '+str(t2)
	if id == 13: # Hyperbl
		p2 = (x[0]*(y[0]-1.) - x[npt/2]*(y[npt/2]-1.))/(y[npt/2]-y[0])
		p1 = p2*y[npt/2] + x[0]*(y[0]-1.)
		p =  str(p1)+ ', '+ str(p2) 
	if id == 14: # ExpDecay
		x0 = x[0]
		y0 = ymax
		a = ymax-ymin
		t = (x[npt-1]-x[0])
		p =  str(x0)+ ', '+ str(y0) + ', '+str(a) + ', '+str(t)

	print 'coeffs=',p 
	self.parms[1].insert(0,p)

    def apply(self):
	"apply(self) - accept fit id and coeffs and pass data to fit calculation"
	from plot2d import parsefloat,parseint
	id = string.atoi(self.parms[0].get())
	ll = self.parms[1].get()
	print 'ID # =', id
	print 'parms=', ll 
	parms = parsefloat(ll)
	list = functions.keys()
	fn = list[id]
	f= functions[list[id]]
	steps = string.atoi(self.parms[2].get()) 
	self.legd = self.legdVar.get()
	ret = testfit(self,data=self.data,fn=fn,parms=parms,legd=self.legd,steps=steps)
#	print 'ret=',ret
	if ret == None:
		message(self.fm,text='Error: Least square data fitting failed with function\n\n'+f['Exp'],title='Fitting Info')

    def setlegend(self):
	"setlegend(self) - check for writing fit coeffs legend on plot"
	self.legd = self.legdVar.get()
	if self.legd == 1:
	    figure(1)
	    xmin,xmax = xlim()
	    dx = (xmax-xmin)*.1	
	    xlim(xmin-dx,xmax+dx)
	    ymin,ymax = ylim()
	    dy = .1*(ymax-ymin)
	    ret = self.RETS
	    err = str(ret[1])
	    parms = ret[0]
	    text(0,ymax-.5*dy,err)
	    text(0,ymax-dy,'coeffs='+str(self.f['Par']))
	    for i in range(len(parms)):
		text(0,ymax-1.5*dy-i*.5*dy,str(parms[i]))

def fitdata(data,xl=None,xr=None):
	"""
	fitdata(data,xl=None,xr=None) - construct and return fit data list tuple [(X,Y),...]
	data - input list of Y vector with N data points 
	xl   - specify start X value at data[0], default to 1
	xr   - specify end X value at data[N-1], default to N the number of 
		data points in Y data vector
	"""
    	if str(type(data[0])) == "<type 'tuple'>": return data
	if xl != None and xr != None:
		dx = (xr-xl)/float(len(data)-1)
	else:
		dx = 1
		xl = 1
	da = []
	for i in range(len(data)):
		x = xl + i*dx
		da.append( (x,data[i]) )
	return da

def fitdialog(root,data=None,title=None):
	"""
	fitdialog(root,data=None) - function fit dialog with specified input data list
	root - specify the parent widget
	data - specify the input  Y, or (X,Y) data list to be fitted
	"""
	Fit = FitDialog(root)
	if data == None:
	    data = [ (0., 0.), (1., 1.1), (2., 1.98), (3., 3.05), (4.,2.) ]
	if data != None:
    		if str(type(data[0])) != "<type 'tuple'>": 
			data = fitdata(data)
		Fit.data = data
		x=[]
		y=[]
		for i in range(len(data)):
			x.append(data[i][0])
			y.append(data[i][1])
	Fit.x = x
	Fit.y = y	
	Fit.legd = 0 
	Fit.Wtitle= ''
	if title != None: Fit.Wtitle=title 
	Fit.createDialog(root)

def polyfitdialog(root,data=None,title=None):
	"""
	polyfitdialog(root,data=None) - polynomial fit dialog with specified input data list
	root - specify the parent widget
	data - specify the input Y or (X,Y) data list to be fitted
	"""
	Fit = FitDialog(root)
	if data == None:
	    data = [ (0., 0.), (1., 1.1), (2., 1.98), (3., 3.05), (4.,2.) ]
	if data != None:
	    	if str(type(data[0])) != "<type 'turple'>": data = fitdata(data)
		Fit.data = data
		x=[]
		y=[]
		for i in range(len(data)):
			x.append(data[i][0])
			y.append(data[i][1])
	Fit.x = x
	Fit.y = y	
	Fit.legd = 0 
	Fit.Wtitle = ''
	if title != None: Fit.Wtitle= title
	Fit.createPolyDialog(root,title)

def pickVect():
	"pickVect() - pick (X,Y) pair vector out of ascii column data array to be fitted"
	if FIT['ncol'] <= 0: 
		message(FIT['root'],text='Error:  No data found !!!\n\nFirst Load Data Array in from an Ascii file\n\n')
		return
	cols = FIT['cols']
	xcol = FIT['xcol']
	ycol = FIT['ycol']
	ix = xcol.get()
	iy = ycol.get()
	if ix >= FIT['ncol']: ix= -1
	if iy >= FIT['ncol']: ix= FIT['ncol'] - 1
	if iy < ix: iy = ix+1
	if ix < 0: 
		x = range(1,len(cols[0])+1)
	else:
		x = cols[ix]
	y = cols[iy]
	data = []
	fo = open('xy.txt','w')
	for i in range(len(x)):
		data.append((x[i],y[i]))
		fo.write('%18.7f %18.7f \n' % (x[i],y[i]) )
	fo.close()	
	
	title='Least Square Fit: ix='+str(ix)+' ,iy='+str(iy)
	FIT['title'] = title
	xdisplayfile('xy.txt',title='xy.txt: '+title)
	fit(data,title=title)


def pickFile():
	"pickFile() - use file selection dialog to load in Ascii data array"
        import tkFileDialog,os
	path = '.'
	if os.path.isfile('fit.config'):
		fi =open('fit.config')
		fname = fi.read()
		fi.close()
		(path,fn) = os.path.split(fname)
        fname = tkFileDialog.askopenfilename(initialdir=path,
                initialfile='*.txt')
        if fname ==(): exit() 
	FIT['fname'] = fname
	xdisplayfile(fname)
	arr = readArray(fname)
	cols = transposeA(arr)
	FIT['cols'] = cols
	FIT['ncol'] = len(cols)
	fo = open('fit.config','w')
	fo.write(fname)
	fo.close()

def fit(data=None,title=None):
	"""
	fit(data=None,title=None) - least square fitting dialog for input data vector
	data - speicify a list of (x,y) vector to be fitted
	title - specify the title of fit dialog window to be used
	"""
	if data == None:
	    data = [ (0., 0.), (1., 1.1), (2., 1.98), (3., 3.05), (4.,2.) ]
	root = Tk()
	if title == None: title = 'fit.py - Least Square Fit Program'
	root.title(title)
	fm = Frame(root)
	Button(fm,text='Polynomial Fit...',command=lambda s=fm,da=data,ti=title: polyfitdialog(s,da,ti)).pack(side=LEFT)
	Button(fm,text='Other Fit...',command=lambda s=fm,da=data,ti=title: fitdialog(s,da,ti)).pack(side=LEFT)
	Button(fm,text='Close',command=root.destroy).pack(side=LEFT)
        fm.pack()
	root.mainloop()

def fithelp():
	"fithelp() - help info about fit.py"
	info = 'If the fitting failed with real X vector values,\n user can try to fit with X vector index values, i.e.\n set X Vector Column Seq # to -1 to use X index vector'
	message(FIT['root'],text=info,title='Fit - Help Info')

def initFit():
	"initFit() - initialize global variable FIT"
	FIT = { 'root': None,
		'fname': '',
		'cols': None,
		'xcol': None,
		'ycol': None,
		'ncol': 0,
		'title': '',
		'ix': 0,
		'iy': 2 }
	return FIT
	
if __name__ == '__main__':
#	fit()
	FIT = initFit()

	root = Tk()
	FIT['root'] = root
	root.title('fit.py - Extract (X,Y) Vector & Fit')
	Label(root,text='Extract X,Y columns from an ASCII File then pass').pack(side=TOP)
	Label(root,text='(X,Y) vector to least square fit routines').pack(side=TOP)
	fm = Frame(root)
	xcol = IntVar()
	ycol = IntVar()
	Label(fm,text='X Vector Column Seq #:').grid(row=2,column=1,sticky=W)
	Label(fm,text='Y Vector Column Seq #:').grid(row=3,column=1,sticky=W)
	Entry(fm,width=10,textvariable=xcol).grid(row=2,column=2,sticky=W)
	Entry(fm,width=10,textvariable=ycol).grid(row=3,column=2,sticky=W)
	xcol.set(0)
	ycol.set(2)
	FIT['xcol'] = xcol
	FIT['ycol'] = ycol
	Button(fm,text='Load Data Array from Ascii...',command=pickFile).grid(row=1,column=1,sticky=W)
	Button(fm,text='Help...',command=fithelp).grid(row=1,column=2,sticky=W)
	Button(fm,text='Close',command=root.destroy).grid(row=1,column=3,sticky=W)
	Button(fm,text='Pass (X,Y) to Fitting... ',command=pickVect).grid(row=4,column=1,sticky=W)
        fm.pack()
	fm1 = Frame(root)
        fm1.pack()
	FIT['root_fit'] = fm1
	root.mainloop()

