#!/usr/bin/env python

from   Tkinter import *
import AppShell,Tkinter
from tkFileDialog import askopenfilename
from tkSimpleDialog import Dialog
from  imageUtil import *
from plotAscii import readArray,transposeA,initSH,writeSH
import ImageTk, Pmw
from view2d import PNGImage1
#	from tv import Scrapbook
#        from tv import pickCT,chosenCT,drawCT for colortable

def scatterplot(data,title='Scatter plot',symbol=None,X=None):
    "multiline scater plot"
    from graph import GraphBase,GraphLine,GraphSymbols,GraphObjects 
    from plotAscii import PSprint,initSH
    SH = initSH()
    try:
        npt = len(data[0]) 
    except TypeError:
	print 'Input Error, multiple line vectors required'
	return	
    rows = len(data)
    top = Toplevel()
    top.title(title) 
    graph = GraphBase(top,300,300,relief=SUNKEN,border=2)
    w = string.atoi(graph.canvas.cget('width'))
    h = string.atoi(graph.canvas.cget('height'))
    bb  = graph._textBoundingBox(title)
    x = w/2-(bb[2]-bb[0])/2
    y = .05*h
    graph.canvas.create_text(x,y,text=title,anchor=W,font=SH['font'])


#    markers=['circle','square','cross','plus','dot','triangle','triangle_down']
    lines = []
    for j in range(rows):
	npt = []
	da = data[j]
	npts = len(da)
	if X != None: 
		xa = X[j]
		if len(xa) < npts: xa = range(npts)
	else: 
		xa = range(npts)
	for i in range(npts): npt.append((xa[i],da[i]))
	line = GraphLine(npt,color='blue')
	lines.append(line)
	# plot symbols
	if symbol != None:
	    npt_s = linesubset(npt)
#	    sym = markers[j%7]
	    linea = GraphSymbols(npt_s,color='blue',marker='circle',size=1.5,
		fillcolor='blue')
	    lines.append(linea)

    graphObject = GraphObjects(lines)
    graph.pack(side=TOP,fill=BOTH,expand=YES)
    graph.draw(graphObject,'automatic','automatic')
    Button(top,text='Print',command=lambda g=graph,p=SH['printer']: PSprint(g,p)).pack(side=LEFT)
    Button(top,text='Close',command=top.destroy).pack(side=LEFT)
    top.mainloop()

def linesubset(pts,space=10):
	"linesubset(pts) - returns subset of data points every 10 points"
	nr =len(pts)
	nr_1 = nr/10
	if nr_1 < 1: nr_1 = 1
	pts_1 = []
	for j in range(0,nr,nr_1): 
	   pts_1.append(pts[j])	
	pts_1.append(pts[nr-1])
	return pts_1

def lineplot(data,title='Line plot',symbol=None,X=None):
	from graph import GraphBase,GraphLine,GraphSymbols,GraphObjects 
	from plotAscii import PSprint,initSH
	SH = initSH()
	npt = []
	for i in range(len(data)):
	    if X != None:
		npt.append((X[i],data[i]))
	    else:
		npt.append((float(i),data[i]))
	top = Toplevel()
	top.title(title) 
	graph = GraphBase(top,300,300,relief=SUNKEN,border=2)

	w = string.atoi(graph.canvas.cget('width'))
	h = string.atoi(graph.canvas.cget('height'))
	bb  = graph._textBoundingBox(title)
	x = w/2-(bb[2]-bb[0])/2
	y = .05*h
	graph.canvas.create_text(x,y,text=title,anchor=W,font=SH['font'])

	line = GraphLine(npt,color='blue')
	# plot symbols
	if symbol != None:
	    npt_s = linesubset(npt)
	    linea = GraphSymbols(npt_s,color='blue',marker='circle',size=1.5,
		fillcolor='blue')
	    graphObject = GraphObjects([line,linea])
	else:
	    graphObject = GraphObjects([line])

	graph.pack(side=TOP,fill=BOTH,expand=YES)
	graph.draw(graphObject,'automatic','automatic')
	Button(top,text='Print',command=lambda g=graph,p=SH['printer']: PSprint(g,p)).pack(side=LEFT)
	Button(top,text='Close',command=top.destroy).pack(side=LEFT)

class Scrapbook:
    "Scrapbook - picture browser for any gif, jpg, png, ppm image files"
    def __init__(self, master=None):
        self.master = master
	self.width = 400
	self.height = 480
        self.frame = Frame(master, width=self.width, height=self.height,
		bg='gray50', relief=RAISED, bd=4)
              
        self.lbl = Label(self.frame)
        self.lbl.place(relx=0.5, rely=0.48, anchor=CENTER)


        xpos = 0.1
	Button(self.master,text='File...', bg='blue',fg='yellow', 
		command=self.pickfile).place(relx=xpos, rely=0.99, anchor=S)
            
        Button(self.master, text='Done',  command=self.exit,
               bg='red', fg='yellow').place(relx=0.99, rely=0.99, anchor=SE)
        Button(self.master, text='Info', command=self.info,
	       bg='blue', fg='yellow').place(relx=0.28, rely=0.99, anchor=S)
	self.infoDisplayed = FALSE
        Button(self.master, text='Printer...', command=self.printer,
	       bg='blue', fg='yellow').place(relx=0.5, rely=0.99, anchor=S)
        Button(self.master, text='Print', command=self.Print,
	       bg='blue', fg='yellow').place(relx=0.72, rely=0.99, anchor=S)
        self.frame.pack()
        
    def Print(self):
	if os.name == 'posix':
        	SH = initSH()
		printImage(self.fname,1,printer=SH['printer'])
	else:
		str = 'start '+ self.fname +' &'
		os.system(str)

    def printer(self):
	root = self.master
 	dialog = setupPrinter(root)	

    def pickfile(self):
        fname = askopenfilename(initialdir='',
		title='Pick Picture File...',
                filetypes=[("JPEG", '.jpg'),
                ("PNG",".png"),
                ("GIF",".gif"),
                ("All Files","*")])
        if fname == '':
                return
	self.fname = fname
	(self.path, self.fn) = os.path.split(fname)
	self.getImg(fname)

    def getImg(self, fname):
        if self.infoDisplayed:
	    self.fm.destroy()
	    self.infoDisplayed = FALSE
        self.masterImg = Image.open(fname)
	(W,H) = self.masterImg.size
 	if H > (self.height-120) or W > self.width:	
        	self.masterImg.thumbnail((self.width, self.height-120))
        self.img = ImageTk.PhotoImage(self.masterImg)
        self.lbl['image'] = self.img
        
    def exit(self):
        self.master.destroy()

    def info(self):
        if self.infoDisplayed:
	    self.fm.destroy()
	    self.infoDisplayed = FALSE
        else:
	    self.fm = Frame(self.master, bg='gray10')
	    self.fm.place(in_=self.lbl, relx=0.5, relwidth=1.0, height=60,
			  anchor=S, rely=0.0, y=-4, bordermode='outside')

	    Label(self.fm,text=self.path,bg='gray10',fg='white',
		font=('verdana', 8)).place(relx=0.0,rely=0.1,anchor=W)
	    Label(self.fm,text='File: '+self.fn,bg='gray10',fg='white',
		font=('verdana', 8)).place(relx=0.3,rely=0.3,anchor=W)
	    ypos = 0.50
	    for lattr in ['Format', 'Size', 'Mode']:
	        Label(self.fm, text='%s:\t%s' % (lattr,
		      getattr(self.masterImg, '%s' % string.lower(lattr))),
		      bg='gray10', fg='white',font=('verdana', 8)).place(\
		      relx=0.3, rely= ypos, anchor=W)
	        ypos = ypos + 0.20
            self.infoDisplayed = TRUE

class setupPrinter(Dialog):
   "setupPrinter(Dialog) - Dialog for setting up printer "
   def body(self,master):
        self.title("Set Printer Dialog")
        self.label = StringVar()
        Label(master, text='Enter Printer Name:').grid(row=1, sticky=W)
        self.label = Entry(master, width = 26 )
        self.label.grid(row=1,column=1)   
	SH = initSH()
        self.label.insert(0,SH['printer'])
	self.SH = SH
        return self.label

   def apply(self):
	print self.label.get()
	self.SH['printer'] = self.label.get()
	writeSH(self.SH)

class tv_plot(AppShell.AppShell):
    usecommandarea = 1
    appname        = '2D Image Data/Picture Displayer'        
    copyright      = 'Copyright BCDA-APS, ANL. All Rights Reserved'
    contactname    = 'Ben-chin Cha'
    contactphone   = '630-252-8653'
    contactemail   = 'cha@aps.anl.gov'
    frameWidth     = 400
    frameHeight    = 480
    fixed 	   = 1 
    
    def addMoremenuBar(self):
	self.menuBar.addmenuitem('File', 'command',
                'Read 2D image data array ...',
                label='Open Ascii Data ...',
                command=self.openAscii)
	self.menuBar.addmenuitem('File','command', '',label='--------------')
	self.menuBar.addmenuitem('File', 'command',
                'View JPEG/PNG/GIF/PPM image files',
                label='Picture Files ...',
                command=self.runSB)
	self.menuBar.addmenuitem('File','command', '',label='--------------')
	self.menuBar.addmenuitem('File', 'command',
                'Print tv image',
                label='Print',
                command=self.Print)
	self.menuBar.addmenuitem('File', 'command',
                'Dialot to setup printer',
                label='Printer...',
                command=self.Printer)
	self.menuBar.addmenuitem('File','command', '',label='--------------')
	self.menuBar.addmenuitem('File', 'command',
                'Close tv displayer',
                label='Close',
                command=self.root.destroy)
	self.menuBar.addmenuitem('Setup', 'command',
                'Display ascii file',
                label='Display picked ascii file',
                command=self.displayFile)
	self.menuBar.addmenuitem('Setup', 'command',
                'Test data indgen([30,20])',
                label='Test indgen([30,20])',
                command=self.testData)
	self.menuBar.addmenuitem('Setup','command', '',label='--------------')
	self.menuBar.addmenuitem('Setup', 'command',
                'Load different Color Table',
                label='Color Table...',
                command=self.changeCT)
	self.menuBar.addmenuitem('Setup','command', '',label='--------------')
	self.menuBar.addmenuitem('Setup', 'command',
                'Transpose image data array',
                label='Transpose Data Array',
                command=self.transposeA)
	self.menuBar.addmenuitem('Setup','command', '',label='--------------')
	self.menuBar.addmenuitem('Setup', 'command',
                'Flip UpsideDown',
                label='Flip Image Upside/Down',
                command=self.flipV)
	self.menuBar.addmenuitem('Setup', 'command',
                'Flip LeftRight',
                label='Flip Image Left/Right',
                command=self.flipH)
	
	self.menuBar.addmenu('ImageOption', 'Various Image Display Option ')
	self.menuBar.addmenuitem('ImageOption', 'command',
                'Plot Image Range',
                label='Set Plot Image Range',
                command=self.setIRange)
	self.menuBar.addmenuitem('ImageOption', 'command',
                'Reset to Default Image Range',
                label='Default Image Range',
                command=self.resetIRange)
	self.menuBar.addmenuitem('ImageOption','command', '',label='--------------')
	self.menuBar.addmenuitem('ImageOption', 'command',
                'Display as Log10 Image',
                label='Log10 Image',
                command=self.log10Image)
	self.menuBar.addmenuitem('ImageOption', 'command',
                'Display as Log Image',
                label='Log Image',
                command=self.logImage)
	self.menuBar.addmenu('3DGraph', '3D multiline  plot Option ')
	self.menuBar.addmenuitem('3DGraph', 'command',
                'Plot multiline as color filled 3D surface plot',
                label='3D Graph...',
                command=self.plot3D)

    def plot3D(self):
	fo = open('3dgraph.config','w')
        fo.write(self.fname)
        fo.close()
	os.system('python 3dgraph.py &')

    def displayFile(self):
        "displayFile(self) - display picked text file"
        from plotAscii import xdisplayfile
        if self.fname != '': xdisplayfile(self.fname)

    def log10Image(self):
	if self.fname == '': return
	from Numeric import log10
	data = self.data
	da = log10(data)
	self.createImage(da)

    def logImage(self):
	if self.fname == '': return
	from Numeric import log
	data = self.data
	da = log(data)
	self.createImage(da)

    def resetIRange(self):
	if self.fname == '': return
	data = readArray(self.fname)
	data = transposeA(data)
	self.H = len(data)
	self.W = len(data[0])
	self.raw_data = data
	self.createImage(data)

    def setIRange(self):
	import Tkinter
	if self.fname == '': return
	data = self.data
	v1,v2 = minmax(data)
	self.vmin = v1
	self.vmax = v2
	top= Toplevel()	
	top.title('Set Image Range')
	self.IRFrame = top
	fm = Frame(top,borderwidth=0)
	self.IRW = [ StringVar(),StringVar()]
	Label(fm,text='Image Range: ').grid(row=0,column=1,sticky=W)
	Label(fm,text='Vmin = '+str(v1)).grid(row=0,column=2,sticky=W)
	Label(fm,text='Vmax = '+str(v2)).grid(row=0,column=3,sticky=W)
	Label(fm,text='Image Display ').grid(row=1,column=1,sticky=W)
	Label(fm,text='Start Value:').grid(row=1,column=2,sticky=W)
	Entry(fm,width=15,textvariable=self.IRW[0]).grid(row=1,column=3,sticky=W)
	Label(fm,text='Image Display ').grid(row=2,column=1,sticky=W)
	Label(fm,text='End Value:').grid(row=2,column=2,sticky=W)
	Entry(fm,width=15,textvariable=self.IRW[1]).grid(row=2,column=3,sticky=W)
	Button(fm,text='Reset',command=self.resetIRange2).grid(row=3,column=1,sticky=W)
	Button(fm,text='Accept',command=self.showIRange).grid(row=3,column=2,sticky=W)
	Button(fm,text='Cancel',command=self.closeIRange).grid(row=3,column=3,sticky=W)
	self.IRW[0].set(str(v1))
	self.IRW[1].set(str(v2))
	fm.pack(fill=BOTH)
	
    def closeIRange(self):
	self.IRFrame.destroy()

    def resetIRange2(self):
	self.IRW[0].set(str(self.vmin))
	self.IRW[1].set(str(self.vmax))
	data = self.raw_data
	self.createImage(data)

    def showIRange(self):
	v1 = string.atof(self.IRW[0].get())
	v2 = string.atof(self.IRW[1].get())
	data = self.raw_data
	if v1 > v2: 
		self.IRW[0].set(v2)
		self.IRW[1].set(v1)
		da = dataRange(data,v2,v1)
	else:
		da = dataRange(data,v1,v2)
	self.createImage(da)
	self.data = data

    def runSB(self):
	top = Tkinter.Toplevel()
	top.title('Picture Browser')
	sb = Scrapbook(top)

    def changeCT(self):
	entry = pickCT(self.interior())
	chosenCT(entry)
        try:
	  self.colorbar.destroy()
        except AttributeError:
	  pass
	root = Tkinter.Toplevel()
	fm = drawCT(root,title=entry)
	self.colorbar = root 
	self.refresh()

    def Printer(self):
	root = self.root
	dialog = setupPrinter(root)

    def Print(self):
        "for python2.3 on unix it only works for png,jpg not for gif"
	from plotAscii import readSH
	print self.im.mode
	SH = readSH()
	printer = SH['printer']
	fn = 'out.png'
	im = self.im
	im.save(fn)
	if os.name == 'posix':
	  if printer != '':
	    str="pilprint.py -c -p -P %s %s" % (printer,fn)
	  else:
	    str="pilprint.py -c -p %s" % fn
	else:
	  if printer != '':
	    str="python pilprint.py -c -p -P %s %s" % (printer, fn)
	  else:
	    str = "python pilprint.py -c -p %s" % fn
	print str
	os.system(str)


    def save(self):
        self.save = TRUE
	fn = self.oname.get()
        im = self.im
	im.save(fn)

    def close(self):
        self.quit()

    def transposeA(self):
	if self.fname == '': return
	data = self.data
	data = transposeA(data)
        self.createImage(data)

    def refresh(self):
	if self.fname == '': return
	data = self.data
	self.createImage(data)

    def flipV(self):
	if self.fname == '': return
	im = self.im
	self.im = flipVImage(im)
        self.im.save("out.ppm")
        self.img = PhotoImage(file="out.ppm")
        self.label['image'] = self.img

    def flipH(self):
	if self.fname == '': return
	im = self.im
	self.im = flipHImage(im)
        self.im.save("out.ppm")
        self.img = PhotoImage(file="out.ppm")
        self.label['image'] = self.img

    def fixedSize(self):
	if self.fname == '': return
	if self.fixed == 0:
	  im = self.im_raw
	  self.im = im.resize((300,300))
	  self.fixed = 1
	else:
	  im = self.im
	  self.im = self.im_raw
	  self.fixed = 0
        self.im.save("out.ppm")
        self.img = PhotoImage(file="out.ppm")
        self.label['image'] = self.img

    def testData(self):
        data = indgen([30,20])
	self.H = 20
	self.W = 30
        self.createImage(data)


    def openAscii(self):
        fname = askopenfilename(initialdir='',
                filetypes=[("ASCII Data", '.txt'),
                ("Image Files","*im*"),
                ("Data Files",".dat"),
                ("All Files","*")])
        if fname == '':
                return
        self.fname = fname
	self.displayImage()

    def displayImage(self):
	data = readArray(self.fname)
	data = transposeA(data)
	self.H = len(data)
	self.W = len(data[0])
	self.raw_data = data
	self.createImage(data)


    def createButtons(self):
        self.buttonAdd('Save Image',
              helpMessage='Save current image',
              statusMessage='Write current image in Save As',
              command=self.save)
        self.buttonAdd('Close',
              helpMessage='Close Screen',
              statusMessage='Exit',
               command=self.root.destroy)
        
    def createDisplay(self):
        self.width  = self.root.winfo_width()-10
        self.height = self.root.winfo_height()-95
        self.form = self.createcomponent('form', (), None,
                                         Frame, (self.interior(),),
                                         width=self.width,
                                         height=self.height)
        self.form.pack(side=TOP, expand=YES, fill=BOTH)
        self.im = Image.new("P", (self.width, self.height), 0)
        self.label = self.createcomponent('label', (), None,
                                           Label, (self.form,),)
        self.label.pack(padx=30,pady=30)
        
    def initData(self):
	ct = readCT()
        self.save        = FALSE
	self.fname = ''
	if os.path.isfile('3dgraph.config'):
		f = open('3dgraph.config','r')
		self.fname = f.read()	
		f.close
        
    def createImage(self,data):
	self.data = data
        self.updateProgress(0, self.height)
        self.updateProgress(.5*self.height)
	im = display2D(data)
	self.im_raw = im
	self.im = im 
        self.updateProgress(self.height, self.height)
	if self.fixed : 
		self.im = self.im_raw.resize((300,300))
        self.im.save("out.ppm")
        self.img = PhotoImage(file="out.ppm")
        self.label['image'] = self.img
#	self.label['text'] = Label(self.form,text='text').pack()
	self.label.bind('<Button-1>',self.reportEvent)

    def reportEvent(self,event):
#	print event.x,event.y,event.type,event.widget
	px = 300/self.W
	py = 300/self.H
	ix = event.x /px
	iy = event.y /py
	data = self.raw_data
	xa = data[iy]
	da = transpose(data)
	ya = da[ix]	
	lineplot(xa,title='X profile @ y Index='+str(iy))
	lineplot(ya,title='Y profile @ x Index='+str(ix))

 
    def createInterface(self):
        AppShell.AppShell.createInterface(self)
	self.addMoremenuBar()
        self.createButtons()
        self.initData()
        self.createDisplay()
	Label(self.interior(),text='Save As:').pack(side=LEFT)
	self.oname=StringVar()
	Entry(self.interior(),width=20,textvariable=self.oname).pack(side=LEFT,fill='x')
	self.oname.set('1.png')
	Checkbutton(self.interior(),text='Raw Data',state=NORMAL,anchor=W,
		command=self.fixedSize).pack(side=LEFT)
	if os.path.isfile(self.fname):
		self.displayImage()

def pickCT(frame):
	"pickCT(frame) - dialog to select desired CT from list" 
	dname=('0 B-W LINEAR','1 BLUE/WHITE','2 GRN-RED-BLU-WHT',
	'3 RED TEMPERATURE','4 BLUE/GREEN/RED/YELLOW','5 STD GAMMA-II',
	'6 PRISM','7 RED-PURPLE','8 GREEN/WHITE LINEAR',
	'9 GRN/WHT EXPONENTIAL','10 GREEN-PINK','11 BLUE-RED',
	'12 16-LEVEL','13 RAINBOW','14 STEPS',
	'15 STERN SPECIAL','16 Haze','17 Blue-Pastel-Red',
	'18 Pastels','19 Hue Sat Lightness1','20  Hue Sat Lightness2',
	'21 Hue Sat Value 1','22 Hue Sat Value 2','23 Purple-Red + Stripes',
	'24 Beach','25 Mac Style','26 Eos A',
	'27 Eos B','28 Hardcandy','29 Nature',
	'30 Ocean','31 Peppermint','32 Plasma',
	'33 Blue-Red','34 Rainbow',
	'35 Blue Waves','36 Volcano','37 Waves',
	'38 Rainbow18','39 Rainbow + white','40 Rainbow + black')
        dialog = Pmw.ComboBoxDialog(frame,
		buttons=('OK','Cancel'), defaultbutton='OK',
                title='Change Color Table Dialog',
		combobox_labelpos=N, label_text='Pick color table',
                scrolledlist_items=dname,listbox_width=40)
	dialog.tkraise()
	result = dialog.activate()		
	return dialog.get()

    
def chosenCT(entry):
	"chosenCT(entry) - extract selected index and save CT[i] in pal.dat"
	sels = string.split(entry)
	CT_id = string.atoi(sels[0])
        CT = readCT()
	ps = str(CT[CT_id])
	fo = open('pal.dat','wb')
	fo.write(ps)
	fo.close()

def drawCT(root,title='Current ColorTable'):
     "drawCT(root,title='Current ColorTable') - window to display the current CT "
     root.title(title)
     frame = Canvas(root)
     l1 = range(256)
     da = []
     for i in range(10):
	da.append(l1)
     da = array(da)
     im = PNGImage1(frame,da)
     im.pack(side=LEFT,padx=10,pady=10)
     frame.pack(expand=1,fill='both')
     return frame

def tv(data=None,vmin=None,vmax=None):
    "tv(data) - display 2D data as image"
    v = tv_plot()
    if data != None and vmin == None:
	v.W = len(data[0])
	v.H = len(data)
	v.createImage(data)
    else:
	v2,v1 = minmax(data)
	if vmin < v1: vmin=v1
	if vmax > v2: vmax=v2
	v.W = len(data[0])
	v.H = len(data)
	data = dataRange(data,vmin,vmax)
	v.createImage(data)
	return v

def dataRange(data,vmin,vmax):
	W = len(data[0])
	H = len(data)
	data = array(data)
	da = clip(data,vmin,vmax)	
	return da

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

def testTV(w,h):
    "testTV(w,h) - generate a indgen([w,h]) sequence list and display as image"
    if h > 1:
	data = indgen([w,h])
	v = tv_plot()
	v.W = len(data[0])
	v.H = len(data)
	v.createImage(data)
        
def SB():
    "SB() - pictures browser by using Scrapbook class"
    root = Tk()
    root.option_add('*font', ('verdana', 10, 'bold'))
    root.title('Picture Browser')
    scrapbook = Scrapbook(root)

if __name__ == '__main__':
    v = tv_plot()
    v.run()



