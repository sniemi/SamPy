"""This module consists of a set of easy to use image process routines
developed
   based on the PIL python image library routines.

__author__ = "Ben-chin Cha <cha@aps.anl.gov>"
__date__ = "August 2005"
__version__ = "$Revision: 1.0 $"
__credits__ = "PIL Python Image Libary"

"""

import os, sys, string
from Numeric import *
import Image, ImagePalette
import ImageDraw, ImageFont
from xdrlib import *

def grabImage():
    "print screen for WIN system"
    import ImageGrab
    im = ImageGrab.grab()
    if isinstance(im, Image.Image):
	 im.show()
	 fn = 'tmp.png'
	 im.save(fn)
	 saveImageFile(fn,'tmp.jpg')
	 pilDriver('tmp.jpg',0)

def updown(data):
	"updown(data) - return the new upside down data list"
        nr = len(data)
        nc = len(data[0])
	da = []
	for i in range(nr):
		ls = data[nr-1-i]
		da.append(ls)
	return da

def rowreverse(data):
        "rowreverse(data) - return the new list by reversing the row order of input list "
        nr = len(data)
        nc = len(data[0])
        da = indgen([nr,nc])
        for i in range(nc):
            for j in range(nr):
                da[i][j] = data[j][i]
        return da

def preprocess(image):
    "preprocess(image) - scaled image data array to (0-255) values"
    assert len(image.shape) in (1, 2) or \
           len(image.shape) == 3 and image.shape[2] == 3, \
           "image not in correct format"
    themin = float(minimum.reduce(ravel(image)))
    themax = float(maximum.reduce(ravel(image)))
    if image.typecode() != 'b':
        denom = themax-themin
        if (denom < 1.e-6): denom = 1
        image = 255 * (image - themin) / denom
        image = image.astype('b')
    return image


def pilDriver(file,unix):
     "pilDriver(file,unix) - show the image file as a 100x100 thumbnail image"
     if unix == 1:
	str = "python /opt/local/bin/pildriver.py show thumbnail 200 200 open %s" % file 
     else:
	str = "pildriver.py show thumbnail 200 200 open %s" % file 
     print str
     os.system(str + ' &')

def loadPalette(file=file):
    "loadPalette(file=file) - return palette list from a palette file"
    p = readPalette(file=file)
    return p

def readCT(id=39):
	"""readCT(id=39) - Read 41 color tables from master palette file CT.dat,
	   and save ranbow + white (39 th) to palette file 'pal.dat' 
	   id - keyword override the default 39 color table saved in 'pal.dat'
	   return the complete list of 41 color table ct[756,41] 
	   The complete set of CT.dat was ported from IDL program. 
	"""
	fn = os.environ['PYTHONSTARTUP']+os.sep+'CT.dat'
        file = open(fn,'rb')
        file.seek(0,2)
        fsize = file.tell()
        file.seek(0)
        buf = file.read(fsize)
        file.close()
        u = Unpacker(buf)
        ct = []
        for i in range(41):
            slist=[]
            for j in range(768):
                val = u.unpack_int()
                slist.append(val)
            ct.append(slist)
	if id <0 : id = 0
	if id > 40 : id = 40
	ps = str(ct[id])
	ofile = open('pal.dat','wb')
	ofile.write(ps)
	ofile.close()
        return ct

def indgen(tp):
    "indgen([w,h]) - 1D or 2D index list generator"
# tp list of dim specification
# 1D or 2D index list generation
    np = len(tp)
    if np == 1:
	data = range(tp[0])
    if np == 2:
	data = []
	w,h = tp[0],tp[1]
	for j in range(h):
		jj = j*w*1.
		p = range(w)
		for i in p:
			p[i] = p[i]+jj
		data.append(p)
    if np == 3:
	data = []
	w,h,d = tp[0],tp[1],tp[2]
	for k in range(d):
	    kk = w*h*k
	    d1 = []
	    for j in range(h):
		jj = j*w*1. + kk
		p = range(w)
		for i in p:
			p[i] = p[i]+jj
		d1.append(p)
	    data.append(d1)
    return data

def testData(w,h):
	"testData(w,h) - Test indgen([w,h]) and passed to display2D"
	data = indgen([w,h])
	im = display2D(data,show=1)
	return im

def blackwhite2D(data,xsize=None,ysize=None,show=1):
        """blackwhite2D(data,xsize=None,ysize=None,show=1)) - display list or array data as black white image
	default popup window with (300x300) pixels
	"""
        if type(data) == type([]):
                data = array(data)
	w,h = data.shape[1],data.shape[0]
        d = preprocess(data)
	im = Image.new('L',(w,h))
	for j in range(h):
	   for i in range(w):
		ij = i+j*w
		im.putpixel((i,j),d[j][i])
	if show:
		if xsize == None:
			xsize = 300
		if ysize == None:
			ysize = 300
		resizeImage(im,xsize,ysize)
	return im

def TV(data,xsize=None,ysize=None,pal=None):
	"TV(data,xsize=None,ysize=None,pal=None) - display 2D data list or array as imagewindow"
# data can be 2D list or array
	display2D(data,show=1,xsize=xsize,ysize=ysize,pal=pal)

def display2D(data,show=None,xsize=None,ysize=None,pal=None):
	"""display2D(data,show=None,xsize=None,ysize=None) - create color image object 
	from 2D list or array data, and the color palette is extracted from  'pal.dat', 
	if show=1 specified by default a 300x300 window shows the data image
	xsize, ysize override the default 300 pixel setting
	pal[768] - if specified the color table palette will be used
	"""
	if type(data) == type([]):
		data = array(data)
	w,h = data.shape[1],data.shape[0]
	if pal == None:
	    file = "pal.dat"
	    if os.path.isfile(file) == 0:
		CT = readCT()
	        pal = readPalette()
	pixel = data2pixel(data,p=pal)
	im = Image.new('RGB',(w,h))
	for j in range(h):
	   for i in range(w):
		ij = i+j*w
		im.putpixel((i,j),pixel[ij])
	if show != None:
		if xsize == None:
			xsize = 300
		if ysize == None:
			ysize = 300
		resizeImage(im,xsize,ysize)
	return im

def data2pixel(data,file=None,p=None):
	"""data2pixel(data,file=None,p=None) - convert 2D list or array data to color pixel tripplet list"
	data   - specifies input 2D data array
	file   - specifies the color palette file name, default to pal.dat
	p[768] - list to specifies the color table palette 
	"""
	if type(data) == type([]):
		data = array(data)
	d = preprocess(data) 
	if p == None:
		if file == None: file='pal.dat'
		p = readPalette(file=file)
	if len(p) == 768:
	  pixel=[]
	  for j in range(d.shape[0]):
	    jj = d.shape[1]*j
	    slist =[]
	    for i in range(d.shape[1]):
		id = d[j][i]
		ip = id*3
		dd = (p[ip],p[ip+1],p[ip+2])
	        slist.append(dd)
#		print i,j,id,ip,dd
	    pixel = pixel + slist
	return pixel 

def readPalette(file=''):
	"readPalette(file='') - return palette from palette file, default 'pal.dat'"
	if file == "" :
		file = "pal.dat"
	ifile = open(file,'rb')
	q = ifile.read()
	ifile.close()
	q = string.replace(q,'[',' ')	
	q = string.replace(q,']',' ')	
	q = string.split(q,',')
	print "readPalette len:",len(q)
	p = 3*256*[0] 
	for i in range(0,len(p)):
		p[i] = int(q[i])
#	print p
	return p

def savePalette(im,file=''):
    "savePalette(im,file='') - get image palette from the im object and save in test.pal"
    if im.mode == "P":
	if file == "" :
		file = "test.pal"
	p = im.getpalette()
	print "savePalette lengh: ", len(p)
	ps = str(p)
#	print len(ps)
	ofile = open(file,'wb')
	ofile.write(ps)
	ofile.close()
    else:
	print "Sorry, no palette found!"

def createThumbnails(path,type='jpg'):
    """createThumbnails(path,type='jpg') - under specified path directory find all 
    image files matched the specified file type and create corresponding 128x128
    *.thumb.jpg files. Valid input file type include: 'jpg','png','gif','bpm','ppm' 
    """
    import glob,string
    for infile in glob.glob(path + os.sep + '*.'+type):
        file, ext = os.path.splitext(infile)
	if string.find(file,'.thumb') == -1:
	  print infile
          im = Image.open(infile)
	  if im.mode == 'P':
		im=im.convert("RGB")
          im.thumbnail((128, 128), Image.ANTIALIAS)
          im.save(file + ".thumb.jpg", "JPEG")

def printImage(file,unix=1,printer=''):
     "printImage(file,unix=1) - to send image file to a color printer"
     if unix == 1:
	if printer =='':
	  str = "pilprint.py -c -p %s" % file 
	else:
	  str = "pilprint.py -c -p -P %s %s" % (printer,file)
     else:
	str = 'start '+ file + ' &'
     print str
     os.system(str)

def drawText(im,(x,y),str):
    "drawText(im,(x,y),str)  - draw str on the im object at x,y position"
    ImageFont.load_default()
    draw = ImageDraw.Draw(im)
    draw.text((x,y),str)

def savePNG(im,ofile):
    "savePNG(im,ofile) -  Save im as PNG format in ofile"
    try:
	    im.save(ofile)
    except IOError:
	    print "can not save to file", ofile
	    return
    else:
	    print "saved in:",ofile

def saveImageFile(infile,outfile):
    "saveImageFile(infile,outfile) - Save image infile to a JPEG outfile"

    f, e = os.path.splitext(infile)
    outfile = f +'.jpg'
    if infile != outfile:
        try:
            im = Image.open(infile)
	    im.show()
	    if im.mode == 'P':
		im = im.convert('RGB')
	    im.save(outfile)
        except IOError:
	    print "can not convert to file", outfile
	    return
	else:
	    print infile, outfile

def rollImage(image, delta):
    "rollImage(image, delta) - Roll the image sideways by delta pixels"
    xsize, ysize = image.size
    delta = delta % xsize
    if delta == 0: return image
    part1 = image.crop((0, 0, delta, ysize))
    part2 = image.crop((delta, 0, xsize, ysize))
    image.paste(part2, (0, 0, xsize-delta, ysize))
    image.paste(part1, (xsize-delta, 0, xsize, ysize))
    return image

def flipHImage(image):
    "flipHImage(image) - Flip and return a new image sideway"
    xsize, ysize = image.size
    region = image.crop((0, 0, xsize, ysize)).transpose(Image.FLIP_LEFT_RIGHT)
    image.paste(region,(0,0,xsize,ysize))
    return image

def flipVImage(image):
    "flipVImage(image) - Flip and return a new image upsidedown"
    xsize, ysize = image.size
    region = image.crop((0, 0, xsize, ysize)).transpose(Image.FLIP_TOP_BOTTOM)
    image.paste(region,(0,0,xsize,ysize))
    return image

def rotateImage(image,i):
    "rotateImage(image,i)  - return new image by rotation , 1-90, 2-180,3-270"
    xsize, ysize = image.size
    print i
    if i == 0 :
	return image
    if i == 1: 
        region = image.crop((0, 0, xsize, ysize)).transpose(Image.ROTATE_90)
    if i == 2: 
        region = image.crop((0, 0, xsize, ysize)).transpose(Image.ROTATE_180)
    if i == 3: 
        region = image.crop((0, 0, xsize, ysize)).transpose(Image.ROTATE_270)
    return region

def resizeImage(image,W,H,show=1):
	"resizeImage(image,W,H) - resize and return image with new W,H "
	im = image
	xs, ys = im.size
	im = im.resize((W,H))
	if show: im.show()
	return im

def getPixel(image,x,y):
	"getPixel(image,x,y) - get pixel value at x,y"
	xs,ys = image.size
	if x < 0 or x >= xs :
		return -1
	if y < 0 or y >= ys :
		return -1
	return image.getpixel((x,y))

def getData(image):
	"getData(image) - return image data as a list"
	xs,ys = image.size
	p = image.getdata()
	print p
	print xs,ys,len(p)
	return list(p)

def showPaste(im,image,box):
	"""showPaste(im,image,box) - pasted image on im object at specified box region
	 box: (XL,YL) or (XL,YL,XR,YR)
	"""
	im.paste(image,box)
	im.show()
	
def readImageFile(file):
    "readImageFile(file)  -  file can be any valid image file supported by PIL"
    try:
        im = Image.open(file)
    except IOError:
	print "fail to read!"
	return
    else:
	print im.format, im.size, im.mode
	return im


def showImageInfo(file='',save=0):
	"showImageInfo(file,save=0) - show image info"
	if file == "": return

	im = readImageFile(file)
	drawText(im,(10,10),file)

	print im.info
	print im.getbands()
	print im.getbbox()
	"""list an object"""
# print list(im.getdata())   
	print "image length:", len(im.getdata())
	print "image pixel min,max value", im.getextrema()
	if im.mode == "P" and save ==1 :
		savePalette(im,file='test.pal')
		p = readPalette(file='test.pal')
		print "palette 'test.pal' saved: ",type(p)
		print len(p)

	# show expanded image
	xs, ys = im.size
	resizeImage(im,2*xs, 2*ys)
	# show histogram bin #
	print 'histogram bin #:',len(im.histogram())
	return im


def test(ID='',file=file):
	"""test(ID='',file=file) - test image process functions in this module
	   file - specifies any input image file name
	   ID can be 'printImage','savePNG','rotation','palette','info','data'
	"""
	#file = "images/dive.png"
	#file = "images/castle.gif"
        #file = "images/beach.jpg"
	# check color plot 
	if ID == 'data':
	    im = testData(10,5)
	    savePNG(im,'test.png')

	if ID == 'printImage':
	# win 0 unix 1
	    pilDriver(file,1)
	    printImage(file,1)

	if ID == 'savePNG':
	    im = testData(10,5)
	    savePNG(im,"images/1.png")

	if ID == 'rotation':
	    im = Image.open(file)
	    im = flipVImage(im)
	    im = flipHImage(im)
	    im = rotateImage(im,3)
	    im.show()

	if ID == 'info':
	    if os.path.isfile(file): 
		im = showImageInfo(file)
	
	if ID == 'palette':
	# check palette
            im = Image.open(file)
	    if im.mode == 'P':
	      p = im.getpalette()
	      print p
	      print len(p)
	    else:
	      print "No palette found for this file"


