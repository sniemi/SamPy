#!/usr/bin/env python

import os
import sys
print "os.environ['PYTHONPATH'] = ", os.environ['PYTHONPATH']
#os.environ['EPICS_CA_ADDR_LIST'] = "164.54.53.99"
#sys.path[:0] = ['../../..']
#print "sys.path = ",  sys.path
import string
import Tkinter
import tkFileDialog
import Pmw
from ca_util import *
from tempfile import *
import time

minBox = 5	# smallest mouse motion considered an attempt to draw a zoom box
prefix = "xxx:"
prefix = "cha:"
scan_name = "scan1"
x_var = "P1"
y_var = ["D01", "D02", "D03", "D04"]
num_vars = 4
new_y = [-1, -2, -3, -4]
new_x = 0
new_cpt = 0
new_arrays = 0
log_min_value = .0001
scan_number = -1
scan_npts = -1
save_path = '?'
symbols = ['square', 'circle', 'diamond', 'triangle']
smooth_options ={'None':'linear', 'Step':'step', 'Natural': 'natural', 'Quadratic': 'quadratic'}
pointSize = "0.125i"
ignore_events = 0
scan_in_progress = 0


detlist = ('X',
"D01", "D02", "D03", "D04", "D05", "D06", "D07", "D08", "D09", "D10",
"D11", "D12", "D13", "D14", "D15", "D16", "D17", "D18", "D19", "D20",
"D21", "D22", "D23", "D24", "D25", "D26", "D27", "D28", "D29", "D30",
"D31", "D32", "D33", "D34", "D35", "D36", "D37", "D38", "D39", "D40",
"D41", "D42", "D43", "D44", "D45", "D46", "D47", "D48", "D49", "D50",
"D51", "D52", "D53", "D54", "D55", "D56", "D57", "D58", "D59", "D60",
"D61", "D62", "D63", "D64", "D65", "D66", "D67", "D68", "D69", "D70",
)
#colorList = Pmw.Color.spectrum(num_vars)
colorList = ['#ff0000', '#ffd000', '#00e070', '#3fa0ff']
dashList = ['', (2, 2), (4, 8), (2, 4, 8, 4)]

# The next two functions are customized functions for making menus.
def myaddmenu(menuBar, owner, label, command):
    menuBar.addmenuitem(owner, 'command', '<help context>', 
                         label = label, command = command)

def mychkmenu(menuBar, owner, label, command):
    menuBar.addmenuitem(owner, 'checkbutton', '<help context>', 
            label = label, command = command, variable = Tkinter.IntVar())


class GraphDemo(Pmw.MegaToplevel):

	def __init__(self, parent=None, **kw):
		global dragging
		dragging = 0

		# Define the megawidget options.
		optiondefs = (('size', 10, Pmw.INITOPT),)
		self.defineoptions(kw, optiondefs)

		# Initialise the base class (after defining the options).
		Pmw.MegaToplevel.__init__(self, parent)

		# Start periodic ca.pend_io calls
		self._periodicCB()

		# Create the graph.
		self.createWidgets()

		# Check keywords and initialise options.
		self.initialiseoptions(GraphDemo)

		self.protocol("WM_DELETE_WINDOW", root.destroy)


	def _newScan(self):
		msg = "scan %d in progress; " % scan_number
		self._vectorSize = 0
		vector_x.__delslice__(0, vector_x.__len__())
		vector_xnum.__delslice__(0, vector_xnum.__len__())
		for i in range(num_vars):
			vector_y[i].__delslice__(0, vector_y[i].__len__())
		self._graph.xaxis_configure(min="", max="")
		self._graph.yaxis_configure(min="", max="")
		self.xScrollbar.set(0, 1)
		self.yScrollbar.set(0, 1)
		msg = msg + '%d/%d points' % (self._vectorSize, scan_npts)
		self._userMessageBar.message('state', msg)

	def _periodicCB(self):
		global new_arrays, ignore_events, scan_in_progress
#		ca.pend_io(.1)
		ca.poll()
		if new_arrays:
			ignore_events=1
			self._getScanArrays()
			self._updatePlot()
			new_arrays = 0
			ignore_events=0

			# If a scan started while we were getting and plotting data,
			# then _DATA_monitorCB() did not get a chance to respond.
			if scan_in_progress:
				print "_periodicCB: scan started while I was plotting"
				self._newScan()

		self.after(100,self._periodicCB)


	def _DATA_monitorCB(self, epics_args, user_args):
		global new_arrays, vector_x, vector_xnum, vector_y, num_vars, scan_number, scan_npts
		global ignore_events, scan_in_progress
		new_arrays = epics_args['pv_value']
		scan_in_progress = 1 - epics_args['pv_value']
		if (ignore_events):
			print "_DATA_CB: ignoring event DATA=", epics_args['pv_value']
			return
		if (scan_in_progress):
			msg = "scan %d in progress; " % scan_number
			self._vectorSize = 0
			vector_x.__delslice__(0, vector_x.__len__())
			vector_xnum.__delslice__(0, vector_xnum.__len__())
			for i in range(num_vars):
				vector_y[i].__delslice__(0, vector_y[i].__len__())
			self._graph.xaxis_configure(min="", max="")
			self._graph.yaxis_configure(min="", max="")
			self.xScrollbar.set(0, 1)
			self.yScrollbar.set(0, 1)
		else:
			msg = "scan %d complete; " % scan_number
		msg = msg + '%d/%d points' % (self._vectorSize, scan_npts)
		self._userMessageBar.message('state', msg)


	def _VAL_monitorCB(self, epics_args, user_args):
		global new_arrays, num_vars, vector_y, new_y, y_var
		global vector_x, vector_xnum, new_x, new_cpt, x_var, scan_number, save_path, scan_npts
		global ignore_events
		if (ignore_events): return
		what = user_args[0]
		if (what == 'VAL'):
			#print 'VAL=', epics_args['pv_value']
			if not new_arrays:
				for i in range(num_vars):
					vector_y[i].append(new_y[i])
				vector_x.append(new_x)
				vector_xnum.append(new_cpt+1) 
		elif (what == y_var[0]):
			new_y[0] = epics_args['pv_value']
		elif (what == y_var[1]):
			new_y[1] = epics_args['pv_value']
		elif (what == y_var[2]):
			new_y[2] = epics_args['pv_value']
		elif (what == y_var[3]):
			new_y[3] = epics_args['pv_value']
		elif (what == x_var):
			new_x = epics_args['pv_value']
		elif (what == 'CPT'):
			new_cpt = epics_args['pv_value']
			self._vectorSize = new_cpt
		elif (what == 'NPTS'):
			scan_npts = epics_args['pv_value']
		elif (what == 'SNUM'):
			scan_number = epics_args['pv_value']
		elif (what == 'SPATH'):
			save_path = epics_args['pv_value']

		if (what == 'CPT' or what == 'SNUM'):
			if new_arrays:
				msg = "scan %d complete; " % scan_number
			else:
				msg = "scan %d in progress; " % scan_number
			msg = msg + '%d/%d points' % (self._vectorSize, scan_npts)
			self._userMessageBar.message('state', msg)


	def createWidgets(self):
		# Create vectors for x and y[i] data points.
		global num_vars, vector_y, vector_x, vector_xnum, prefix, scan_name, x_var, y_var

		self.raw_y = []
		for y in range(num_vars):
			self.raw_y.append(Pmw.Blt.Vector())
			vector_y.append(Pmw.Blt.Vector())
		# get data
		self._getScanArrays()
		for y in range(num_vars):
			for index in range(self._vectorSize):
				vector_y[y].append(self.raw_y[y][index])
		for index in range(self._vectorSize):
			vector_x.append(self.raw_x[index])
			vector_xnum.append(index+1)

		interior = self.interior()
		topFrame = Tkinter.Frame(interior)
		topFrame.pack(side = 'top', fill = 'x', expand = 0)

		# Create and pack the MenuBar.        
		menuBar = Pmw.MenuBar(topFrame, hull_relief = 'raised',
			hull_borderwidth=1)        
#		menuBar.pack(fill = 'x')
		menuBar.pack(side = 'left')

		# Make the File menu
		menuBar.addmenu('File', 'Open, Postscript, Quit')
		myaddmenu(menuBar, 'File', 'Open...', self._openFile)
		myaddmenu(menuBar, 'File', 'SaveAs...', self._saveFile)
		myaddmenu(menuBar, 'File', 'Print graph to color PostScript printer',
			self._print)
		myaddmenu(menuBar, 'File', 'Print graph to B&W PostScript printer',
			self._printBW)
		myaddmenu(menuBar, 'File', 'Save graph as PostScript file',
			self._postscript)
		menuBar.addmenuitem('File', 'separator')
		myaddmenu(menuBar, 'File', 'Quit', root.quit)
   
		# Make the Axis menu                
		menuBar.addmenu('Axis', '')
		menuBar.addmenuitem('Axis', 'checkbutton', '', label='hide', command=self._showAxis, variable=Tkinter.IntVar())
		self.x_is_cpt = Tkinter.BooleanVar()
		menuBar.addmenuitem('Axis', 'checkbutton', '', label='x is point #', command=self._xSetSource, variable=self.x_is_cpt)
		self.xlog = Tkinter.BooleanVar()
		menuBar.addmenuitem('Axis', 'checkbutton', '', label='x log', command=self._xlogScale, variable=self.xlog)
		self.ylog = Tkinter.BooleanVar()
		menuBar.addmenuitem('Axis', 'checkbutton', '', label='y log', command=self._ylogScale, variable=self.ylog)
		menuBar.addmenuitem('Axis', 'checkbutton', '', label='x neg', command=self._x_descending, variable=Tkinter.IntVar())
		menuBar.addmenuitem('Axis', 'checkbutton', '', label='y neg', command=self._y_descending, variable=Tkinter.IntVar())
		self.xlog.set(0)
		self.ylog.set(0)
		self.x_is_cpt.set(0)

		# Make the legend menu
		menuBar.addmenu('Options', '')
		self.show_legend = Tkinter.BooleanVar()
		menuBar.addmenuitem('Options', 'checkbutton', '', label = 'Show Legend',
			command = self._showLegend, variable = self.show_legend)
		self.show_legend.set(1)

		self.plot_lines = Tkinter.BooleanVar()
		menuBar.addmenuitem('Options', 'checkbutton', '', label = 'Plot Lines',
			command = self._setelementtype, variable = self.plot_lines)
		self.plot_lines.set(1)

		self.plot_points = Tkinter.BooleanVar()
		menuBar.addmenuitem('Options', 'checkbutton', '', label = 'Plot Points',
			command = self._setelementtype, variable = self.plot_points)
		self.plot_points.set(0)

		menuBar.addcascademenu('Options', 'Smoothing', '', traverseSpec = 'z')
		self.smoothing = Tkinter.StringVar()
		menuBar.addmenuitem('Smoothing', 'radiobutton', '', label = 'None',
			command = self._setsmoothing, variable = self.smoothing)
		menuBar.addmenuitem('Smoothing', 'radiobutton', '', label = 'Step',
			command = self._setsmoothing, variable = self.smoothing)
		menuBar.addmenuitem('Smoothing', 'radiobutton', '', label = 'Natural',
			command = self._setsmoothing, variable = self.smoothing)
		menuBar.addmenuitem('Smoothing', 'radiobutton', '', label = 'Quadratic',
			command = self._setsmoothing, variable = self.smoothing)
		self.smoothing.set('None')

		bottomFrame = Tkinter.Frame(interior)
		bottomFrame.pack(side = 'bottom', fill = 'x', expand = 0)

		xScrollFrame = Tkinter.Frame(bottomFrame)
		xScrollFrame.pack(side = 'top', fill = 'x', expand = 0)
		self.xScrollbar = Tkinter.Scrollbar(xScrollFrame, orient="horizontal",
			command=self._xScroll)
		self.xScrollbar.pack(side = 'left', fill='x', expand=1)
		self.xScrollbar.set(0, 1)

		leftFrame = Tkinter.Frame(interior)
		leftFrame.pack(side = 'left', fill = 'y', expand = 0)
		self.yScrollbar = Tkinter.Scrollbar(leftFrame, orient="vertical",
			command=self._yScroll)
		self.yScrollbar.pack(side = 'left', fill='y', expand=1)
		self.yScrollbar.set(0, 1)

		controlFrame = Tkinter.Frame(bottomFrame)
		controlFrame.pack(side = 'bottom', fill = 'x', expand = 0)

		self.prefixEntry = Pmw.EntryField(controlFrame,
#			labelpos = 'nw', label_text = "prefix",
			value = prefix,
			entry_width = 5, validate = None,
			command = Pmw.busycallback(self._set_prefix))
		self.prefixEntry.pack(side = 'left')

		self.scan_nameEntry = Pmw.EntryField(controlFrame,
#			labelpos = 'nw', label_text = "scan rec",
			value = "scan1",
			entry_width = 5, validate = None,
			command = Pmw.busycallback(self._set_scan_name))
		self.scan_nameEntry.pack(side = 'left')

		# Make widgets to select which scan detectors are to be plotted
		self.y_var_spec = []
		for v in range(num_vars):
			c = colorList[v]
			self.y_var_spec.append(Pmw.ComboBox(controlFrame,
				#labelpos = 'n', label_text = 'var%1d'%v, label_bg = c,
				entry_bg = c, arrowbutton_bg = c,
				scrolledlist_items = detlist, entry_width=4,
				selectioncommand = Pmw.busycallback(lambda tag, s=self, vv=v: s._setvar(tag, vv))
			))
			self.y_var_spec[v].pack(side = 'left', padx = 5)
			self.y_var_spec[v].selectitem('D0%d'%(v+1))

		# create places for x,y coordinate displays
		self._messagebar_y = Pmw.MessageBar(controlFrame,
			entry_width = 9, entry_relief='groove',
			labelpos = 'w', label_text = 'Y:')
		self._messagebar_y.pack(side = 'right', fill = 'x',
			expand = 0, padx = 0, pady = 0)

		self._messagebar_x = Pmw.MessageBar(controlFrame,
			entry_width = 9, entry_relief='groove',
			labelpos = 'w', label_text = 'X:')
		self._messagebar_x.pack(side = 'right', fill = 'x',
			expand = 0, padx = 10, pady = 0)

		# User message
		self._userMessageBar = Pmw.MessageBar(topFrame,
			entry_width = 30, entry_relief='groove',
			labelpos = 'w', label_text = 'Msg:')
		self._userMessageBar.pack(side = 'left', fill = 'x',
			expand = 1, padx = 0, pady = 0)

		# Create the graph and its elements.
		self._graph = Pmw.Blt.Graph(interior)
		self._graph.pack(expand = 1, fill = 'both')
		self._graph.yaxis_configure(command = self._yaxisCommand)
		self._setelementtype()
		self._graph.legend_configure(hide = not self.show_legend.get())

		self._graph.bind(sequence="<ButtonPress>",   func = self._mouseDown)
		self._graph.bind(sequence="<ButtonRelease>", func = self._mouseUp  )
		self._graph.crosshairs_configure(hide=0, linewidth=1,
			position="@120, 120",color="lightblue")
		self._graph.bind("<Motion>", self._mouseMove)

		# set up monitors on required fields
		self._monitor(prefix, scan_name)

		self.title = "title"
		self._graph.configure(title = self.title)


	def _set_title(self):
		self.title = prefix + scan_name + "." + `scan_number` + " -- "
		t = time.localtime()
		timestring = time.asctime(t)
		#timestring = `t[3]`+':'+`t[4]`+'  '+`t[1]`+'/'+`t[2]`+'/'+`t[0]`
		self.title = self.title + timestring
		self._graph.configure(title = self.title)


	def _set_prefix(self):
		global prefix
		self._unmonitor(prefix, scan_name)
		prefix = self.prefixEntry.get()
		self._monitor(prefix, scan_name)
		self._getScanArrays()
		self._updatePlot(elements=[0,1,2,3], new_x=1, rescale=1)


	def _set_scan_name(self):
		global scan_name
		self._unmonitor(prefix, scan_name)
		scan_name = self.scan_nameEntry.get()
		self._monitor(prefix, scan_name)
		self._getScanArrays()
		self._updatePlot(elements=[0,1,2,3], new_x=1, rescale=1)


	def _unmonitor(self, prefix, scan_name):
		name = prefix + scan_name
		caunmonitor(name+".DATA")
		caunmonitor(name+'.VAL')
		caunmonitor(name+'.CPT')
		caunmonitor(name+'.NPTS')
		caunmonitor(name+'.R'+x_var[1]+'CV')
		for i in range(num_vars):
			caunmonitor(name+'.'+y_var[i]+'CV')
		caunmonitor(prefix+'saveData_scanNumber')
		caunmonitor(prefix+'saveData_fullPathName')


	def _monitor(self, prefix, scan_name):
		name = prefix + scan_name
		try:
			camonitor(name+".DATA", self._DATA_monitorCB, self._userMessageBar)
			camonitor(name+'.VAL', self._VAL_monitorCB, 'VAL')
			camonitor(name+'.CPT', self._VAL_monitorCB, 'CPT')
			camonitor(name+'.NPTS', self._VAL_monitorCB, 'NPTS')
			camonitor(name+'.R'+x_var[1]+'CV', self._VAL_monitorCB, x_var)
			for i in range(num_vars):
				camonitor(name+'.'+y_var[i]+'CV', self._VAL_monitorCB, y_var[i])
			camonitor(prefix+'saveData_scanNumber', self._VAL_monitorCB, 'SNUM')
			camonitor(prefix+'saveData_fullPathName', self._VAL_monitorCB, 'SPATH')
		except CaChannelException:
			# yell, but basically do nothing
			self._userMessageBar.message('systemerror', "Can't monitor scan record")
			i = 0


	def _xScroll(self, *args):
		(gl,gr) = self._graph.xaxis_limits()
		(l,r) = self.xScrollbar.get()
		if (args[0] == 'moveto'):
			dx = string.atof(args[1]) - l
		elif (args[0] == 'scroll'):
			gdx = (gr-gl) * string.atof(args[1])
			if (args[2] == 'units'): gdx = gdx/4
			dx =  gdx * (r-l)/(gr-gl)
		if (r+dx) > 1.0: dx = 1-r
		if (l+dx) < 0: dx = -l
		gdx =  dx * (gr-gl)/(r-l)
		self.xScrollbar.set(l+dx, r+dx)
		self._graph.xaxis_configure(min = gl+gdx, max = gr+gdx)


	def _yScroll(self, *args):
		(gb,gt) = self._graph.yaxis_limits()
		(t,b) = self.yScrollbar.get()
		if (args[0] == 'moveto'):
			dy = string.atof(args[1]) - t
		elif (args[0] == 'scroll'):
			gdy = (gb-gt) * string.atof(args[1])
			if (args[2] == 'units'): gdy = gdy/4
			dy =  gdy * (b-t)/(gb-gt)
		if (b+dy) > 1.0: dy = 1-b
		if (t+dy) < 0: dy = -t
		gdy =  dy * (gb-gt)/(b-t)
		self.yScrollbar.set(t+dy, b+dy)
		self._graph.yaxis_configure(min = gb+gdy, max = gt+gdy)


	# The next functions configure the axes
	def _yaxisCommand(self, graph, value):
		try:
			num = string.atoi(value)
			return '%3d' % num
		except ValueError:
			num = string.atof(value)
			return '%3g' % num


	def _showAxis(self):
		state = int(self._graph.axis_cget("x", 'hide'))
		self._graph.axis_configure(["x", "y"], hide = not state)
    

	def _showLegend(self):
		self._graph.legend_configure(hide = not self.show_legend.get())


	def _xSetSource(self):
		#print self.x_is_cpt.get()
		self._updatePlot(elements=[0,1,2,3], new_x=1, rescale=1)


	def _xlogScale(self):
		self.xlog.set(1-int(self._graph.xaxis_cget('logscale')))
		self._set_xlog()


	def _set_xlog(self):
		global vector_x, vector_xnum, log_min_value
		if self.xlog.get():
			if (self.x_is_cpt.get() and (vector_xnum.min() < log_min_value)):
				self.xlog.set(0)
				self._userMessageBar.message('help', "Can't make X axis log")
			if (not self.x_is_cpt.get() and (vector_x.min() < log_min_value)):
				self.xlog.set(0)
				self._userMessageBar.message('help', "Can't make X axis log")
		self._graph.xaxis_configure(logscale = self.xlog.get())


	def _ylogScale(self):
		self.ylog.set(1-int(self._graph.yaxis_cget('logscale')))
		self._set_ylog()


	def _set_ylog(self):
		global vector_y, log_min_value
		if self.ylog.get():
			for i in range(num_vars):
				if (y_var[i] != 'X') & (vector_y[i].min() < log_min_value):
					self.ylog.set(0)
					self._userMessageBar.message('help', "Can't make Y axis log")
		self._graph.yaxis_configure(logscale = self.ylog.get())


	def _x_descending(self):
		state = int(self._graph.axis_cget("x", 'descending'))
		self._graph.xaxis_configure(descending = not state)


	def _y_descending(self):
		state = int(self._graph.axis_cget("y", 'descending'))
		self._graph.yaxis_configure(descending = not state)


	def _setelementtype(self):
		global num_vars, vector_x, vector_xnum, vector_y
		elements = self._graph.element_names()
		apply(self._graph.element_delete, elements)
		for elem in range(num_vars):
			if (y_var[elem] == 'X'):
				pass
			else:
				foreground = colorList[elem]
				background = Pmw.Color.changebrightness(self, foreground, 0.8)
				sym = ''
				lw = 0
				if self.plot_points.get(): sym = symbols[elem]
				if self.plot_lines.get(): lw = 2
				if (self.x_is_cpt.get()):
					self._graph.line_create(y_var[elem], linewidth = lw,
						symbol=sym, scalesymbols=0, pixels=pointSize, 
						xdata=vector_xnum, ydata=vector_y[elem],
						smooth = smooth_options[self.smoothing.get()],
						color = foreground)
				else:
					self._graph.line_create(y_var[elem], linewidth = lw,
						symbol=sym, scalesymbols=0, pixels=pointSize,
						xdata=vector_x, ydata=vector_y[elem],
						smooth = smooth_options[self.smoothing.get()],
						color = foreground)


	def _getDataLimits(self):
		if (self.x_is_cpt.get()):
			xmin = vector_xnum.min()
			xmax = vector_xnum.max()
		else:
			xmin = vector_x.min()
			xmax = vector_x.max()
		ymin = vector_y[0].min()
		ymax = vector_y[0].max()
		found = 0
		for i in range(num_vars):
			if (y_var[i] <> 'X'):
				if (not found):
					ymin = vector_y[i].min()
					ymax = vector_y[i].max()
					found = 1
				else:
					min = vector_y[i].min()
					max = vector_y[i].max()
					if (min < ymin): ymin = min
					if (max > ymax): ymax = max
		if (not found):
			ymin = 0
			ymax = 1
		return(xmin, xmax, ymin, ymax)


	def _zoom(self, x0, y0, x1, y1):
		#print "zoom to ", x0, y0, x1, y1
		self._graph.xaxis_configure(min=x0, max=x1)
		self._graph.yaxis_configure(min=y0, max=y1)
		(xmin, xmax, ymin, ymax) = self._getDataLimits()
		self.xScrollbar.set((x0-xmin)/(xmax-xmin), (x1-xmin)/(xmax-xmin))
		self.yScrollbar.set((y1-ymax)/(ymin-ymax), (y0-ymax)/(ymin-ymax))


	def _mouseMove(self, event):
		global x0, y0, x1, y1, dragging

		pos = "@" +str(event.x) +"," +str(event.y)
		self._graph.crosshairs_configure(position = pos)
		(user_x, user_y) = self._graph.invtransform(event.x, event.y)
		self._messagebar_x.message('state', '%3.4g' % user_x)
		self._messagebar_y.message('state', '%3.4g' % user_y)

		if (dragging):
			(x1, y1) = self._graph.invtransform(event.x, event.y)        
			self._graph.marker_configure("zoom_rect", 
				coords = (x0, y0, x1, y0, x1, y1, x0, y1, x0, y0))


	def _mouseUp(self, event):
		global dragging, x0, y0, x1, y1, rx0, ry0, minBox

		if dragging:
			dragging = 0;
			self._graph.marker_delete("zoom_rect")

			(rx1, ry1) = (event.x, event.y)
			if ((abs(rx0-rx1) > minBox) and (abs(ry0-ry1) > minBox)):
				# sort coordinates and zoom to box
				if x0 > x1: x0, x1 = x1, x0
				if y0 > y1: y0, y1 = y1, y0
				#print "zooming to ", x0, y0, x1, y1
				self._zoom(x0, y0, x1, y1) # zoom in
			else:
				(X0, X1) = self._graph.xaxis_limits()
				(Y0, Y1) = self._graph.yaxis_limits()
				x = (X0+X1)/2; dx = X1-X0
				y = (Y0+Y1)/2; dy = Y1-Y0
				if event.num == 1: # zoom in
					self._zoom(x0-dx/4, y0-dy/4, x0+dx/4, y0+dy/4)
				elif event.num == 2: # zoom reset
					self._graph.axis_configure(["x", "y"], min="", max="")
					self.xScrollbar.set(0, 1)
					self.yScrollbar.set(0, 1)
				else: # zoom out
					self._zoom(x-dx, y-dy, x+dx, y+dy)


	def _mouseDown(self, event):
		global dragging, x0, y0, x1, y1, rx0, ry0
		dragging = 0
    
		if self._graph.inside(event.x, event.y):
			dragging = 1
			(rx0, ry0) = (event.x, event.y)
			(x0, y0) = self._graph.invtransform(event.x, event.y)
			(x1, y1) = (x0, y0)
			self._graph.marker_create("line", name="zoom_rect", dashes=(2, 2))

			# Give user some help on mouse buttons
			if event.num == 1:
				msg = "Left button: zoom in X2 and center, or zoom to box"
			elif event.num == 2:
				msg = "Middle button: autoscale, or zoom to box"
			else:
				msg = "Right button: zoom out X2, or zoom to box"
			self._userMessageBar.message('help', msg)


	def _setsmoothing(self):
		for element in self._graph.element_show():
			if self._graph.element_type(element) == 'line':
				self._graph.element_configure(element, smooth =
					smooth_options[self.smoothing.get()])


	def _setvar(self, tag, v):
		global detlist, prefix, scan_name, y_var
		if (tag in detlist) and ((tag == 'X') or not (tag in (y_var[:v] + y_var[v+1:]))):
			name = prefix+scan_name
			# Change to new variable
			if (y_var[v] <> 'X'):
				self._graph.element_delete(y_var[v])
				caunmonitor(name+'.'+y_var[v]+'CV')
			y_var[v] = tag
			if (tag <> 'X'):
				camonitor(name+'.'+y_var[v]+'CV', self._VAL_monitorCB, y_var[v])
				self.raw_y[v] = caget(prefix + scan_name + "." + y_var[v] + "DA")
				self._updatePlot(elements=[v], new_x=0)
		else:
			# Stay with old variable
			self._userMessageBar.message('help', "'" + tag + "'" + " is already being displayed")
			self.y_var_spec[v].selectitem(y_var[v])
			self.y_var_spec[v].setlist(detlist)


	def _openFile(self):  
		fname = tkFileDialog.Open().show()
		if fname <> "":
			file = open(fname, 'r')
			i = 0
			for input_line in file.readlines():
				line = string.strip(input_line)
				if line[0] <> "#":
					[x, y0, y1, y2, y3] = string.split(line)
					self.raw_x[i] = float(x)
					self.raw_y[0][i] = float(y0)
					self.raw_y[1][i] = float(y1)
					self.raw_y[2][i] = float(y2)
					self.raw_y[3][i] = float(y3)
					i = i + 1
			self._vectorSize = i
			self._updatePlot(elements=[0, 1, 2, 3])


	def _saveFile(self):  
		fname = tkFileDialog.SaveAs().show()
		if fname <> "":
			file = open(fname, 'w')
			for i in range(self._vectorSize):
				s = "%14.6f %14.6f %14.6f %14.6f %14.6f\n" % (self.raw_x[i], self.raw_y[0][i], self.raw_y[1][i], self.raw_y[2][i], self.raw_y[3][i])
				file.write(s)
				

	def _getScanArrays(self):
		PVname = prefix + scan_name + ".CPT"
		try:
			self._vectorSize = caget(PVname)
		except CaChannelException:
			#self._userMessageBar.message('systemerror', "Can't read " + PVname)
			print "Can't get current point number."
			self._vectorSize = 2

		PVname = prefix + scan_name + "." + x_var + "RA"
		try:
			self.raw_x = caget(PVname)
		except CaChannelException:
			#self._userMessageBar.message('systemerror', "Can't read " + PVname)
			print "_getScanArrays: Can't get X data from ", PVname
			self.raw_x = [0] * self._vectorSize

		for i in range(num_vars):
			if y_var[i] <> 'X':
				PVname = prefix + scan_name + "." + y_var[i] + "DA"
				try:
					self.raw_y[i] = caget(PVname)
				except CaChannelException:
					#self._userMessageBar.message('systemerror', "Can't read " + PVname)
					print "_getScanArrays: Can't get Y data from ", PVname
					self.raw_y[i] = [0] * self._vectorSize


	def _updatePlot(self, elements=[0,1,2,3], new_x=1, rescale=1):
		if new_x:
			vector_x.__delslice__(0, vector_x.__len__())
			vector_xnum.__delslice__(0, vector_xnum.__len__())
			for j in range(self._vectorSize):
				try:
				    tmp=self.raw_x[j]
				except IndexError:
				    print "IndexError for raw_x, len=", len(self.raw_x), " _vectorSize=", self._vectorSize
				    tmp = 0
				vector_x.append(tmp)
				vector_xnum.append(j+1)
			self._graph.xaxis_configure(logscale = self.xlog.get())
		element_list = list(self._graph.element_show())
		#print "element_list = ", element_list
		for i in elements:
			if y_var[i] <> 'X':
				if y_var[i] in element_list:
					self._graph.element_delete(y_var[i])
				vector_y[i].__delslice__(0, vector_y[i].__len__())
				for j in range(self._vectorSize):
					# IndexError here
					#print "i=", i, " j=", j
					try:
						tmp = self.raw_y[i][j]
					except IndexError:
						print "IndexError: i=", i, " j=", j, " self._vectorSize=", self._vectorSize
						tmp = 0
					vector_y[i].append(tmp)
				sym = ''
				lw = 0
				if self.plot_points.get(): sym = symbols[i]
				if self.plot_lines.get(): lw = 2
				if self.x_is_cpt.get():
					self._graph.line_create(y_var[i], linewidth = lw, symbol=sym,
						xdata = vector_xnum, ydata=vector_y[i], pixels=pointSize,
						smooth = smooth_options[self.smoothing.get()],
						color = colorList[i])
				else:
					self._graph.line_create(y_var[i], linewidth = lw, symbol=sym,
						xdata = vector_x, ydata=vector_y[i], pixels=pointSize,
						smooth = smooth_options[self.smoothing.get()],
						color = colorList[i])
		if rescale:
			self._graph.xaxis_configure(min="", max="")
			self._graph.yaxis_configure(min="", max="")
			self.xScrollbar.set(0, 1)
			self.yScrollbar.set(0, 1)

		# check and set log-axis settings
		self._set_xlog()
		self._set_ylog()

		self._set_title()


	def _printBW(self):
		element = list(self._graph.element_show())
		for i in range(num_vars):
			self._graph.element_configure(y_var[i],
				dashes = dashList[i], color = 'black')
		self._print()
		for i in range(num_vars):
			self._graph.element_configure(y_var[i],
				dashes = "", color = colorList[i])


	def _print(self):
		self._set_title()
		tmpfilename = mktemp(".ps")
		self._graph.postscript_output(tmpfilename)
		if os.environ.has_key('PS_PRINTER'):
			printerstring = os.environ['PS_PRINTER']
			os.system("lpr -P" + printerstring + " " + tmpfilename)
		else:
			printerstring = 'default'
			self._userMessageBar.message('help', 'environment variable PS_PRINTER is not set.')
			os.system("lpr " + tmpfilename)
		os.system("rm " + tmpfilename)
		self._userMessageBar.message('state', 'graph sent to ' + printerstring + ' printer.')


	def _postscript(self):
		self._set_title()
		fname = tkFileDialog.SaveAs().show()
		if fname <> "":
			self._graph.postscript_output(fname)

######################################################################

root = Tkinter.Tk()
root.withdraw()
Pmw.initialise(root, fontScheme = 'pmw1')
if Pmw.Blt.haveblt(root):
	root.title("plot v15")
	vector_x = Pmw.Blt.Vector()
	vector_xnum = Pmw.Blt.Vector()
	vector_y = []
	widget = GraphDemo(root)
	root.mainloop()
else:
	print "plot.py: No BLT"
