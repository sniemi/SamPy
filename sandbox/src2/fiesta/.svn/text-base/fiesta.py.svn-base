#!/usr/bin/python2.4

from gui import MainForm, Qwt
from qt import *
import sys
import datahandlers
from datahandlers import DBException
import guiupdate
from Qwt5.anynumpy import *

class MyForm(MainForm):

    """
        Main class, inhereting the GUI (MainForm) and adding update control
        through QTimer and managing switching between widget stacks (table and
        diagram views)
    """

    def __init__(self, *args, **kw):

        """
            Upon initialization, start Timer, define datahandler and show table
            view per default
        """

        MainForm.__init__(self, *args, **kw)


        # Initialize the Exposure Meter plots

        emc = self.ExposureMeterCur
        self.alignScales(emc)
        emc.t = arange(-1000.1, 0.0, 1.0)
        emc.x = zeros(len(emc.t), Float)
        emc.lastcounts = 0
        emc.counter = 0
        emc.setTitle("Current Counts")
        emc.CountPlot = Qwt.QwtPlotCurve("Counts")
        emc.CountPlot.attach(emc)
        emc.CountPlot.setPen(QPen(Qt.red))
        emc.setAxisTitle(Qwt.QwtPlot.xBottom, " ")
        emc.setAxisScale(Qwt.QwtPlot.xBottom, -1000, 0, 200)
        emc.setAxisTitle(Qwt.QwtPlot.yLeft, " ")


        ema = self.ExposureMeterAcc
        self.alignScales(ema)
        ema.t = arange(-1000.1, 0.0, 1.0)
        ema.x = zeros(len(ema.t), Float)
        ema.setTitle("Accumulated Counts")
        ema.CountPlot = Qwt.QwtPlotCurve("Counts")
        ema.CountPlot.attach(ema)
        ema.CountPlot.setPen(QPen(Qt.red))
        ema.setAxisTitle(Qwt.QwtPlot.xBottom, "<font size=-1>Last 100 seconds</font>")
        ema.setAxisScale(Qwt.QwtPlot.xBottom, -1000, 0, 10)
        ema.setAxisTitle(Qwt.QwtPlot.yLeft, " ")






        # Setup the timer
        self.myTimer = QTimer(self)
        self.connect(self.myTimer, SIGNAL("timeout()"),
                     self.updateStatus)
        self.myTimer.start(1000)

	try:
          self.dh = datahandlers.MySQLhandler()
        except DBException, e:
	  print e 
	  sys.exit (1)

        self.showDiagram()

        mb = self.MenuBar
	self.timerLabelTxt 	= QLabel("TCS UT ", mb)
        self.timerLabel 	= QLabel("XXXX-XX-XX XX:XX:XX", mb)
  	mb.insertItem(self.timerLabel)
	mb.insertItem(self.timerLabelTxt)
      
        self.statusBar().message("(c)2006 Nordic Optical Telescope")

    def showTable(self):
        
        """
            Show Table View and point updateGUI class to
            the updateTable class
        """
        self.widgetStack.raiseWidget(0)
        self.updateGUI = guiupdate.updateTable    

    def showDiagram(self):

        """
            Show Diagram View and point updateGUI class to  
            the updateDiagram class
        """
        
        self.widgetStack.raiseWidget(1)
        self.updateGUI = guiupdate.updateDiagram
        

    def showPositions(self):
        """
            Show available positions of the FIES mechanisms
        """

        self.widgetStack.raiseWidget(2)    


    def showExposure(self):
        """
            Show Exposure meter graph
        """

        self.widgetStack.raiseWidget(3)    
        self.updateGUI = guiupdate.updateExposure

    def close(self, *args, **kw):

        """
            Redefine the close() method so we can close datahandler
            connections before closing the form. This works both for
            exit via menu and exit via window manager
        """
        
        self.dh.close()
        return MainForm.close(self, *args, **kw)

    def updateStatus(self):
    
        """
            Routine called by QTimer, responsable for retrieving
            up-to-date status values and updating the GUI
        """
        
	status_fies = self.dh.InitFiesStatus()
	status_tcs  = self.dh.InitTCSStatus()

	try:
          status_fies  = self.dh.queryFiesStatus()
	  fies_status  = 'OK'
 	except DBException, e:
	  fies_status  = str(e)

	try:
          status_tcs   = self.dh.queryTcsStatus()
	  tcs_status   = 'OK'
 	except DBException, e:
	  tcs_status   = str(e)

	statusMessage = "Communication: FIES=%s TCS=%s " % (fies_status,tcs_status)

	self.statusBar().message(statusMessage)

        # Update the current widget GUI 
        self.updateGUI(self, status_fies, status_tcs)

        # Always update the ExposureMeter GUI except if this widget is
        # the active one. Otherwise it would be updated twice in a cycle and screw
        # up the timeline.
        if (self.updateGUI != guiupdate.updateExposure):
           guiupdate.updateExposure(self, status_fies, status_tcs)


    def alignScales(self,plot):
        plot.canvas().setFrameStyle(QFrame.Box | QFrame.Plain)
        plot.canvas().setLineWidth(1)
        for i in range(Qwt.QwtPlot.axisCnt):
            scaleWidget = plot.axisWidget(i)
            if scaleWidget:
                scaleWidget.setMargin(0)
            scaleDraw = plot.axisScaleDraw(i)
            if scaleDraw:
                scaleDraw.enableComponent(
                    Qwt.QwtAbstractScaleDraw.Backbone, False)


if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = MyForm()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()

