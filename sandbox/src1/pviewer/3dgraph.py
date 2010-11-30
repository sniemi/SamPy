#! /usr/bin/env python

from   Tkinter import *
import Pmw, AppShell, math
from tkFileDialog import askopenfilename
from tkSimpleDialog import Dialog
from plotAscii import readArray,transposeA,xdisplayfile,readST,initSH,writeSH
from imageUtil import indgen,readCT
from tv import minmax
import os
from Numeric import divide,subtract,multiply,reshape
from plot2d import message

class Graph3D(AppShell.AppShell):
    usecommandarea = 1
    appname        = '3-Dimensional Graph'        
    frameWidth     = 650 
    frameHeight    = 450
    
    def addMoremenuBar(self):
	'addMoremenuBar(self) - create menubar interface'
        self.menuBar.addmenuitem('File', 'command',
                'Read 2D image data array ...',
                label='Open Ascii File ...',
                command=self.openAscii)
        self.menuBar.addmenuitem('File', 'command',label='-------------------')
        self.menuBar.addmenuitem('File', 'command',
                'setup printer to override default ',
                label='Printer...',
                command=self.Printer)

        self.menuBar.addmenuitem('Setup', 'command',
                'Display ascii file',
                label='Display Ascii File...',
                command=self.displayFile)
        self.menuBar.addmenuitem('Setup', 'command',
                'Transpose the X,Y axis',
                label='Transpose X,Y',
                command=self.transpose)
        self.menuBar.addmenuitem('Setup', 'command',
                'clear canvas plot area',
                label='Clear Canvas Plot',
                command=self.clearcanvas)
	self.showlineVar = IntVar()
        self.menuBar.addmenuitem('Setup', 'checkbutton',
                'show edge line on plot',
		variable=self.showlineVar,
                label='Show Edge Line',
                command=self.lineon)
	self.extractVar = IntVar()
        self.menuBar.addmenuitem('Setup', 'checkbutton',
                'Rebin the data array as 200x200',
		variable=self.extractVar,
                label='Display Rebin Array',
                command=self.extracton)

        self.menuBar.addmenu('SpectrumColor', 'Various surface plot option')
        self.menuBar.addmenuitem('SpectrumColor', 'command',
		'surface plot rowwise',
                label='Surface Shading',
                command=self.drawsurf2)
        self.menuBar.addmenuitem('SpectrumColor', 'command',
		'plot surface stepwise',
                label='Surface Shading (stepwise)',
                command=self.drawsurf1)
        self.menuBar.addmenuitem('SpectrumColor', 'command',label='-------------------')
        self.menuBar.addmenuitem('SpectrumColor', 'command',
                'draw as surfaceplot',
                label='Surface plot',
                command=self.surfaceon)
        self.menuBar.addmenuitem('SpectrumColor', 'command',
                'draw as surfaceplot',
                label='Surface with Vertical Bar',
                command=self.surfaceskirt)

        self.menuBar.addmenu('ColorTable', 'Use different color table')
	self.menuBar.addmenuitem('ColorTable', 'command',
		'Color Table Dialog',
		label='Change Color Table...',
		command=self.changeCT)
        self.menuBar.addmenuitem('ColorTable', 'command',
		'Rainbow + White Color Table',
                label='Use Rainbow+While Color Table',
                command=self.drawsurf3)
        self.menuBar.addmenuitem('ColorTable', 'command',label='-------------------')
	self.averageVar = IntVar()
        self.menuBar.addmenuitem('ColorTable', 'checkbutton',
                'Toggle cell average color option on or off ',
		variable=self.averageVar,
                label='Average Cell Color On',
                command=self.averageOn)

        self.menuBar.addmenu('MeshLine', 'Mesh Line plot')
        self.menuBar.addmenuitem('MeshLine', 'command',
		'surface mesh grid plot',
                label='Surface Mesh Plot',
                command=self.drawmesh)
        self.menuBar.addmenuitem('MeshLine', 'command',label='-------------------')
        self.menuBar.addmenuitem('MeshLine', 'command',
		'Horizontal row plot',
                label='All Row Lines',
                command=self.drawrows)
        self.menuBar.addmenuitem('MeshLine', 'command',
		'Horizontal row plot',
                label='All Step Lines',
                command=self.drawsteps)
        self.menuBar.addmenuitem('MeshLine', 'command',label='-------------------')
        self.menuBar.addmenuitem('MeshLine', 'command',
		'Selected horizontal row plot',
                label='Pick Row Lines...',
                command=self.drawrowsdialog)
        self.menuBar.addmenuitem('MeshLine', 'command',
		'Selected step lines plot',
                label='Pick Step Lines...',
                command=self.drawstepsdialog)

        self.menuBar.addmenuitem('Help', 'command',
		'help on 3dgraph',
                label='3dgrah_help.txt...',
                command=self.help3dgraph)

    def help3dgraph(self):
	'help3dgraph(self) - display online help 3dgraph_help.txt '
	fname = os.environ['PYTHONSTARTUP']+os.sep+'3dgraph_help.txt'
	xdisplayfile(fname)

    def defaultreadin(self):
	'defaultreadin(self) - display return to the default readin data array'
	da = self.data0
	self.extractSubArray(da)
        self.spectrum    = Pmw.Color.spectrum(self.steps,
                               saturation=0.8,
                               intensity=0.8, extraOrange=1)
	self.clearcanvas()
	self.createAxis()
	self.draw()

    def transpose(self):
	'transpose(self) - transpose and redraw the data array'
	da = self.data
	data = transposeA(da)
	self.extractSubArray(data)
        self.spectrum    = Pmw.Color.spectrum(self.steps,
                               saturation=0.8,
                               intensity=0.8, extraOrange=1)
	self.clearcanvas()
	self.createAxis()
	self.draw()
	if self.CRFrame != None: self.CRFclose()

    def clearcanvas(self):
	'clearcanvas(self) - clear 3D canvas area'
	idss = self.canvas.find_all()
	for id in idss:
		self.canvas.delete(id)

    def lineon(self):
	'lineon(self) - 3D specturm with edge line on or off'
	self.showline = self.showlineVar.get()
	self.clearcanvas()
	self.createAxis()
	self.draw()

    def extracton(self):
	'extracton(self) - rebin(extract) spectrum subaarray on or off'
	self.extract = self.extractVar.get()
	if self.extract == 0: return
	da = self.data
	self.extractSubArray(da)
	self.clearcanvas()
	self.createAxis()
	self.draw()

    def surfaceon(self):
	'surfaceon(self) - draw spectrum surface cell elements'
	self.clearcanvas()
	self.createAxis()
	self.drawsurf()

    def surfaceskirt(self):
	'surfaceon(self) - draw spectrum surface cell elements with skirt'
	self.clearcanvas()
	self.createAxis()
	self.drawsurf(1)

    def drawsurf(self,type=None):
	'drawsurf(self,type=None) - draw spectrum surface with/without skirt'
	da = self.data
	dv = self.vmax-self.vmin
	if dv != 0.:
		data = divide(subtract(da,self.vmin),dv/self.maxY)
	else:
		data = da
	rows= len(data)
	steps= len(data[0])
	lasthv = self.maxY*self.yfac
	
	for row in range(rows):
            rootx  = self.xorg - row*self.hoff/self.rows
            rooty  = self.yorg + row*self.voff/self.rows
	    rowdata = data[rows-1-row]
	    for cidx in range(steps):
		datum = rowdata[cidx]
		lside = datum*self.yfac
		color = self.spectrum[cidx]
		if type == None:
                    self.canvas.create_polygon(rootx, rooty-lside, 
                        fill=color, outline=color,
                        width=self.xincr)
		else:
                    self.canvas.create_polygon(rootx, rooty-lside, 
			rootx+self.hroff, rooty-lside-self.vroff,
			rootx+self.hroff, rooty-self.vroff,
			rootx,rooty-lside,
                        fill=color, outline=color,
                        width=self.xincr)
		rootx = rootx + self.xincr
	    self.root.update()

    def changeCT(self):
	'changeCT(self) - change CT dialog and redraw surface with new CT'
	from viewCT import *
	self.ct = getCTI(self.interior())
	self.ctable = 1
	self.drawsurf2()
	self.ctable = 0
	self.drawImage()

    def averageOn(self):
	'averageOn(self) - redraw surface use cell average value with CT'
	self.average = self.averageVar.get()
	self.ctable = 1
	self.drawsurf2()
	self.ctable = 0

    def drawsurf3(self):
	'drawsurf3(self) - redraw surface use rainbow+white color table'
	self.ct = 39
	self.ctable = 1
	self.drawsurf2()
	self.ctable = 0
	self.drawImage()

    def drawsurf2(self):
	'drawsurf2(self) - draw surface use color table instead of spectrum color'
	self.clearcanvas()
	self.createAxis()
	# use color table if ctable is set
	if self.ctable:
	    p = reshape(self.CT[self.ct],(256,3))
	    spec=[]
	    for i in range(256):
		pp = p[i]
		st = '#%02x%02x%02x' % (int(pp[0]),int(pp[1]),int(pp[2]))
		spec.append(st)	
	    self.ctc = spec
	da = self.data
	dv = self.vmax-self.vmin

	if dv != 0.:
		data = divide(subtract(da,self.vmin),dv/self.maxY)
		da1 = divide(subtract(da,self.vmin),dv/255)
	else: 
		data = da
		da1 = divide(da,1)
	rows= len(data)
	steps= len(data[0])
	lasthv = self.maxY*self.yfac
        xadj   = float(self.xincr)/4.0
	if xadj < 2: xadj=2	
	for row in range(rows-1):
            rootx  = self.xorg - row*self.hoff/self.rows
            rooty  = self.yorg + row*self.voff/self.rows
	    rowdata1 = data[rows-1-row]
	    rowdata2 = data[rows-1-row-1]
	    for cidx in range(steps-1):
		datum = [rowdata2[cidx],rowdata1[cidx],rowdata1[cidx+1],rowdata2[cidx+1]]
		lside = multiply(datum,self.yfac)
		if self.ctable:
		     if not(self.average):
			ind = int(da1[rows-1-row,cidx])
		     else:
			ind = int((da1[rows-1-row,cidx]+da1[rows-1-row-1,cidx]+ da1[rows-1-row,cidx+1]+da1[rows-1-row-1,cidx+1])/4)
		     color = self.ctc[ind]
		else:
		     color = self.spectrum[cidx]
		self.canvas.create_polygon(rootx-self.hroff,rooty-lside[0]+self.vroff,
			rootx,rooty-lside[1],
			rootx+self.xincr,rooty-lside[2],
			rootx+self.xincr-self.hroff,rooty-lside[3]+self.vroff,
                        fill=color, outline=color,
                        width=xadj)
		rootx = rootx + self.xincr

	    self.root.update()

    def drawsurf1(self,steplist=None):
	'drawsurf1(self,steplist=None) - draw spectrum surface cell by stepwise'
	self.clearcanvas()
	self.createAxis()
	# use color table if ctable is set
	if self.ctable:
	    p = reshape(self.CT[self.ct],(256,3))
	    spec=[]
	    for i in range(256):
		pp = p[i]
		st = '#%02x%02x%02x' % (int(pp[0]),int(pp[1]),int(pp[2]))
		spec.append(st)	
	    self.ctc = spec
	da = self.data
	dv = self.vmax-self.vmin
	if dv != 0.:
		data = divide(subtract(da,self.vmin),dv/self.maxY)
		da1 = divide(subtract(da,self.vmin),dv/255)
	else:
		data = da
		da1 = divide(da,self.vmin/255)

	rows= len(data)
	steps= len(data[0])
	lasthv = self.maxY*self.yfac
        xadj   = float(self.xincr)/4.0
	if xadj < 2: xadj=2	
	if steplist == None:
		steplist = range(steps-1)
#	for cidx in range(steps-1):
	for cidx in steplist:
	    for row in range(rows-1):
                rootx  = self.xorg + cidx*self.xincr - row*self.hoff/self.rows
                rooty  = self.yorg + row*self.voff/self.rows
		datum = [data[rows-1-row][cidx+1],data[rows-1-row][cidx],data[rows-1-row-1][cidx],data[rows-1-row-1][cidx+1]]
	        lside = multiply(datum,self.yfac)
		if self.ctable:
		     if not(self.average):
			ind = int(da1[rows-1-row,cidx])
		     else:
			ind = int((da1[rows-1-row,cidx]+da1[rows-1-row-1,cidx]+ da1[rows-1-row,cidx+1]+da1[rows-1-row-1,cidx+1])/4)
		     color = self.ctc[ind]
		else:
		     color = self.spectrum[cidx]
		self.canvas.create_polygon(
			rootx+self.xincr,rooty-lside[0],
			rootx,rooty-lside[1],
			rootx-self.hroff,rooty-lside[2]+self.vroff,
			rootx+self.xincr-self.hroff,rooty-lside[3]+self.vroff,
                        fill=color, outline=color,
                        width=xadj)

	    self.root.update()


    def drawmesh(self):
	'drawmesh(self) - draw surface elements as mesh elements'
	self.clearcanvas()
	self.createAxis()
	da = self.data
	dv = self.vmax-self.vmin
	if dv != 0.:
	    data = divide(subtract(da,self.vmin),dv/self.maxY)
	else:
	    data = da
	rows= len(data)
	steps= len(data[0])
	lasthv = self.maxY*self.yfac
	
	for row in range(rows-1):
            rootx  = self.xorg - row*self.hoff/self.rows
            rooty  = self.yorg + row*self.voff/self.rows
	    rowdata1 = data[rows-1-row]
	    rowdata2 = data[rows-1-row-1]
	    for cidx in range(steps-1):
		datum = [rowdata2[cidx],rowdata1[cidx],rowdata1[cidx+1],rowdata2[cidx+1]]
		lside = multiply(datum,self.yfac)
		self.canvas.create_line(
			rootx-self.hroff,rooty-lside[0]+self.vroff,
			rootx,rooty-lside[1],
			rootx+self.xincr,rooty-lside[2],
			rootx+self.xincr-self.hroff,rooty-lside[3]+self.vroff,
			fill='darkblue')
		if (row+1) == (rows-1):
			self.canvas.create_line(
			rootx+self.xincr-self.hroff,rooty-lside[3]+self.vroff,
			rootx-self.hroff,rooty-lside[0]+self.vroff,
			fill='darkblue')
		rootx = rootx + self.xincr

	    self.root.update()

    def drawrowsclose(self):
	'drawrowsclose(self) - close row selection dialog'
	self.RSFrame.destroy()
	self.RSFrame = None

    def drawrowsset(self):
	'drawrowsset(self) - accept row slices and draw 3D row lines'
	from plot2d import parseint
	st = self.RSW[0].get()
	try:
	    ll = parseint(st)
	except:
	    message(self.RSFrame,'Error in\n\nEnter Row # list Field')
	    return 
	try:
	    self.linewidth = self.RSW[1].get()
	except:
	    message(self.RSFrame,'Error in\n\nEnter Line Width Field')
	    return
	self.drawrows(ll)

    def drawrowsdialog(self):
	'drawrowsdialog(self) - pop up row selection dialog'
	if self.RSFrame != None: return
	try:
	    import Tkinter
            top=Toplevel()
            top.title('Dialog pick row slices')
            self.RSFrame=top
            fm = Frame(top,borderwidth=0)
            self.RSW=[StringVar(),IntVar()]
            Label(fm,text='Enter Row # list [0-'+str(self.rows-1)+']:').grid(row=1,column=1,sticky=W)
	    Entry(fm,width=45,textvariable=self.RSW[0]).grid(row=1,column=2,sticky=W)
            Label(fm,text='Enter Line Width ').grid(row=2,column=1,sticky=W)
	    Entry(fm,width=5,textvariable=self.RSW[1]).grid(row=2,column=2,sticky=W)
	    self.RSW[0].set('0,1,2')
	    self.RSW[1].set(self.linewidth)
	    Tkinter.Button(fm,text='OK',command=self.drawrowsset).grid(row=3,column=1,sticky=W)
	    Tkinter.Button(fm,text='Close',command=self.drawrowsclose).grid(row=3,column=2,sticky=W)
	    fm.pack(fill=BOTH)
	except:
	    pass
	

    def drawrows(self,list=None):
	'drawrows(self,list=None) - draw all or list of rows in 3D coordinates'
	self.clearcanvas()
	self.createAxis()
	da = self.data
	dv = self.vmax-self.vmin
	if dv != 0.0:
		data = divide(subtract(da,self.vmin),dv/self.maxY)
	else:
		data = da
	rows= len(data)
	steps= len(data[0])
	lasthv = self.maxY*self.yfac
	
	if list == None: list = range(rows)
	for row in list:
	  if row < rows and row >=0 :
#            rootx  = self.xorg - row*self.hoff/self.rows
#            rooty  = self.yorg + row*self.voff/self.rows
#	     rowdata1 = data[rows-1-row]
            rootx  = self.xorg - (rows-1-row)*self.hoff/self.rows
            rooty  = self.yorg + (rows-1-row)*self.voff/self.rows
	    rowdata1 = data[row]
	    for cidx in range(steps-1):
		datum = [rowdata1[cidx],rowdata1[cidx+1]]
		lside = multiply(datum,self.yfac)
		self.canvas.create_line( rootx,rooty-lside[0],
			rootx+self.xincr,rooty-lside[1],
			capstyle=ROUND,
			width=self.linewidth,fill='darkblue')
		rootx = rootx + self.xincr

	    self.root.update()

    def drawstepsclose(self):
	'drawstepsclose(self) - close step selection dialog'
	self.SSFrame.destroy()
	self.SSFrame = None

    def drawstepsset(self):
	'drawstepsset(self) - accept and draw step slices selected in 3D coordinates'
	from plot2d import parseint
	st = self.SSW[0].get()
	try:
	    ll = parseint(st)
	except:
	    message(self.SSFrame,'Error in\nEnter Step # list Field')
	    return 
	try:
	    self.linewidth = self.SSW[1].get()
	except:
	    message(self.SSFrame,'Error in\nEnter Line Width Field')
	    return
	self.stepline = self.SSW[2].get()
	if self.stepline: 
	    self.drawstepSline(ll)
	else:
	    self.linewidth = self.SSW[1].get()
	    self.drawsteps(ll)

    def drawstepsdialog(self):
	'drawstepsdialog(self) - pop up step slices dialog'
	if self.SSFrame != None: return
	try:
	    import Tkinter
            top=Toplevel()
            top.title('Dialog pick step slices')
            self.SSFrame=top
            fm = Frame(top,borderwidth=0)
            self.SSW=[StringVar(),IntVar(),IntVar()]
            Label(fm,text='Enter Step # list [0-'+str(self.steps-1)+']:').grid(row=1,column=1,sticky=W)
	    Entry(fm,width=45,textvariable=self.SSW[0]).grid(row=1,column=2,sticky=W)
            Label(fm,text='Enter Line Width').grid(row=2,column=1,sticky=W)
	    Entry(fm,width=5,textvariable=self.SSW[1]).grid(row=2,column=2,sticky=W)
	    Checkbutton(fm,text='Color Shaded ',state=NORMAL,anchor=W,
		command=self.drawstepsset,
		variable=self.SSW[2]).grid(row=4,column=2,sticky=W)

	    self.SSW[0].set('0,1,2')
	    self.SSW[1].set(self.linewidth)
	   
	    Tkinter.Button(fm,text='OK',command=self.drawstepsset).grid(row=5,column=1,sticky=W)
	    Tkinter.Button(fm,text='Close',command=self.drawstepsclose).grid(row=5,column=2,sticky=W)
	    fm.pack(fill=BOTH)
	except:
	    pass
	
    def drawsteps(self,list=None):
	'drawsteps(self,list=None) - draw all or selected step list in 3D coordinates'
	self.clearcanvas()
	self.createAxis()
	da = self.data
	dv = self.vmax-self.vmin
	if dv != 0.0:
		data = divide(subtract(da,self.vmin),dv/self.maxY)
	else:
		data = da
	rows= len(data)
	steps= len(data[0])
	lasthv = self.maxY*self.yfac
	
	if list == None: list=range(steps)
	else:
		ll = []
		for i in range(len(list)):
			if list[i] < steps:
				ll.append(list[i])	
		list = ll
    	np = len(list)
	for row in range(rows-1):
            rootx  = self.xorg - row*self.hoff/self.rows
            rooty  = self.yorg + row*self.voff/self.rows
	    rowdata1 = data[rows-1-row]
	    rowdata2 = data[rows-1-row-1]
	    for i in range(np):
	      cidx = list[i]
	      if cidx >=0 and cidx < steps:
		datum = [rowdata1[cidx],rowdata2[cidx]]
		lside = multiply(datum,self.yfac)
		self.canvas.create_line(
			rootx,rooty-lside[0],
			rootx-self.hroff,rooty-lside[1]+self.vroff,
#			capstyle=ROUND,
			width=self.linewidth,fill='darkblue')
		if np < steps:
		    if i < (np-1):
		        rootx = rootx + self.xincr*(list[i+1]-cidx)
		else:
		    rootx = rootx + self.xincr

	    self.root.update()

    def drawstepSline(self,list=None):
	'drawstepSline(self,list=None) - draw selected step slices in spectrum color'
	self.clearcanvas()
	self.createAxis()
	da = self.data
	dv = self.vmax-self.vmin
	if dv != 0.0:
		data = divide(subtract(da,self.vmin),dv/self.maxY)
	else:
		data = da
	rows= len(data)
	steps= len(data[0])
	lasthv = self.maxY*self.yfac
	
	if list == None: list=range(steps)
	else:
		ll = []
		for i in range(len(list)):
			if list[i] < steps:
				ll.append(list[i])	
		list = ll
    	np = len(list)
	for row in range(rows-1):
            rootx  = self.xorg - row*self.hoff/self.rows
            rooty  = self.yorg + row*self.voff/self.rows
	    rowdata1 = data[rows-1-row]
	    rowdata2 = data[rows-1-row-1]
	    for i in range(np):
	      cidx = list[i]
	      if cidx >=0 and cidx < steps:
		datum = [rowdata2[cidx],rowdata1[cidx]]
		lside = multiply(datum,self.yfac)
		color = self.spectrum[cidx]
		self.canvas.create_polygon(
			rootx-self.hroff,rooty-lside[0]+self.vroff,
			rootx,rooty-lside[1],
			rootx,rooty,
			rootx-self.hroff,rooty+self.vroff,
			outline=color,width=self.linewidth,
			fill=color)
		if np < steps:
		    if i < (np-1):
		        rootx = rootx + self.xincr*(list[i+1]-cidx)
		else:
		    rootx = rootx + self.xincr

	    self.root.update()

    def openAscii(self):
	'openAscii(self) - Ascii file selection dialog and display as 3D edged spectrum'
	(path,fn) = os.path.split(self.fname)
        fname = askopenfilename( initialdir = path,
                filetypes=[("ASCII Data", '.txt'),
                ("Image Files","*im*"),
                ("Data Files",".dat"),
                ("All Files","*")])
        if fname == ():
                fname=None 
        self.fname = fname
	fn = os.path.split(fname)
	if len(fn) > 1: self.path = fn[0]
	self.clearcanvas()
        self.initData(fname)
        self.createAxis()
#	self.drawmesh()
	self.ct = 39
	self.draw()

    def displayFile(self):
	'displayFile(self) - display content of Ascii file loaded in'
	if os.path.isfile(self.fname): xdisplayfile(self.fname)
	else: 
		message(self.interior(),text='Error: \n\n'+self.fname+'\nFile not found!')

    def createButtons(self):
	'createButtons(self) - create action buttons in command area'
        self.buttonAdd('Print',
              helpMessage='Print current graph (PostScript)',
              statusMessage='Print graph as PostScript file',
              command=self.Print)
        self.buttonAdd('Close',
              helpMessage='Close Screen',
              statusMessage='Exit',
               command=self.close)
        self.buttonAdd('ROI...',
              helpMessage='Extract 2D ROI data',
              statusMessage='Extract 2D ROI image data',
               command=self.resetArray)
        
    def resetArray(self):
	    'resetArray(self) - ROI... dialog to extract region of interest'
	    import Tkinter
	    if self.CRFrame != None: self.CRFclose()
            top=Toplevel()
            top.title('Dialog Pick Step/Row Slices')
            self.CRFrame=top
            fm = Frame(top,borderwidth=0)
            self.CRW=[IntVar(),IntVar(),IntVar(),IntVar()]
	    da = self.data  # self.data0
	    nc = len(da)
	    ns = len(da[0])
	    Label(fm,text='Extract 2D ROI Steps(X) and Rows (Y)\n(If ascii file contains X info, then\nexclude the X info from 2D ROI)').grid(row=0,column=1,sticky=W)
	    Tkinter.Button(fm,text='Reset ROI...',command=self.CRFdefault).grid(row=0,column=2,sticky=W)
            Label(fm,text='Start Step [1-'+str(ns)+']:').grid(row=1,column=1,sticky=W)
	    Entry(fm,width=4,textvariable=self.CRW[0]).grid(row=1,column=2,sticky=W)
            Label(fm,text='End Step [1-'+str(ns)+']:').grid(row=2,column=1,sticky=W)
	    Entry(fm,width=4,textvariable=self.CRW[1]).grid(row=2,column=2,sticky=W)
            Label(fm,text='Begin Row [1-'+str(nc)+']:').grid(row=3,column=1,sticky=W)
	    Entry(fm,width=4,textvariable=self.CRW[2]).grid(row=3,column=2,sticky=W)
            Label(fm,text='End Row [1-'+str(nc)+']:').grid(row=4,column=1,sticky=W)
	    Entry(fm,width=4,textvariable=self.CRW[3]).grid(row=4,column=2,sticky=W)
	    Tkinter.Button(fm,text='Ok',command=self.CRFresetArray).grid(row=5,column=1,sticky=W)
	    Tkinter.Button(fm,text='Close',command=self.CRFclose).grid(row=5,column=2,sticky=W)
	    self.CRW[0].set('1')
	    self.CRW[1].set(str(ns))
	    self.CRW[2].set('1')
	    self.CRW[3].set(str(nc))
	    fm.pack(fill=BOTH)

    def CRFresetArray(self):
	'CRFresetArray(self) - extract and display ROI from array in memory'
	import string
	i1 = self.CRW[0].get()
	i2 = self.CRW[1].get()
	j1 = self.CRW[2].get()
	j2 = self.CRW[3].get()
	if i1 == i2 or j1 == j2: return
	if i2 < i1: 
		tp = i1
		i1 = i2
		i2 = tp
	if j2 < j1: 
		tp = j1
		j1 = j2
		j2 = tp
	if i1 <1 : i1=1
	if j1 <1 : j1=1
	da = self.data0
	data=[]
	for j in range(j1-1,j2):
		ls = da[j]
		data.append(da[j][i1-1:i2])
	self.data = data
	v1,v2 = minmax(data)
	self.vmax = v2
	self.vmin = v1
	self.clearcanvas()
	self.maxX = len(data[0])
	self.maxY = len(data)
	self.steps = len(data[0])
	self.rows = len(data)
	self.createAxis()
	self.draw()
#	self.CRFclose()

    def CRFdefault(self):
	'CRFdefault(self) - reset ROI to raw data read in from Ascii file'
	self.defaultreadin()
	self.CRFclose()
	self.resetArray()

    def CRFclose(self):
	'CRFclose(self) - close ROI dialog'
	self.CRFrame.destroy()
	self.CRFrame = None

    def createBase(self):
	'createBase(self) - create main window canvas widgets'
        self.width0  = self.root.winfo_width()-10
        self.width  = self.width0 -100
        self.height = self.root.winfo_height()-95
        self.Frame0 = Frame(self.interior(),width=self.width0,height=self.height)
        self.Frame1 = Frame(self.Frame0,width=self.width,height=self.height)
        self.canvas = self.createcomponent('canvas', (), None,
#                                           Canvas, (self.interior(),),
                                           Canvas, (self.Frame1,),
                                           width=self.width,
                                           height=self.height,
                                           background="white")
        self.canvas.pack(side=TOP, expand=YES, fill=BOTH)
	self.createAxis()
	self.Frame1.pack(side=LEFT)

        self.Frame2 = Frame(self.Frame0,width=100,height=self.height)
	self.canvas_image = Canvas(self.Frame2)
        self.canvas_image.pack(side=TOP, expand=YES, fill=BOTH)
	self.Frame2.pack(side=RIGHT)
	self.Frame0.pack()

    def createAxis(self):
	'createAxis(self) - create and draw 3D axis'
        self.xorg  = self.width/3
        self.yorg  = self.height/2
        self.awid  = self.width  * 0.55 #68)
        self.ahgt  = self.height * 0.45
        self.hoff  = self.awid /4 # 3
        self.voff  = self.ahgt + 2
        self.vht   = self.voff # /2
        self.hroff = self.hoff / self.rows
        self.vroff = self.voff / self.rows
        self.xincr = self.awid / self.steps
        self.yfac  = float(self.vht) / float(self.maxY-self.minY)

        self.canvas.create_polygon(self.xorg, self.yorg, 
             self.xorg+self.awid, self.yorg,
             self.xorg+self.awid-self.hoff, self.yorg+self.voff,
             self.xorg-self.hoff, self.yorg+self.voff,
             self.xorg, self.yorg, fill='', outline=self.lineColor)

        self.canvas.create_rectangle(self.xorg, self.yorg-self.vht,
             self.xorg+self.awid, self.yorg,
             fill='', outline=self.lineColor)

        self.canvas.create_polygon(self.xorg, self.yorg, 
             self.xorg-self.hoff, self.yorg+self.voff,
             self.xorg-self.hoff, self.yorg+self.voff-self.vht,
             self.xorg, self.yorg-self.vht,
             fill='', outline=self.lineColor)

        self.canvas.create_text(self.xorg-self.hoff-5, self.yorg+self.voff,
             text='%f' % self.vmin, fill=self.lineColor, anchor=E)

        self.canvas.create_text(self.xorg-self.hoff-5, self.yorg+self.voff-self.vht,
             text='%f' % self.vmax, fill=self.lineColor, anchor=E)
        
        self.canvas.create_text(self.xorg-self.hoff, self.yorg+self.voff+5,
             text='%d' % self.minX, fill=self.lineColor, anchor=N)

        self.canvas.create_text(self.xorg+self.awid-self.hoff, self.yorg+self.voff+5,
             text='%d' % self.maxX, fill=self.lineColor, anchor=N)

    def initData(self,fname=None):     
	"initData(self,fname=None) - initialized data array loaded in from fname "
        self.minY        =   0
        self.minX        =   0
	if os.path.isfile(fname):
		da = readArray(fname)
		da = transposeA(da)  # column oriented
	else:
	 	da = indgen([100,50])
		print '***Test data: indgen([100,50]) used'

	v1,v2 = minmax(da)
	self.vmax = v2
	self.vmin = v1
        self.steps       = len(da[0]) #100
        self.rows        = len(da) #30 #10
	self.maxX = self.steps
	self.maxY = self.rows
	self.data = da

	self.extractSubArray(da)
	self.data0 = self.data

        self.spectrum    = Pmw.Color.spectrum(self.steps,
                               saturation=0.8,
                               intensity=0.8, extraOrange=1)
        self.lineColor   = 'gray80'
        self.lowThresh   = 0 # 30
        self.highThresh  = 255 # 70
        
    def extractSubArray(self,da):
	'extractSubArray(self,da) - rebin to 200x200 subarray if large dimension detected in da array'
	if self.extract == 0: return
	rows = len(da)
	steps = len(da[0])
	if steps > 200:
		self.steps = 200
	if rows > 200:
		self.rows = 200
	iy = len(da)/self.rows
	if iy < 1: iy=1
	ix = steps/self.steps
	if ix < 1: ix=1
	if ix >1 or iy > 1:
	  da1 = []
	  for i in range(0,rows,int(iy)):
	    ls = da[i]
	    ls = ls[::ix]    
	    da1.append(ls)
	  da = da1
	self.data = da
	self.maxX = len(da[0])
	self.maxY = len(da)
	self.rows = self.maxY
	self.steps = self.maxX

    def transform(self, base, factor):
	'transform(self, base, factor) - convent color base to a string representation'
        rgb = self.winfo_rgb(base)
        retval = "#"
        for v in [rgb[0], rgb[1], rgb[2]]:
	    v = (v*factor)/256
            if v > 255: v = 255
            if v < 0:   v = 0
            retval = "%s%02x" % (retval, v)
        return retval

    def plotData(self, row, rowdata):
	"""plotData(self, row, rowdata) - plot edged spectrum rowdata in 3D coordinates
	row - specify the input row index 
	rowdata - specify row vector of data
	""" 
	rootx  = self.xorg - row*self.hoff/self.rows
        rooty  = self.yorg + row*self.voff/self.rows
        cidx   = 0
        lasthv = self.maxY*self.yfac
        xadj   = float(self.xincr)/4.0
#	if xadj < 2: xadj=2
        lowv   = self.lowThresh*self.yfac
        for datum in rowdata:
            lside = datum*self.yfac
            color = self.spectrum[cidx]
            if datum <= self.lowThresh:
                color = self.transform(color, 0.8)
            elif datum >= self.highThresh:
                color = self.transform(color, 1.2)
                
            self.canvas.create_polygon(rootx, rooty, rootx, rooty-lside,
                        rootx-self.hroff, rooty-lside+self.vroff,
                        rootx-self.hroff, rooty+self.vroff,
                        rootx, rooty, fill=color, outline=color,
                        width=xadj)
	    if self.showline:
                base = min(min(lside, lasthv), lowv)
                self.canvas.create_line(rootx-xadj/2, rooty-lside,
                       rootx-self.hroff-xadj/2, rooty-lside+self.vroff,
                       rootx-self.hroff-xadj/2, rooty+self.vroff-base,
                       fill='black', width=1)
            lasthv = lowv = lside
            
            cidx = cidx + 1
            rootx = rootx + self.xincr

    def draw(self):
	'draw(self) - draw 3D spectrum plot and 2D image plot of input data array'
	da = self.data
	dv = self.vmax-self.vmin
        for i in range(self.rows):
	    if dv == 0: 
	       data = self.steps* [1.]
	    else:
	       data = divide(subtract(da[self.maxY-1-i],self.vmin),dv/self.maxY)
            self.plotData(i, data)
            self.root.update()
	self.drawImage()

    def drawImage(self):
	'drawImage(self) - display image and info on right panel of main window'
	# draw image value frame
	try:
		self.Frame2.destroy()
	except:
		pass
	pal = self.CT[self.ct]
	from view2d import PNGImage2
        self.Frame2 = Frame(self.Frame0,width=100,height=self.height)
	Label(self.Frame2,text='Vmax:'+str(self.vmax)).pack(side=TOP)
	Label(self.Frame2,text='Vmin:'+str(self.vmin)).pack(side=TOP)
	self.canvas_image = Canvas(self.Frame2)
        self.canvas_image.pack(side=TOP, expand=YES, fill=BOTH)
	from imageUtil import updown
	da = updown(self.data)
	im = PNGImage2(self.canvas_image,da,pal=pal,tmpNm='tmp.ppm')
	im.bind('<Motion>',self.cursorpos_im)
	im.pack(side=BOTTOM,padx=20,pady=20)
	self.valVar=[StringVar(),StringVar(),StringVar()]
	Label(self.Frame2,text='Cursor Value:').pack(side=TOP)
	Label(self.Frame2,textvariable=self.valVar[0],anchor=W).pack(side=TOP)
	Label(self.Frame2,textvariable=self.valVar[1],anchor=W).pack(side=TOP)
	Label(self.Frame2,textvariable=self.valVar[2],anchor=W).pack(side=TOP)
	self.valVar[0].set('Ix:')
	self.valVar[1].set('Iy:')
	self.valVar[2].set('Z:')
	self.Frame2.pack(side=RIGHT)

    def cursorpos_im(self,event):
      'cursorpos_im(self,event) - display mouse move event on right panel of main window'
      try:
	ix = self.steps * event.x / 60
	iy = self.rows * (60-event.y) / 60
	self.valVar[0].set('Ix: '+str(ix))
	self.valVar[1].set('Iy: '+str(iy))
	self.valVar[2].set('Z: '+str(self.data[iy][ix]))
      except:
	pass

    def Printer(self):
        "Printer(self) - dialog to set up printer"
        from tv import setupPrinter
        root=self.interior()
        dialog = setupPrinter(root)

    def Print(self):
	'Print(self) - send PS 3D canvas plot to printer'
	from plotAscii import PSprint
	SH = initSH()
	PSprint(self,printer=SH['printer'])
    
    def close(self):
	"close(self) - close window and exit the 3dgraph program"
	if self.fname == None: 
		self.quit()
		return
        fo = open('3dgraph.config','w')
	fo.write(self.fname)
	fo.close()
        self.quit()

    def createInterface(self):
	'createInterface(self) - create 3dgraph user interface '
        AppShell.AppShell.createInterface(self)
	self.addMoremenuBar()
        self.createButtons()
	path='.'
	if os.path.isfile('3dgraph.config'):
		lines = readST('3dgraph.config')
		fname = lines[0]
	else:
	        fname = askopenfilename( initialdir = path,
                filetypes=[("ASCII Data", '.txt'),
                ("Image Files","*im*"),
                ("Data Files",".dat"),
                ("All Files","*")])
       		if fname == () : fname=None 
	(path,fn) = os.path.split(fname)
        self.fname = fname
	self.SSFrame = None
	self.RSFrame = None
	self.CRFrame = None
	self.path = path
	self.showline = 1 
	self.linewidth = 1 
	self.average = 0
	self.extract = 1 
	self.ctable = 0 
	self.ct = 39 
	self.CT = readCT()
        self.initData(fname)
	self.showlineVar.set(self.showline)
	self.extractVar.set(self.extract)
        self.createBase()
        
if __name__ == '__main__':
    graph = Graph3D()
    graph.root.after(100, graph.draw)
    graph.run()



