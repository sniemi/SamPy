#!/usr/bin/env python
"""This python program reads any ASCII text file and allows user flexiblly
re-configure the multi-line plot. By default only the first 2 data columns
form the input file will be plotted. 

#Usage:   plotAscii.py   [ <file>  <ix>  ]

where  file - optional ascii data file
	ix  - optional input specifies the column of x vaules
	      ix = 0 first column contains x vector values, defualt
	      ix = -1 no x vector in text file
	      ix = 1 second column contains x vector values
 	      remaining columns contains the data vectors

__author__ = "Ben-chin Cha <cha@aps.anl.gov>"
__date__ = "August 2005"
__version__ = "Version: 1.0"

"""

from tkSimpleDialog import Dialog
from tkFileDialog import askopenfilename
from graph import *
import string, math
import os
import sys
import Pmw

global DD,legVar

def writeSH(SH):
	"writeSH(SH) - write shared dictionary SH to file 'SH'"
        fo = open('SH','w')
        fo.write(str(SH))
        fo.close()

def readSH():
	"readSH() - return shared SH dictionary from the file 'SH'"
	fo = open('SH')
	st = fo.read()
	fo.close()
	code = 'SH = ' + st
	exec code
	SH['ix'] = string.atoi(str(SH['ix']))
	return SH

def initSH():
	if os.path.isfile('SH'):
		SH = readSH()
	else:
		SH = { 'ix':0, 'printer':'', 'font':'Verdana 10 bold'}
		writeSH(SH)
	return SH

def readPTS(file=''):
	"readPTS() - read scattering multi-line X,Y row vectors from 'pts.txt' file"
	if file == '': file = 'pts.txt'
        fo = open(file,'r')
        lines = fo.read()
	fo.close()
        lines = string.split(lines,'\n')
        data = []
        for i in range(len(lines)):
                st = lines[i]
                if len(st) > 1:
		   if (st[0] != ';') & (st[0] != '#'):
                      st = string.split(st)
                      data.append(st)

        nr = len(data)/2
	pts = []
        for j in range(nr):
        	nc = len(data[j*2])
		list = []
                for i in range(nc):
			x = string.atof(data[j*2][i])
                        y = string.atof(data[j*2+1][i])
			list.append((x,y))
		pts.append(list)
	return pts

def writePTS(pts,file=''):
	"writePTS(pts,file='') - write scattering pts array as X,Y row vectors to 'pts.txt' file"
	if file =='': file = 'pts.txt'
	nl = len(pts)
	fo = open(file,'w')
	for i in range(nl):
	    fo.write("# line "+ str(i+1) +"\n")
	    npts = len(pts[i])
	    vec = pts[i]
	    vec = transposeA(vec)
	    x = vec[0]	
	    y = vec[1]	
	    for j in range(npts):
	        fo.write(('%18.7f' % x[j]),)
	    fo.write('\n')
	    for j in range(npts):
	        fo.write(('%18.7f' % y[j]),)
	    fo.write('\n')
	fo.close()
	return file

def readST(file):
	"readST(file) - read python string list from a file"
        fd = open(file,'r')
        pick = fd.read()
        fd.close()
        pick=string.replace(pick,'[','')
        pick=string.replace(pick,']','')
        pick=string.replace(pick,"'","")
        pick=string.replace(pick," ","")
        pick=string.split(pick,',')
        return pick

def loadpvs():
	file = 'pvs'
	if os.path.isfile(file):
		V = readST(file)
	else:
		V = []
		for i in range(85):
			V.append('D'+str(i+1))
	return V

class setupPrinter(Dialog):
   "Dialog for setting up printer "
   def body(self,master):
        self.title("Set Printer Dialog")
	self.label = StringVar()
        Label(master, text='Enter Printer Name:').grid(row=1, sticky=W)
        self.label = Entry(master, width = 26 )
	self.label.grid(row=1,column=1)   
	self.label.insert(0,DD['printer'])
	return self.label

   def apply(self):
	DD['printer'] = self.label.get()

class setupXrangeIndex(Dialog):
   "setupXrangeIndex(Dialog) - Dialog for setting up Xrange Index for plot"
   def body(self,master):

      nr = DD['nr']
      fm = master
      self.title("Set Xrange Index Dialog")
      Label(fm,font=DD['font'],text='Select Range of Data Index to be Plotted ').pack(side=TOP)
      Label(fm,font=DD['font'],text='(Default Begin:0, End:'+str(nr-1)+')\n').pack(side=TOP)
      Button(fm,text='Reset',command=resetrange).pack(side=LEFT)
      xrange = DD['xrange']
      sldr1 = Scale(fm,orient=HORIZONTAL,from_=0,to=nr-1,variable=xrange[0],
               label='Begin Index',command=getMinInd)
      sldr2 = Scale(fm,orient=HORIZONTAL,from_=0,to=nr-1,variable=xrange[1],
               label='End Index',command=getMaxInd)
      sldr1.set(xrange[0])
      sldr2.set(xrange[1])
      sldr1.pack(side=LEFT)
      sldr2.pack(side=LEFT)
      DD['Iindex'] = [sldr1,sldr2]
      Button(fm,text='Replot',command=acceptXrange).pack(side=LEFT)
      return sldr1

   def apply(self):
	self.destroy()
	replot()

def resetrange():
	DD['Iindex'][0].set(0)
	DD['Iindex'][1].set(DD['nr']-1)
	DD['xrange'][0] = 0
	DD['xrange'][1] = DD['nr']-1
	replot()

def acceptXrange():
	replot()

def getMinInd(self):
	DD['xrange'][0] = string.atoi(self)

def getMaxInd(self):
	DD['xrange'][1] = string.atoi(self)


class GetLegendPos(Dialog):
    "GetLegendPos(Dialog) - Dialog for setting new legend position on plot"
    def body(self,master):
        self.title("Set Legend location")
        Label(master, font=DD['font'],text='Dialog to Reset Legend').grid(row=0, sticky=W)
        Label(master, font=DD['font'],text='Relative Plot Location').grid(row=0,column=1, sticky=W)

	self.labels =[StringVar(), StringVar()]
        Label(master, text='Legend loc X:').grid(row=1, sticky=W)
        Label(master, text='Legend loc Y:').grid(row=2, sticky=W)

        self.labels[0] = Entry(master, width = 16 )
        self.labels[1] = Entry(master, width = 16 )

        self.labels[0].grid(row=1, column=1, sticky=W)
        self.labels[1].grid(row=2, column=1, sticky=W)

	self.labels[0].insert(0,DD['legX'])
	self.labels[1].insert(0,DD['legY'])

        return self.labels[0]

    def apply(self):
	DD['legX'] = string.atof(self.labels[0].get())
	DD['legY'] = string.atof(self.labels[1].get())
	replot()

class GetLegends(Dialog):
   "Dialog to get and modify legend name for multi-line plot"
   def body(self,master):
      self.title("Define Curve Legends")

      nc = 85
      try:
        V = loadpvs()
      except IOError:
        V =[]
        for i in range(nc):
                st = 'D'+str(i+1)
                V.append(st)
      else:
        pass

      pa = []
      for i in range(nc):
        row = i%20
        col = i/20
	pa_e = StringVar()
	Entry(master, width=21,textvariable=pa_e).grid(row=row,column=col,sticky=W)
	pa_e.set(V[i])
        pa.append(pa_e)
      self.fields = pa
      Label(master,text='Modifiable legends').grid(row=row+1,column=col,sticky=W)
      Label(master,text='used in multi-line plot').grid(row=row+2,column=col,sticky=W)
      Button(master,text='Reset:D01-D70',command=self.reset1).grid(row=21,column=1)
      Button(master,text='Reset:D1-DF,D01-D70',command=self.reset).grid(row=21,column=2)
      Button(master,text='Sequence',command=self.resetseq).grid(row=21,column=3)
#      return pa[0]

   def resetseq(self):
        pa = self.fields
	V = []
        for i in range(85):
	   V.append('D_'+str(i+1))
        for i in range(85):
	   pa[i].set(V[i])
	file='pvs'
	fd = open(file,'w')
	fd.write(str(V))
	fd.close()


   def reset(self):
        pa = self.fields
	V = []
        for i in range(70):
	   V.append('D'+str(i+1))
	V = V[0:9]+['DA','DB','DC','DD','DE','DF','D01','D02','D03','D04','D05','D06','D07','D08','D09']+V[9:70]
        for i in range(85):
	   pa[i].set(V[i])
	file='pvs'
	fd = open(file,'w')
	fd.write(str(V))
	fd.close()

   def reset1(self):
        pa = self.fields
	V = []
        for i in range(70):
	   V.append('D'+str(i+1))
	V = ['D01','D02','D03','D04','D05','D06','D07','D08','D09']+V[9:70]+['','','','','','','','','','','','','','','']
        for i in range(85):
	   pa[i].set(V[i])
	file='pvs'
	fd = open(file,'w')
	fd.write(str(V))
	fd.close()
#	self.destroy()

   def apply(self):
        nc = 85
        pa = self.fields
	st = []
        for i in range(nc):
          st.append(pa[i].get())

	file='pvs'
	fd = open(file,'w')
	fd.write(str(st))
	fd.close()


class GetLabels(Dialog):
    "GetLabels(Dialog) - Dialog for entering plot labels"
    def body(self,master):
        self.title("Enter PLOT Labels")
        
	self.labels =[StringVar(), StringVar(), StringVar()]
        Label(master,font=DD['font'], text='PLOT TITLE:').grid(row=0, sticky=W)
        Label(master,font=DD['font'], text='XTITLE:').grid(row=1, sticky=W)
        Label(master,font=DD['font'], text='YTITLE:').grid(row=2, sticky=W)

        self.labels[0] = Entry(master, width = 46 )
        self.labels[1] = Entry(master, width = 46 )
        self.labels[2] = Entry(master, width = 46 )

        self.labels[0].grid(row=0, column=1, sticky=W)
        self.labels[1].grid(row=1, column=1, sticky=W)
        self.labels[2].grid(row=2, column=1, sticky=W)

	labels=DD['labels']
	self.labels[0].insert(0,labels[0])
	self.labels[1].insert(0,labels[1])
	self.labels[2].insert(0,labels[2])

        return self.labels[0]

    def apply(self):
        labels = [self.labels[0].get(),self.labels[1].get(),self.labels[2].get()]
	DD['labels'] = labels
	replot()

class CB(Frame):
  "CB(Frame) - collection of Checkbuttons for defined curves"
  def __init__(self,nc,master=None):
      	Frame.__init__(self,master,width=700,height=400)
	self.nc = nc
      	self.pack()

  def noneCB(self):
	for i in range(self.nc):
	   self.var[i].set(0)

	self.tot=0
	sel = []
	for i in range(self.nc):
	   sel.append(self.var[i].get())
	   self.tot = self.tot + self.var[i].get()
	self.sel = sel
	DD['sel'] = sel
	graph = self.graph
	self.acceptCB(graph)

  def allCB(self):
	for i in range(self.nc):
	   self.var[i].set(1)

	self.tot=0
	sel = []
	for i in range(self.nc):
	   sel.append(self.var[i].get())
	   self.tot = self.tot + self.var[i].get()
	self.sel = sel
	DD['sel'] = sel
	graph = self.graph
	self.acceptCB(graph)

  def toggleCB(self):
	self.tot = 0
	sel = []
	for i in range(self.nc):
	   sel.append(self.var[i].get())
	   self.tot = self.tot + self.var[i].get()
	self.sel = sel
	DD['sel'] = sel
	graph = self.graph
	self.acceptCB(graph)

  def abortCB(self):
	self.quit()

  def acceptCB(self,graph):
	graph.clear()
	if self.tot > 0:
	   self.updateGraph()

  def updateGraph(self):
    nc = self.nc
    ya = self.ya
    sel = self.sel
    graph = self.graph
    plotSelected(graph,ya,nc,sel)

  def abortCB(self):
	self.quit()

  def acceptCB(self,graph):
	graph.clear()
	if self.tot > 0:
	   self.updateGraph()

  def updateGraph(self):
    nc = self.nc
    ya = self.ya
    sel = self.sel
    graph = self.graph
    plotSelected(graph,ya,nc,sel)



  def createCB(self,nc=16):
	self.nc = nc 
	checkD = []
	var = []
	nm = DD['name']
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
#	print checkD

	self.var = var
	value = []
	for i in range(nc):
          Checkbutton(self,text=checkD[i][0],state=checkD[i][3], anchor=W,
	  command=self.toggleCB,
          variable=var[i]).grid(row=checkD[i][1],column=checkD[i][2],sticky=W)
	  value.append(var[i].get())
	
def toggleLegend():
	if DD['legend']: 
		DD['legend'] = 0
	else:
		DD['legend'] = 1
	nc = DD['nc']
	ya = DD['ya']
	ya = DD['ya']
	sel = DD['sel']
	graph = DD['graph']
	graph.clear()
    	plotSelected(graph,ya,nc,sel)

def CBdialog(root,ya,graph,nc=20):
	"CBdialog(root,ya,graph,nc=20) - create checkbutton dialog"
	test = CB(root)
	test.ya = ya
	test.graph = graph
	test.createCB(nc=nc)
    	Button(root,text='All On',command=test.allCB).pack(side=LEFT)
    	Button(root,text='All Off',command=test.noneCB).pack(side=LEFT)

def extractV(s,iy,ix=1):
    """extractV(s,iy,ix=1) - extract and construct (x,y) pair vector from s array,
       where ix specifies the x column number in s data array, ix < iy
	     iy specifies the y column number in s data array
    """
    nr = len(s)
    nc = len(s[0])
    if iy> nc or iy< 0:
	return None
    V = []
    if ix < 0 or ix >= nc:
      for j in range(nr):
        V.append((1.*j, s[j][iy]))
    else:
      for j in range(nr):
        V.append((s[j][ix], s[j][iy]))
    return V


def readArray(file):
    "readArray(file) - read ASCII file and return a 2D float list"
    try:
        fo = open(file,'r')
        lines = fo.read()
	fo.close()
        lines = string.split(lines,'\n')
        data = []
	nc = 0
        for i in range(len(lines)):
                st = lines[i]
                if len(st) > 1:
		   if (st[0] != ';') & (st[0] != '#'):
                      st = string.split(st)
		      if len(st) > nc : nc = len(st)
                      data.append(st)
	
        nr = len(data)
        for j in range(nr):
                for i in range(nc):
			tmp = string.atof(data[j][i])
                        data[j][i] = tmp
    except IndexError:
	data = -1
    return data

def constructCPtA(data,ix):
  """constructCPtA(data,ix) - extract and construct 2D (x,y) point list
from 2D data list of column vectors
  ix specifies the column of x value resides, treat remaining
  columns as y vectors
  """
  ya = []
  nr = len(data)
  nc = len(data[0])
  for i in range(nc):
     if i != ix: 
	v = extractV(data,i,ix=ix)
	ya.append(v)

  return ya

def plotLegends(graph,width,height):
     "plotLegends(graph,width,height) - draw legend on graph(width,height)"
     afont = DD['font']
     name = DD['name']
     sel = DD['sel']
     colors = DD['color']
     x0 = width *DD['legX']
     y0 = height*DD['legY']
     it = 0
     for i in range(DD['nc']):
	if sel[i] : 
          bb = graph._textBoundingBox(name[i])
	  color = colors[i%10]
	  y = y0+bb[3]*it
	  dy = (bb[3]-bb[1])/2
	  graph.canvas.create_text(x0,y,text=name[i],anchor=W,font=afont)
	  graph.canvas.create_line(x0,y,x0-20,y,width=DD['thick'],
		fill=color)
	  it = it + 1

def plotLabels(graph,width,height):
     "plotLabels(graph,width,height) - draw labels on graph(width,height)"
     afont = DD['font']
     labels  = DD['labels']
     bb = graph._textBoundingBox(labels[0])
     x = width/2 - (bb[2] - bb[0])/2 +10
     y = .05*height
     graph.canvas.create_text(x,y,text=labels[0],anchor=W, font=afont)
 
     bb = graph._textBoundingBox(labels[1])
     x = (width - bb[2] + bb[0])/2 +10
     y = .95*height
     graph.canvas.create_text(x,y,text=labels[1],anchor=W, font=afont)
 
     if os.name == 'nt' or os.name == 'dos':
	user = 'User:'+os.environ['USERNAME']
     else:
	user = 'User:'+os.environ['USER']
     bb = graph._textBoundingBox(user)
     x = width -bb[2]+bb[0]-10
     y = .975*height
     graph.canvas.create_text(x,y,text=user,anchor=W)
 

def plotSelected(graph,ya,nc,sel):
    "plotSelected(graph,ya,nc,sel) - plot only selected curves on graph"
    ip = []
    for i in range(nc):
        if sel[i]:
                ip.append(i)

    nr = DD['nr']
    colors = DD['color']
    lines = []
    for i  in ip:
	i1 = DD['xrange'][0]
	i2 = DD['xrange'][1]
	if i1 > i2: pts = ya[i][i2:i1+1]
	else: pts = ya[i][i1:i2+1]
        line = GraphLine(pts,color=colors[i%10],width=DD['thick'],
		smooth=DD['smooth'])
        lines.append(line)
	
	# symbol on 
	if DD['symon']:
           nr =len(pts)
    	   nr_1 = nr/10
	   if nr_1 < 1: nr_1 = 1
	   pts_1 = []
	   for j in range(0,nr,nr_1): 
		pts_1.append(pts[j])	
	   pts_1.append(pts[nr-1])
   	   sym = GraphSymbols(pts_1,color='black',width=DD['thick'],
		marker='circle',size=1.75,fillcolor=colors[i%10])
	   lines.append(sym)

    graphObject = GraphObjects(lines)

    graph.pack(side=TOP,fill=BOTH,expand=YES)
    graph.draw(graphObject,'automatic','automatic')

    w = string.atoi(graph.canvas.cget('width'))
    h = string.atoi(graph.canvas.cget('height'))
    plotLabels(graph,w,h)
    if DD['legend']:
        plotLegends(graph,w,h)

def xrangeIndexDialog():
	root = DD['root']
	dialog = setupXrangeIndex(root)

def labeldialog():
	root = DD['root']
    	dialog = GetLabels(root)

def datadialog():
	da = DD['data']
        textWin(da)	

def legendposition():
	root = DD['root']
	dialog = GetLegendPos(root)

def setlegends():
	top = Toplevel()
	GetLegends(top)
	st = loadpvs()
	DD['name'] = st
	replot()

def printerDialog():
	root = DD['root']
	dialog = setupPrinter(root)

def convertData():
	data = DD['data']
	da = transposeA(data)
	textWin(da)
	ix = DD['ix']
	st = 'plotAscii.py 1.txt '+str(ix) + ' &'
	print st
	os.system(st)

def replot():
	"replot() - replot graph"
	labels = DD['labels']
        nc = DD['nc']
        ya = DD['ya']
        sel = DD['sel']
        graph = DD['graph']
	graph.clear()
        plotSelected(graph,ya,nc,sel)


def toggleSymbol():
	"toggleSymbol() - toggle symbol on or off"
	if DD['symon']: 
		DD['symon'] = 0
	else:
		DD['symon'] = 1
	replot()
	

	
def textWin(da):
    "textWin(da) - use Pmw.Scrolled text window to display 2D da list"
    file='1.txt'
    nr = len(da)
    pts =  len(da[0])
    fo = open(file,'w')
    fo.write( '# File:1.txt, data (%d,%d)' % (pts,nr))
    fo.write('\n')
    fo.write( '# '),
    for i in range(pts):
	fo.write('%16d  ' % i),
    fo.write('\n')
    for j in range(nr):
	ls =  da[j]
	for i in range(pts):
	     fo.write( ('%18.7f' % ls[i]), )
	fo.write('\n')
    fo.close()
    xdisplayfile(file)

def xdisplayfile(file,title=None):
    root = Tk()
    if title != None: root.title(title)
    else: root.title(file)
    st = Pmw.ScrolledText(root,usehullsize=1,hull_width=600,hull_height=300, 
   		text_wrap='none')
    st.importfile(file)
    st.pack(fill=BOTH, expand=1,padx=5,pady=5) 
    fm = Frame(root)
    Button(fm,text='Print',command=lambda f=file: printtext(f)).pack(side=LEFT,padx=10)
    Button(fm,text='Close',command=root.destroy).pack(side=LEFT,padx=10)
    fm.pack()

def printtext(file):
	os.system('lpr '+file)

def transposeA(data):
    nr = len(data)
    nc = len(data[0])
    da = []
    for j in range(nc):
	ls = []
	for i in range(nr):
	    ls.append(data[i][j])
	da.append(ls)
    return da

def constructRPtA(data,ix=0):
    """constructRPtA(data,ix=0) - extract and construct 2D (x,y) point list from 2D data list if row vectors
	ix - specify the row number where X vector resides, default 0 indicates  the 1st row containing X vector values
    """
    nc = len(data)
    ya=[]
    if ix < 0 or ix >= nc:
      for j in range(nc):
	y = data[j]
	ls = []
    	for i in range(len(y)):
		 ls.append((i,y[i]))
	ya.append(ls)
    else:
      xa = data[ix]
      for j in range(nc):
	if j != ix:
	  y = data[j]
	  ls = []
	  for i in range(len(y)):
		ls.append((xa[i],y[i]))
	  ya.append(ls)
    return ya

def PSprint(graph,printer=''):
        "PSprint() - send graph to PS printer"
        graph.canvas.postscript(file='pyplot.ps')
        
        if os.name == 'nt' or os.name == 'dos':
            if printer == '':
		printer = '\\\\sodium\\funky-chicken'
		st = 'copy pyplot.ps ' + printer 
		print st, os.name
                os.system(st)
            else:
		st = 'copy pyplot.ps ' + printer 
		print st, os.name
                os.system(st)
        else:
            if printer == '':
                os.system('lpr pyplot.ps')
            else:
                os.system('lpr -P '+ printer + ' pyplot.ps')

def sketch1D(da,ix=0,symbol=0):
    """sketch1D(da,ix=0,symbol=0) - draw 2D data list array as simple multi-line plot, 
    data - contain a set of row oriented vector values
    ix - specify the row number of X vector vaules reside in data list
    default ix=0 indicates the 1st row containing X values 
    ix = -1 no X vector defined in data
    symbol - 0 line only, -1 symbol only, > 0 line + symbol every symbol steps 

    e.g.
	from imageUtil import indgen
	from plotAscii import *
	da = indgen([10,5])
	sketch1D(da)
    """
    ya = constructRPtA(da,ix=ix)
    print ix,symbol
    plot1D(ya,symbol)

def plot1D(ya,symbol=0):
    nc = len(ya)
    if nc == 0:  return
   
    colors=['red','orange','green','blue','gray','yellow','magenta','cyan','pink','purple']
    root = Tk()
    lines=[]
    for i in range(nc):
        nr = len(ya[i])
	if symbol != 0:
	   pts = []
	   if symbol > 0 :
	       for k in range(0,nr,symbol): pts.append(ya[i][k])
	   else:
	       for k in range(0,nr,-symbol): pts.append(ya[i][k])
   	   sym = GraphSymbols(pts,color='black',width=2,
		marker='circle',size=1.75,fillcolor=colors[i%10])
	   lines.append(sym)
 	if symbol >= 0:
           lines.append(GraphLine(ya[i][:], color=colors[i%10], smooth=0))

    graphObject = GraphObjects(lines)

    graph  = GraphBase(root, 400, 300, relief=SUNKEN, border=2)
    graph.pack(side=TOP, fill=BOTH, expand=YES)
    graph.draw(graphObject, 'automatic', 'automatic')
    Button(root,text='Clear',  command=graph.clear).pack(side=LEFT)
    Button(root,text='Redraw', command=graph.replot).pack(side=LEFT)
    Button(root,text='Print', command=lambda g=graph,p='': PSprint(g,p)).pack(side=LEFT)
    Button(root,text='Data...',command=lambda f=writePTS(ya): xdisplayfile(f)).pack(side=LEFT)
    Button(root,text='Title...',command=labeldialog).pack(side=LEFT)
    Button(root,text='Quit',   command=root.destroy).pack(side=RIGHT)
    root.mainloop()

def plotInit(data):

    try:
	if os.path.isfile('SH'):
		SH = readSH()
		ix = SH['ix']
		ptr = SH['printer']
		font = SH['font']
	else: 
		ix = 0
		ptr = ''
		font = 'Verdana 10 bold'
        if ix < -1 or ix > 1:
    	    ix = 0 
    except IOError:
	ix = 0

    colors=['red','orange','green','blue','gray','yellow','magenta','cyan','pink','purple']
    symbols = ['circle','square','triangle','triangle_down','cross','plus','dot']
    labels=['Title','X axis label','Y axis_label']

    DD = { 
	 'thick': 2,
 	'smooth': 0,
	'legend': 0,
	'legX': 0.8,
	'legY': 0.2,
	'color': colors,
	'symon': 0,
	'symbol': symbols,
	'labels': labels,
	'Ixvar': None,
	'Iindex': [None,None],
	'ix': ix,
	'printer': ptr,
        'font': font,
	'data': data
	}
    return DD


if __name__ == '__main__':

 if len(sys.argv) < 2:
 	fname = askopenfilename(filetypes=[("ASCII Data", '.txt'),
		("Data Files",".dat"),
		("All Files","*")])
 else:
	fname=sys.argv[1]

 if len(fname) > 0:
    data = readArray(fname)
    if data != -1:
      DD = plotInit(data)
      ix = DD['ix']
      # sys.argv[2] override SH['ix'] value
      if len(sys.argv) == 3:
	ix = string.atoi(sys.argv[2])
      ya = constructCPtA(data,ix)
    else:  # row vector 
	ya = readPTS(fname)
        DD = plotInit(ya)
	ix = -1

    nc = len(ya)
    nr = len(ya[0])
    if data == -1 :
	for i in range(nc):
	    if len(ya[i]) > nr : nr = len(ya[i])

    DD['ix'] = ix
    DD['nc'] = nc 
    DD['nr'] = nr 
    DD['ya'] = ya
    DD['xrange'] = [0,nr-1]

    sel = []
    name = []
    for i in range(nc):
      	sel.append(0)
	name.append('D'+str(i+1))
	if i < 2:
	  sel[i] = 1

    try:
	fr = open('pvs','r')
	fr.close()
	name = readST('pvs')
    except IOError:
	pass

    root = Tk()
    root.title('plotAscii.py')
    DD['root'] = root
    DD['name'] = name  

    fm = Frame(root)
    if data != -1:
      Button(fm,text='Data...',command=datadialog).pack(side=LEFT)
      Button(fm,text='Transpose...',command=convertData).pack(side=LEFT)
    else:
      Button(fm,text='Data...',command=lambda f=fname: xdisplayfile(f)).pack(side=LEFT)
    Button(fm,text='XRange...',command=xrangeIndexDialog).pack(side=LEFT)
    Button(fm,text='Legend...',command=setlegends).pack(side=LEFT)
    Button(fm,text='LegLoc...',command=legendposition).pack(side=LEFT)
    Checkbutton(fm,text='Legend',state=NORMAL,anchor=W,
		command=toggleLegend).pack(side=LEFT)
    Checkbutton(fm,text='Symbol',state=NORMAL,anchor=W,
		command=toggleSymbol).pack(side=LEFT)
    fm.pack(side=TOP)

    graph = GraphBase(root,450,300,relief=SUNKEN,border=2)

    DD['sel'] = sel 
    DD['graph'] = graph

    plotSelected(graph,ya,nc,sel)

    CBdialog(root,ya,graph,nc=nc)
    Button(root,text='Clear',command=graph.clear).pack(side=LEFT)
    Button(root,text='Redraw',command=replot).pack(side=LEFT)
    Button(root,text='Printer...',command=printerDialog).pack(side=LEFT)
    prt = DD['printer'] 
    Button(root,text='Print',command=lambda g=graph,p=prt: PSprint(g,p)).pack(side=LEFT)
    Button(root,text='Title...',command=labeldialog).pack(side=LEFT)
    Button(root,text='Quit',command=root.quit).pack(side=RIGHT)

    root.mainloop()
