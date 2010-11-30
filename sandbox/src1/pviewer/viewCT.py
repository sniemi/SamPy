import Pmw
from Tkinter import *
from tkSimpleDialog import Dialog
import os,string
from tv import readCT


class viewCT(Dialog):
    "ColorTable(Dialog) - dialog to preview color table"
    def body(self,master):
	self.cwidth = 256
	self.cheight = 40
	self.title("Color Table Dialog...")
	self.canvas = Canvas(master,width=self.cwidth,height=self.cheight)
	self.canvas.create_rectangle(0,0,self.cwidth,self.cheight)
	self.canvas.pack()
	self.CT = readCT()

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
        self.dialog = Pmw.ScrolledListBox(master,
		labelpos=NW, label_text='Pick color table',
		selectioncommand=self.apply,
                items=dname,listbox_width=40)
	self.dialog.pack(fill=BOTH,expand=1,padx=5,pady=5)
	return self.dialog.curselection()

    def apply(self):
	rts = self.dialog.curselection()
	index = string.atoi(rts[0])
	from Numeric import reshape
	rgb = reshape(self.CT[index],(256,3))
	for i in range(256):
		pp = rgb[i]
		col = '#%02x%02x%02x' % (int(pp[0]),int(pp[1]),int(pp[2]))
		self.canvas.create_line(i,0,i,self.cheight,fill=col)
	fo = open('1.txt','w')
	fo.write(str(index))
	fo.close

def getCTI(root):
	dialog=viewCT(root)
	fi = open('1.txt','r')
	x = fi.read()
	fi.close
	return int(x)
