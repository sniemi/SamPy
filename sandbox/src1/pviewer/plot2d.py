#!/usr/bin/env python

from Tkinter import *
import Pmw
import  AppShell
import sys, os
import string
from plotAscii import xdisplayfile
from tkSimpleDialog import Dialog
from plotAscii import transposeA
from readMDA import *
from mdaAscii import *
from pylab import *

legends=['best','upper right','upper left', 'lower left','lower right','right', 'center left','center right','lower center','upper center','center']
Colors=['blue','green','red','cyan','magenta','yellow','black']
cmaps=['autumn','bone','cool','copper','flag','gray','hot','hsv','jet','pink','prism','spring','summer','winter']
interp=['nearest', 'bilinear', 'bicubic', 'spline16', 'spline36',
'hanning', 'hamming', 'hermite', 'kaiser', 'quadric',
'catrom', 'gaussian', 'bessel', 'mitchell', 'sinc',
'lanczos', 'blackman']
facecolor='w'

def ct0():
    "ct0() - rainbow color map"
    _jet_data = {
	'red': ((0,0,0),(.45,0,0),(.75,1,1),(.91,1,1),(1,1,1)),
	'green': ((0,0,0),(.125,.4,.4),(.35,.8,.8),(.75,1,1),(1,0,0)),
	'blue': ((0,.3,.3),(.11,.8,.8),(.34,1,1),(.65,0,0),(1,0,0)) }
    return matplotlib.colors.LinearSegmentedColormap('jet',_jet_data)

def ct1():
    "ct1() - rainbow + white color map"
    _jet_data = {
	'red': ((0,.2,.2),(.15,.5,.5),(.35,0,0),(.75,1,1),(.99,1,1),(1,1,1)),
	'green': ((0,0,0),(.35,1,1),(.75,1,1),(.99,0,0),(1,1,1)),
	'blue': ((0,.1,.1),(.15,1,1),(.35,1,1),(.65,0,0),(.99,0,0),(1,1,1)) }
    return matplotlib.colors.LinearSegmentedColormap('jet',_jet_data)

def ct2():
    "ct1() - rainbow + black color map"
    _jet_data = {
	'red': ((0,0,0),(.45,0,0),(.75,1,1),(.91,1,1),(.99,1,1),(1,0,0)),
	'green': ((0,0,0),(.125,.4,.4),(.35,.8,.8),(.75,1,1),(.99,0,0),(1,0,0)),
	'blue': ((0,.3,.3),(.15,.8,.8),(.34,1,1),(.65,0,0),(.99,0,0),(1,0,0)) }
    return matplotlib.colors.LinearSegmentedColormap('jet',_jet_data)

def message(root,text=None,nm=None,title=None):
        """
        message(root,text=None,nm=None) - display message info
        title - specify message window title
        text - specify message infomation
        nm - specify function name where error occurs
        """
        if title == None: title='Info'
        if text == None: text='\n'
        dialog = Pmw.Dialog(root,buttons=('OK','Canel'),
                defaultbutton='OK', title=title)
        if nm == None:
          w = Label(dialog.interior(),text=text,pady=20)
        else:
          w = Label(dialog.interior(),text='Warning: ValueError detected in\n\n --> '+nm,pady=20)
        w.pack(expand=1,fill=BOTH,padx=4,pady=4)
        dialog.activate()

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

def parsefloat(ll):
	"parsefloat(ll) - parse string ll and return a float list"
	if string.find(ll,',') > 0:
		ll = string.split(ll, ',')
	else: 
		ll = string.split(ll)
	lw =[]
	for i in range(len(ll)):
		lw.append(string.atof(ll[i]))
	print type(lw)
	return lw

def parseint(ll):
	"parseint(ll) - parse string ll and return a int list"
	if string.find(ll,',') > 0:
		ll = string.split(ll,',')
	else:
		ll = string.split(ll)
	lw=[]
	for i in range(len(ll)):
		if string.find(ll[i],'-') > 0:
			sl= string.split(ll[i],'-')
			sl1 = string.atoi(sl[0])
			sl2 = string.atoi(sl[1])
			for j in range(sl1,sl2+1):
				lw.append(j)
		else:
			lw.append(string.atoi(ll[i]))
	return lw

def printPicture(fn,ptr='',size=None):
    """
    printPicture(fn,ptr='',size=None) - send PNG or JPEF picture file to pilprint.py
	ptr - specify desired printer to override the default printer
	size - (W,H) specifies the resize width and height of new print image 
    """ 
    import Image
    from imageUtil import printImage
    f1,f2 = string.split(fn,'.')
    im = Image.open(fn)
    if im.mode == 'P': 
	im = im.convert("RGB")
    if size != None:
	im = im.resize(size)
    ff = f1 +'.jpg'
    im.save(ff,"JPEG")
    printImage(ff,printer=ptr)

class plot2d(AppShell.AppShell):
    usecommandarea = 1
    appname 	= '2D Array Image Data Plotter'
    frameWidth =550
    frameHeight=450

    def createButtons(self):
	"createButtons(self) - create command buttons"
	self.buttonAdd('Close',helpMessage='Close this program',
		statusMessage='Close plot2d dialog',
		command=self.closeup)
	self.buttonAdd('CloseAllPlot',helpMessage='Close all plot figures',
		statusMessage='Close figures',
		command=self.closefigures)

    def addMoreMenuBar(self):
	"addMoreMenuBar(self) - create menubar user interface"
        self.menuBar.addmenuitem('File','command',
                'Read MDA files',
                label='MDA 2D/3D Files...',
                command = self.pickMDAFile)
	self.menuBar.addmenuitem('File','command',label='------------------')
        self.menuBar.addmenuitem('File','command',
                'Read a column or row oriented ASCII file',
                label='ASCII 2D Data...',
                command = self.pickFile)
	self.menuBar.addmenuitem('File','command',label='------------------')
        self.menuBar.addmenuitem('File','command',
                'Display picture files',
                label='Picture Files...',
                command = self.pickPicture)
	self.menuBar.addmenuitem('File','command',label='------------------')
        self.menuBar.addmenuitem('File','command',
                'Save plot2d.jpg and send to printer',
                label='Print plot2d.jpg',
                command = self.Print)
        self.menuBar.addmenuitem('File','command',
                'Setup printer',
                label='Printer...',
                command = self.printer)
	self.menuBar.addmenuitem('File','command',label='------------------')
        self.menuBar.addmenuitem('File','command',
                'Quit this program',
                label='Quit',
                command = self.closeup)

        self.menuBar.addmenuitem('Setup', 'command',
              'Pick 2D image from opened MDA image array',
              label='Show MDA 2D Images',
              command=self.showDetector)
	self.menuBar.addmenuitem('Setup','command',label='-----------------')
        self.menuBar.addmenuitem('Setup','command',
                'Display the loaded file',
                label='Display Ascii File...',
                command = self.displayFile)
	self.menuBar.addmenuitem('Setup','command',label='------------------')
        self.menuBar.addmenuitem('Setup','command',
                ' Setup X,Y coorinates',
                label='Set X,Y Data Ranges...',
                command = self.setXYrange)
	self.menuBar.addmenuitem('Setup','command',label='------------------')
	self.captionVar = IntVar()
        self.menuBar.addmenuitem('Setup','checkbutton',
                'Display the title,xlabel,ylabel if checked',
		variable=self.captionVar,
                label='Caption On',
                command = self.captionOff)
	self.captionVar.set(1)
	self.menuBar.addmenuitem('Setup','command',label='------------------')
	self.columnVar = IntVar()
        self.menuBar.addmenuitem('Setup','checkbutton',
                'Default column oriented, uncheck for row oriented data',
		variable=self.columnVar,
                label='Data Column Oriented',
                command = self.columnOn)

	self.menuBar.addmenu('MDARpt','MDAImage operation menu')
        self.menuBar.addmenuitem('MDARpt', 'command',
              'Generate MDA image report files',
              label='2D Report',
              command=self.report2D)
        self.menuBar.addmenuitem('MDARpt', 'command',
              'Generate MDA image report as IGOR format',
              label='2D IGOR Report',
              command=self.reportIGOR)
        self.menuBar.addmenuitem('MDARpt', 'command',
              'Generate MDA 2D to 1D files',
              label='Report 2D->1D',
              command=self.report2D1D)
        self.menuBar.addmenuitem('MDARpt', 'command',
              'Generate MDA image row oriented report files',
              label='2D Report (stepwise/row oriented)',
              command=self.report2Drow)
	self.menuBar.addmenuitem('MDARpt','command',label='-----------------')
        self.menuBar.addmenuitem('MDARpt', 'command',
              'Generate All report for selected MDA directory',
              label='Report All',
              command=self.reportALL)
	self.menuBar.addmenuitem('MDARpt','command',label='-----------------')
        self.menuBar.addmenuitem('MDARpt', 'command',
              'Display ASCII file ',
              label='View Ascii File...',
              command=self.displayAscii)
	self.menuBar.addmenuitem('MDARpt','command',label='-----------------')
        self.menuBar.addmenuitem('MDARpt', 'command',
              'Remove All ASCII file ',
              label='Delete ASCII/*.txt Files...',
              command=self.removeAscii)

	self.menuBar.addmenu('Image','Image operation menu')
        self.menuBar.addmenuitem('Image', 'command',
              'plot as color image',
              label='TV Image...',
              command=self.tvimage)
        self.menuBar.addmenuitem('Image','command',
              'Setup Smooth method',
              label='Image Smoothing...',
              command = self.changeinterp)
        self.menuBar.addmenuitem('Image','command',
              'Image color limits',
              label='Image Color Limits...',
              command = self.changeclim)
	self.menuBar.addmenuitem('Image','command',label='-----------------')
        self.menuBar.addmenuitem('Image', 'command',
              'plot as rainbow+white color image',
              label='Rainbow+peak White...',
              command=self.tvimage1)
	self.menuBar.addmenuitem('Image','command',label='-----------------')
        self.menuBar.addmenuitem('Image','command',
              'plot X slices ',
              label='Plot X Slices...',
              command = self.takeXslice)
        self.menuBar.addmenuitem('Image','command',
              'plot Y slices ',
              label='Plot Y Slices...',
              command = self.takeYslice)
	self.menuBar.addmenuitem('Image','command',label='-----------------')
        self.menuBar.addmenuitem('Image', 'command',
              'transpose image data',
              label='Image Transposed',
              command=self.tvimagetranspose)
        self.menuBar.addmenuitem('Image', 'command',
              'flip image data horizontally',
              label='Image Flip Horizontally',
              command=self.tvimagehoriz)
        self.menuBar.addmenuitem('Image', 'command',
              'flip image data upside down',
              label='Image Flip Vertically',
              command=self.tvimageupdown)

	self.menuBar.addmenu('Colorbar','Image with colorbar options ')
        self.menuBar.addmenuitem('Colorbar','command',
                'Setup color table',
                label='Reset Color Map...',
                command = self.changecmap)
	self.menuBar.addmenuitem('Colorbar','command',label='-----------------')
        self.menuBar.addmenuitem('Colorbar', 'command',
                   'Image with colorbar plot',
                   label='With Colorbar...',
                   command=self.toggleColorbar)

	self.menuBar.addmenu('Contour','various contour plot ')
        self.menuBar.addmenuitem('Contour', 'command',
                                 'plot as countour',
                                 label='Contour...',
                                 command=self.tvcontour)
        self.menuBar.addmenuitem('Contour', 'command',
                                 'plot as color filled contour',
                                 label='Contour Filled...',
                                 command=self.tvcontourf)
        self.menuBar.addmenuitem('Contour', 'command',
                                 'dialog to configure contour plot',
                                 label='Contour Setup...',
                                 command=self.setcontour)

	self.menuBar.addmenu('3DGraph','pass data to 3D graph  ')
        self.menuBar.addmenuitem('3DGraph','command',
              'call 3D graph to display as surface plot ',
              label='3D Graph ...',
              command = self.draw3dgraph)

        self.menuBar.addmenuitem('Help','command',
                'Help Info about plot2d',
                label='Help Info...',
                command = self.helpinfo)


    def draw3dgraph(self):
      "draw3dgraph(self) - save image to pass to 3dgraph.py program "
      try:
	da = self.y
	fo = open('1.txt','w')
	self.Rg[0] = int(self.xmin.get())
	self.Rg[1] = int(self.xmax.get())
	self.Rg[2] = int(self.ymin.get())
	self.Rg[3] = int(self.ymax.get())
# pass extracted image to d3graph
# write as column vectors
	for j in range(self.Rg[0],self.Rg[1]):
		for i in range(self.Rg[2],self.Rg[3]):
			fo.write(('%18.4f' % da[i][j]), )
		fo.write('\n')
	fo.close()
	fr = open('3dgraph.config','w')
	fr.write('1.txt')
	fr.close()
	os.system('sleep 2')
	os.system('3dgraph.py &')
      except:
	pass

    def closefigures(self):
	"closefigures(self) - close all matplotlib generated figures"
	close('all')
	self.fig = 0

    def closeup(self):
	"closeup(self) - close window and exit the plot2d program"
	close('all')
        fo = open('plot2d.config','w')
	self.title = self.W[0].get()
	self.xlabel = self.W[1].get()
	self.ylabel = self.W[2].get()
        st = [ self.fname,self.title,self.xlabel,self.ylabel,self.mdapath]
        fo.write(str(st))
        fo.close()
	self.root.destroy()
        self.quit()

    def printer(self):
	"printer(self) - dialog to set up printer"
	from tv import setupPrinter
	root=self.interior()
	dialog = setupPrinter(root)

    def Print(self):
	"Print(self) - save current figure as plot2d.png and send to printPicture"
	savefig('plot2d.png')
	ptr = self.SH['printer']
	printPicture('plot2d.png',ptr)

    def helpinfo(self):
	"helpinfo(self) - display plot2d_help.txt with scrolled text"
	fname = os.environ['PYTHONSTARTUP']+os.sep+'plot2d_help.txt'
	top = Toplevel()
	st = Pmw.ScrolledText(top,borderframe=1,labelpos=N,
		label_text=fname,usehullsize=1,
		hull_width=600,hull_height=400,
		text_padx=10,text_pady=10,
		text_wrap='none')
	st.importfile(fname)
	st.pack(fill=BOTH, expand=1, padx=1, pady=1)

    def message(self,text=None,nm=None):
	"""message(self,text=None,nm=None) - display message info
	text - specify message infomation
	nm - specify function name where error occurs
	"""
	if text == None:
	    text='First, You have to use File->Load\n to load data array from an ascii data file'
		
	dialog = Pmw.Dialog(self.form,buttons=('OK','Cancel'),
		defaultbutton='OK', title='plot2d-info')
	if nm == None:
	  w = Label(dialog.interior(),text=text,pady=20)
	else:
	  w = Label(dialog.interior(),text='Warning: ValueError detected in\n\n --> '+nm,pady=20)
	w.pack(expand=1,fill=BOTH,padx=4,pady=4)
	dialog.activate()

    def showPNG(self):
	"showPNG(self) - disply plot2d.png image if file exists"
        if os.path.isfile('plot2d.png') == 0: return
	a = imread('plot2d.png')
	self.fig = self.fig+1
	figure(self.fig,figsize=(4,4))
	imshow(a,origin='lower',interpolation=self.interp)

    def pickPicture(self):
	"pickPicture(self) - invoke the Scrapbook python program for graphic picture file"
	from tv import Scrapbook
	top = Toplevel()
	top.title('Picture Browser')
	sb = Scrapbook(top)

    def displayAscii(self):
	"displayAscii(self) - pick and disply the text file"
        import tkFileDialog
        fname = tkFileDialog.askopenfilename(initialdir=self.txtpath,
                initialfile='*.txt')
        if fname == (): return
	xdisplayfile(fname)

    def displayFile(self):
	"displayFile(self) - display picked text file and update fields"
	from plotAscii import readArray
	if self.fname != '': xdisplayfile(self.fname)
	if self.NPT < 1:
	    data = readArray(self.fname)
	    self.data = data
	    self.columndata()

    def initfigure(self):
	"initfigure(self) - initialize new figure window for image plot"
	figure(self.fig,figsize=(5,5),facecolor=facecolor)
	clf()
	axes([.15,.15,.7,.7])

    def captionOff(self):
	"captionOff(self) - toggle caption on or off"
	self.caption = self.captionVar.get()
	
    def columnOn(self):
	"columnOn(self) - set text data in column or default row oriented "
	self.column = self.columnVar.get()
        try:
	    if len(self.data) > 2:
		if self.column : self.columndata()
		else: self.rowdata()
		self.tvimage()
	except AttributeError:
	    pass
	
    def rowdata(self):
      "rowdata(self) - extract x,y vectors from row oriented text array"
      try:
	data = self.data
	nc = len(data)
	NPT = len(data[0])
	self.NPT = NPT
	self.NC = nc
	self.xa = arange(self.NPT)
	self.ya = arange(self.NC)
	xid = int(self.xrid.get())
	yid = int(self.yrid.get())
	if xid < 0 or xid >= nc: 
		x = range(NPT) 
		y = data[0:nc]
	else:
		x = data[xid]
		y = []
		for i in range(nc):
#		     if i != xid:
		     if i >= yid:
			y.append(data[i])
	self.initfields(x,y)
      except AttributeError:
	self.message()
	return

    def columndata(self):
      "columndata(self) - extract x,y vectors from column oriented text array"
      try:
	data = self.data
	NPT = len(data)
	self.NPT = NPT
	NC = len(data[0])
	self.NC = NC
	self.xa = arange(self.NPT)
	self.ya = arange(self.NC)
	if NC <= 1: 
		print 'bad file'
		return
	self.W[0].setentry(self.fname)
	da = transposeA(data)
	xid = int(self.xcid.get())
	yid = int(self.ycid.get())
	if xid < 0:  
		x = range(NPT)
		y = da[0:NC]
	else:
		x = da[xid]
		y=[]
		for i in range(NC):
#		    if i != xid:
		    if i >= yid:
			y.append(da[i])
	self.initfields(x,y)
      except AttributeError:
	self.message()
	return

    def pickMDAFile(self):
	"pickMDAFile(self) - dialog to pick a MDA file"
	import tkFileDialog
        fname = tkFileDialog.askopenfilename( initialdir=self.mdapath,
                filetypes=[("MDA File", '.mda'),
                ("All Files","*")])
        if fname == (): return
        (self.mdapath, fn) = os.path.split(fname)
        self.mdafile = fn # fname
        d = readMDA(fname)
	self.d = d
	try:
	    if d[1].nd> 0:
		print '1D data found'
	except IndexError:
	    pass
	try:
	    if d[2].nd> 0:
		self.panimage()
		print '2D data found'
	except IndexError:
	    pass
	try:
	    if d[3].nd> 0:
		print '3D data found'
	except IndexError:
	    pass

    def panimage(self):
	"panimage(self) - generate panimage window for picked MDA file"
	if self.mdafile == '': 
		self.message(text='Please use File->MDA 2D/3D to pick MDA file')
		return
	d = self.d
	nd = d[2].nd
	xa = d[2].p[0].data
	self.xa = xa[0]
	ya = d[1].p[0].data
	self.ya = ya
	self.NPT = len(self.xa)
	self.NC = len(self.ya)
	w=61
	h=61
	w = self.NPT +1
	h = self.NC +1
	nd = d[2].nd
	nr = nd/10+1
	width = w*10
	height = h*nr
	self.width = w
	self.height= h
	self.nr = nr
	self.nd = nd
	da = reshape(width*height*[0.],(height,width))
	for i in range(nd):
		ic = i % 10
		ir = i /10
		x0 = w * ic
		y0 = h*ir
#		y0 = height - h *(ir+1)
		y0 = h*ir
		data = array(d[2].d[i].data)
		vmin,vmax = minmax(data)
		if vmax > vmin:
			dv = vmax-vmin
			data = divide(subtract(data,vmin),dv)
		else:
			data = reshape(self.NPT*self.NC*[.5],(self.NC,self.NPT))
	#	da[y0:y0+self.NC-1,x0:x0+self.NPT-1]=data[0:self.NC-1,0:self.NPT-1]
		for j in range(self.NC): 
	          da[y0+self.NC-1-j,x0:x0+self.NPT-1]=data[j,0:self.NPT-1]
	close(0)
	figure(0,figsize=(5.5,5.5),facecolor=facecolor)
	xl = .8
	yl = xl/10*nr
	ys = .8-yl
	axes([.1,.1+ys,xl,yl])
	imshow(da,interpolation=self.interp) 
	connect('button_press_event',self.pickDetector)
	axis('off')
	title(self.mdafile)
	ax=axis()
	dx = ax[1]-ax[0]
	dy = ax[3]-ax[2]
	text(.5*dx,-.15*dy,'Click the thumbnail image desired',
		horizontalalignment='center')
	show()

    def report2Drow(self):
	"report2D(self) - generate 2D row oriented ascii file for picked MDA file"
	if self.mdafile == '': 
		self.message(text='Please use File->MDA 2D/3D to pick MDA file')
		return
	d = self.d
	mdaAscii_2D(d,row=1)

    def report2D(self):
	"report2D(self) - generate 2D file for picked MDA file"
	if self.mdafile == '': 
		self.message(text='Please use File->MDA 2D/3D to pick MDA file')
		return
	d = self.d
	mdaAscii_2D(d)

    def reportIGOR(self):
	"reportIGOR(self) - generate 2D IGOR file for picked MDA file"
	if self.mdafile == '': 
		self.message(text='Please use File->MDA 2D/3D to pick MDA file')
		return
	d = self.d
	mdaAscii_IGOR(d)

    def report2D1D(self):
	"report2D1D(self) - generate 1D report from 2D MDA array "
	if self.mdafile == '': 
		self.message(text='Please use File->MDA 2D/3D to pick MDA file')
		return
	d = self.d
	mdaAscii_2D1D(d)

    def reportALL(self):
	"reportALL(self) - generate all report for selected MDA directory"
	if self.mdapath == '.': 
		self.message(text='Please use File->MDA 2D/3D to pick MDA file')
		return
	mdaAscii_all(self.mdapath)

    def removeAscii(self):
	"removeAscii(self) - remove all ascii file "
        from Dialog import *
#        dir = os.getcwd() +os.sep+'ASCII'+os.sep+'*.txt'
        dir = self.txtpath+os.sep+'*.txt'
        dir = 'rm -fr '+dir
        pa = {'title': 'Remove ASCII files',
                'text': dir + '\n\n'
                        'All ascii text files will be removed\n'
                        'from the sub-directory ASCII.\n'
                        'Is it OK to remove all files ?\n ',
                'bitmap': DIALOG_ICON,
                'default': 1,
                'strings': ('OK','Cancel')}
        dialog = Dialog(self.interior(),pa)
        ans = dialog.num
        if ans == 0:
          print dir
          os.system(dir)

    def showDetector(self):
	"showDetector(self) - draw panimage and pick detector image "
	if self.mdafile == '': return
	self.panimage()

    def pickDetector(self,event):
	"pickDetector(self,event) - use mouse event to select desired detector"
	if event.button == 3:
		close(0)
		return
        try:
	  event0 = event
	  ix,iy = int(event0.xdata),int(event0.ydata)
	  ix = ix / self.width
	  iy = self.nr - 1 - iy / self.height
	  id = iy * 10 + ix
	  if id >= self.nd: return
	  d = self.d
	  dname = d[2].d[id].fieldName
	  self.W[0].setentry(self.mdafile+'-'+dname)
	  data = array(d[2].d[id].data)
	  self.data = data
	  self.initfields(range(self.NPT),data)
	  self.fig = self.fig+1
	  self.tvimage()
     	except:
	  pass 

    def pickFile(self):
	"pickFile(self) - dialog to pick a row  oriented text data file"
	from plotAscii import readArray
	import tkFileDialog
	fname = tkFileDialog.askopenfilename(initialdir=self.txtpath,
                initialfile='*.txt')
        if fname == (): return
	self.fname = fname
	data = readArray(fname)
	self.data = data
	self.axisset = 0
	if self.column: self.columndata()
	else: self.rowdata()
	self.tvimage()

    def drawcaption(self):
	"drawcaption(self) - draw title, x and y labels if caption is desired"
	if self.caption: 
	    title(self.W[0].get())
	    xlabel(self.W[1].get())
	    ylabel(self.W[2].get())
	    self.heading()

    def toggleColorbar(self):
	"toggleColorbar(self) - toggle colorbar on the image plot"
	if self.NPT <1 : return
	self.fig = self.fig+1
	figure(self.fig,figsize=(5,5),facecolor=facecolor)
	cax = axes([.1,.2,.65,.65])
	if self.imagetype == 2:
	    y = self.y
	    y = transpose(y)
	    imshow(y,origin='lower',interpolation=self.interp) 
	    xlim(self.Rg[2],self.Rg[3])
	    ylim(self.Rg[0],self.Rg[1])
	else:
	  imshow(self.y,origin='lower',interpolation=self.interp) 
	  if self.imagetype == 1:
	    xlim(self.Rg[0],self.Rg[1])
	    ylim(self.Rg[2],self.Rg[3])
	  if self.imagetype == 3:
	    xlim(self.Rg[0],self.Rg[1])
	    ylim(self.Rg[3],self.Rg[2])
	  if self.imagetype == 4:
	    ylim(self.Rg[2],self.Rg[3])
	    xlim(self.Rg[1],self.Rg[0])
	self.drawcaption()
	self.colorbar()
	self.CBexist = 1
	cid = connect('button_press_event',self.lineprofile)
	show()

    def colorbar(self):
	"colorbar(self) - define colorbar region and draw colorbar"
	cax = axes([.80,.225,.03,.5])
	colorbar(cax=cax)

    def refreshimage(self):
	"refreshimage(self) - refresh image plot"
	if self.imagetype < 1: return
	clf()
	self.fig = self.fig - 1
	if self.imagetype==1: self.tvimage()
	if self.imagetype==2: self.tvimagetranspose()
	if self.imagetype==3: self.tvimageupdown()
	if self.imagetype==4: self.tvimagehorizon()

    def imageshow(self):
	"imageshow(self) - redraw image with specified interpolation method"
	if self.NPT <1 : return
	self.initfigure()
	imshow(self.y,origin='lower',interpolation=self.interp)
	if self.caption:
		title('Interpolate method: ' + self.interp)
	show()
	
    def closewin(self,event):
	"closewin(slef,event) - check for button 3 and close window"
	if event.button == 3:
		close(self.fig)
		self.fig = self.fig-1
	
    def lineprofile(self,event):
	"lineprofile(slef,event) - draw line profiles at the mouse clicked cursor location of image area"
	if event.button == 3:
		close(self.fig)
		self.fig = self.fig-1
		return
	try:
	  ix,iy = int(event.xdata), int(event.ydata)
	  from tv import lineplot
	  da = self.y
	  st = 'Cursor -> '+str(ix)+', '+str(iy)+', '+str(da[iy][ix])
	  self.cursorVar.set(st)
	  if event.button == 1:
		return
	  x = self.xa
	  y = self.ya
	  ya = da[iy]
	  d = transpose(da)
	  xa = d[ix]
	  ti = str(da[iy][ix])+'['+str(ix)+','+str(iy)+']'
	  lineplot(xa,title='Y profile @ '+ti,X=y)
	  lineplot(ya,title='X profile @ '+ti,X=x)
        except TypeError:
	  return
	
    def tvimage1(self):
        "tvimage(self) - draw a new image window"
        if self.NPT <1 : return
        try: close(self.fig)
        except: pass
	self.fig = self.fig #+1
	self.imagetype = 1
	self.fig = self.fig+1
	figure(self.fig,figsize=(5,5),facecolor=facecolor)
	cax = axes([.1,.2,.65,.65])
	imshow(self.y,cmap=ct1(),origin='lower',interpolation=self.interp,vmin=self.Rg[4],vmax=self.Rg[5]) 
	cid = connect('button_press_event',self.lineprofile)
	self.drawcaption()
	self.colorbar()
	self.CBexist = 1
	show()
	return cid

    def tvimage(self):
        "tvimage(self) - draw a new image window"
        if self.NPT <1 : return
        try: close(self.fig)
        except: pass
	self.fig = self.fig #+1
	self.imagetype = 1
	self.initfigure()
	imshow(self.y,origin='lower',interpolation=self.interp) 
#	xlim(self.Rg[0],self.Rg[1])
#	ylim(self.Rg[2],self.Rg[3])
	cid = connect('button_press_event',self.lineprofile)
	self.drawcaption()
	self.CBexist = 0
	show()
	return cid

    def heading(self):
	"heading(self) - draw image vmin, vmax heading"
	v = axis()
	vx = (v[1]-v[0])/10.
	vy = (v[3]-v[2])/10.
	text(v[0]-1.35*vx,v[2]-1.8*vy,'vmin='+str(self.Rg[4]))
	text(v[0]-1.35*vx,v[2]-1.5*vy,'vmax='+str(self.Rg[5]))

    def tvimagetranspose(self):
	"tvimagetranspose(self) - draw a transposed new image window"
	if self.NPT <1: return
	self.fig = self.fig+1
	self.imagetype = 2
	self.initfigure()
	y = self.y
	NC = len(y)
	y = transpose(y)
	self.initfields(range(NC),y)
	imshow(y,origin='lower',interpolation=self.interp) 
	xlim(self.Rg[2],self.Rg[3])
	ylim(self.Rg[0],self.Rg[1])
	close(self.fig-1)
	cid = connect('button_press_event',self.lineprofile)
	if self.caption:
		title(self.W[0].get())
		xlabel(self.W[2].get())
		ylabel(self.W[1].get())
	show()

    def tvimageupdown(self):
	"tvimageupdown(self) - draw image flip upside down"	
	if self.NPT <1: return
	close(self.fig)
	self.fig = self.fig #+1
	self.imagetype = 3
	y = self.y
	self.initfigure()
	imshow(y,origin='lower',interpolation=self.interp) 
	xlim(self.Rg[0],self.Rg[1])
	ylim(self.Rg[3],self.Rg[2])
	self.drawcaption()
	connect('button_press_event',self.lineprofile)
#	axis('off')
	show()

    def tvimagehoriz(self):
	"tvimagehoriz(self) - draw image flip horizontally"	
	if self.NPT <1: return
	close(self.fig)
	self.fig = self.fig #+1
	self.imagetype = 4
	y = self.y
	self.initfigure()
	imshow(y,origin='lower',interpolation=self.interp) 
	ylim(self.Rg[2],self.Rg[3])
	xlim(self.Rg[1],self.Rg[0])
	self.drawcaption()
	connect('button_press_event',self.lineprofile)
#	axis('off')
	show()

    def setXYrangedone(self):
	"setXYrangedown(self) - close X, Y range diallog"
	self.XYFrame.destroy()

    def setXYrangearray(self):
	"setXYrangarray(self) - set X,Y range array"
	xmin = string.atof(self.XYW[0].get())
	xmax = string.atof(self.XYW[1].get())
	ymin = string.atof(self.XYW[2].get())
	ymax = string.atof(self.XYW[3].get())
	self.XYFrame.destroy()
	dx = (xmax-xmin)/(self.NPT-1)
	dy = (ymax-ymin)/(self.NC-1)
	x = xmin + dx * arange(self.NPT)
	y = ymin + dy * arange(self.NC)
	self.axisset = 1
	self.xa = x
	self.ya = y
	self.xa_min = xmin
	self.xa_max = xmin
	self.ya_min = ymin
	self.ya_max = ymin

    def setXYrange(self):
        "setXYrange(self) - set X,Y coordinate ranges "
	if self.NPT < 1: return
	import Tkinter
	top=Toplevel()
	top.title('X,Y Range Setup Dialog')
	self.XYFrame=top
	fm = Frame(top,borderwidth=0)
	self.XYW=(StringVar(),StringVar(),StringVar(),StringVar())
	Label(fm,text='Enter X Axis: ').grid(row=1,column=1,sticky=W)
	Label(fm,text='Xmin:').grid(row=1,column=2,sticky=W)
	Entry(fm,width=15,textvariable=self.XYW[0]).grid(row=1,column=3,sticky=W)
	Label(fm,text='Xmax:').grid(row=2,column=2,sticky=W)
	Entry(fm,width=15,textvariable=self.XYW[1]).grid(row=2,column=3,sticky=W)
	Label(fm,text='Enter Y Axis: ').grid(row=3,column=1,sticky=W)
	Label(fm,text='Ymin:').grid(row=3,column=2,sticky=W)
	Entry(fm,width=15,textvariable=self.XYW[2]).grid(row=3,column=3,sticky=W)
	Label(fm,text='Ymax:').grid(row=4,column=2,sticky=W)
	Entry(fm,width=15,textvariable=self.XYW[3]).grid(row=4,column=3,sticky=W)
	self.XYW[0].set(self.xa[0])
	self.XYW[1].set(self.xa[self.NPT-1])
	self.XYW[2].set(self.ya[0])
	self.XYW[3].set(self.ya[self.NC-1])

	Tkinter.Button(fm,text='OK',command=self.setXYrangearray).grid(row=6,column=2,sticky=W)
	Tkinter.Button(fm,text='Close',command=self.setXYrangedone).grid(row=6,column=3,sticky=W)
	fm.pack(fill=BOTH)

    def takeXslice(self):
        "takeXslice(self) - extract X slices from image array "
	if self.NPT < 1: return
	import Tkinter
	top=Toplevel()
	top.title('Dialog pick X slices')
	self.XSFrame=top
	fm = Frame(top,borderwidth=0)
	self.XSW=[StringVar(),StringVar(),StringVar()]
	Label(fm,text='Multi-Line Plotter').grid(row=0,column=2,sticky=W)
	Label(fm,text='Enter X index # list ').grid(row=1,column=1,sticky=W)
	Label(fm,text='['+str(self.Rg[0])+' - '+ str(self.Rg[1]-1)+' ]: ').grid(row=1,column=2,sticky=W)
	Entry(fm,width=45,textvariable=self.XSW[0]).grid(row=1,column=3,sticky=W)
	Label(fm,text='Set   Xaxis ').grid(row=2,column=1,sticky=W)
	Label(fm,text='Start Value:').grid(row=2,column=2,sticky=W)
	Entry(fm,width=15,textvariable=self.XSW[1]).grid(row=2,column=3,sticky=W)
	Label(fm,text='End Value:').grid(row=3,column=2,sticky=W)
	Entry(fm,width=15,textvariable=self.XSW[2]).grid(row=3,column=3,sticky=W)
	self.XSW[0].set('0')
	self.XSW[1].set(self.ya[0])
	self.XSW[2].set(self.ya[self.NC-1])
	self.lineVar = IntVar()
	Label(fm,text='Line Width :').grid(row=5,column=2,sticky=W)
	Entry(fm,width=5,textvariable=self.lineVar).grid(row=5,column=3,sticky=W)
	self.lineVar.set(1)

	Tkinter.Button(fm,text='All',command=self.takeXsliceall).grid(row=7,column=1,sticky=W)
	Tkinter.Button(fm,text='OK',command=self.takeXsliceset).grid(row=7,column=2,sticky=W)
	Tkinter.Button(fm,text='Close',command=self.takeXsliceclose).grid(row=7,column=3,sticky=W)
	fm.pack(fill=BOTH)

    def takeXsliceclose(self):
	"takeXsliceclose(self) - close X slice dialog"
	self.XSFrame.destroy()

    def takeXsliceall(self):
	"takeXsliceall(self) - plot all X slices"
	ll = str(self.Rg[0])+ '-' + str(self.Rg[1])
	ls = parseint(ll)
	self.takeXsliceselect(ls)

    def takeXsliceset(self):
	"takeXsliceset(self) - accept and parse entered X slices"
	try:
		ll = self.XSW[0].get()
		if ll =='': return
		ls = parseint(ll)
	except:
		message(self.XSFrame,
		  text='Error in\n\nX index # list Field,\nfix it first.')
		return
	self.takeXsliceselect(ls)

    def takeXsliceselect(self,ls):
	"takeXsliceselect(self,ls) - plot the entered vertical slices"
        try:
		x1 = string.atof(self.XSW[1].get())
	except:
		message(self.XSFrame,
		  text='Error in \n\nStart Value Field,\nfix it first.')
		return
	try:
		x2 = string.atof(self.XSW[2].get())
	except:
		message(self.XSFrame,
		  text='Error in \n\nEnd Value Field, \nfix it first.')
		return
	try:
		thick = self.lineVar.get()
	except:
		message(self.XSFrame,
		  text='Error in \n\nLine Width Field,\nonly integer allowed.')
		return
	lss = []
	for i in range(len(ls)):
		if ls[i] < self.Rg[1] and ls[i]>= self.Rg[0]:
			lss.append(ls[i])
	ls = lss
	y = self.y
	l = take(y,ls,axis=1)
	l = transpose(l)
	x =[]
	xa = self.ya
	i1 = 0
	for i in range(self.NC):
	    if xa[i] >= x1 and xa[i] <= x2:
		i2 = i
		x.append(xa[i])
	    if xa[i] <= x1:
		i1 = i 
	x = array(x)
	self.fig=self.fig+1
	figure(self.fig,figsize=(5,4))
	axes([.15,.15,.7,.7])
	nl = len(l)
	nx = len(x)
	for i in range(nl):
		ll = l[i]
		plot(x,ll[i1:i1+nx],label=str(ls[i]),linewidth=thick)
	if self.caption: 
		tit = 'X slices:'+self.XSW[0].get()
		title(tit)
		if nl > 1:
			legend()
  			self.pickLegpos()
	connect('button_press_event',self.closewin)
	
    def takeYslice(self):
        "takeYslice(self) - extract column  slices from image array "
	if self.NPT < 1: return
	import Tkinter
	top=Toplevel()
	top.title('Dialog pick Y slices')
	self.YSFrame=top
	fm = Frame(top,borderwidth=0)
	self.YSW= [StringVar(),StringVar(),StringVar()]
	Label(fm,text='Multi-Line Plotter').grid(row=0,column=2,sticky=W)
	Label(fm,text='Enter Y index # list ').grid(row=1,column=1,sticky=W)
	Label(fm,text='['+str(self.Rg[2])+' - '+ str(self.Rg[3]-1)+' ]: ').grid(row=1,column=2,sticky=W)
	Entry(fm,width=45,textvariable=self.YSW[0]).grid(row=1,column=3,sticky=W)
	Label(fm,text='Set   Xaxis ').grid(row=2,column=1,sticky=W)
	Label(fm,text='Start Value:').grid(row=2,column=2,sticky=W)
	Entry(fm,width=15,textvariable=self.YSW[1]).grid(row=2,column=3,sticky=W)
	Label(fm,text='End Value:').grid(row=3,column=2,sticky=W)
	Entry(fm,width=15,textvariable=self.YSW[2]).grid(row=3,column=3,sticky=W)
	self.YSW[0].set('0')
	self.YSW[1].set(self.xa[0])
	self.YSW[2].set(self.xa[self.NPT-1])

	self.lineVar = IntVar()
	Label(fm,text='Line Width :').grid(row=5,column=2,sticky=W)
	Entry(fm,width=5,textvariable=self.lineVar).grid(row=5,column=3,sticky=W)
	self.lineVar.set(1)
	Tkinter.Button(fm,text='All',command=self.takeYsliceall).grid(row=7,column=1,sticky=W)
	Tkinter.Button(fm,text='OK',command=self.takeYsliceset).grid(row=7,column=2,sticky=W)
	Tkinter.Button(fm,text='Close',command=self.takeYsliceclose).grid(row=7,column=3,sticky=W)
	fm.pack(fill=BOTH)

    def takeYsliceclose(self):
	"takeYsliceclose(self) - close Y slices dialog"
	self.YSFrame.destroy()

    def takeYsliceall(self):
	"takeYsliceall(self) - plot all Y slices"
	ll = str(self.Rg[2]) + '-' + str(self.Rg[3])
	ls = parseint(ll)
	self.takeYsliceselect(ls)

    def takeYsliceset(self):
	"takeYsliceset(self) - accept and parse entered Y slices"
	try:
	    ll = self.YSW[0].get()
	    if ll =='': return
	    ls = parseint(ll)
	except:
	    message(self.YSFrame,
		  text='Error in \n\nY index # list Field\nfix it first')
	    return
	self.takeYsliceselect(ls)

    def takeYsliceselect(self,ls):
	"takeYsliceselect(self,ls) - plot entered horizontal curves in ls"
        try:
		x1 = string.atof(self.YSW[1].get())
	except:
		message(self.YSFrame,
		  text='Error in \n\nStart Value Field, \nfix it first.')
		return
	try:
		x2 = string.atof(self.YSW[2].get())
	except:
		message(self.YSFrame,
		  text='Error in \n\nEnd Value Field,\nfix it first.')
		return
	try:
		thick = self.lineVar.get()
	except:
		message(self.YSFrame,
		  text='Error in \n\nLine Width Field,\nonly integer allowed.')
		return
	lss = []
	for i in range(len(ls)):
		if ls[i] < self.Rg[3] and ls[i]>= self.Rg[2]:
			lss.append(ls[i])
	ls = lss
	y = self.y
	l = take(y,ls,axis=0)
	x =[]
	xa = self.xa
	i1 = 0
	for i in range(self.NPT):
 	    if xa[i] >= x1 and xa[i] <= x2:
		x.append(xa[i]) 
		i2 = i
	    if xa[i] <= x1: i1 = i
	x = array(x)
	self.fig=self.fig+1
	figure(self.fig,figsize=(5,4))
	axes([.15,.15,.7,.7])
	nl = len(l)
	nx = len(x)
	for i in range(nl):
		ll = l[i]
		plot(x,ll[i1:i1+nx],label=str(ls[i]),linewidth=thick)
	if self.caption: 
		tit = 'Y slices:'+self.YSW[0].get()
		title(tit)
		if nl > 1: 
			legend(loc='best')
  			self.pickLegpos()
	connect('button_press_event',self.closewin)
	
    def toggleLegclose(self):
	"toggleLegclose(self) - close toggle legend dialog"
        self.legFrame.destroy()

    def toggleLeg(self):
        "toggleLeg(self) - get default legend position"
        self.legloc = self.legVar.get()
        try:
                legend(loc=legends[self.legloc])
        except:
                pass

    def pickLegpos(self):
        "pickLegpos(self) - dialog to pick legend position"
        import Tkinter
        top=Toplevel()
	top.title('LegPosition')
        self.legFrame=top
        fm = Frame(top,borderwidth=0)
	Label(fm,text='Set Legend Position').pack()
        var = IntVar()
        for i in range(len(legends)):
                Radiobutton(fm,text=legends[i],value=i,variable=var,
                        command=self.toggleLeg,
                        indicatoron=1).pack(anchor=W)
        var.set(0)
        self.legVar= var
	Tkinter.Button(fm,text='Close',command=self.toggleLegclose).pack(anchor=W)
        fm.pack(fill=BOTH)


    def changeclimdone(self):
	"changeclimdone(self) - close image color limit dialog"
	self.CLFrame.destroy()

    def changeclimreset(self):
	"changeclimreset(self) - reset to image default limit color"
	self.CLW[0].set(self.Rg[4])
	self.CLW[1].set(self.Rg[5])
	clim(self.Rg[4],self.Rg[5])
	if self.CBexist: self.colorbar()

    def changeclimset(self):
	"changeclimset(self) - accept color limit and redraw image"
	v1 = string.atof(self.CLW[0].get())
	v2 = string.atof(self.CLW[1].get())
	clim(v1,v2)
	if self.CBexist: self.colorbar()

	
    def changeclim(self):
        "changeclim(self) - set image color limit "
	if self.NPT < 1: return
	import Tkinter
	top=Toplevel()
	top.title('Image Color Limit Setup Dialog')
	self.CLFrame=top
	fm = Frame(top,borderwidth=0)
	self.CLW=(StringVar(),StringVar())
	Label(fm,text='Enter Lower Limit: '+str(self.Rg[4])).grid(row=1,column=1,sticky=W)
	Entry(fm,width=15,textvariable=self.CLW[0]).grid(row=1,column=2,sticky=W)
	Label(fm,text='Enter Upper Limit: '+str(self.Rg[5])).grid(row=2,column=1,sticky=W)
	Entry(fm,width=15,textvariable=self.CLW[1]).grid(row=2,column=2,sticky=W)
	self.CLW[0].set(str(self.Rg[4]))
	self.CLW[1].set(str(self.Rg[5]))
	Tkinter.Button(fm,text='Reset',command=self.changeclimreset).grid(row=3,column=1,sticky=W)
	Tkinter.Button(fm,text='Accept',command=self.changeclimset).grid(row=3,column=2,sticky=W)
	Tkinter.Button(fm,text='Close',command=self.changeclimdone).grid(row=3,column=3,sticky=W)
	fm.pack(fill=BOTH)

    def setcolormapclose(self):
	"setcolormapclose(self) - close setcolormap dialog"
	self.cmapW.destroy()

    def setcolormap(self):
	"setcolormap(self) - set color map to picked new value"
	st = cmaps[self.colormapvar.get()]
	st = st +'()'
	exec(st)
	if self.CBexist:
		self.colorbar()

    def changecmap(self):
	"changecmap(self) - call change color map dialog"
	import Tkinter
	top=Toplevel()
	top.title('Reset CMAP')
	self.cmapW=top
	self.colormapvar = IntVar()
	for i in range(len(cmaps)):
		Radiobutton(top,text=cmaps[i],value=i,
			command=self.setcolormap,
			variable=self.colormapvar,indicatoron=0).pack(fill=X)
	self.colormapvar.set(8) # jet
	Tkinter.Button(top,text='Close',command=self.setcolormapclose).pack()

    def setinterpclose(self):
	"setinterpclose(self) - close smoothing interpolation dialog"
	self.interpW.destroy()

    def setinterp(self):
	"setinterp(self) - redraw with picked interpolation method"
	st = interp[self.interpvar.get()]
	self.interp = st
	self.imageshow()
	
    def changeinterp(self):
	"changeinterp(self) - pop up change interpolation dialog"
	import Tkinter
	top=Toplevel()
	top.title('Set Interpolation Method')
	self.interpW=top
	self.interpvar = IntVar()
	for i in range(len(interp)):
		Radiobutton(top,text=interp[i],value=i,
			command=self.setinterp,
			variable=self.interpvar,indicatoron=0).pack(fill=X)
	self.interpvar.set(1) # bilinear
	Tkinter.Button(top,text='Close',command=self.setinterpclose).pack()

    def contourdone(self):
	"contourdone(self) - close contour setting dialog"
	self.ctrFrame.destroy()

    def getcontour(self):
	"getcontour(self) - redraw contour with current contour setting "
	st = self.CTW[3].get()
	if len(st) > 2:
		LL = parsefloat(st)	
		self.contour_N = len(LL)
	else:
		self.contour_N = self.CTW[0].get()
	self.contour_color = self.CTW[1].get()
	self.contour_lwidth = (.5,1.,1.5) 
	ll = self.CTW[2].get()
	if ll == 'None':
		self.contour_lwidth = None
 	else:
	# extract line width field
		if string.find(ll,',') > 0:
			ll = string.split(ll, ',')
		else: 
			ll = string.split(ll)
		lw =[]
		for i in range(len(ll)):
			lw.append(string.atof(ll[i]))
		self.contour_lwidth = (lw[0:len(lw)])
		
	self.fig = self.fig+1
	self.initfigure()
	if len(st) > 2:
	    [L,C] = contour(self.y,LL,colors=self.contour_color,
		linewidths=self.contour_lwidth)
	else:
	    [L,C]= contour(self.y,self.contour_N,colors=self.contour_color,
		linewidths=self.contour_lwidth)
	print L
	clabel(C,L)
	self.drawcaption()
	connect('button_press_event',self.closewin)
	show()

    def setcolorfield(self):
	"setcolorfield(self) - set contour line color"
	self.CTW[1].set(Colors[self.colorvar.get()])

    def setcolor(self):
	"setcolor(self) - set color from a set of radio button"
	self.colorvar = IntVar()
	for i in range(len(Colors)):
		Radiobutton(self.ctrFrame,text=Colors[i],value=i,
			command=self.setcolorfield,
			variable=self.colorvar,indicatoron=0).pack(fill=X)
	self.colorvar.set(6) # set black

    def setcontour(self):
        "setcontour(self) - dialog to set up contour properties "
	if self.NPT < 1: return
	import Tkinter
	top=Toplevel()
	top.title('Contour Setup Dialog')
	self.ctrFrame=top
	fm = Frame(top,borderwidth=0)
	self.CTW=(IntVar(),StringVar(),StringVar(),StringVar())
	Label(fm,text='Contour lines, N:').grid(row=1,column=1,sticky=W)
	Entry(fm,width=15,textvariable=self.CTW[0]).grid(row=1,column=2,sticky=W)
	self.CTW[0].set(7)
	Label(fm,text='Line Color:').grid(row=2,column=1,sticky=W)
	Entry(fm,width=15,textvariable=self.CTW[1]).grid(row=2,column=2,sticky=W)
	self.CTW[1].set('black')
	Label(fm,text='Linewidths List:').grid(row=3,column=1,sticky=W)
	Entry(fm,width=25,textvariable=self.CTW[2]).grid(row=3,column=2,sticky=W)
	self.CTW[2].set('.2,.5,.8,1.1,1.4,1.7,2.')
	Label(fm,text='Value Ranges:').grid(row=4,column=1,sticky=W)
	st = '[' + str(self.Rg[4]) + ' , '+ str(self.Rg[5]) +']'
	Label(fm,text=st).grid(row=4,column=2,sticky=W)
	Label(fm,text='Contour Values').grid(row=5,column=1,sticky=W)
	Entry(fm,width=50,textvariable=self.CTW[3]).grid(row=5,column=2,sticky=W)
	self.CTW[3].set('')

	Tkinter.Button(fm,text='Reset Line Color',command=self.setcolor).grid(row=6,column=1,sticky=W)
	Tkinter.Button(fm,text='Draw Contours...',command=self.getcontour).grid(row=6,column=2,sticky=W)
	Tkinter.Button(fm,text='Close',command=self.contourdone).grid(row=6,column=3,sticky=W)
	fm.pack(fill=BOTH)

    def tvcontour(self):
	"tvcontour(self) - default contour plot"
	if self.NPT < 1: return
	self.fig = self.fig+1
	self.initfigure()
	contour(self.y)
	self.drawcaption()
	connect('button_press_event',self.closewin)
	show()

    def tvcontourf(self):
	'tvcontourf(self) - default filled contour plot'
	if self.NPT < 1: return
	self.fig = self.fig+1
	self.initfigure()
	contourf(self.y)
	self.drawcaption()
	connect('button_press_event',self.closewin)
	show()

    def setxcid(self):
	"setxcid(self) - reset data as column array"
	if self.NPT < 1: return
	self.columndata()

    def setxrid(self):
	"setxrid(self) - reset data as row array"
	if self.NPT < 1: return
	self.rowdata()

    def settitle(self):
	"settitle(self) - update the title of plot figure"
	if self.fig < 1: return
	if self.caption:
		title(self.W[0].get())

    def setxlabel(self):
	"setxlabel(self) - update the xlabel of plot figure"
	if self.fig < 1: return
	if self.caption:
		xlabel(self.W[1].get())

    def setylabel(self):
	"setylabel(self) - update the ylabel of plot figure"
	if self.fig < 1: return
	if self.caption:
		ylabel(self.W[2].get())

    def setxlimit(self):
	"setxlimit(self) - set and update xlim for plot figure"
	if self.fig < 1: return
	self.Rg[0] = self.xmin.get()
	self.Rg[1] = self.xmax.get()
	xlim(self.Rg[0],self.Rg[1])

    def setylimit(self):
	"setylimit(self) - set and update ylim for plot figure"
	if self.fig < 1: return
	self.Rg[2] = self.ymin.get()
	self.Rg[3] = self.ymax.get()
	ylim(self.Rg[2],self.Rg[3])

    def setvlimit(self):
	"setvlimit(self) - set and update array vlim for plot figure"
	if self.NPT < 1: return
	v1 = string.atof(self.vmin.get())
	v2 = string.atof(self.vmax.get())
	clim(v1,v2)

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
		label_text = 'Xrange Imin:', command=self.setxlimit,
#		validate = {'validator':'real','min':0,'max':100,'minstrict':0}
		)
	self.xmax = Pmw.EntryField(frame,labelpos=W,value=self.Rg[1],
		label_text = ' Imax:', command=self.setxlimit
		)
	self.xmin.grid(row=1,column=1,sticky=W)
	self.xmax.grid(row=1,column=2,sticky=W)

	self.ymin = Pmw.EntryField(frame,labelpos=W,value=self.Rg[2],
		label_text = 'Yrange Jmin:', command=self.setylimit,)
	self.ymax = Pmw.EntryField(frame,labelpos=W,value=self.Rg[3],
		label_text = ' Jmax:', command=self.setylimit)
	self.ymin.grid(row=2,column=1,sticky=W)
	self.ymax.grid(row=2,column=2,sticky=W)

	self.vmin = Pmw.EntryField(frame,labelpos=W,value=self.Rg[4],
		label_text = 'Array Vmin:', command=self.setvlimit,)
	self.vmax = Pmw.EntryField(frame,labelpos=W,value=self.Rg[5],
		label_text = ' Vmax:', command=self.setvlimit)
	self.vmin.grid(row=3,column=1,sticky=W)
	self.vmax.grid(row=3,column=2,sticky=W)

	self.xcid = Pmw.EntryField(frame,labelpos=W,value='0',
		command=self.setxcid,
		label_text = '   XCol #:')
	self.ycid = Pmw.EntryField(frame,labelpos=W,value='2',
		label_text = 'YCol start #:')
	self.xrid = Pmw.EntryField(frame,labelpos=W,value='-1',
		command=self.setxrid,
		label_text = '   XRow #:')
	self.yrid = Pmw.EntryField(frame,labelpos=W,value='0',
		label_text = 'YRow start #:')
	Label(frame,text='2D Column Vectors:').grid(row=4,column=1,sticky=W)
	Label(frame,text='2D Row Vectors:').grid(row=7,column=1,sticky=W)
	self.xcid.grid(row=5,column=1,sticky=W)
	self.ycid.grid(row=5,column=2,sticky=W)
	self.xrid.grid(row=8,column=1,sticky=W)
	self.yrid.grid(row=8,column=2,sticky=W)

	self.cursorVar = StringVar()
	Label(frame,textvariable=self.cursorVar).grid(row=9,column=1,sticky=W)
	self.cursorVar.set('Cursor Values ?')
	frame.pack()

    def initfields(self,x,y):
	"initfields(self,x,y) - initialize X,Y Index fields from x,y vectors"
	self.x = x
	self.y = array(y)
	self.nc = len(y)
	xmax = max(x)
	xmin = min(x)
	self.Rg[0] = 0 #xmin
	self.Rg[1] = len(x) #xmax+1
	self.Rg[2] = 0
	self.Rg[3] = len(y)
	ymin,ymax = minmax(y)
	self.Rg[4] = ymin
	self.Rg[5] = ymax
	self.xmin.setentry('0')
	self.xmax.setentry(str(len(x)))
	self.ymin.setentry('0')
	self.ymax.setentry(str(len(y)))
	self.vmin.setentry(str(ymin))
	self.vmax.setentry(str(ymax))

    def startup(self):
      "startup(self) - initialize variables at object plot2d creation"
      from plotAscii import readST,loadpvs,initSH
      self.fig = 1
      self.NPT = -1
      self.imagetype = 0
      self.caption = 1
      self.column = 1
      self.interp = interp[0]
      self.SH = initSH()
      self.mdapath='.'
      self.mdafile=''
	
      if os.path.isfile('plot2d.config'):
        lines = readST('plot2d.config')
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
	self.Rg=['0','0','0','0','0','0']
      else:
	self.fname=''
	self.txtpath='.'
	self.title=''
	self.xlabel=''
	self.ylabel=''
	self.Rg=['0','0','0','0','0','0']

    def createInterface(self):
	"createInterface(self) - plot2d object creation"
        AppShell.AppShell.createInterface(self)
        self.createButtons()
        self.addMoreMenuBar()
        self.startup()
	self.columnVar.set(self.column)
	self.createFields()

if __name__ == '__main__':
        plt = plot2d()
	plt.run()
