#!/usr/bin/env python

from Tkinter import *
import Pmw
import AppShell
import sys, os
import string
from plotAscii import xdisplayfile
from tkSimpleDialog import Dialog
 
from pylab import *
#from fit import *
import MLab

colors = ['b','g','r','c','m','y','k','w']
linestyles = ['-','--','-.',':','.-.','-,']
symbols = ['o','^','v','<','>','s','+','x','D','d','1','2','3','4','h','H','p','|','_']
legends=['best','upper right','upper left', 'lower left','lower right','right','center left','center right','lower center','upper center','center']

def subplot_i(t,s,id,xlog,ylog):
	"""
	subplot_i(t,s,id,xlog,ylog) - create subplot as linear or log scale
	where
		t    - X axis value
		s    - Y variable
		id   - specify the 3 digits sequence number(RC#) of the subplot
		       (at most 9 subplots allowd in a figure)
		       R specify the subplot row number
		       C specify the the subplot column number
		       # specify the sequence number < 10
		xlog - specify X axis scale (0 linear scale, 1 logarithm scale)
		ylog - specify Y axis scale (0 linear scale, 1 logarithm scale)
		     
	"""
        subplot(id)
	if ylog or xlog:
	  if ylog * xlog :
	    loglog(t,s)
	  else:
	    if ylog:
	      semilogy(t,s)
	    else:
	      semilogx(t,s)
	else: 
          plot(t,s)


def minmax(y):
	"minmax(y) - return minimum, maximum of 2D array y"
	nc = len(y)
	l1 = []
	l2 = []
	for i in range(0,nc):
		l1.append(min(y[i]))
		l2.append(max(y[i]))
	ymin = min(l1)
	ymax = max(l2)
	return ymin,ymax

class plot1d(AppShell.AppShell):
    usecommandarea  = 1
    appname     = 'plot1d Python Program'
    frameWidth  = 500
    frameHeight = 500

    def createButtons(self):
	"createButtons(self) - create command area buttons"
        self.buttonAdd('Close',helpMessage='Close program',
            statusMessage='Close and terminate this program',
            command=self.closeup)
        self.buttonAdd('Plot Curves',helpMessage='Use matplotlib plot',
            statusMessage='Accept input and pass to matplotlib',
            command=self.plotcurves)
        self.buttonAdd('Subplots',helpMessage='Use matplotlib subplot',
            statusMessage='Plot first 9 selected curves as separate subplots',
            command=self.plotsubplot)
        self.buttonAdd('CloseFigures', helpMessage='Close All Figures Windows',
	    statusMessage='Close all figure plot windows',
            command = self.closeall)

    def plotsubplot(self):
     "plotsubplot(self) - plot selected curves in a subplot figure (at most 9 allowed)"
     try:
	CB = self.getCB()
	if max(CB) < 1: return
	xlog = self.xlog.get()
	ylog = self.ylog.get()
      	t = self.x
      	sl = self.y
      	NC = len(sl)
	wid=[431,432,433,434,435,436,437,438,439]
	self.fig = self.fig+1
#	close(self.fig)
	figure(self.fig)
	ndd = 0
	for i in range(0,NC):
	    if CB[i] and ndd<9:
		subplot_i(t,sl[i],wid[ndd],xlog,ylog)
		ndd = ndd+1
	connect('button_press_event',self.closewin)
	show()
     except ValueError:
	self.message()
	return
     except AttributeError or ValueError:
	return

    def plotcurves(self):
     "plotcurves(self) - plot all selected curves in a figure"
     try:
	CB = self.getCB()
	if max(CB) < 1: return
	ylog=self.ylog.get()
	xlog=self.xlog.get()
      	t = self.x
      	sl = self.y
      	NC = len(sl)
	self.fig = self.fig+1
#	close(self.fig)
	figure(self.fig,figsize=(5.5,4))
	subplot(111)
	nc = len(colors)-1
	ns = len(symbols)
	nt = len(linestyles)
	t0 = []
	NP = self.spp # 20
	for k in range(len(t)):
	    if k % NP == 0:
		t0.append(t[k])    
	labels =[]
	for i in range(0,NC):
	    if CB[i]:
       	 	icl = i % nc
       	 	ism = i % ns
        	sty = colors[icl]   
		if self.symOn or self.styOn:
			if self.symOn: sty = sty + symbols[i%ns]
			if self.styOn:
				sty = sty + linestyles[i%nt] 
			else: 
				sty = sty + '-'
		ty = sty  
		if (self.styOn+self.symOn) == 0: ty=ty+'-'
		lbl = self.pvs[i]
		labels.append(lbl)
		if self.symOn == 0:
			t0 = t
			s0 = sl[i]
		else:
			s0 = []
			for k in range(len(t)):
		    	  if k % NP == 0:
			    s0.append(sl[i][k])    
		if ylog or xlog:
		  if ylog * xlog :
		    loglog(t0,s0,ty,linewidth=1,label=lbl)
		  else:
		    if ylog:
		      semilogy(t0,s0,ty,linewidth=1,label=lbl)
		    else:
		      semilogx(t0,s0,ty,linewidth=1,label=lbl)
		else: 
		  if self.symOn or self.styOn:
		     try:
        	  	   plot(t0,s0,ty,linewidth=1,label=lbl)
		     except:
			   ty = sty + '-'
        	  	   plot(t0,s0,ty,linewidth=1,label=lbl)
		  else:
        	  	plot(t,sl[i],linewidth=1,label=lbl)
	self.labels = labels
	gl = self.toggleGridVar.get()
	if gl: grid()
	xlabel(self.xlabel)
	ylabel(self.ylabel)
	title(self.title)
	if self.legOn: legend(loc=legends[self.legloc])
	connect('button_press_event',self.closewin)
        show()
     except ValueError:
	self.message(nm='self.plotcurves()')	
	return
     except AttributeError :
	return

    def message(self,nm=None,info=None):
	"message(self) - display message info"
	dialog = Pmw.Dialog(self.form,buttons=('OK','Cancel'),
		defaultbutton='OK', title='plot1d-info')
	if nm == None:
	  w = Label(dialog.interior(),text='First, You have to use File->Load\nto load data array from an ascii data file ',pady=20)
	else:
	  if info == None: 
	      w = Label(dialog.interior(),text='Warning: ValueError detected in\n\n --> '+nm,pady=20)
	  else:
	      w = Label(dialog.interior(),text= info +'\n\n --> '+nm,pady=20)

	w.pack(expand=1,fill=BOTH,padx=4,pady=4)
	dialog.activate()

    def closeup(self):
	"closeup(self) - close window and exit the plot1d program"
	close('all')
        fo = open('plot1d.config','w')
	self.title = self.W[0].get()
	self.xlabel = self.W[1].get()
	self.ylabel = self.W[2].get()
        st = [ self.fname,self.title,self.xlabel,self.ylabel,self.mdapath]
        fo.write(str(st))
        fo.close()
	self.root.destroy()
        self.quit()

    def setxlimit(self):
	"setxlimit(self) - set and update xlim for plot figure"
	self.Rg[0] = self.xmin.get()
	self.Rg[1] = self.xmax.get()
	xlim(self.Rg[0],self.Rg[1])

    def setylimit(self):
	"setxlimit(self) - set and update xlim for plot figure"
	self.Rg[2] = self.ymin.get()
	self.Rg[3] = self.ymax.get()
	ylim(self.Rg[2],self.Rg[3])

    def setxcid(self):
	"setxcid(self) - reset data as column array"
	self.columndata()

    def setxrid(self):
	"setxrid(self) - reset data as row array"
	self.rowdata()

    def addMoreMenuBar(self):
	"addMoreMenuBar(self) - create menubar user interface"
        self.menuBar.addmenuitem('File','command',
                'Read a MDA 1D array',
                label='MDA 1D Data...',
                command = self.pickMDA)
        self.menuBar.addmenuitem('File','command',
                'Read a column or row oriented ASCII file',
                label='Load Ascii Data...',
                command = self.pickFile)
	self.menuBar.addmenuitem('File','command',label='------------------')
        self.menuBar.addmenuitem('File','command',
                'Print the plot',
                label='Print plot1d.jpg',
                command = self.Print)
        self.menuBar.addmenuitem('File','command',
                'Setup printer',
                label='Printer... ',
                command = self.printer)
	self.menuBar.addmenuitem('File','command',label='------------------')
        self.menuBar.addmenuitem('File','command',
                'Quit this program',
                label='Quit',
                command = self.closeup)
        self.menuBar.addmenuitem('Setup','command',
                'Display the loaded file',
                label='Display Ascii file...',
                command = self.displayFile)
	self.menuBar.addmenuitem('Setup','command',label='------------------')
        self.menuBar.addmenuitem('Setup','command',
                'Row Oriented Data Array',
                label='Row Oriented',
                command = self.rowdata)
        self.menuBar.addmenuitem('Setup','command',
                'Column Oriented Data Array',
                label='Column Oriented',
                command = self.columndata)
	self.menuBar.addmenuitem('Setup','command',label='------------------')
        self.menuBar.addmenuitem('Setup','command',
                'Initialize X data range',
                label='Set Full X Range...',
                command = self.setupXrange)
	self.menuBar.addmenuitem('Setup','command',label='------------------')
        self.menuBar.addmenuitem('Setup','command',
                'Select All buttons for defined curves',
                label='Select All CheckButton',
                command = self.CBallon)
        self.menuBar.addmenuitem('Setup','command',
                'Select None curves',
                label='Select None CheckButton',
                command = self.CBalloff)

        self.menuBar.addmenuitem('Help','command',
                'Help Info about plot1d',
                label='Help Info...',
                command = self.helpinfo)

	self.menuBar.addmenu('PlotOption',' ')
        self.toggleStyVar = IntVar()
        self.menuBar.addmenuitem('PlotOption', 'checkbutton',
                                 'Toggle Line style on or off',
                                 label='Line Style On',
                                 variable = self.toggleStyVar,
                                 command=self.toggleSty)
        self.toggleGridVar = IntVar()
        self.menuBar.addmenuitem('PlotOption', 'checkbutton',
                                 'Toggle grid lines on or off',
                                 label='Grid Line On',
                                 variable = self.toggleGridVar,
                                 command=self.toggleGrid)
	self.menuBar.addmenuitem('PlotOption','command',label='------------------')
	self.xlog = IntVar()
        self.menuBar.addmenuitem('PlotOption', 'checkbutton',
                                 'Toggle Xlog plot on or off',
                                 label='Log Xaxis On',
                                 variable = self.xlog)
	self.ylog = IntVar()
        self.menuBar.addmenuitem('PlotOption', 'checkbutton',
                                 'Toggle Ylog plot on or off',
                                 label='Log Yaxis On',
                                 variable = self.ylog)
	
	self.menuBar.addmenuitem('PlotOption','command',label='------------------')
        self.toggleSymVar = IntVar()
        self.menuBar.addmenuitem('PlotOption', 'checkbutton',
                                 'Toggle symbol on or off',
                                 label='Symbol On',
                                 variable = self.toggleSymVar,
                                 command=self.toggleSym)
	self.menuBar.addmenuitem('PlotOption','command',
		'Dialog to setup up symbols',
		label='Setup Symbols...',
		command=self.setsymbols)

	self.menuBar.addmenu('Legend','set up legend ')
        self.toggleLegVar = IntVar()
        self.menuBar.addmenuitem('Legend', 'checkbutton',
                                 'Toggle legend on or off',
                                 label='Legend On',
                                 variable = self.toggleLegVar,
                                 command=self.toggleLegend)
        self.menuBar.addmenuitem('Legend', 'command',
                                 'pick desired location',
                                 label='Default Legend Location',
                                 command=self.pickLegpos)
	self.menuBar.addmenuitem('Legend','command',label='------------------')
	self.menuBar.addmenuitem('Legend','command',
		'Dialog to setup up new legend position',
		label='User Legend Location...',
		command=self.setlegpos)
	self.menuBar.addmenuitem('Legend','command',label='------------------')
        self.menuBar.addmenuitem('Legend','command',
                'Setup legend names',
                label='Setup Legend Labels...',
                command = self.getlegend)

	self.menuBar.addmenu('Analysis','set up polynomial fitting ')
        self.menuBar.addmenuitem('Analysis','command',
                'Setup curve # for statistic plot',
                label='Statistic ...',
                command = self.statisticDialog)
        self.menuBar.addmenuitem('Analysis','command',
                'Setup line # for least square fitting',
                label='Fitting ...',
                command = self.fittingNumDialog)
        self.menuBar.addmenuitem('Analysis','command',
                'Setup bin numbers # for histogram plot',
                label='Histogram ...',
                command = self.histDialog)
        self.menuBar.addmenuitem('Analysis','command',
                'Setup curve # for errorbar plot',
                label='Errorbar ...',
                command = self.errorbarDialog)


    def statisticDialog(self):
	"statisticDialog(self) - statistic calculation"
	import Tkinter
	if self.stdFrame != None: self.statisticDone()
	top=Toplevel()
	self.stdFrame=top
	fm = Frame(top,borderwidth=0)
	top.title('Statistic Dialog...')
	Label(fm,text='Curve # [1-'+str(self.nc)+']').grid(row=1,column=1,sticky=W)

	asply = tuple(range(1,self.nc+1))
	self.stdVar = Pmw.ComboBox(fm,label_text='Pick:',
		labelpos=W, listbox_width=5,dropdown=1,
		scrolledlist_items=asply)
	self.stdVar.selectitem(0)
	
	self.stdVar.grid(row=1,column=2,sticky=W)

	Tkinter.Button(fm,text='Close',command=self.statisticDone).grid(row=4,column=1,stick=W)	
	Tkinter.Button(fm,text='Accept',command=self.statisticCalc).grid(row=4,column=2,stick=W)	
	Tkinter.Button(fm,text='Next',command=self.statisticNext).grid(row=4,column=3,stick=W)	
	Tkinter.Button(fm,text='Prev',command=self.statisticPrev).grid(row=4,column=4,stick=W)	
	Tkinter.Button(fm,text='All...',command=self.statisticAll).grid(row=4,column=5,stick=W)	
	fm.pack()
	fm2 = Frame(top,borderwidth=0)
	self.stdL = [StringVar(),StringVar(),StringVar(),StringVar(),StringVar(),StringVar()]
	Label(fm2, textvariable=self.stdL[0]).pack(side=TOP)
	Label(fm2, textvariable=self.stdL[1]).pack(side=TOP)
	Label(fm2, textvariable=self.stdL[2]).pack(side=TOP)
	Label(fm2, textvariable=self.stdL[3]).pack(side=TOP)
	Label(fm2, textvariable=self.stdL[4]).pack(side=TOP)
	Label(fm2, textvariable=self.stdL[5]).pack(side=TOP)
	self.stdL[0].set('Mean:')
	self.stdL[1].set('Standard Deviation:')
	self.stdL[2].set('Ymin,Ymax:')
	self.stdL[3].set('Ymax @ Xpos:')
	self.stdL[4].set('Y-hpeak @ X-hpeak:')
	self.stdL[5].set('FWHM:')
	fm2.pack()
	
    def statisticAll(self):
      "statisticAll(self) - calculate statistic for all curves"
      out = []
      for id in range(self.nc):
	y = self.y[id-1]
	ymin,ymax = min(y),max(y)
	y_hpeak = ymin + .5 *(ymax-ymin)
	x = self.x
	x_hpeak = []
	for i in range(self.NPT):
		if y[i] >= y_hpeak:
			i1 = i
			break
	for i in range(i1+1,self.NPT):
		if y[i] <= y_hpeak:
			i2 = i
			break
		if i == self.NPT-1: i2 = i
	x_hpeak = [x[i1],x[i2]]
	fwhm = abs(x_hpeak[1]-x_hpeak[0])
	for i in range(self.NPT):
		if y[i] == ymax: 
			jmax = i
			break
	xpeak = x[jmax]

	out.append([MLab.mean(y),MLab.std(y),ymin,ymax,xpeak,jmax,y_hpeak,x_hpeak,fwhm])
      fo = open('fwhm.txt','w')
      fo.write('File:  '+self.fname)
      for id in range(self.nc):
		list = out[id]
		fo.write('\n\nCurve #'+str(id+1))
		fo.write('\nMean: '+ str(list[0]))
		fo.write('\nStandard Deviation: '+ str(list[1]))
		fo.write('\nYmin, Ymax: '+ str(list[2]) + ', '+ str(list[3]))
		fo.write('\nYmax @ Xpos[i]: ' + str(list[4]) +'[i='+str(list[5])+']')
		fo.write('\nY-hpeak @ X-hpeak: ' + str(list[6]) +' @ '+str(list[7]))
		fo.write('\nFWHM: ' + str(list[8]))
      fo.close()
      xdisplayfile('fwhm.txt')

    def statisticPrev(self):
	"statisticPrev(self) - statistic calculation for previous curve"
	id = string.atoi(self.stdVar.get())
	id = id - 1
	if id < 1: id = self.nc
	self.stdVar.selectitem(id-1)
	self.statisticCalc()
	
    def statisticNext(self):
	"statisticNext(self) - statistic calculation for next curve"
	id = string.atoi(self.stdVar.get())
	id = id+1
	if id > self.nc: id = 1
	self.stdVar.selectitem(id-1)
	self.statisticCalc()
	
    def statisticCalc(self):
	"statisticCalc(self) - statistic calculation "
	id = string.atoi(self.stdVar.get())
	if id <1 or id > self.nc: return

	y = self.y[id-1]
	ymin,ymax = min(y),max(y)
	y_hpeak = ymin + .5 *(ymax-ymin)
	x = self.x
	x_hpeak = []
	for i in range(self.NPT):
		if y[i] >= y_hpeak:
			i1 = i
			break
	for i in range(i1+1,self.NPT):
		if y[i] <= y_hpeak:
			i2 = i
			break
		if i == self.NPT-1: i2 = i
	if y[i1] == y_hpeak: x_hpeak_l = x[i1]
	else:
		x_hpeak_l = (y_hpeak-y[i1-1])/(y[i1]-y[i1-1])*(x[i1]-x[i1-1])+x[i1-1]
	if y[i2] == y_hpeak: x_hpeak_r = x[i2]
	else:
		x_hpeak_r = (y_hpeak-y[i2-1])/(y[i2]-y[i2-1])*(x[i2]-x[i2-1])+x[i2-1]
	x_hpeak = [x_hpeak_l,x_hpeak_r]

	self.fwhm = abs(x_hpeak[1]-x_hpeak[0])
	for i in range(self.NPT):
		if y[i] == ymax: 
			jmax = i
			break
	xpeak = x[jmax]
		
	self.stdL[0].set('Curve #'+str(id)+'  Mean: '+ str(MLab.mean(y)))
	self.stdL[1].set('Standard Deviation: '+ str(MLab.std(y)))
	self.stdL[2].set('Ymin, Ymax: '+ str(ymin) + ', '+ str(ymax))
	self.stdL[3].set('Ymax @ Xpos[i]: ' + str(xpeak) +'[i='+str(jmax)+']')
	self.stdL[4].set('Y-hpeak @ X-hpeak: ' + str(y_hpeak) +' @ '+str(x_hpeak))
	self.stdL[5].set('FWHM: ' + str(self.fwhm))

    def statisticDone(self):
	"statisticDone(self) - close statistic dialog"
	self.stdFrame.destroy()
	self.stdFrame = None

    def errorbarDialog(self):
	"errorbarDialog(self) - dialog to setup errorbar plot"
	import Tkinter
	if self.errFrame != None: self.errDone()
	top=Toplevel()
	self.errFrame=top
	fm = Frame(top,borderwidth=0)
	top.title('Errorbar Dialog...')
	self.errVar = [IntVar(),StringVar(),IntVar()]
	Label(fm,text='Curve # [1-'+str(self.nc)+']:').grid(row=1,column=1,sticky=W)
	asply = tuple(range(1,self.nc+1))
	self.errVar[0] = Pmw.ComboBox(fm,label_text='Pick:',
		labelpos=W, listbox_width=5,dropdown=1,
		scrolledlist_items=asply)
	self.errVar[0].grid(row=1,column=2,sticky=W)
	self.errVar[0].selectitem(0)

	Label(fm,text='Relative Y Errorbar:').grid(row=2,column=1,sticky=W)
	Entry(fm,width=10,textvariable=self.errVar[1]).grid(row=2,column=2,sticky=W)
	Label(fm,text='Plot Horizontally:').grid(row=3,column=1,sticky=W)
	Checkbutton(fm,variable=self.errVar[2],state=NORMAL).grid(row=3,column=2,sticky=W)
	self.errVar[1].set('.1')
	Tkinter.Button(fm,text='Accept',command=self.errRun).grid(row=4,column=1,stick=W)	
	Tkinter.Button(fm,text='Close',command=self.errDone).grid(row=4,column=2,stick=W)	
	fm.pack(fill=BOTH)

    def errDone(self):
	"errDone(self) - close error bar dialog"
	self.errFrame.destroy()
	self.errFrame = None

    def errRun(self):
	"errRun(self) - plot error bar for selected curve"
	ic = string.atoi(self.errVar[0].get())
	if ic > 0 and ic < self.nc:
	   err = string.atof(self.errVar[1].get())
	   hz = self.errVar[2].get()
	   self.fig = self.fig+1
	   figure(self.fig,figsize=(5.5,4))
	   x = self.x
	   y = self.y
	   from Numeric import multiply
	   yerr = multiply(y[ic-1],err)
	   if hz:
		errorbar(y[ic-1],x,xerr=yerr)
	   else:
		errorbar(x,y[ic-1],yerr=yerr)
	   title('Curve # '+str(ic))
	   connect('button_press_event',self.closewin)
	   show()

    def histDialog(self):
	"histogramDialog(self) - dialog to setup histogram plot"
	import Tkinter
	if self.histFrame != None: self.histDone()
	top=Toplevel()
	self.histFrame=top
	fm = Frame(top,borderwidth=0)
	top.title('Histogram Dialog...')
	self.histVar = [StringVar(),IntVar(),IntVar()]
	Label(fm,text='Curve # [1-'+str(self.nc)+']:').grid(row=1,column=1,sticky=W)
	asply = tuple(range(1,self.nc+1))
	self.histVar[0] = Pmw.ComboBox(fm,label_text='Pick:',
		labelpos=W, listbox_width=5,dropdown=1,
		scrolledlist_items=asply)
	self.histVar[0].grid(row=1,column=2,sticky=W)
	self.histVar[0].selectitem(0)

	Label(fm,text='Number of bins:').grid(row=2,column=1,sticky=W)
	Entry(fm,width=10,textvariable=self.histVar[1]).grid(row=2,column=2,sticky=W)
	Label(fm,text='Horizontal:').grid(row=3,column=1,sticky=W)
	Checkbutton(fm,variable=self.histVar[2],state=NORMAL).grid(row=3,column=2,sticky=W)
	self.histVar[1].set(20)
	Tkinter.Button(fm,text='Accept',command=self.histRun).grid(row=4,column=1,stick=W)	
	Tkinter.Button(fm,text='Close',command=self.histDone).grid(row=4,column=2,stick=W)	
	fm.pack(fill=BOTH)

    def histRun(self):
	"histRun(self) - do histogram plot for selected curve"
	ic = string.atoi(self.histVar[0].get())
	if ic > 0 and ic < self.nc:
	   nbin = self.histVar[1].get()
	   hz = self.histVar[2].get()
	   self.fig = self.fig+1
	   figure(self.fig,figsize=(5.5,4))
	   y = self.y
	   if hz: 
		n,bins,patches =  hist(y[ic-1],nbin,orientation='horizontal')
	   	xlabel('Occurance')
	   else: 
		n,bins,patches =  hist(y[ic-1], nbin)
	   	ylabel('Occurance')
	   title('Curve # '+str(ic)+': Histogram for bin='+str(nbin))
	   connect('button_press_event',self.closewin)
	   show()
	   print n

    def histDone(self):
	"histDone(self) - close histogram dialog"
	self.histFrame.destroy()
	self.histFrame = None

    def setupXrange(self,title=None):
	"setupXrange(self) - dialog to reset X axis data range"
	import Tkinter
	top=Toplevel()
	self.setXFrame=top
	fm = Frame(top,borderwidth=0)
	if title == None: ntitle='Set New Data XRange...'
	else: ntitle = title
	top.title(ntitle)
	self.xVar = [StringVar(),StringVar()]
	Label(fm,text='Plot Start Coordinate X[0]:').grid(row=1,column=1,sticky=W)
	Entry(fm,width=20,textvariable=self.xVar[0]).grid(row=1,column=2,sticky=W)
	sz = len(self.x)
	Label(fm,text='Plot Stop Coordinate X['+str(sz-1)+']:').grid(row=2,column=1,sticky=W)
	Entry(fm,width=20,textvariable=self.xVar[1]).grid(row=2,column=2,sticky=W)
	self.xVar[0].set(0)
	self.xVar[1].set(sz-1)
	Tkinter.Button(fm,text='Close',command=self.setupXrangeDone).grid(row=4,column=1,stick=W)	
	Tkinter.Button(fm,text='Accept',command=self.setupXrangeRun).grid(row=4,column=2,stick=W)	
	Tkinter.Button(fm,text='Reset',command=self.setupXrangeReset).grid(row=2,column=3,stick=W)	
#	if title != None:
#		Tkinter.Button(fm,text='Functions Fit...',command=self.otherfit).grid(row=4,column=3,stick=W)	
	fm.pack(fill=BOTH)

    def setupXrangeReset(self):
	"setupXrangeReset(self) - set X range value"
	self.xVar[0].set(str(self.xcord[0]))
	self.xVar[1].set(str(self.xcord[self.NPT-1]))


    def setupXrangeDone(self):
	"setupXrangeDone(self) - close X range dialog"
	self.setXFrame.destroy()

    def setupXrangeRun(self):
	"setupXrangeRun(self) - accept and setup X range"
	x1 = string.atof(self.xVar[0].get())
	x2 = string.atof(self.xVar[1].get())
	dx = (x2-x1)/(self.NPT-1)
	x = arange(x1,x2+.001,dx)
	y = self.y	
	self.initfields(x,y)

    def fittingNumDialog(self):
	"fittingNumDialog(self) - dialog to enter curve # for fitting"
	import Tkinter
	if self.fitFrame != None: self.fittingDone()
	top=Toplevel()
	self.fitFrame=top
	fm = Frame(top,borderwidth=0)
	top.title('Least Square  Fitting Dialog...')
	self.fitVar = [IntVar(),IntVar(),StringVar(),StringVar(),StringVar(),StringVar()]
	Label(fm,text='Curve # to be fitted').grid(row=1,column=1,sticky=W)
	asply = tuple(range(1,self.nc+1))
	self.fitVar[0] = Pmw.ComboBox(fm,label_text='[1-'+str(self.nc)+'] Pick:',
		labelpos=W, listbox_width=5,dropdown=1,
		scrolledlist_items=asply)
	self.fitVar[0].grid(row=1,column=2,sticky=W)
	self.fitVar[0].selectitem(0)

	Label(fm,text='Polynomial order #:').grid(row=2,column=1,sticky=W)
	Entry(fm,width=10,textvariable=self.fitVar[1]).grid(row=2,column=2,sticky=W)
	Tkinter.Button(fm,text='Polynomial Fit...',command=self.fittingRun).grid(row=4,column=1,stick=W)	
#	Tkinter.Button(fm,text='Functions Fit...',command=self.otherfit).grid(row=4,column=2,stick=W)	
	Tkinter.Button(fm,text='Close',command=self.fittingDone).grid(row=4,column=3,stick=W)	
#	Tkinter.Button(fm,text='Help...',command=self.fittingHelp).grid(row=5,column=1,stick=W)	
#	Tkinter.Button(fm,text='Try New Fit Xrange...',command=self.otherxfit).grid(row=5,column=2,stick=W)	
	Label(fm,text='Output Title:').grid(row=15,column=1,sticky=W)
	Entry(fm,width=40,textvariable=self.fitVar[2]).grid(row=15,column=2,sticky=W)
	Label(fm,text='Output Xlabel:').grid(row=16,column=1,sticky=W)
	Entry(fm,width=40,textvariable=self.fitVar[3]).grid(row=16,column=2,sticky=W)
	Label(fm,text='Output Ylabel:').grid(row=17,column=1,sticky=W)
	Entry(fm,width=40,textvariable=self.fitVar[4]).grid(row=17,column=2,sticky=W)
	Label(fm,text='Ouput Fitting Coeffs:').grid(row=18,column=1,sticky=W)
	Entry(fm,width=40,textvariable=self.fitVar[5]).grid(row=18,column=2,sticky=W)
#	self.fitVar[0].set(1)
	self.fitVar[1].set(2)
	self.fitVar[2].set('Fitting Result Curve #')
	self.fitVar[3].set('Polynomial Power')
	self.fitVar[4].set('Polynomial Regression')
	fm.pack(fill=BOTH)

    def fittingDone(self):
	"fittingDone(self) - close fitting dialog"
	self.fitFrame.destroy()
	self.fitFrame = None

    def fittingHelp(self):
	'fittingHelp(self) - help on fitting dialog'
	text = 'Polynomial Fit... - use curve # and order # to do polynomial fit\n-->Functions Fit... - use default X value in various fitting functions\n --> Try New Fit Xrange... - if fit failed with default X values use the Xrange dialog to try oher X range' 
	self.message(nm=text,info='Fitting Info')


    def otherxfit(self):
	'otherxfit(self) - try fit with different X range'
	if self.setXFrame != None: self.setXFrame.destroy()
	self.setupXrange(title='Try New Fitting X Range')
	self.xVar[0].set('-'+self.xVar[1].get())


    def otherfit(self):
	'otherfit(self) - pop up Least Square fit dialog'
	id = string.atoi(self.fitVar[0].get())
	if id > 0 and id <= self.nc:
		x = self.x
		y = self.y[id-1]
		x1 = string.atof(self.xmin.get())
		x2 = string.atof(self.xmax.get())
		i1 = 0
		for i in range(self.NPT):
			if x[i] <= x1: 
				i1 = i
			else: 
				break
		for i in range(i1,self.NPT):
			if x[i] <= x2: 
				i2 = i
			else: 
				break

		data = []
		for k in range(i1,i2+1):
			data.append( (x[k],y[k]) )	
		Fit = FitDialog(self.fitFrame)
                Fit.x = x
                Fit.y = y
		Fit.data = data
		Fit.legd = 0
		Fit.Wtitle = 'Curve # '+str(id)
		Fit.createDialog(self.fitFrame)

    def fittingRun(self):
	"fittingRun(self) - accept power and curve # to do polynomial fit"
	id = string.atoi(self.fitVar[0].get())
	pow = self.fitVar[1].get()
	if id > 0 and id < self.nc:
		x = self.x
		y = self.y[id-1]
		x1 = string.atof(self.xmin.get())
		x2 = string.atof(self.xmax.get())
		i1 = 0
		for i in range(self.NPT):
			if x[i] <= x1: 
				i1 = i
			else: 
				break
		for i in range(i1,self.NPT):
			if x[i] <= x2: 
				i2 = i
			else: 
				break
		x = x[i1:i2+1]
		y = y[i1:i2+1]
	# linear polynomial fit
		coeffs = polyfit(x,y,pow)
		self.fitVar[5].set(str(coeffs))
		z = polyval(coeffs,x)
		self.fig=self.fig+1
		figure(self.fig,figsize=(5.5,4))
		plot(x,y,'b+', x, z ,'-k',linewidth=1)
		tit = self.fitVar[2].get() +' ' + str(id)
		title(tit)
		xtit = self.fitVar[3].get() + ' '+str(pow) 
		xlabel(xtit)
		ytit = self.fitVar[4].get() 
		ylabel(ytit)
		gl = self.toggleGridVar.get()
		grid(gl)
		connect('button_press_event',self.closewin)
		show()

    def closewin(self,event):
	'closewin(self,event) - right mouse button to close plot window'
	if event.button == 3: close()

    def closeall(self):
	'closeall(self) - close all plot windows'
	close('all')
	self.fig = 0

    def printer(self):
	'printer(self) - dialog to set up printer'
        from tv import setupPrinter
        root=self.interior()
        dialog = setupPrinter(root)

    def Print(self):
	'Print(self) - save plot to plot1d.png and send to PS printer'
	from plot2d import printPicture
        savefig('plot1d.png')
        ptr = self.SH['printer']
        printPicture('plot1d.png',ptr)

    def doneLeg(self):
	'doneLeg(self) - close setup legend dialog'
	self.legFrame.destroy()
	self.legFrame = None

    def toggleLeg(self):
	"toggleLeg(self) - get default legend position"
	self.legloc = self.legVar.get()
	self.doneLeg()
	try: 
		if self.legOn: legend(self.labels,loc=legends[self.legloc])
	except:
		pass

    def pickLegpos(self):
	"pickLegpos(self) - dialog to pick legend position"
	import Tkinter
	if self.legFrame != None: self.doneLeg()
	top=Toplevel()
	self.legFrame=top
	fm = Frame(top,borderwidth=0)
	var = IntVar()
	for i in range(len(legends)):
		Radiobutton(fm,text=legends[i],value=i,variable=var,
			command=self.toggleLeg,
			indicatoron=1).pack(anchor=W)
	var.set(0)
	self.legVar= var
	fm.pack(fill=BOTH)

    def toggleLegend(self):
	"toggleLegend(self) - set Legend on or off"
	self.legOn = self.toggleLegVar.get()

    def toggleSym(self):
	"toggleSym(self) - set symbols on or off"
	self.symOn = self.toggleSymVar.get()

    def toggleGrid(self):
	"toggleGrid(self) - set grid line on or off"
	gl = self.toggleGridVar.get()
	grid(gl)

    def toggleSty(self):
	"toggleSty(self) - set line style on or off"
	self.styOn = self.toggleStyVar.get()

    def getlegpos(self):
	"getlegpos(self) - get and set new legposition"
	locx = self.locx.get()
	locy = self.locy.get()
	self.legFrame.destroy()
	self.legFrame = None
	try:
	  loc = (string.atof(locx),string.atof(locy))
	  if self.legOn: legend(self.labels, loc=loc)
	except:
	  pass

    def setlegpos(self):
	"setlegpos(self) - dialog to set legend position"
	import Tkinter
	if self.legFrame != None: return
	top=Toplevel()
	top.title('Enter Legend Location')
	self.legFrame=top
	fm = Frame(top,borderwidth=0)
	self.locx,self.locy = StringVar(), StringVar()
	Label(fm,text='ENTER LEGEND LOCATION').grid(row=0,column=1,sticky=W)
	Label(fm,text='Normalized X loc[0-1]:').grid(row=1,column=1,sticky=W)
	Entry(fm,width=5,textvariable=self.locx).grid(row=1,column=2,sticky=W)
	self.locx.set(0.8)
	Label(fm,text='Normalized Y loc[0-1]:').grid(row=2,column=1,sticky=W)
	Entry(fm,width=5,textvariable=self.locy).grid(row=2,column=2,sticky=W)
	self.locy.set(0.8)
	fm.pack(fill=BOTH)
	Tkinter.Button(top,text='OK',command=self.getlegpos).pack()

    def getsymbols(self):
	"getsymbols(self) - get and set new symbols"
	self.spp = string.atoi(self.sppVar.get())
	if self.spp < 1: self.spp = 1
	for i in range(len(symbols)):
		symbols[i] = self.sym[i].get()

    def getsymbolClose(self):
	'getsymbolClose(self) - close symbol dialog'
	self.SymFrame.destroy()

    def setsymbols(self):
	"setsymbols(self) - dialog to modify and set new symbols"
	import Tkinter
	top=Toplevel()
	top.title('Symbol Definition')
	self.SymFrame=top
	sym=[]
	for i in range(len(symbols)):
		sym.append(StringVar())
	fm = Frame(top,borderwidth=0)
	for i in range(len(symbols)):
	    Label(fm,text='symbol for line '+str(i+1)).grid(row=i,column=1,sticky=W)
	    Entry(fm,width=1,textvariable=sym[i]).grid(row=i,column=2,sticky=W)
	    sym[i].set(symbols[i])
	self.sym = sym
	Label(fm,text='DataSteps/symbol').grid(row=20,column=1,sticky=W)
	self.sppVar = StringVar()
	Entry(fm,width=5,textvariable=self.sppVar).grid(row=20,column=2,sticky=W)
	self.sppVar.set(str(self.spp))
	fm.pack(fill=BOTH)
	fm1 = Frame(top,borderwidth=1)
	Tkinter.Button(fm1,text='  OK  ',command=self.getsymbols).pack(side=LEFT)
	Tkinter.Button(fm1,text='Cancel',command=self.getsymbolClose).pack(side=LEFT)
	fm1.pack(fill=BOTH)
	
    def helpinfo(self):
	"helpinfo(self) - display plot1d_help.txt with scrolled text"
	fname = os.environ['PYTHONSTARTUP']+os.sep+'plot1d_help.txt'
	top = Toplevel()
	st = Pmw.ScrolledText(top,borderframe=1,labelpos=N,
		label_text=fname,usehullsize=1,
		hull_width=600,hull_height=400,
		text_padx=10,text_pady=10,
		text_wrap='none')
	st.importfile(fname)
	st.pack(fill=BOTH, expand=1, padx=1, pady=1)

    def getlegend(self):
	"getlegend(self) - dialog to set legends for plot at most 85"
	from plotAscii import GetLegends,loadpvs
	V = 85*['']
	for i in range(self.nc):
		V[i] = 'D_'+str(i+1)
	file='pvs'
	fd = open(file,'w')
	fd.write(str(V))
	fd.close()
	top = self.form
	GetLegends(top)
	self.pvs = loadpvs()

    def displayFile(self):
	"displayFile(self) - display picked text file"
	if self.fname != '': xdisplayfile(self.fname)
	
    def rowdata(self):
      "rowdata(self) - extract x,y vectors from row oriented text array"
      try:
	data = self.data
	nc = len(data)
	NPT = len(data[0])
	self.NPT = NPT
	try:
		xid = int(self.xrid.get())
		yid = int(self.yrid.get())
	except ValueError:
		self.message(nm='Row data array - X row #:\nonly single integer # allowed')
		return
	if xid < 0 or xid >= nc: 
		x = range(NPT) 
		y = data[0:nc]
	else:
		x = data[xid]
		y = []
		for i in range(nc):
		     if i >= yid:
			y.append(data[i])
	self.initfields(x,y)
      except AttributeError:
	self.message()
	return

    def columndata(self):
      "columndata(self) - extract x,y vectors from column oriented text array"
      try:
	from plotAscii import transposeA
	data = self.data
	NPT = len(data)
	self.NPT = NPT
	NC = len(data[0])
	if NC <= 1: 
		print 'bad file'
		return
	self.W[0].setentry(self.fname)
	da = transposeA(data)
	try:
		xid = int(self.xcid.get())
		yid = int(self.ycid.get())
	except ValueError:
		self.message(nm='Column: X col #:\nonly single integer # allowed')
		return
	if xid < 0:  
		x = range(NPT)
		y = da[0:NC]
	else:
		x = da[xid]
		y=[]
		for i in range(NC):
		    if i >= yid:
			y.append(da[i])
	self.initfields(x,y)
	self.xcord = x
      except AttributeError:
	self.message()
	return

    def pickMDA(self):
	'pickMDA(self) - dialog to pick MDA file and load 1D array into memory'
        import tkFileDialog
	from readMDA import *
        fname = tkFileDialog.askopenfilename( initialdir=self.mdapath,
                filetypes=[("MDA File", '.mda'),
                ("All Files","*")])
        if fname == (): return
        (self.mdapath, fn) = os.path.split(fname)
        self.mdafile = fn # fname
	self.W[0].setentry(fname)
        d = readMDA(fname,maxdim=1)
        try:
            if d[1].nd> 0:
               # print '1D data found'
		self.W[1].setentry(d[1].p[0].fieldName)
		x = d[1].p[0].data
		self.NPT = len(x)
		data = []
		labels = []
		for i in range(d[1].nd):
			data.append(array(d[1].d[i].data))
			labels.append(d[1].d[i].name)
		self.pvs = labels
		self.initfields(x,data)
		self.xcord = x
        except IndexError:
            pass

    def pickFile(self):
	"pickFile(self) - dialog to pick a text data file"
	from plotAscii import readArray
	import tkFileDialog
	fname = tkFileDialog.askopenfilename(initialdir=self.txtpath,
                initialfile='*.txt')
        if fname ==(): return
	self.fname = fname
	data = readArray(fname)
	self.data = data
	self.columndata()

    def initfields(self,x,y):
	"initfields(self,x,y) - initialize X,Y ranges fields from x,y vectors"
	self.x = x
	self.y = y
	self.nc = len(y)
	xmax = max(x)
	xmin = min(x)
	self.Rg[0] = xmin
	self.Rg[1] = xmax
	ymin,ymax = minmax(y)
	self.Rg[2] = ymin
	self.Rg[3] = ymax
	self.xmin.setentry(str(xmin))
	self.xmax.setentry(str(xmax))
	self.ymin.setentry(str(ymin))
	self.ymax.setentry(str(ymax))
	self.createCB()

    def createCB(self):
	"createCB(self) - update CheckButtons to reflect the defined y vectors"
	nc = self.nc # 85
	checkD=[]
	var =[]
	for i in range(nc):
	  di = str(i+1)
	  var.append(IntVar())
	  if i < 2:
	    var[i].set(1)
	  if i > 9: 
	    ii = i % 10
	    ij = i / 10
            checkD.append((di,ij,ii,NORMAL))
	  else:
            checkD.append((di,0,i,NORMAL))

	self.var = var
	if self.CBframe != -1: self.CBframe.destroy()
	frame = Frame(self.form,borderwidth=0)
	for i in range(nc):
          Checkbutton(frame,text=checkD[i][0],state=checkD[i][3], anchor=W,
          variable=var[i]).grid(row=checkD[i][1],column=checkD[i][2],sticky=W)
	frame.pack()
	self.CBframe = frame
#	self.getCB()

    def getCB(self):
	"getCB(self) - get the state of all checked buttons"
	value=[]
	for i in range(self.nc):
		value.append(self.var[i].get())
	return value

    def CBallon(self):
	"CBallon(self) - select all check buttons for Y vectors"
	if self.nc > 1:
	  for i in range(self.nc):
		self.var[i].set(1)

    def CBalloff(self):
	"CBalloff(self) - unselect all check buttons for Y vectors"
	if self.nc > 1:
	  for i in range(self.nc):
		self.var[i].set(0)

    def settitle(self):
	"settitle(self) - update the title of plot figure"
	title(self.W[0].get())

    def setxlabel(self):
	"setxlabel(self) - update the xlabel of plot figure"
	xlabel(self.W[1].get())

    def setylabel(self):
	"setylabel(self) - update the ylabel of plot figure"
	ylabel(self.W[2].get())

    def createFields(self):
	"createFields(self) - create modifiable control fields for plot"
	self.form = self.interior()
	self.W = [StringVar(),StringVar(),StringVar()]
	self.W[0] = Pmw.EntryField(self.form,labelpos=W,value=self.title,
		label_text = 'Title', command=self.settitle)
	self.W[1] = Pmw.EntryField(self.form,labelpos=W,value=self.xlabel,
		label_text = 'Xlabel', command=self.setxlabel)
	self.W[2] = Pmw.EntryField(self.form,labelpos=W,value=self.ylabel,
		label_text = 'Ylabel', command=self.setylabel)
	self.W[0].pack(fill=X)
	self.W[1].pack(fill=X)
	self.W[2].pack(fill=X)


	frame = Frame(self.form,borderwidth=0)
	self.xmin = Pmw.EntryField(frame,labelpos=W,value=self.Rg[0],
		label_text = 'Xrange Xmin:', command=self.setxlimit,
#		validate = {'validator':'real','min':0,'max':100,'minstrict':0}
		)
	self.xmax = Pmw.EntryField(frame,labelpos=W,value=self.Rg[1],
		label_text = ' Xmax:', command=self.setxlimit
		)
	self.xmin.grid(row=1,column=1,sticky=W)
	self.xmax.grid(row=1,column=2,sticky=W)

	self.ymin = Pmw.EntryField(frame,labelpos=W,value=self.Rg[2],
		label_text = 'Yrange Ymin:', command=self.setylimit,)
	self.ymax = Pmw.EntryField(frame,labelpos=W,value=self.Rg[3],
		label_text = ' Ymax:', command=self.setylimit)
	self.ymin.grid(row=2,column=1,sticky=W)
	self.ymax.grid(row=2,column=2,sticky=W)
	self.xcid = Pmw.EntryField(frame,labelpos=W,value='0',
		command=self.setxcid,
		label_text = 'Column Data: X col #:')
	self.ycid = Pmw.EntryField(frame,labelpos=W,value='1',
		label_text = '       Start Y col #:')
	self.xrid = Pmw.EntryField(frame,labelpos=W,value='-1',
		command=self.setxrid,
		label_text = ' Row data: X row #:')
	self.yrid = Pmw.EntryField(frame,labelpos=W,value='0',
		label_text = '       Start Y row #:')
	self.xcid.grid(row=3,column=1,sticky=W)
	self.ycid.grid(row=4,column=1,sticky=W)
	self.xrid.grid(row=5,column=1,sticky=W)
	self.yrid.grid(row=6,column=1,sticky=W)
	frame.pack()

    def startup(self):
      "startup(self) - initialize variables at object plot1d creation"
      from plotAscii import readST,loadpvs,initSH
      self.CBframe = -1
      self.nc = -1
      self.fig = 0
      self.symOn = 0
      self.legOn = 1
      self.spp = 1
      self.styOn = 0
      self.legloc = 0
      self.pvs = loadpvs()
      self.linestyles = linestyles
      self.colors = colors
      self.symbols = symbols
      self.SH = initSH()
      self.stdFrame = None
      self.fitFrame = None
      self.histFrame = None
      self.errFrame = None
      self.legFrame = None
      self.Fit = None
      self.setXFrame = None
	
      if os.path.isfile('plot1d.config'):
        lines = readST('plot1d.config')
	self.fname = lines[0]
	if len(lines[0]) >2:
	    pth,fnm = os.path.split(lines[0])
	    self.txtpath = pth
	else :
	    self.txtpath='.'
        self.title = lines[1]
        self.xlabel = lines[2]
        self.ylabel = lines[3]
	self.mdapath = lines[4]
	self.Rg=['0','100','0','100']
      else:
	self.fname=''
	self.txtpath='.'
	self.mdapath='.'
	self.title=''
	self.xlabel=''
	self.ylabel=''
	self.Rg=['0','100','0','100']

    def createInterface(self):
	"createInterface(self) - plot1d object creation"
        AppShell.AppShell.createInterface(self)
        self.createButtons()
        self.addMoreMenuBar()
        self.startup()
        self.toggleSymVar.set(self.symOn)
        self.toggleLegVar.set(self.legOn)
	self.createFields()
        if os.path.isfile(self.fname):
	    from plotAscii import readArray
  	    data = readArray(self.fname)
	    self.data = data
	    self.columndata()


if __name__ == '__main__':
        plt = plot1d()
	plt.run()
