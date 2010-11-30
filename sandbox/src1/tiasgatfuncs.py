import Tkinter as Tk

def messageOut(mt,m):
   mt.config(state="normal")
   mt.insert(Tk.END,m)
   mt.yview(Tk.END)
   mt.config(state="disabled")
#  mt.update_idletasks()
