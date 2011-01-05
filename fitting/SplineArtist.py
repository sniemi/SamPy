import pylab as P
import scipy.interpolate as I
import sys

class SplineArtist:
    def __init__(self, xdata, ydata, xrange, ylog = False, order = 3):
        self.xdata = xdata
        self.ydata = ydata
        self.ylog = ylog
        self.xrange = xrange
        self.k = order
        #data containers
        self.xs = list()
        self.ys = list()
        self.xspline = list()
        self.yspline = list()

    def run(self):
        self._fig()
        
    def _fig(self):
        #figure
        self.fig = P.figure()
        self.ax = self.fig.add_subplot(111)
        #lines
        self.line, = self.ax.plot(self.xdata, self.ydata, 'b-')
        self.line2, = self.ax.plot(self.xs, self.ys, 'r-',
                                   lw = 3, marker = 'o', 
                                   ms = 10, mec ='g', mfc = 'g')
        self.line3, = self.ax.plot(self.xspline, self.yspline,
                                   'g-', lw = 5)
        if self.ylog: self.ax.set_yscale('log')
        #events
        print 'Use mouse to set spline nodes...'
        self.fig.canvas.mpl_connect('button_press_event', self.onclick)
        self.fig.canvas.mpl_connect('key_press_event', self.onpress)
        P.show()

    def onpress(self, event):
        '''
        Define key press events:
        q/Q quits the whole script!
        '''
        if event.key in ('q','Q'): sys.exit()
        if event.key.capitalize() not in ('F', 'A', 'R', 'C', 'D'): return

        if event.key == 'f':
            self.draw_spline()
            self.fig.canvas.mpl_connect('button_press_event', self.onclick)
            print 'Accept or Retry a/r?'
    
        if event.key.capitalize() == 'A':
            #quit and return the spline
            print 'Spline accepted, press "c" to exit...'
            P.savefig('SpineFit.png')
    
        if event.key.capitalize() == 'R':
            print 'Try again'
            #clean up the stuff and try again
            self.xs = list()
            self.ys = list()
            self.xspline = list()
            self.yspline = list()
            self.line2.set_data(self.xs, self.ys)
            self.line3.set_data(self.xspline, self.yspline)
            self.line2.figure.canvas.draw()
            self.line3.figure.canvas.draw()
            P.close()
            self._fig()
	
        if event.key.capitalize() == 'D':
            self.plot_diff()

        if event.key.capitalize() == 'C':
            P.close()

    def onclick(self, event):
        '''
        Define a mouse click event:
        '''

        print 'button=%d, x=%d, y=%d, xdata=%e, ydata=%e'%(
        event.button, event.x, event.y, event.xdata, event.ydata)

        if event.inaxes!=self.line.axes: return
        #appends the clicks to xs and ys list
        self.xs.append(event.xdata)
        self.ys.append(event.ydata)
        #draws the new line,  this could possible be done with update
        #as well... maybe even better
        self.line2.set_data(self.xs, self.ys)
        self.line2.figure.canvas.draw()

    def draw_spline(self):
        '''
        Draws a spline function through the nods that have been set.
        '''
        if self.xrange is None:
            self.yspline = I.splev(self.xdata, I.splrep(self.xs, self.ys, k = self.k))
            self.xspline = self.xdata
        else:
            self.yspline = I.splev(self.xrange, I.splrep(self.xs, self.ys, k = self.k))
            self.xspline = self.xrange

        self.line3.set_data(self.xspline, self.yspline)
        self.line3.figure.canvas.draw()

    def get_spline(self):
        return self.xspline, self.yspline

    def plot_diff(self):
        fig = P.figure(2)
        ax = fig.add_subplot(111)	
        ax.axhline(1, c ='r')
        ax.plot(self.xdata,
                I.splev(self.xdata, I.splrep(self.xs, self.ys, k = self.k)) / self.ydata)
        ax.set_ylabel('Spline / Data')
        ax.set_ylim(0.8, 1.2)
        P.draw()

if __name__ == '__main__':
	import numpy as N
	
	x = N.arange(100) * 0.1
	y = N.sin(x) + 0.15*N.random.rand(100)
	xrange = N.array([-2,-1] + x.tolist() + (N.arange(100,110)*0.1).tolist())
                                                                                    
  	x = SplineArtist(x, y, xrange)	
	x.run()
	print 'Please click spline nodes and then press "f"'
	xspline, yspline = x.get_spline()
