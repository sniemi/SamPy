#! /bin/bash/env python

from Tkinter import *
import numpy as N
import pyfits as PF
from tkFileDialog import *
from tkMessageBox import *


global lightframes
lightframes ="null"


 #functions for opening
def OpenLight():
    #Open if they are the light frames
    global lightimages
    lightimages = askopenfilenames()
    
    #This next part is to display the choices made to alow for checking
    lightbox = Frame(master)
    lightbox.grid(row=2, rowspan=3)
    
    scrolllight = Scrollbar(lightbox, orient=HORIZONTAL)
    fileslist = Listbox(lightbox, xscrollcommand=scrolllight.set)
    scrolllight.config(command=fileslist.xview)
    for item in lightimages:
        fileslist.insert(END, item)
    
    fileslist.pack()
    scrolllight.pack(fill=X)
    
    numlight = len(lightimages)
    tempfile = PF.getdata(lightimages[0], header=False)
    ny, nx = tempfile.shape
    
    global lightframes
    lightframes = N.zeros((numlight, ny, nx), dtype=float)
    
    #Lets actualy read in the lights now
    for i in N.arange(numlight):
        lightframes[i] = PF.getdata(lightimages[i], header=False)
    
    

def OpenDark():
    #Open if they are dark frames
    global darkimages
    darkimages = askopenfilenames()
        
    darkbox = Frame(master)
    darkbox.grid(row=8, rowspan=3)
    
    scrolldark = Scrollbar(darkbox, orient=HORIZONTAL)
    darkslist = Listbox(darkbox, xscrollcommand=scrolldark.set)
    scrolldark.config(command=darkslist.xview)
    for item in darkimages:
        darkslist.insert(END,item)
    
    darkslist.pack()
    scrolldark.pack(fill=X)
    

def OpenBias():
    #Open if they are Bias frames
    global biasimages
    biasimages = askopenfilenames()
    
    biasbox = Frame(master)
    biasbox.grid(row=2, column=2, rowspan=3)
    
    scrollbias = Scrollbar(biasbox, orient=HORIZONTAL)
    biaslist = Listbox(biasbox, xscrollcommand=scrollbias.set)
    scrollbias.config(command=biaslist.xview)
    for item in biasimages:
        biaslist.insert(END, item)
    
    biaslist.pack()
    scrollbias.pack(fill=X)
    
    
    
def OpenFlat():
    #Open if they are Flat field
    global flatframes
    flatframes = askopenfilenames()
    
    flatbox = Frame(master)
    flatbox.grid(row=8, column=2, rowspan=3)
    
    scrollflat = Scrollbar(flatbox, orient=HORIZONTAL)
    flatlist = Listbox(flatbox, xscrollcommand=scrollflat.set)
    scrollflat.config(command=flatlist.xview)
    for item in flatimages:
        flatlist.insert(END, item)
        
    flatlist.pack()
    scrollflat.pack(fill=X)   


def darkfunc():
    numdark = len(darkimages)
    tempfile = PF.getdata(darkimages[0], header=False)
    ny, nx = tempfile.shape
    
    darkframes = N.zeros((numdark, ny, nx), dtype=float)
    
    #Lets actualy read in the darks now
    for i in N.arange(numdark):
        darkframes[i] = PF.getdata(darkimages[i], header=False)
    
    #Now medcombine the darks
    global masterdark 
    masterdark = medcombine(darkframes)
    
    #save the master dark
    if askyesno(message="Would you like to save the master dark? Please include the extension if yes"):
        savefile = asksaveasfilename(defaultextension=".fits")
        PF.writeto(savefile, N.float32(masterdark))
    
    global lightframes
    lightframes -= masterdark
    
def medcombine(data):
    medcombdat = N.median(data)
    return medcombdat

def medlight():
    showwarning(message="Remember the extention!")
    saveplace = asksaveasfilename()
    medfinal = medcombine(lightframes)
    PF.writeto(saveplace, N.float32(medfinal))

def addlight():
    showwarning(message="Remember the extention!")
    saveplace = asksaveasfilename()
    addfile = N.add(lightframes)
    PF.writeto(saveplace, N.float32(addfile))

def avglight():
    showwarning(message="Remember the extention!")
    saveplace = asksaveasfilename()
    avgfile = N.average(lightframes)
    PF.writeto(saveplace, N.float32(avgfile))

root = Tk()
master = Frame(root, width=800, height=600)
master.pack()

# Create for Light frames
lightlabel = Label(master, text="Please Open the Light Frames", borderwidth=2, relief=GROOVE)
lightlabel.grid(row=0, columnspan=2)

filesbutton = Button(master, text="Open Files", command=OpenLight, width=12)
filesbutton.grid(row=1, sticky=W)

#Get the dark frames
darklabel = Label(master, text="Please Open the Dark Frames", borderwidth=2, relief=GROOVE)
darklabel.grid(row=6, columnspan=2)

darkbutton = Button(master, text="Open Darks", command=OpenDark, width=12)
darkbutton.grid(row=7, sticky=W)

#get the Bias Frames
biaslabel = Label(master, text="Please Open The Bias Frames", borderwidth=2, relief=GROOVE)
biaslabel.grid(row=0, column=2, columnspan=2, padx=7)

biasbutton = Button(master, text="Open Bias", command=OpenBias, width=12)
biasbutton.grid(row=1, column=2, sticky=W, padx=7)

#Get the Flat Frames
flatlabel = Label(master, text="Please Open the Flat Frames", borderwidth=2, relief=GROOVE)
flatlabel.grid(row=6, column=2, columnspan=2, padx=7)

flatbutton = Button(master, text="Open Flats", command=OpenFlat, width=12)
flatbutton.grid(row=7, column=2, sticky=W, padx=7)

#apply the corrections
correctframe = Frame(master)
correctframe.grid(row=1, column=4, rowspan=3)

applylabel = Label(master, text="Click to Apply Any of These", borderwidth=2, relief=GROOVE)
applylabel.grid(row=0, column=4, padx=7)

applydarkbutton = Button(correctframe, text="Darks", command=darkfunc, width=12)
applydarkbutton.pack()

applybiasbutton = Button(correctframe, text="Bias", width=12)
applybiasbutton.pack()

applyflatsbutton = Button(correctframe, text="Flats", width=12)
applyflatsbutton.pack()

#things to to do to the image
functionslabel = Label(master, text="What would you like to do you the Data", borderwidth=2, relief=GROOVE)
functionslabel.grid(row=4, column=4, padx=7)

functionsframe = Frame(master)
functionsframe.grid(row=6, column=4, rowspan=4)

medcombutton = Button(functionsframe, text="Medcomine", command=medlight, width=12)
medcombutton.pack()

addcombutton = Button(functionsframe, text="Add", command=addlight, width=12)
addcombutton.pack()

avgcombutton = Button(functionsframe, text="Average", command=avglight, width=12)
avgcombutton.pack()



root.mainloop()

