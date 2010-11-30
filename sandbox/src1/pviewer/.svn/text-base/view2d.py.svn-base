#! /usr/bin/env python

import os
from Tkinter import *
import Tkinter
import Pmw
from readMDA import readMDA
import tempfile
from imageUtil import *
from plotAscii import readSH 


def save_png(im,fname=None):
    "save_png(im,fname=None)  - save image im to a temporary PNG filename"
    if fname == None:
        fname = tempfile.mktemp('.ppm')
    savePNG(im,fname)
    print fname
    return fname

class PNGImage2(Tkinter.Label):
# create PNG image with 60x60 pixels 
    def __init__(self, master, d,pal=None, tmpNm=None):
	im = display2D(d,pal=pal)
	im = im.resize((60,60))
	if tmpNm == None:
		self.image = Tkinter.PhotoImage(file=save_png(im))
	else:
		self.image = Tkinter.PhotoImage(file=save_png(im,tmpNm))
	w, h = self.image.width(), self.image.height()
#	self.image = self.image.zoom(scalex, scaley)
	self.image.configure(width=60, height=60)
        Tkinter.Label.__init__(self, master, image=self.image,
                                   bg="white", bd=0)

class PNGImage1(Tkinter.Label):
# create PNG image without image resize / rescale  
    def __init__(self, master, d):
	im = display2D(d)
        self.image = Tkinter.PhotoImage(file=save_png(im))
        Tkinter.Label.__init__(self, master, image=self.image,
                                   bg="white", bd=0)

class PNGImage(Tkinter.Label):
# create PNG image as widthxheight pixels  
    def __init__(self, master, d, (width, height),fname=None):
	im = display2D(d)
	im = im.resize((width,height))
        self.image = Tkinter.PhotoImage(file=save_png(im,fname=fname))
        Tkinter.Label.__init__(self, master, image=self.image,
                                   bg="white", bd=0)

def det2D(dets, scale=(1,1), columns=10,file=file,pal=None):
    """det2D(dets, scale=(1,1), columns=10,file=file) - 
    # det2D displays the image data in a list of 'class scanDetector', as
    # returned by readMDA() (see readMDA.py)
    #
    # dets:    data to display.  Each element of dets has this structure:
    #              number     number              detector number
    #              fieldName  string              detector name
    #              name       string              detector name
    #              desc       string              detector description
    #              unit       string              detector units
    #              data       2D array of numbers detector data
    #
    # scale:   x,y scale factor to apply to images
    # columns: number of columns.  If 'dets' contains more than 'columns' images,
    #          the images will be arranged in two or more rows.
    """
    top = Tkinter.Toplevel()
    top.title('panimage - det2D')
    Pmw.initialise()
    sf = Pmw.ScrolledFrame(top, labelpos=N, label_text=file,
                usehullsize=1, hull_width=700, hull_height=420)
    sf.pack(fill='both',expand=1)
    data = []
    if type(dets) == type([]):
        for i in range(len(dets)): data.append(array(dets[i].data))
    else:
        data.append(array(dets.data))
        dets = [dets]

    frame =[]
    image = []
    pvname = []
    numb = []
    name = []
    maxlen = 0
    for i in range(len(data)):
        maxlen=max(maxlen, len(dets[i].name))
    for i in range(len(data)):
        da = preprocess(data[i])
        frame.append(Tkinter.Frame(sf.interior()))
	image.append(PNGImage2(frame[i], da, pal=pal, tmpNm='tmp.ppm'))
        image[i].pack(side='top')
	dn = dets[i].fieldName +': '
        numb.append(Tkinter.Label(frame[i], text=dn, width=maxlen))
        numb[i].pack(side='top')
        name.append(Tkinter.Label(frame[i], text=dets[i].name, width=maxlen))
        name[i].pack(side='top')
        frame[i].grid(row=i/columns,column=i%columns, padx=0,pady=5)

def panMDA(file=''):
    	"panMDA(file='') - display all 2D images from an MDA file in a scrolled window"
	if file == '':
		file ='/home/beams/CHA/data/xxx/cha_0001.mda'
	d = readMDA(file)
        pal = readPalette()
	det2D(d[2].d[0:d[2].nd],scale=(2,2),columns=5,file=file,pal=pal)
	return d

def panimage(ima,columns=5):
    "panimage(ima) - display ima in a scrolled window"
    top = Tkinter.Toplevel()
    top.title('panimage ')
    Pmw.initialise()
    sf = Pmw.ScrolledFrame(top, labelpos=N, label_text='Image Array',
                usehullsize=1, hull_width=700, hull_height=420)
    sf.pack(fill='both',expand=1)
    frame=[]
    image=[]
    numb=[]
    vminl=[]
    vmaxl=[]
    nd = len(ima)
    h = len(ima[0])
    w = len(ima[0][0])
    pal = readPalette()
    for i in range(nd):
	im = array(ima[i])
	vmin,vmax = max(max(im)),min(min(im))
        da = preprocess(im)
        frame.append(Tkinter.Frame(sf.interior()))
	image.append(PNGImage2(frame[i], da ,pal=pal,tmpNm='tmp.ppm'))
        image[i].pack(side='top')
	dn = 'Image Array : Seq # '+str(i) +': '
        numb.append(Tkinter.Label(frame[i], text=dn) )
        numb[i].pack(side='top')
	vminl.append(Tkinter.Label(frame[i],text='min:'+str(vmin)))
        vminl[i].pack(side='top')
	vmaxl.append(Tkinter.Label(frame[i],text='max:'+str(vmax)))
        vmaxl[i].pack(side='top')
        frame[i].grid(row=i/columns,column=i%columns, padx=0,pady=5)

def pick2d(d,I,updown=0):
    """pick2d(d,I,updown=0) - pick I'th detector image array from MDA data
structure d
    and pass the data to plot2d routine, default the image is plotted
    in negative Y direction
    """ 
# dets - d[2].d  whole 2D array
# I    - specify the detector number 
    dets = d[2].d
    y = d[1].p[0].data
    px = d[2].p[0].data
    x = px[0]
    data = dets[I].data

    # for aborted 2D scan
    if len(data) < d[1].npts:
	t = d[2].npts*[0.]
	for i in range(d[1].npts)[d[1].curr_pt:d[1].npts]:
		data.append(t)
	
    title = dets[I].fieldName+': '+dets[I].name
    x_str = 'X: '+ d[2].p[0].name+ ': '+ d[2].p[0].desc + ' ('+ d[2].p[0].unit+')'
    y_str = 'Y: '+ d[1].p[0].name + ': '+ d[1].p[0].desc + ' ('+ d[1].p[0].unit+')'
    if type(data) == type([]):
		data = array(data)
    if updown == 0:
    	plot2d(data,x,y,title=title,xtitle=x_str,ytitle=y_str)
    else:
    	plot2dUpdown(data,x,y,title=title,xtitle=x_str,ytitle=y_str)


def plot2dUpdown(data,x,y,title='',xtitle='',ytitle=''):
    """plot2dUpdown(data,x,y,title='',xtitle='',ytitle='') - plot 2D data as an
    upside down color image plot
    	data - specifies the input data
    	x    - specifies the corresponding X axis value
    	y    - specifies the corresponding Y axis value
    	title - specifies the plot title
    	xtitle - specifies the X axis plot title
    	ytitle - specifies the Y axis plot title
    """
    W = data.shape[1]
    H = data.shape[0]
    da = []
    for j in range(H):
		tp = data[H-1-j]
		da.append(tp)
    data = da
    xs,ys = 450,450
    x0,y0 = 80,80
    width,height = 300,300 
    scalex,scaley = (xs-150)/W,(ys-150)/H
    xf,yf = float(xs-150)/W,float(ys-150)/H
    top = Tkinter.Toplevel()
    top.title('plot2d')
    Pmw.initialise()
    sf = Pmw.ScrolledFrame(top, labelpos=N, label_text=title,
                usehullsize=1, hull_width=xs*1.2, hull_height=ys*1.2)
    sf.pack(fill='both',expand=1)
    frame = Canvas(sf.interior())
    frame.create_line(x0,y0+height,x0+width,y0+height,width=2)
    frame.create_line(x0,y0,x0,y0+height,width=2)
    xmax,xmin = max(x),min(x)
    ymax,ymin = max(y),min(y)
    zmax,zmin = max(max(data)),min(min(data))
    dx = xmax-xmin
    dy = ymax-ymin
    if dx == 0.: 
	dx=1.
    if dy == 0.: 
	dy=1.
    frame.create_text(.6*width,10,text=ytitle,anchor=CENTER)
    frame.create_text(.6*width,20,text=xtitle,anchor=CENTER)
    nstep=5
    for j in range(nstep):
	yj = y0 + height - float(j)/(nstep-1)*height
	yjj = ymin + dy*j/(nstep-1)
	frame.create_line(x0-5,yj,x0,yj,width=2)
	frame.create_text(x0-10,yj,text=('%s'% yjj)[0:5],anchor=E)
    for k in range(nstep):
	xj = float(k)/(nstep-1)*width + x0
	xjj = xmin+dx*k/(nstep-1)
	y0l = y0+height
	frame.create_line(xj,y0l,xj,y0l+5,width=2)
	frame.create_text(xj,y0l+25,text=('%s'% xjj)[0:5],anchor=S)
    fname = tempfile.mktemp('.ppm')
    image = PNGImage(frame, data, (width,height),fname=fname)
    image.pack(anchor=NW,padx=x0,pady=y0)
    hh = 2*y0 + height 
    colorbar(frame,xs,hh,zmin,zmax)
    frame.pack()
    Button(top,text='Close',command=top.destroy).pack(side=LEFT)
    Button(top,text='Print Clicked Window',command=lambda f=fname: printWindow(f)).pack(side=RIGHT)
#    Button(top,text='Print',command=grabImage).pack(side=RIGHT)

def grabImage(fname):
	print os.name, fname
	im = Image.open(fname)
	im.save('1.jpg')
	os.system('start '+'1.jpg' + ' &')
#	printImage(fname,0)

def printWindow(fname):
  "printWindow(fname) - use mouse click the drawing area and send the window to PS printer"
  if os.name == 'posix':
    print 'click the window'
    if os.path.isfile('1.gif'):
    	os.system('rm 1.gif')
#    os.system('window2gif > 1.gif')
    os.system('xwd -frame -nobdrs | xwdtopnm | pnmquant 256 | ppmtogif > 1.gif')
    im = Image.open('1.gif')
    if im.mode == 'P':
		im2 = im.convert("RGB")
		im2.save('1.png')
		os.system('mv 1.png 1.gif')
    if os.path.isfile('SH'):
 	SH = readSH()
	if SH['printer'] == '':
	  os.system('pilprint.py -c -p 1.gif')
	else:
	  os.system("pilprint.py -c -p -P "+SH['printer'] +" 1.gif")
    else:
	  os.system('pilprint.py -c -p 1.gif')
  else:
	grabImage(fname)

def plot2d(data,x,y,title='',xtitle='',ytitle=''):
    """plot2d(data,x,y,title='',xtitle='',ytitle='') - plot 2D data as a
    color image plot
    	data - specifies the input data
    	x    - specifies the corresponding X axis value
    	y    - specifies the corresponding Y axis value
    	title - specifies the plot title
    	xtitle - specifies the X axis plot title
    	ytitle - specifies the Y axis plot title
    """
    W = data.shape[1]
    H = data.shape[0]
    xs,ys = 450,450
    x0,y0 = 80,80
    width,height = xs-150,ys-150
    scalex,scaley = (xs-150)/W,(ys-150)/H
    xf,yf = float(xs-150)/W,float(ys-150)/H
    top = Tkinter.Toplevel()
    top.title('plot2d')
    Pmw.initialise()
    sf = Pmw.ScrolledFrame(top, labelpos=N, label_text=title,
                usehullsize=1, hull_width=xs*1.2, hull_height=ys*1.2)
    sf.pack(fill='both',expand=1)
    frame = Canvas(sf.interior())
    frame.create_line(x0,y0,x0+width,y0,width=2)
    frame.create_line(x0,y0,x0,y0+height,width=2)
    xmax,xmin = max(x),min(x)
    ymax,ymin = max(y),min(y)
    zmax,zmin = max(max(data)),min(min(data))
    dx = xmax-xmin
    dy = ymax-ymin
    if dx == 0.: 
	dx=1.
    if dy == 0.: 
	dy=1.
    frame.create_text(.6*width,10,text=ytitle,anchor=CENTER)
    frame.create_text(.6*width,20,text=xtitle,anchor=CENTER)
    nstep=5
    for j in range(nstep):
	yj = float(j)/(nstep-1)*height + y0
	yjj = ymin+dy*j/(nstep-1)
	frame.create_line(x0-5,yj,x0,yj,width=2)
	frame.create_text(x0-10,yj,text=('%s'% yjj)[0:5],anchor=E)
    for k in range(nstep):
	xj = float(k)/(nstep-1)*width + x0
	xjj = xmin+dx*k/(nstep-1)
	frame.create_line(xj,y0,xj,y0-5,width=2)
	frame.create_text(xj,y0-10,text=('%s'% xjj)[0:5],anchor=S)
    fname = tempfile.mktemp('.ppm')
    image = PNGImage(frame, data, (width,height),fname=fname)
    image.pack(anchor=NW,padx=x0,pady=y0)
    hh = 2*y0 + height
    colorbar(frame,xs,hh,zmin,zmax)
    frame.pack()
    Button(top,text='Close',command=top.destroy).pack(side=LEFT)
    Button(top,text='Print Clicked Window',command=lambda f=fname: printWindow(f)).pack(side=RIGHT)
#    Button(top,text='Print',command=grabImage).pack(side=RIGHT)


def colorbar(frame,width,height,zmin,zmax):
    """colorbar(frame,width,height,zmin,zmax - draw a horizontal colorbar
    with 256x10 pixels
	width - specify window width
	height - specify window height
	zmin - specify minimum value for colorbar
	zmax - specify maximum value for colorbar
    """
    W = 256 
    clrbar =[]
    for j in range(10):
	clrbar.append(range(W))
    clrbar = array(clrbar)
    imagebar = PNGImage1(frame,clrbar)
    xl,xr = .5*(width-W),.5*(width+W)
    imagebar.pack(side=LEFT,padx=xl,pady=2)
    np = 5
    dx = float(W)/(np-1)
    dz = float(zmax-zmin)/(np-1)
    y0 = height
    for k in range(np):
	xj = xl + k*dx
	xjj = zmin + k*dz
	frame.create_line(xj,y0+5,xj,y0-5,width=2)
	frame.create_text(xj,y0-10,text=('%s'% xjj)[0:5],anchor=S)

def testplot2d(w,h):
        """testplot2d(w,h) - a simple test routine for checking plot2d 
	it call	indgen([w,h]) then pass data to plot2d directly
	    w - specify width
	    h - specify height
        """
	data = indgen([w,h])
	data = array(data)
	x = range(w)
	y = range(h)
	plot2d(data,x,y)

#from view2d import *
#d = panMDA(file='/home/beams/CHA/data/xxx/cha_0001.mda')
#  d = readMDA('/home/beams/CHA/Yorick/data/2idd_0087.mda')
# pick2d(d,13)

