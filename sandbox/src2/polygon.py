#! /usr/bin/env python

from Tkinter import *

root = Tk()

root.title('Canvas')
canvas = Canvas(root, width =400, height=400)

canvas.create_polygon(205,105,285,125,166,177,210,199,205,105, fill='white')

canvas.pack()
root.mainloop()
