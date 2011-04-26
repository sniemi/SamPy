import numpy as np
import wx
import matplotlib
from matplotlib.figure import Figure
import matplotlib.dates as mdates
import matplotlib.ticker as mtickers
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
import matplotlib.patches as mpatches

class DraggableRectangle:
    lock = None
    def __init__(self, rect, master, xMin, xMax):       
        self.rect = rect        
        self.press = None
        self.background = None
        self.xMax = xMax
        self.xMin = xMin
        self.master = master
    def connect(self):      
        self.cidpress = self.rect.figure.canvas.mpl_connect('button_press_event', self.on_press)
        self.cidrelease = self.rect.figure.canvas.mpl_connect('button_release_event', self.on_release)
        self.cidmotion = self.rect.figure.canvas.mpl_connect('motion_notify_event', self.on_motion)
    def on_press(self, event):      
        if event.inaxes != self.rect.axes: return
        if DraggableRectangle.lock is not None: return
        contains, attrd = self.rect.contains(event)
        if not contains: return     
        x0, y0 = self.rect.xy
        self.press = x0, y0, event.xdata, event.ydata
        DraggableRectangle.lock = self
        canvas = self.rect.figure.canvas
        axes = self.rect.axes
        self.rect.set_animated(True)
        canvas.draw()
        self.background = canvas.copy_from_bbox(self.rect.axes.bbox)
        axes.draw_artist(self.rect)
        canvas.blit(axes.bbox)
    def on_motion(self, event):
        if DraggableRectangle.lock is not self: return
        if event.inaxes != self.rect.axes: return
        x0, y0, xpress, ypress = self.press
        dx = event.xdata - xpress
        dy = 0
        if x0+dx > self.xMax:
            self.rect.set_x(self.xMax)
        elif x0+dx < self.xMin:
            self.rect.set_x(self.xMin)
        else:
            self.rect.set_x(x0+dx)
        self.rect.set_y(y0+dy)
        canvas = self.rect.figure.canvas
        axes = self.rect.axes
        canvas.restore_region(self.background)
        self.master.set_xlim(self.rect.get_x(), self.rect.get_x() + 92)
        axes.draw_artist(self.rect)
        canvas.blit(axes.bbox)
    def on_release(self, event):        
        if DraggableRectangle.lock is not self: return
        self.press = None
        DraggableRectangle.lock = None
        self.rect.set_animated(False)
        self.background = None
        self.rect.figure.canvas.draw()
    def disconnect(self):
        self.rect.figure.canvas.mpl_disconnect(self.cidpress)
        self.rect.figure.canvas.mpl_disconnect(self.cidrelease)
        self.rect.figure.canvas.mpl_disconnect(self.cidmotion)

class MplCanvasFrame(wx.Frame): 
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, title='First Chart', size=(800, 700))
        datafile = matplotlib.get_example_data('goog.npy')
        r = np.load(datafile).view(np.recarray)
        datesFloat = matplotlib.dates.date2num(r.date)
        figure = Figure()
        xMaxDatetime = r.date[len(r.date)-1]
        xMinDatetime = r.date[0]
        xMaxFloat = datesFloat[len(datesFloat)-1]
        xMinFloat = datesFloat[0]
        yMin = min(r.adj_close) // 5 * 5
        yMax = (1 + max(r.adj_close) // 5) * 5      
        master = figure.add_subplot(211) 
        master.plot(datesFloat, r.adj_close)
        master.xaxis.set_minor_locator(mdates.MonthLocator())
        master.xaxis.set_major_locator(mdates.MonthLocator(bymonth=(1,4,7,10)))
        master.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
        master.set_xlim(datesFloat[120], datesFloat[120]+92)
        master.yaxis.set_minor_locator(mtickers.MultipleLocator(50))
        master.yaxis.set_major_locator(mtickers.MultipleLocator(100))
        master.set_ylim(yMin, yMax)
        master.set_position([0.05,0.20,0.92,0.75])
        master.xaxis.grid(True, which='minor')
        master.yaxis.grid(True, which='minor')
        slave = figure.add_subplot(212, yticks=[]) 
        slave.plot(datesFloat, r.adj_close)
        slave.xaxis.set_minor_locator(mdates.MonthLocator())
        slave.xaxis.set_major_locator(mdates.YearLocator())
        slave.xaxis.set_major_formatter(mdates.DateFormatter('%b-%y'))
        slave.set_xlim(xMinDatetime, xMaxDatetime)
        slave.set_ylim(yMin, yMax)
        slave.set_position([0.05,0.05,0.92,0.10])
        rectangle = mpatches.Rectangle((datesFloat[120], yMin), 92, yMax-yMin, facecolor='yellow', alpha = 0.4)     
        slave.add_patch(rectangle)
        canvas = FigureCanvas(self, -1, figure)
        drag = DraggableRectangle(rectangle, master, xMinFloat, xMaxFloat - 92)
        drag.connect()

if __name__ == '__main__':

    app = wx.PySimpleApp()
    frame = MplCanvasFrame()
    frame.Show(True)
    app.MainLoop()