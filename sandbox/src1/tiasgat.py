#!/usr/local/bin/python2.4
##!/usr/bin/python

# This is a little script to analyse data taken with the align
# scripts.  As the main result it will show recommended values for
# ALFOSC grism/slit wheel motor units.

# This script requires a valid IRAF login.cl file to be present
# in the 'present working directory'.   I'm using PyRAF.

# All temporary files will be under /tmp/tiasgat/

# The IRAF to DS9 communication is setup to use private fifos.
# To tell IRAF where the fifos are, this script sets the environment like
#   setenv IMTDEV fifo:/.../tiasgat/imt1i:/.../tiasgat/imt1o
# See the 'start_ds9' function below.

# To make the fifo's use "mknod imt1i p" and "mknod imt1o p"; 
# check the fifopath variable below.

# JHT, Mar/Apr 2006
# thanks to Ricardo for help with python issues!!



####### Load modules #######
# standard library
import Tkinter as Tk
import os
import time
import subprocess

# Define where Tiasgat modules are to be found
# This is only necesary if those modules are not in the
# same directory as the main program tiasgat.py
#import sys
#modulepath = "/home/jht/python"
#sys.path.append(modulepath)
#print sys.path

# Load Tiasgat module stuff
import HG, VG, HS, VS
from tiasgatfuncs import *



####### Define and initialize global variables #######
filename  = "ALalgn0001"
ds9_pid   = -99
datapath  = "/data/alfosc/"
#fifopath  = "/var/scratch/staff/jht/alfosc/tiasgat/"
fifopath  = "/var/postprocess/alfoscAlignTool/"



####### Define functions #######

def start_ds9():
   global ds9_pid, ds9_proc

   if ds9_pid == -99:         # start-up of first instance of ds9

     # Tell IRAF where to find the DS9 communication fifos
     os.putenv("IMTDEV","fifo:"+fifopath+"imt1i:"+fifopath+"imt1o")
     #os.system("env")

     messageOut(messageTextWidget,"Starting ds9 ...\n")
     wortel.update_idletasks()
     ds9_proc=subprocess.Popen(["/usr/local/bin/ds9", "-title", "Tiasgat!",
                    "-fifo", fifopath+"imt1", "-fifo_only",
                    "-zoom", "4", "-geometry", "620x780", "-cmap", "blue"])
     ds9_pid=ds9_proc.pid
     # give ds9 some time to start up
     time.sleep(1.0)

   if ds9_proc.poll() == 0:   # start-up of ds9 if any have been killed by user
     messageOut(messageTextWidget,"Starting new instance of ds9 ...\n")
     wortel.update_idletasks()
     ds9_proc=subprocess.Popen(["/usr/local/bin/ds9", "-title", "Tiasgat!",
                    "-fifo", fifopath+"imt1", "-fifo_only",
                    "-zoom", "4", "-geometry", "620x780", "-cmap", "blue"])
     ds9_pid=ds9_proc.pid
     # give ds9 some time to start up
     time.sleep(1.0)



# Now the wrappers for the actual PyRAF stuff; the reason is because
# the Widgets do not allow arguments, such as the filename to be
# passed on.  The Widgets can only invoke functions that have no parameters.

def VertSlit():
   global filename
   filename=fname.get()
   start_ds9()
   resultstr.set(VS.doit(filename,datapath,messageTextWidget))
   wortel.tkraise()
   wortel.update_idletasks()

def HorSlit():
   global filename
   filename=fname.get()
   start_ds9()
   resultstr.set(HS.doit(filename,datapath,messageTextWidget))
   wortel.tkraise()
   wortel.update_idletasks()

def VertGrism():
   global filename
   filename=fname.get()  
   start_ds9()
   resultstr.set(VG.doit(filename,datapath,messageTextWidget)) 
   wortel.tkraise()
   wortel.update_idletasks()

def HorGrism():
   global filename
   filename=fname.get()
   start_ds9()
   resultstr.set(HG.doit(filename,datapath,messageTextWidget))
   wortel.tkraise()
   wortel.update_idletasks()



# Function to get latest image file name
def GetLatest():
   # Use simple pipe command os.popen
   dummy=os.popen("cd "+datapath+"; ls -1rt *fits")
   latestfile=dummy.readlines()[-1].split(".")[0]
   dummy.close()

   messageOut(messageTextWidget,
              "\nLatest ALFOSC file is  "+datapath+latestfile+".fits\n")
   fname.set(latestfile)
   wortel.update_idletasks()


# This to prevent that the messages window is killed while the
# main window is still alive
def interceptDestroyProtocol():
   # This is a message that is displayed when the WM 'delete' is used.
   print "Use the \'Quit\' button ...."
   wortel.tkraise()



####### Define GUI #######
# Define window and some settings
wortel=Tk.Tk()
wortel.config(background="pink")
wortel.resizable(False,False)
wortel.title("The incredible ALFOSC slit/grism align tool !")
wortel.iconname("Tiasgat!")

fname=Tk.StringVar()
fname.set(filename)
resultstr=Tk.StringVar()
resultstr.set("Result: none yet")


# top row of GUI
fw=Tk.Frame(wortel)
Tk.Button(fw,activebackground="lightgoldenrod",background="LightSteelBlue1",
          text="Align horizontal slit",command=HorSlit,height=2).pack(side="left")
Tk.Button(fw,activebackground="lightgoldenrod",background="LightSteelBlue1", 
          text="Align vertical slit",command=VertSlit).pack(side="left",fill="both")
Tk.Button(fw,activebackground="lightgoldenrod",background="LightSteelBlue1",
          text="Align horizontal grism",command=HorGrism).pack(side="left",fill="both")
Tk.Button(fw,activebackground="lightgoldenrod",background="LightSteelBlue1",
          text="Align vertical grism",command=VertGrism).pack(side="left",fill="both")
fw.pack()


# middle row of GUI
fw=Tk.Frame(wortel)
Tk.Label(fw,height=2,width=70,background="hotpink",
          textvariable=resultstr).pack(side="left",fill="x",expand=True)
fw.pack(side="top",fill="x",expand=True)


# bottom row of GUI
Tk.Label(background="pink",anchor="e",
          text="File name:").pack(side="left",fill="both",expand=True)
entryWidget=Tk.Entry(background="pink",width=10,textvariable=fname)
entryWidget.pack(side="left",fill="both")
Tk.Button(background="pink",activebackground="lightgoldenrod",text="Latest file",
          command=GetLatest).pack(side="left",fill="both",expand=False)
Tk.Label(background="pink",text=" ").pack(side="left",fill="both",expand=True)
Tk.Button(background="pink",activebackground="lightgoldenrod",text="Quit",
          command=wortel.quit,height=2).pack(side="left",fill="both",expand=True)


# set focus to entry widget, so you dont have to click on it first
entryWidget.focus_set()

# Define a message window with Text widget
messageWindow=Tk.Toplevel()
messageWindow.geometry("586x300")
messageWindow.title("Tiasgat!   messages")
messageWindow.iconname("Tiasgat!   messages")
messageTextWidget=Tk.Text(messageWindow,background="pink")
messageTextWidget.pack(side="left",fill="both",expand=True)
messageTextWidget.config(state="disabled")

# Bind a scrollbar to the text and vice-versa
scrollIt=Tk.Scrollbar(messageWindow,command=messageTextWidget.yview,
          troughcolor="hotpink",
          background="LightSteelBlue1",activebackground="lightgoldenrod")
scrollIt.pack(side="left",fill="y")
messageTextWidget.config(yscrollcommand=scrollIt.set)

# intercept WM DELETE
messageWindow.protocol("WM_DELETE_WINDOW", interceptDestroyProtocol)



###### Start event loop ######
# the event loop can be stopped by clicking the 'Quit' button
Tk.mainloop()

# Commands to be executed once the event loop has stopped
if ds9_pid != -99:  os.kill(ds9_pid,15)
print '\nClear skies !\n'
