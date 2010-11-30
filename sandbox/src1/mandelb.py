# the Numeric, Tkinter, and PIL modules can be used
# to create a relatively speedy Mandelbrot set with Python
# download Numeric from: http://numeric.scipy.org/
# or for Windows only:
# http://rene.f0o.com/~rene/stuff/Numeric-24.2.win32-py2.5.exe
# download Python Image Library (PIL) from:
# http://www.pythonware.com/products/pil/index.htm
# modified and tested with Python25    vegaseat    23dec2007

try:
    import Numeric as nm
except:
    print "program requires the Numeric module"
    print "from --> http://numeric.scipy.org/"
    raise SystemExit

import Tkinter as tk
import Image          # PIL
import ImageTk        # PIL

# set width and height of window
w = 640
h = 600

class Mandelbrot(object):
    def __init__(self):
        # create window
        self.root = tk.Tk()
        self.root.title("Mandelbrot Set")
        self.create_image()
        self.create_label()
        # start event loop
        self.root.mainloop()

    def draw(self, x1, x2, y1, y2, maxiter=30):
        # draw the Mandelbrot set, from numpy example
        xx = nm.arange(x1, x2, (x2-x1)/w*2)
        yy = nm.arange(y2, y1, (y1-y2)/h*2) * 1j
        q = nm.ravel(xx+yy[:, nm.NewAxis])
        z = nm.zeros(q.shape, nm.Complex)
        output = nm.resize(nm.array(0,), q.shape)
        for iter in range(maxiter):
            z = z*z + q
            done = nm.greater(abs(z), 2.0)
            q = nm.where(done,0+0j, q)
            z = nm.where(done,0+0j, z)
            output = nm.where(done, iter, output)
        output = (output + (256*output) + (256**2)*output) * 8
        # convert output to a string
        self.mandel = output.tostring()

    def create_image(self):
        """
        create the image from the draw() string
        """
        self.im = Image.new("RGB", (w/2, h/2))
        # you can experiment with these x and y ranges
        self.draw(-2.13, 0.77, -1.3, 1.3)
        self.im.fromstring(self.mandel, "raw", "RGBX", 0, -1)

    def create_label(self):
        # put the image on a label widget
        self.image = ImageTk.PhotoImage(self.im)
        self.label = tk.Label(self.root, image=self.image)
        self.label.pack()

# test the class
if __name__ == '__main__':
    test = Mandelbrot()
