#!/usr/bin/env python

from readMDA import *
from Tkinter import *
import Pmw
import AppShell
import sys, os
import string
from plotAscii import xdisplayfile,readST

def mdaAscii_all(path):
	"""
	mdaAscii_all(path) - this routine automatically generates 1D/2D ascii reports 
	for all the MDA files detected in the mda data directory specified by path 
	"""
	fn = os.popen('ls '+path+os.sep+'*.mda').readlines()
	fname=[]
	for i in range(len(fn)):
		f = string.split(fn[i],'\n')
		fname.append(f[0])
	fn = fname
	for i in range(len(fn)):
	   if os.path.isfile(fn[i]):
		d = readMDA(fn[i],2)
		print ""
		print "=====>Source: ",fn[i],'( **'+str(d[0]['rank'])+'D Scan** )'
		if d[0]['rank'] == 1: 
			f = mdaAscii_1D(d)
		if d[0]['rank'] >= 2: 
			f = mdaAscii_2D(d)
			f = mdaAscii_1D(d)
	return f

def mdaAscii_IGOR(d):
	"""
	mdaAscii_IGOR(d) - for input specified MDA scan data structure d, this function
	will extract all 2D image arrays and sequentially saved in IGOR ASCII format,
	it returns the output IGOR file name which contains the list of all  2D images saved 

	e.g.
	The 2idd_0004.mda contains 2D array:

		from mdaAscii import *
		d = readMDA("2idd_0004.mda")
		fn = mdaAscii_IGOR(d)
	"""
	if d[0]['rank'] < 2 : return
#	print d[0].keys()
	path,fname = os.path.split(d[0]['filename'])
	froot = string.split(fname,'.mda')
	if os.path.exists('ASCII') == 0 :
		os.mkdir('ASCII')
	dir = os.getcwd()
	ofname = dir+os.sep+'ASCII'+ os.sep + froot[0] + '_IGOR.txt'
#	print ofname

        # number of positioners, detectors
        np = d[2].np
        nd = d[2].nd
        min_column_width = 16
        # make sure there's room for the names, etc.
	ny = d[1].curr_pt
	nx = d[2].npts
        for i in range(np):
		print i, d[2].p[i].name,d[2].p[i].desc,d[2].p[i].unit
	py = d[1].p[0].data
	px = d[2].p[0].data
	px = px[0]
	fo = open(ofname,"w")
	fo.write('IGOR'+'\n')
        for i in range(nd):
		fo.write('X // '+ d[2].d[i].name +'\n')
		fo.write(('Waves/O/D/N='),)
		fo.write(('(%s, ' % nx),)
		fo.write(('%s) ' % ny),)
		fo.write(('%s' % d[2].d[i].fieldName),)
		fo.write(('_%s_mda' % froot[0]),)
		fo.write('\n')

		fo.write('BEGIN\n')
		data = d[2].d[i].data
		for j in range(nx):
		    for k in range(ny):
		       fo.write(('%18.7f' % data[k][j]),)
		    fo.write('\n')
		fo.write('END\n')

		fo.write(('X SetScale/I x '),)
		fo.write(('%s, ' % px[0]),)
		fo.write(('%s, ' % px[nx-1]),)
		fo.write(('%s' % d[2].d[i].fieldName),)
		fo.write(('_%s_mda' % froot[0]),)
		fo.write('\n')
		
		fo.write(('X SetScale/I y '),)
		fo.write(('%s, ' % py[0]),)
		fo.write(('%s, ' % py[ny-1]),)
		fo.write(('%s' % d[2].d[i].fieldName),)
		fo.write(('_%s_mda' % froot[0]),)
		fo.write('\n')
		fo.write('\n')
	fo.close()
	return ofname 



def mdaAscii_2D(d,row=None):
	"""
	mdaAscii_2D(d) - for input specified MDA scan data structure d, this function
	will automatically generate separate 2D ASCII text file for each extract 2D image array,
	it will return the last 2D ASCII text file name created

	e.g.
	The 2idd_0004.mda contains 2D array:

		from mdaAscii import *
		d = readMDA("2idd_0004.mda")
		fn = mdaAscii_2D(d)
	"""
#	print d[0].keys()
	path,fname = os.path.split(d[0]['filename'])
	froot = string.split(fname,'.mda')
	if os.path.exists('ASCII') == 0 :
		os.mkdir('ASCII')
	dir = os.getcwd()
	ofname = dir+os.sep+'ASCII'+ os.sep + froot[0]+'.'

        # number of positioners, detectors
        np = d[2].np
        nd = d[2].nd
	if nd == 0 : return
        min_column_width = 16
        # make sure there's room for the names, etc.
	nx = d[2].curr_pt
	ny = d[1].npts
        for i in range(np):
		print i, d[2].p[i].name,d[2].p[i].desc,d[2].p[i].unit
#		print type(d[2].p[i].data)
	py = d[1].p[0].data
	px = d[2].p[0].data
	px = px[0]
        for i in range(nd):
		imfile = ofname+d[2].d[i].fieldName+'.txt'
	        print imfile
		fo = open(imfile,"w")
		fo.write('# Image from: '+d[0]['filename'] +'\n')
		fo.write('# Detector: '+d[2].d[i].fieldName +', '+
			 d[2].d[i].name+', '+
			 d[2].d[i].desc+', '+
			 d[2].d[i].unit)
		fo.write('\n# dim('+ str(nx)+','+str(ny)+')\n')

		if row != None:	
		  fo.write(('# X:'),)
		  for j in range(nx):
	 	    fo.write( ('%18.7f' % px[j]),)
		  fo.write('\n')
		
		fo.write(('#              (yvalues):'),)
		for j in range(ny):
	 	    fo.write( ('%18.7f' % py[j]),)
		fo.write('\n')

		if row != None:
		  fo.write(('# I:'),)
		  for j in range(nx):
	 	    fo.write( ('%18d' % j),)
		  fo.write('\n')
		  data = d[2].d[i].data
		  for j in range(ny):
		    for k in range(nx):
		         fo.write(('%18.7f' % data[j][k]),)
		    fo.write('\n')
		else:
		  fo.write(('#                   \ (J)'),)
		  for j in range(ny):
	 	    fo.write( ('%18d' % (j+1)),)
		  fo.write(('\n#      (xvalues)    (I) \    '),)
		  fo.write('\n')
		  data = d[2].d[i].data
		  for j in range(nx):
	 	    fo.write( (('%18.7f %6d') % (px[j],(j+1))),)
		    for k in range(ny):
		       if k < d[1].curr_pt:
		         fo.write(('%18.7f' % data[k][j]),)
		       else:
		         fo.write(('%18.7f' % 0.),)
		    fo.write('\n')
		fo.close()
	return imfile


def mdaAscii_1D(d):
	"""
	mdaAscii_1D(d) - for input specified MDA scan data structure d, this function
	will generate 1D ASCII text file for 1D data array detected,
	it returns the 1D ASCII text file name created

	e.g.
	The 2idd_0004.mda contains 1D array: 

		from mdaAscii import *
		d = readMDA("2idd_0004.mda")
		fn = mdaAscii_1D(d)
	"""
	# number of positioners, detectors
	np = d[1].np
	nd = d[1].nd

	min_column_width = 18
	# make sure there's room for the names, etc.
	phead_format = []
	dhead_format = []
	pdata_format = []
	ddata_format = []
	columns = 1
	for i in range(np):
		cw = max(min_column_width, len(d[1].p[i].name)+1)
		cw = max(cw, len(d[1].p[i].desc)+1)
		cw = max(cw, len(d[1].p[i].fieldName)+1)
		phead_format.append("%%-%2ds " % cw)
		pdata_format.append("%%- %2d.8f " % cw)
		columns = columns + cw + 1
	for i in range(nd):
		cw = max(min_column_width, len(d[1].d[i].name)+1)
		cw = max(cw, len(d[1].d[i].desc)+1)
		cw = max(cw, len(d[1].d[i].fieldName)+1)
		dhead_format.append("%%-%2ds " % cw)
		ddata_format.append("%%- %2d.8f " % cw)
		columns = columns + cw + 1
	
	path,fname = os.path.split(d[0]['filename'])
	froot = string.split(fname,'.mda')
	if os.path.exists('ASCII') == 0 :
		os.mkdir('ASCII')
	dir = os.getcwd()
	ofname = dir +os.sep+'ASCII'+ os.sep + froot[0]+'.1d.txt'
	print ofname

	cr = '\n'
	fo = open(ofname,'w')
	for i in d[0].keys():
		if (i != 'sampleEntry'):
			fo.write( "# "+ str(i)+ ' '+ str(d[0][i])+cr)

	fo.write( "#\n# "+ str(d[1])+cr)
	fo.write( "#  scan time: "+ d[1].time+cr)
	sep = "#"*columns
	fo.write( sep+cr)

	# print table head

	fo.write( "# ",)
	for j in range(np):
		fo.write( phead_format[j] % (d[1].p[j].fieldName),)
	for j in range(nd):
		fo.write( dhead_format[j] % (d[1].d[j].fieldName),)
	fo.write(cr)

	fo.write( "# ",)
	for j in range(np):
		fo.write( phead_format[j] % (d[1].p[j].name),)
	for j in range(nd):
		fo.write( dhead_format[j] % (d[1].d[j].name),)
	fo.write(cr)

	fo.write( "# ",)
	for j in range(np):
		fo.write( phead_format[j] % (d[1].p[j].desc),)
	for j in range(nd):
		fo.write( dhead_format[j] % (d[1].d[j].desc),)
	fo.write(cr)

	fo.write( "# ",)
	for j in range(np):
		fo.write( phead_format[j] % (d[1].p[j].unit),)
	for j in range(nd):
		fo.write( dhead_format[j] % (d[1].d[j].unit),)
	fo.write(cr)

	fo.write( sep+cr)

	for i in range(d[1].curr_pt):
		fo.write( "",)
		for j in range(d[1].np):
			fo.write( pdata_format[j] % (d[1].p[j].data[i]),)
		for j in range(d[1].nd):
			fo.write( ddata_format[j] % (d[1].d[j].data[i]),)
		fo.write(cr)
	fo.close()

	return ofname


def mdaAscii_2D1D(d,start=None,stop=None):
    """ 
	mdaAscii_2D1D(d,start=None,stop=None) - for input specified MDA scan data structure d, 
	based on user specified index range this function will generate sequential
	1D ASCII text files extrcated from 2D data array detected in data stucture d,
	it returns the last 1D ASCII text file name created

	where
	  start - specifies the beginning sequence number, default 0 
	  stop  - specifies the ending sequence number, default the last 

	e.g.
	The 2idd_0004.mda contains 2D array:

		from mdaAscii import *
		d = readMDA("2idd_0004.mda")
		fn = mdaAscii_2D1D(d)
    """
    if d[0]['rank'] < 2 : return
	# number of positioners, detectors
    else:
	np = d[2].np
	nd = d[2].nd
	if nd == 0: return

	min_column_width = 18
	# make sure there's room for the names, etc.
	phead_format = []
	dhead_format = []
	pdata_format = []
	ddata_format = []
	columns = 1
	for i in range(np):
		cw = max(min_column_width, len(d[2].p[i].name)+1)
		cw = max(cw, len(d[2].p[i].desc)+1)
		cw = max(cw, len(d[2].p[i].fieldName)+1)
		phead_format.append("%%-%2ds " % cw)
		pdata_format.append("%%- %2d.8f " % cw)
		columns = columns + cw + 1
	for i in range(nd):
		cw = max(min_column_width, len(d[2].d[i].name)+1)
		cw = max(cw, len(d[2].d[i].desc)+1)
		cw = max(cw, len(d[2].d[i].fieldName)+1)
		dhead_format.append("%%-%2ds " % cw)
		ddata_format.append("%%- %2d.8f " % cw)
		columns = columns + cw + 1
	
    if start == None: start=0
    if stop == None: stop = d[1].curr_pt
    for k in range(start,stop):
	path,fname = os.path.split(d[0]['filename'])
	froot = string.split(fname,'.mda')
	if os.path.exists('ASCII') == 0 :
		os.mkdir('ASCII')
	dir = os.getcwd()
	ofname = dir +os.sep+'ASCII'+ os.sep + froot[0]+'.1d_'+str(k+1)+'.txt'
	print ofname

	cr = '\n'
	fo = open(ofname,'w')
	for i in d[0].keys():
		if (i != 'sampleEntry'):
			fo.write( "# "+ str(i)+ ' '+ str(d[0][i])+cr)

	fo.write( "#\n# "+ str(d[2])+cr)
	fo.write( "# 2D SCAN (zero based) Line Sequence # ="+str(k) + cr)
	fo.write( "#  scan time: "+ d[2].time+cr)
	sep = "#"*columns
	fo.write( sep+cr)

	# print table head

	fo.write( "# ",)
	for j in range(np):
		fo.write( phead_format[j] % (d[2].p[j].fieldName),)
	for j in range(nd):
		fo.write( dhead_format[j] % (d[2].d[j].fieldName),)
	fo.write(cr)

	fo.write( "# ",)
	for j in range(np):
		fo.write( phead_format[j] % (d[2].p[j].name),)
	for j in range(nd):
		fo.write( dhead_format[j] % (d[2].d[j].name),)
	fo.write(cr)

	fo.write( "# ",)
	for j in range(np):
		fo.write( phead_format[j] % (d[2].p[j].desc),)
	for j in range(nd):
		fo.write( dhead_format[j] % (d[2].d[j].desc),)
	fo.write(cr)

	fo.write( "# ",)
	for j in range(np):
		fo.write( phead_format[j] % (d[2].p[j].unit),)
	for j in range(nd):
		fo.write( dhead_format[j] % (d[2].d[j].unit),)
	fo.write(cr)

	fo.write( sep+cr)

	for i in range(d[2].curr_pt):
		fo.write( "",)
		for j in range(d[2].np):
			fo.write( pdata_format[j] % (d[2].p[j].data[k][i]),)
		for j in range(d[2].nd):
			fo.write( ddata_format[j] % (d[2].d[j].data[k][i]),)
		fo.write(cr)

	fo.close()

    return ofname

def mdaAsciiReport(fname):
	d = readMDA(fname,2)
	dim = d[0]['rank']
	if dim == 1: 
	    if d[1].nd > 0:
		ofname = mdaAscii_1D(d)
	        return ofname
	if dim > 1: 
	    if d[1].nd > 0:
		ofname = mdaAscii_1D(d)
	    if d[2].nd > 0:
		ofname = mdaAscii_2D(d)
	        return ofname

class mdaAscii(AppShell.AppShell):
    usecommandarea  = 1
    appname 	= 'MDA ASCII Report Python Program'
    frameWidth	= 500
    frameHeight	= 250

    def createButtons(self):
	self.buttonAdd('Close',helpMessage='Close program',
	statusMessage='Close and terminate this program',
	command=self.closeup)

    def unimplemented(self):
	pass

    def closeup(self):
	fo = open('mdaAscii.config','w')
        st = [ self.mdapath,self.txtpath]
#       print str(st)
        fo.write(str(st))
        fo.close()
        self.quit()

    def addMoreMenuBar(self):
        self.menuBar.addmenuitem('File','command',
		'Generate ascii reprot for a picked mda file',
		label='Geneate 1D/2D Report file ...',
		command = self.pickmdaRpt)
        self.menuBar.addmenuitem('File','command',
		'Generate 1D report from mda 2D data array ',
		label='Generate 1D report from 2D array...',
		command = self.pickmda2D1D)
        self.menuBar.addmenuitem('File','command',label='------------------')
        self.menuBar.addmenuitem('File','command',
		'Generate IGOR report for a picked 2D/3D mda file',
		label='Generate 2D report for IGOR...',
		command = self.pickmdaIGOR)
        self.menuBar.addmenuitem('File','command',label='------------------')
        self.menuBar.addmenuitem('File','command',
		'Generate all reports for every mda file found in mda data directory',
		label='Generate report for All mda file ...',
		command = self.pickmdaALL)
        self.menuBar.addmenuitem('File','command',label='------------------')
	self.menuBar.addmenuitem('File','command','Quit the application',
		label='Quit',
		command= self.closeup)

	self.menuBar.addmenu('ASCII','ASCII menu')
        self.menuBar.addmenuitem('ASCII','command','View text file ',
		label='View Ascii File ...',
		command = self.viewAscii)
        self.menuBar.addmenuitem('ASCII','command',label='------------------')
        self.menuBar.addmenuitem('ASCII','command','Remove all text file ',
		label='Remove All Ascii File',
		command = self.removeAscii)

    def pickmdaIGOR(self):
	fname = tkFileDialog.askopenfilename(initialdir=self.mdapath,
		initialfile='*.mda')
	if fname ==(): return
	(self.mdapath, fn) = os.path.split(fname)
	d = readMDA(fname,2)
	dim = d[0]['rank']
	if dim < 2: return
	st='Generating IGOR report for picked file : \n'
	self.txtWid.settext(st+fname)
  	ofname = mdaAscii_IGOR(d)
	(self.txtpath, fn) = os.path.split(ofname)
	xdisplayfile(ofname)

    def pickmdaALL(self):
	fname = tkFileDialog.askopenfilename(initialdir=self.mdapath,
		initialfile='*.mda')
	if fname ==(): return
	(self.mdapath, fn) = os.path.split(fname)
	st='Generating all ascii reports for picked directory : \n'
	self.txtWid.settext(st+self.mdapath)
	ofname = mdaAscii_all(self.mdapath)
	(self.txtpath, fn) = os.path.split(ofname)
	xdisplayfile(ofname)

    def pickmda2D1D(self):
	fname = tkFileDialog.askopenfilename(initialdir=self.mdapath,
		initialfile='*.mda')
	if fname ==(): return
	st='Generating 2D->1D ascii report for picked file : \n'
	self.txtWid.settext(st+fname)
	(self.mdapath, fn) = os.path.split(fname)
	d = readMDA(fname,2)
	dim = d[0]['rank']
	if dim < 2: return
  	ofname = mdaAscii_2D1D(d)
	(self.txtpath, fn) = os.path.split(ofname)
	xdisplayfile(ofname)

    def pickmdaRpt(self):
	fname = tkFileDialog.askopenfilename(initialdir=self.mdapath,
		initialfile='*.mda')
	if fname ==(): return
	st='Generating ascii report for picked file : \n'
	self.txtWid.settext(st+fname)
	(self.mdapath, fn) = os.path.split(fname)
  	ofname = mdaAsciiReport(fname)
	(self.txtpath, fn) = os.path.split(ofname)
	xdisplayfile(ofname)

    def viewAscii(self):
	fname = tkFileDialog.askopenfilename(initialdir=self.txtpath,
		initialfile='*txt*')
	if fname ==(): return
	xdisplayfile(fname)

    def removeAscii(self):
        from Dialog import *
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

    def startup(self):
      if os.path.isfile('mdaAscii.config'):
        lines = readST('mdaAscii.config')
        self.mdapath = lines[0]
        self.txtpath = lines[1]
        print 'self.mdapath=', self.mdapath
        print 'self.txtpath=', self.txtpath
      else:
        self.mdapath = os.curdir
        self.txtpath = os.curdir + os.sep +'ASCII'

    def textRegion(self):
	txtWid = Pmw.ScrolledText(self.interior(),borderframe=1,labelpos=N,
		label_text='',usehullsize=1,
		hull_width=500,hull_height=150,
		text_padx=10,text_pady=10,
		text_wrap='none')
	st = 'MDA path= '+self.mdapath+'\n'+ 'TXT path= '+self.txtpath
	txtWid.settext(st)
	txtWid.pack(fill=BOTH,expand=1,padx=5,pady=5)
	self.txtWid = txtWid

    def createInterface(self):
	AppShell.AppShell.createInterface(self)
	self.createButtons()
	self.addMoreMenuBar()
	self.startup()
	self.textRegion()

if __name__ == '__main__':
	ascii = mdaAscii()
	ascii.run()

