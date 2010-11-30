#! /usr/bin/env python

import os
from Numeric import *
import tempfile
import Tkinter
#import Image		from PIL
#import ImageTk		from PIL
from types import *

def preprocess(image):
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

#class PILImage(Tkinter.Label):
#    def __init__(self, master, data):
#        width, height = data.shape[:2]
#        if len(data.shape) == 3:
#            mode = rawmode = 'RGB'
#            bits = transpose(data, (1,0,2)).tostring()
#        else:
#            mode = rawmode = 'L'
#            #bits = transpose(data, (1,0)).tostring()
#            bits = data.tostring()
#        self.image2 = Image.fromstring(mode, (width, height),
#                                          bits, "raw", rawmode)
#        self.image = ImageTk.PhotoImage(self.image2)
#        Tkinter.Label.__init__(self, master, image=self.image,
#                                   bg='black', bd=5)

class PPMImage(Tkinter.Label):
    def __init__(self, master, ppm, (scalex, scaley)):
        #self.image = Tkinter.PhotoImage(file=save_ppm(ppm))
        self.image = Tkinter.PhotoImage(file=save_ppm(ppm))
        w, h = self.image.width(), self.image.height()
        self.image = self.image.zoom(scalex, scaley)
        self.image.configure(width=w*scalex, height=h*scaley)
        Tkinter.Label.__init__(self, master, image=self.image,
                                   bg="white", bd=0)

def save_ppm(ppm, fname=None):
    if fname == None:
        fname = tempfile.mktemp('.ppm')
    f = open(fname, 'wb')
    f.write(ppm)
    f.close()
    return fname

def array2ppm(image):
    # scaling
    if len(image.shape) == 2:
        # B&W:
        #image = transpose(image)
        return "P5\n#PPM version of array\n%d %d\n255\n%s" % \
               (image.shape[1], image.shape[0], ravel(image).tostring())
    else:
        # color
        image = transpose(image, (1, 0, 2))
        return "P6\n%d %d\n255\n%s" % \
               (image.shape[1], image.shape[0], ravel(image).tostring())

# detView displays the image data in a list of 'class scanDetector', as
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

def detView(dets, scale=(1,1), columns=10):
    root = Tkinter.Tk()
    root.withdraw()
    top = Tkinter.Toplevel()
    data = []
    if type(dets) == type([]):
        for i in range(len(dets)): data.append(array(dets[i].data))
    else:
        data.append(array(dets.data))
        dets = [dets]

    frame =[]
    image = []
    pvname = []
    name = []
    maxlen = 0
    for i in range(len(data)):
        maxlen=max(maxlen, len(dets[i].name))
    for i in range(len(data)):
        d = preprocess(data[i])
        frame.append(Tkinter.Frame(top))
        image.append(PPMImage(frame[i], array2ppm(d), scale))
        image[i].pack(side='top')
        #pvname.append(Tkinter.Label(frame[i], text=dets[i].fieldName))
        #pvname[i].pack(side='top')
        name.append(Tkinter.Label(frame[i], text=dets[i].name, width=maxlen))
        name[i].pack(side='top')
        frame[i].grid(row=i/columns,column=i%columns, padx=0,pady=5)
