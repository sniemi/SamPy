# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui.py.ui'
#
# Created: Mon Sep 15 11:33:17 2008
#      by: The PyQt User Interface Compiler (pyuic) 3.17.4
#
# WARNING! All changes made in this file will be lost!


import sys
from qt import *
from Qwt5 import *

class MainForm(QMainWindow):
    def __init__(self,parent = None,name = None,fl = 0):
        QMainWindow.__init__(self,parent,name,fl)
        self.statusBar()

        if not name:
            self.setName("MainForm")

        self.setMinimumSize(QSize(86,151))
        self.setPaletteBackgroundColor(QColor(255,239,213))
        f = QFont(self.font())
        f.setFamily("Sans Serif")
        f.setPointSize(10)
        self.setFont(f)

        self.setCentralWidget(QWidget(self,"qt_central_widget"))
        MainFormLayout = QVBoxLayout(self.centralWidget(),11,6,"MainFormLayout")

        self.widgetStack = QWidgetStack(self.centralWidget(),"widgetStack")
        widgetStack_font = QFont(self.widgetStack.font())
        widgetStack_font.setPointSize(11)
        self.widgetStack.setFont(widgetStack_font)

        self.tableView = QWidget(self.widgetStack,"tableView")

        self.textLabel3 = QLabel(self.tableView,"textLabel3")
        self.textLabel3.setGeometry(QRect(10,330,250,23))

        self.textLabel2 = QLabel(self.tableView,"textLabel2")
        self.textLabel2.setGeometry(QRect(10,206,250,23))

        self.textLabel4 = QLabel(self.tableView,"textLabel4")
        self.textLabel4.setGeometry(QRect(10,456,470,23))

        self.frm_telescope = QFrame(self.tableView,"frm_telescope")
        self.frm_telescope.setGeometry(QRect(10,483,691,80))
        self.frm_telescope.setPaletteBackgroundColor(QColor(255,255,255))
        self.frm_telescope.setFrameShape(QFrame.StyledPanel)
        self.frm_telescope.setFrameShadow(QFrame.Plain)

        self.pickoffMirrorLabel = QLabel(self.frm_telescope,"pickoffMirrorLabel")
        self.pickoffMirrorLabel.setGeometry(QRect(216,20,120,35))
        self.pickoffMirrorLabel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.pickoffMirrorLabel.sizePolicy().hasHeightForWidth()))

        self.guideProbeLabel = QLabel(self.frm_telescope,"guideProbeLabel")
        self.guideProbeLabel.setGeometry(QRect(10,20,110,35))
        self.guideProbeLabel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.guideProbeLabel.sizePolicy().hasHeightForWidth()))

        self.guideProbe = QLabel(self.frm_telescope,"guideProbe")
        self.guideProbe.setGeometry(QRect(126,15,90,50))

        self.pickoffMirror = QLabel(self.frm_telescope,"pickoffMirror")
        self.pickoffMirror.setGeometry(QRect(344,15,100,50))

        self.ccdFilterLabel = QLabel(self.frm_telescope,"ccdFilterLabel")
        self.ccdFilterLabel.setGeometry(QRect(450,20,128,35))

        self.ccdFilter = QLabel(self.frm_telescope,"ccdFilter")
        self.ccdFilter.setGeometry(QRect(576,15,100,50))

        self.frm_science = QFrame(self.tableView,"frm_science")
        self.frm_science.setGeometry(QRect(10,356,691,80))
        self.frm_science.setPaletteBackgroundColor(QColor(255,255,255))
        self.frm_science.setFrameShape(QFrame.StyledPanel)
        self.frm_science.setFrameShadow(QFrame.Plain)

        self.fiberMaskLabel = QLabel(self.frm_science,"fiberMaskLabel")
        self.fiberMaskLabel.setGeometry(QRect(450,20,120,35))

        self.fiberMask = QLabel(self.frm_science,"fiberMask")
        self.fiberMask.setGeometry(QRect(576,15,102,50))

        self.fiberArmLabel = QLabel(self.frm_science,"fiberArmLabel")
        self.fiberArmLabel.setGeometry(QRect(218,20,90,35))

        self.fiberLampsLabel = QLabel(self.frm_science,"fiberLampsLabel")
        self.fiberLampsLabel.setGeometry(QRect(10,20,110,35))

        self.fiberLamps = QLabel(self.frm_science,"fiberLamps")
        self.fiberLamps.setGeometry(QRect(128,15,90,50))

        self.fiberArm = QLabel(self.frm_science,"fiberArm")
        self.fiberArm.setGeometry(QRect(342,15,100,50))

        self.frm_calib = QFrame(self.tableView,"frm_calib")
        self.frm_calib.setGeometry(QRect(10,230,690,80))
        self.frm_calib.setPaletteBackgroundColor(QColor(255,255,255))
        self.frm_calib.setFrameShape(QFrame.StyledPanel)
        self.frm_calib.setFrameShadow(QFrame.Plain)

        self.calShutterLabel = QLabel(self.frm_calib,"calShutterLabel")
        self.calShutterLabel.setGeometry(QRect(450,20,102,35))

        self.calLamps = QLabel(self.frm_calib,"calLamps")
        self.calLamps.setGeometry(QRect(126,15,90,50))

        self.calShutter = QLabel(self.frm_calib,"calShutter")
        self.calShutter.setGeometry(QRect(576,20,102,35))

        self.calLampsLabel = QLabel(self.frm_calib,"calLampsLabel")
        self.calLampsLabel.setGeometry(QRect(10,20,102,35))

        self.calMirror = QLabel(self.frm_calib,"calMirror")
        self.calMirror.setGeometry(QRect(344,15,100,50))

        self.calMirrorLabel = QLabel(self.frm_calib,"calMirrorLabel")
        self.calMirrorLabel.setGeometry(QRect(216,20,120,35))

        self.frm_fies = QFrame(self.tableView,"frm_fies")
        self.frm_fies.setGeometry(QRect(10,106,690,80))
        self.frm_fies.setPaletteBackgroundColor(QColor(255,255,255))
        self.frm_fies.setFrameShape(QFrame.StyledPanel)
        self.frm_fies.setFrameShadow(QFrame.Plain)

        self.ccdShutterLabel = QLabel(self.frm_fies,"ccdShutterLabel")
        self.ccdShutterLabel.setGeometry(QRect(450,20,102,35))

        self.ccdShutter = QLabel(self.frm_fies,"ccdShutter")
        self.ccdShutter.setGeometry(QRect(576,15,102,50))

        self.fiesFocus = QLabel(self.frm_fies,"fiesFocus")
        self.fiesFocus.setGeometry(QRect(126,15,102,50))

        self.fiesFocusLabel = QLabel(self.frm_fies,"fiesFocusLabel")
        self.fiesFocusLabel.setGeometry(QRect(10,20,102,35))
        self.fiesFocusLabel.setSizePolicy(QSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred,0,0,self.fiesFocusLabel.sizePolicy().hasHeightForWidth()))

        self.textLabel1 = QLabel(self.tableView,"textLabel1")
        self.textLabel1.setGeometry(QRect(10,80,240,23))

        self.textLabel1_2 = QLabel(self.tableView,"textLabel1_2")
        self.textLabel1_2.setGeometry(QRect(10,30,690,40))
        self.textLabel1_2.setAlignment(QLabel.WordBreak | QLabel.AlignCenter)
        self.widgetStack.addWidget(self.tableView,0)

        self.diagramView = QWidget(self.widgetStack,"diagramView")

        self.line12 = QFrame(self.diagramView,"line12")
        self.line12.setGeometry(QRect(472,361,2,179))
        self.line12.setPaletteForegroundColor(QColor(255,170,0))
        self.line12.setFrameShape(QFrame.VLine)
        self.line12.setFrameShadow(QFrame.Plain)
        self.line12.setLineWidth(2)
        self.line12.setFrameShape(QFrame.VLine)

        self.fib1_2 = QFrame(self.diagramView,"fib1_2")
        self.fib1_2.setGeometry(QRect(160,560,302,2))
        self.fib1_2.setFrameShape(QFrame.HLine)
        self.fib1_2.setFrameShadow(QFrame.Plain)
        self.fib1_2.setLineWidth(2)
        self.fib1_2.setFrameShape(QFrame.HLine)

        self.fib1_3 = QFrame(self.diagramView,"fib1_3")
        self.fib1_3.setGeometry(QRect(460,540,2,20))
        self.fib1_3.setFrameShape(QFrame.VLine)
        self.fib1_3.setFrameShadow(QFrame.Plain)
        self.fib1_3.setLineWidth(2)
        self.fib1_3.setFrameShape(QFrame.VLine)

        self.fib1_1 = QFrame(self.diagramView,"fib1_1")
        self.fib1_1.setGeometry(QRect(160,540,2,20))
        self.fib1_1.setFrameShape(QFrame.VLine)
        self.fib1_1.setFrameShadow(QFrame.Plain)
        self.fib1_1.setLineWidth(2)
        self.fib1_1.setFrameShape(QFrame.VLine)

        self.fib4_3 = QFrame(self.diagramView,"fib4_3")
        self.fib4_3.setGeometry(QRect(520,540,2,40))
        self.fib4_3.setFrameShape(QFrame.VLine)
        self.fib4_3.setFrameShadow(QFrame.Plain)
        self.fib4_3.setLineWidth(2)
        self.fib4_3.setFrameShape(QFrame.VLine)

        self.fib4_2 = QFrame(self.diagramView,"fib4_2")
        self.fib4_2.setGeometry(QRect(220,580,302,2))
        self.fib4_2.setFrameShape(QFrame.HLine)
        self.fib4_2.setFrameShadow(QFrame.Plain)
        self.fib4_2.setLineWidth(2)
        self.fib4_2.setFrameShape(QFrame.HLine)

        self.fib3_2 = QFrame(self.diagramView,"fib3_2")
        self.fib3_2.setGeometry(QRect(200,570,282,2))
        self.fib3_2.setFrameShape(QFrame.HLine)
        self.fib3_2.setFrameShadow(QFrame.Plain)
        self.fib3_2.setLineWidth(2)
        self.fib3_2.setFrameShape(QFrame.HLine)

        self.fib3_3 = QFrame(self.diagramView,"fib3_3")
        self.fib3_3.setGeometry(QRect(480,540,2,30))
        self.fib3_3.setFrameShape(QFrame.VLine)
        self.fib3_3.setFrameShadow(QFrame.Plain)
        self.fib3_3.setLineWidth(2)
        self.fib3_3.setFrameShape(QFrame.VLine)

        self.fib3_1 = QFrame(self.diagramView,"fib3_1")
        self.fib3_1.setGeometry(QRect(200,540,2,30))
        self.fib3_1.setFrameShape(QFrame.VLine)
        self.fib3_1.setFrameShadow(QFrame.Plain)
        self.fib3_1.setLineWidth(2)
        self.fib3_1.setFrameShape(QFrame.VLine)

        self.fib4_1 = QFrame(self.diagramView,"fib4_1")
        self.fib4_1.setGeometry(QRect(220,540,2,40))
        self.fib4_1.setFrameShape(QFrame.VLine)
        self.fib4_1.setFrameShadow(QFrame.Plain)
        self.fib4_1.setLineWidth(2)
        self.fib4_1.setFrameShape(QFrame.VLine)

        self.textLabel13_2 = QLabel(self.diagramView,"textLabel13_2")
        self.textLabel13_2.setGeometry(QRect(480,-5,170,23))

        self.textLabel13 = QLabel(self.diagramView,"textLabel13")
        self.textLabel13.setGeometry(QRect(110,-5,200,23))

        self.textLabel1_4 = QLabel(self.diagramView,"textLabel1_4")
        self.textLabel1_4.setGeometry(QRect(140,540,20,15))
        self.textLabel1_4.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter | QLabel.AlignRight)

        self.frame7 = QFrame(self.diagramView,"frame7")
        self.frame7.setGeometry(QRect(5,20,370,520))
        self.frame7.setPaletteBackgroundColor(QColor(255,255,255))
        self.frame7.setFrameShape(QFrame.StyledPanel)
        self.frame7.setFrameShadow(QFrame.Plain)

        self.beam3_2 = QFrame(self.frame7,"beam3_2")
        self.beam3_2.setGeometry(QRect(195,410,2,40))
        self.beam3_2.setFrameShape(QFrame.VLine)
        self.beam3_2.setFrameShadow(QFrame.Plain)
        self.beam3_2.setLineWidth(2)
        self.beam3_2.setFrameShape(QFrame.VLine)

        self.beam4_1 = QFrame(self.frame7,"beam4_1")
        self.beam4_1.setGeometry(QRect(215,340,2,20))
        self.beam4_1.setFrameShape(QFrame.VLine)
        self.beam4_1.setFrameShadow(QFrame.Plain)
        self.beam4_1.setLineWidth(2)
        self.beam4_1.setFrameShape(QFrame.VLine)

        self.beam4_2 = QFrame(self.frame7,"beam4_2")
        self.beam4_2.setGeometry(QRect(215,410,2,40))
        self.beam4_2.setFrameShape(QFrame.VLine)
        self.beam4_2.setFrameShadow(QFrame.Plain)
        self.beam4_2.setLineWidth(2)
        self.beam4_2.setFrameShape(QFrame.VLine)

        self.beam2_1 = QFrame(self.frame7,"beam2_1")
        self.beam2_1.setGeometry(QRect(175,340,2,20))
        self.beam2_1.setFrameShape(QFrame.VLine)
        self.beam2_1.setFrameShadow(QFrame.Plain)
        self.beam2_1.setLineWidth(2)
        self.beam2_1.setFrameShape(QFrame.VLine)

        self.b_stancam_2 = QFrame(self.frame7,"b_stancam_2")
        self.b_stancam_2.setGeometry(QRect(185,60,2,20))
        self.b_stancam_2.setFrameShape(QFrame.VLine)
        self.b_stancam_2.setFrameShadow(QFrame.Plain)
        self.b_stancam_2.setLineWidth(2)
        self.b_stancam_2.setFrameShape(QFrame.VLine)

        self.frm_stancam = QFrame(self.frame7,"frm_stancam")
        self.frm_stancam.setGeometry(QRect(130,30,110,30))
        self.frm_stancam.setPaletteBackgroundColor(QColor(225,228,239))
        self.frm_stancam.setFrameShape(QFrame.StyledPanel)
        self.frm_stancam.setFrameShadow(QFrame.Plain)

        self.stancam = QLabel(self.frm_stancam,"stancam")
        self.stancam.setGeometry(QRect(5,5,100,20))
        self.stancam.setAlignment(QLabel.AlignCenter)

        self.b_cal_fibarm = QFrame(self.frame7,"b_cal_fibarm")
        self.b_cal_fibarm.setGeometry(QRect(255,220,2,70))
        self.b_cal_fibarm.setFrameShape(QFrame.VLine)
        self.b_cal_fibarm.setFrameShadow(QFrame.Plain)
        self.b_cal_fibarm.setLineWidth(2)
        self.b_cal_fibarm.setFrameShape(QFrame.VLine)

        self.textLabel5 = QLabel(self.frame7,"textLabel5")
        self.textLabel5.setGeometry(QRect(249,81,70,40))

        self.fiberMask_2 = QLabel(self.frame7,"fiberMask_2")
        self.fiberMask_2.setGeometry(QRect(270,365,98,40))
        self.fiberMask_2.setAlignment(QLabel.AlignCenter)

        self.fiberArm_2 = QLabel(self.frame7,"fiberArm_2")
        self.fiberArm_2.setGeometry(QRect(270,295,98,40))
        self.fiberArm_2.setAlignment(QLabel.AlignCenter)

        self.frm_fiberLamps_2 = QFrame(self.frame7,"frm_fiberLamps_2")
        self.frm_fiberLamps_2.setGeometry(QRect(240,160,100,60))
        self.frm_fiberLamps_2.setFrameShape(QFrame.StyledPanel)
        self.frm_fiberLamps_2.setFrameShadow(QFrame.Plain)

        self.fiberLamps_2 = QLabel(self.frm_fiberLamps_2,"fiberLamps_2")
        self.fiberLamps_2.setGeometry(QRect(10,5,80,50))
        self.fiberLamps_2.setAlignment(QLabel.AlignCenter)

        self.beam1_0 = QFrame(self.frame7,"beam1_0")
        self.beam1_0.setGeometry(QRect(155,210,2,80))
        self.beam1_0.setFrameShape(QFrame.VLine)
        self.beam1_0.setFrameShadow(QFrame.Plain)
        self.beam1_0.setLineWidth(2)
        self.beam1_0.setFrameShape(QFrame.VLine)

        self.beam2_0 = QFrame(self.frame7,"beam2_0")
        self.beam2_0.setGeometry(QRect(175,210,2,80))
        self.beam2_0.setFrameShape(QFrame.VLine)
        self.beam2_0.setFrameShadow(QFrame.Plain)
        self.beam2_0.setLineWidth(2)
        self.beam2_0.setFrameShape(QFrame.VLine)

        self.beam4_0 = QFrame(self.frame7,"beam4_0")
        self.beam4_0.setGeometry(QRect(215,210,2,80))
        self.beam4_0.setFrameShape(QFrame.VLine)
        self.beam4_0.setFrameShadow(QFrame.Plain)
        self.beam4_0.setLineWidth(2)
        self.beam4_0.setFrameShape(QFrame.VLine)

        self.textLabel7 = QLabel(self.frame7,"textLabel7")
        self.textLabel7.setGeometry(QRect(60,145,120,20))
        self.textLabel7.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter | QLabel.AlignRight)

        self.b_telescope = QFrame(self.frame7,"b_telescope")
        self.b_telescope.setGeometry(QRect(2,190,138,2))
        self.b_telescope.setFrameShape(QFrame.HLine)
        self.b_telescope.setFrameShadow(QFrame.Plain)
        self.b_telescope.setLineWidth(2)
        self.b_telescope.setFrameShape(QFrame.HLine)

        self.b_stancam = QFrame(self.frame7,"b_stancam")
        self.b_stancam.setGeometry(QRect(185,120,2,50))
        self.b_stancam.setFrameShape(QFrame.VLine)
        self.b_stancam.setFrameShadow(QFrame.Plain)
        self.b_stancam.setLineWidth(2)
        self.b_stancam.setFrameShape(QFrame.VLine)

        self.beam3_1 = QFrame(self.frame7,"beam3_1")
        self.beam3_1.setGeometry(QRect(195,340,2,20))
        self.beam3_1.setFrameShape(QFrame.VLine)
        self.beam3_1.setFrameShadow(QFrame.Plain)
        self.beam3_1.setLineWidth(2)
        self.beam3_1.setFrameShape(QFrame.VLine)

        self.beam3_0 = QFrame(self.frame7,"beam3_0")
        self.beam3_0.setGeometry(QRect(195,210,2,80))
        self.beam3_0.setFrameShape(QFrame.VLine)
        self.beam3_0.setFrameShadow(QFrame.Plain)
        self.beam3_0.setLineWidth(2)
        self.beam3_0.setFrameShape(QFrame.VLine)

        self.frm_fiberArm_2 = QFrame(self.frame7,"frm_fiberArm_2")
        self.frm_fiberArm_2.setGeometry(QRect(100,290,165,50))
        self.frm_fiberArm_2.setFrameShape(QFrame.StyledPanel)
        self.frm_fiberArm_2.setFrameShadow(QFrame.Plain)

        self.arm1 = QFrame(self.frm_fiberArm_2,"arm1")
        self.arm1.setGeometry(QRect(55,25,2,23))
        self.arm1.setFrameShape(QFrame.VLine)
        self.arm1.setFrameShadow(QFrame.Plain)
        self.arm1.setLineWidth(2)
        self.arm1.setFrameShape(QFrame.VLine)

        self.arm2 = QFrame(self.frm_fiberArm_2,"arm2")
        self.arm2.setGeometry(QRect(75,25,2,23))
        self.arm2.setFrameShape(QFrame.VLine)
        self.arm2.setFrameShadow(QFrame.Plain)
        self.arm2.setLineWidth(2)
        self.arm2.setFrameShape(QFrame.VLine)

        self.arm_entry = QFrame(self.frm_fiberArm_2,"arm_entry")
        self.arm_entry.setGeometry(QRect(155,2,2,25))
        self.arm_entry.setFrameShape(QFrame.VLine)
        self.arm_entry.setFrameShadow(QFrame.Plain)
        self.arm_entry.setLineWidth(2)
        self.arm_entry.setFrameShape(QFrame.VLine)

        self.arm4 = QFrame(self.frm_fiberArm_2,"arm4")
        self.arm4.setGeometry(QRect(115,27,2,21))
        self.arm4.setFrameShape(QFrame.VLine)
        self.arm4.setFrameShadow(QFrame.Plain)
        self.arm4.setLineWidth(2)
        self.arm4.setFrameShape(QFrame.VLine)

        self.armsec1 = QFrame(self.frm_fiberArm_2,"armsec1")
        self.armsec1.setGeometry(QRect(55,25,20,2))
        self.armsec1.setFrameShape(QFrame.HLine)
        self.armsec1.setFrameShadow(QFrame.Plain)
        self.armsec1.setLineWidth(2)
        self.armsec1.setFrameShape(QFrame.HLine)

        self.arm3 = QFrame(self.frm_fiberArm_2,"arm3")
        self.arm3.setGeometry(QRect(95,25,2,23))
        self.arm3.setFrameShape(QFrame.VLine)
        self.arm3.setFrameShadow(QFrame.Plain)
        self.arm3.setLineWidth(2)
        self.arm3.setFrameShape(QFrame.VLine)

        self.armsec2 = QFrame(self.frm_fiberArm_2,"armsec2")
        self.armsec2.setGeometry(QRect(75,25,20,2))
        self.armsec2.setFrameShape(QFrame.HLine)
        self.armsec2.setFrameShadow(QFrame.Plain)
        self.armsec2.setLineWidth(2)
        self.armsec2.setFrameShape(QFrame.HLine)

        self.armsec3 = QFrame(self.frm_fiberArm_2,"armsec3")
        self.armsec3.setGeometry(QRect(95,25,20,2))
        self.armsec3.setFrameShape(QFrame.HLine)
        self.armsec3.setFrameShadow(QFrame.Plain)
        self.armsec3.setLineWidth(2)
        self.armsec3.setFrameShape(QFrame.HLine)

        self.armsec4 = QFrame(self.frm_fiberArm_2,"armsec4")
        self.armsec4.setGeometry(QRect(115,25,40,2))
        self.armsec4.setFrameShape(QFrame.HLine)
        self.armsec4.setFrameShadow(QFrame.Plain)
        self.armsec4.setLineWidth(2)
        self.armsec4.setFrameShape(QFrame.HLine)

        self.frm_fiberMask_2 = QFrame(self.frame7,"frm_fiberMask_2")
        self.frm_fiberMask_2.setGeometry(QRect(100,360,165,50))
        self.frm_fiberMask_2.setFrameShape(QFrame.StyledPanel)
        self.frm_fiberMask_2.setFrameShadow(QFrame.Plain)

        self.mask2 = QFrame(self.frm_fiberMask_2,"mask2")
        self.mask2.setGeometry(QRect(68,2,16,46))
        self.mask2.setFrameShape(QFrame.VLine)
        self.mask2.setFrameShadow(QFrame.Plain)
        self.mask2.setLineWidth(8)
        self.mask2.setFrameShape(QFrame.VLine)

        self.mask1 = QFrame(self.frm_fiberMask_2,"mask1")
        self.mask1.setGeometry(QRect(48,2,16,46))
        self.mask1.setFrameShape(QFrame.VLine)
        self.mask1.setFrameShadow(QFrame.Plain)
        self.mask1.setLineWidth(8)
        self.mask1.setFrameShape(QFrame.VLine)

        self.mask3 = QFrame(self.frm_fiberMask_2,"mask3")
        self.mask3.setGeometry(QRect(88,2,16,46))
        self.mask3.setFrameShape(QFrame.VLine)
        self.mask3.setFrameShadow(QFrame.Plain)
        self.mask3.setLineWidth(8)
        self.mask3.setFrameShape(QFrame.VLine)

        self.mask4 = QFrame(self.frm_fiberMask_2,"mask4")
        self.mask4.setGeometry(QRect(108,2,16,46))
        self.mask4.setFrameShape(QFrame.VLine)
        self.mask4.setFrameShadow(QFrame.Plain)
        self.mask4.setLineWidth(8)
        self.mask4.setFrameShape(QFrame.VLine)

        self.beam1_1 = QFrame(self.frame7,"beam1_1")
        self.beam1_1.setGeometry(QRect(155,340,2,20))
        self.beam1_1.setFrameShape(QFrame.VLine)
        self.beam1_1.setFrameShadow(QFrame.Plain)
        self.beam1_1.setLineWidth(2)
        self.beam1_1.setFrameShape(QFrame.VLine)

        self.guideProbe_2 = QLabel(self.frame7,"guideProbe_2")
        self.guideProbe_2.setGeometry(QRect(5,215,120,60))
        self.guideProbe_2.setAlignment(QLabel.AlignTop)

        self.textLabel1_6 = QLabel(self.frame7,"textLabel1_6")
        self.textLabel1_6.setGeometry(QRect(5,193,80,20))

        self.textLabel2_2 = QLabel(self.frame7,"textLabel2_2")
        self.textLabel2_2.setGeometry(QRect(5,360,85,43))
        self.textLabel2_2.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter | QLabel.AlignRight)

        self.beam1_2 = QFrame(self.frame7,"beam1_2")
        self.beam1_2.setGeometry(QRect(155,410,2,40))
        self.beam1_2.setFrameShape(QFrame.VLine)
        self.beam1_2.setFrameShadow(QFrame.Plain)
        self.beam1_2.setLineWidth(2)
        self.beam1_2.setFrameShape(QFrame.VLine)

        self.beam2_2 = QFrame(self.frame7,"beam2_2")
        self.beam2_2.setGeometry(QRect(175,410,2,40))
        self.beam2_2.setFrameShape(QFrame.VLine)
        self.beam2_2.setFrameShadow(QFrame.Plain)
        self.beam2_2.setLineWidth(2)
        self.beam2_2.setFrameShape(QFrame.VLine)

        self.frm_ccdFilter_2 = QFrame(self.frame7,"frm_ccdFilter_2")
        self.frm_ccdFilter_2.setGeometry(QRect(130,80,110,40))
        self.frm_ccdFilter_2.setFrameShape(QFrame.StyledPanel)
        self.frm_ccdFilter_2.setFrameShadow(QFrame.Plain)

        self.ccdFilter_2 = QLabel(self.frm_ccdFilter_2,"ccdFilter_2")
        self.ccdFilter_2.setGeometry(QRect(8,8,90,25))
        self.ccdFilter_2.setAlignment(QLabel.AlignCenter)

        self.frm_pickoffMirror_2 = QFrame(self.frame7,"frm_pickoffMirror_2")
        self.frm_pickoffMirror_2.setGeometry(QRect(140,170,90,40))
        self.frm_pickoffMirror_2.setFrameShape(QFrame.StyledPanel)
        self.frm_pickoffMirror_2.setFrameShadow(QFrame.Plain)

        self.pickoffMirror_2 = QLabel(self.frm_pickoffMirror_2,"pickoffMirror_2")
        self.pickoffMirror_2.setGeometry(QRect(5,5,80,30))
        self.pickoffMirror_2.setAlignment(QLabel.AlignCenter)

        self.textLabel4_2 = QLabel(self.frame7,"textLabel4_2")
        self.textLabel4_2.setGeometry(QRect(250,30,80,30))

        self.textLabel6 = QLabel(self.frame7,"textLabel6")
        self.textLabel6.setGeometry(QRect(240,130,110,30))

        self.textLabel1_3 = QLabel(self.frame7,"textLabel1_3")
        self.textLabel1_3.setGeometry(QRect(5,290,85,43))
        self.textLabel1_3.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter | QLabel.AlignRight)

        self.frm_fiberHead_2 = QFrame(self.frame7,"frm_fiberHead_2")
        self.frm_fiberHead_2.setGeometry(QRect(130,450,110,60))
        self.frm_fiberHead_2.setPaletteBackgroundColor(QColor(225,228,239))
        self.frm_fiberHead_2.setFrameShape(QFrame.StyledPanel)
        self.frm_fiberHead_2.setFrameShadow(QFrame.Plain)

        self.fiberHead_2 = QLabel(self.frm_fiberHead_2,"fiberHead_2")
        self.fiberHead_2.setGeometry(QRect(5,5,100,50))
        self.fiberHead_2.setAlignment(QLabel.WordBreak | QLabel.AlignCenter)

        self.textLabel1_4_3 = QLabel(self.diagramView,"textLabel1_4_3")
        self.textLabel1_4_3.setGeometry(QRect(180,540,20,15))
        self.textLabel1_4_3.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter | QLabel.AlignRight)

        self.textLabel1_4_4 = QLabel(self.diagramView,"textLabel1_4_4")
        self.textLabel1_4_4.setGeometry(QRect(225,540,20,15))
        self.textLabel1_4_4.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter | QLabel.AlignLeft)

        self.frame22 = QFrame(self.diagramView,"frame22")
        self.frame22.setGeometry(QRect(390,20,311,520))
        self.frame22.setPaletteBackgroundColor(QColor(255,255,255))
        self.frame22.setFrameShape(QFrame.StyledPanel)
        self.frame22.setFrameShadow(QFrame.Plain)

        self.fib5_2 = QFrame(self.frame22,"fib5_2")
        self.fib5_2.setGeometry(QRect(240,110,2,20))
        self.fib5_2.setFrameShape(QFrame.VLine)
        self.fib5_2.setFrameShadow(QFrame.Plain)
        self.fib5_2.setLineWidth(2)
        self.fib5_2.setFrameShape(QFrame.VLine)

        self.fib5_1 = QFrame(self.frame22,"fib5_1")
        self.fib5_1.setGeometry(QRect(160,90,40,2))
        self.fib5_1.setFrameShape(QFrame.HLine)
        self.fib5_1.setFrameShadow(QFrame.Plain)
        self.fib5_1.setLineWidth(2)
        self.fib5_1.setFrameShape(QFrame.HLine)

        self.frm_calLamps_2 = QFrame(self.frame22,"frm_calLamps_2")
        self.frm_calLamps_2.setGeometry(QRect(30,60,130,60))
        self.frm_calLamps_2.setFrameShape(QFrame.StyledPanel)
        self.frm_calLamps_2.setFrameShadow(QFrame.Plain)

        self.calLamps_2 = QLabel(self.frm_calLamps_2,"calLamps_2")
        self.calLamps_2.setGeometry(QRect(10,5,110,50))
        self.calLamps_2.setAlignment(QLabel.AlignCenter)

        self.frm_calMirror_2 = QFrame(self.frame22,"frm_calMirror_2")
        self.frm_calMirror_2.setGeometry(QRect(200,70,90,40))
        self.frm_calMirror_2.setFrameShape(QFrame.StyledPanel)
        self.frm_calMirror_2.setFrameShadow(QFrame.Plain)

        self.calMirror_2 = QLabel(self.frm_calMirror_2,"calMirror_2")
        self.calMirror_2.setGeometry(QRect(10,5,70,30))
        self.calMirror_2.setAlignment(QLabel.AlignCenter)

        self.frm_calShutter_2 = QFrame(self.frame22,"frm_calShutter_2")
        self.frm_calShutter_2.setGeometry(QRect(200,130,90,40))
        self.frm_calShutter_2.setFrameShape(QFrame.StyledPanel)
        self.frm_calShutter_2.setFrameShadow(QFrame.Plain)

        self.calShutter_2 = QLabel(self.frm_calShutter_2,"calShutter_2")
        self.calShutter_2.setGeometry(QRect(10,5,70,30))
        self.calShutter_2.setAlignment(QLabel.AlignCenter)

        self.fib5_3 = QFrame(self.frame22,"fib5_3")
        self.fib5_3.setGeometry(QRect(240,170,2,250))
        self.fib5_3.setFrameShape(QFrame.VLine)
        self.fib5_3.setFrameShadow(QFrame.Plain)
        self.fib5_3.setLineWidth(2)
        self.fib5_3.setFrameShape(QFrame.VLine)

        self.fib1_4 = QFrame(self.frame22,"fib1_4")
        self.fib1_4.setGeometry(QRect(70,380,2,140))
        self.fib1_4.setFrameShape(QFrame.VLine)
        self.fib1_4.setFrameShadow(QFrame.Plain)
        self.fib1_4.setLineWidth(2)
        self.fib1_4.setFrameShape(QFrame.VLine)

        self.textLabel1_4_5_2 = QLabel(self.frame22,"textLabel1_4_5_2")
        self.textLabel1_4_5_2.setGeometry(QRect(120,390,10,15))
        self.textLabel1_4_5_2.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter | QLabel.AlignRight)

        self.textLabel1_4_5_4 = QLabel(self.frame22,"textLabel1_4_5_4")
        self.textLabel1_4_5_4.setGeometry(QRect(80,390,10,15))
        self.textLabel1_4_5_4.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter | QLabel.AlignRight)

        self.textLabel1_4_5 = QLabel(self.frame22,"textLabel1_4_5")
        self.textLabel1_4_5.setGeometry(QRect(60,390,10,15))
        self.textLabel1_4_5.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter | QLabel.AlignRight)

        self.textLabel1_4_5_5 = QLabel(self.frame22,"textLabel1_4_5_5")
        self.textLabel1_4_5_5.setGeometry(QRect(100,390,10,15))
        self.textLabel1_4_5_5.setAlignment(QLabel.WordBreak | QLabel.AlignVCenter | QLabel.AlignRight)

        self.fib5_5 = QFrame(self.frame22,"fib5_5")
        self.fib5_5.setGeometry(QRect(110,380,2,40))
        self.fib5_5.setFrameShape(QFrame.VLine)
        self.fib5_5.setFrameShadow(QFrame.Plain)
        self.fib5_5.setLineWidth(2)
        self.fib5_5.setFrameShape(QFrame.VLine)

        self.fib5_4 = QFrame(self.frame22,"fib5_4")
        self.fib5_4.setGeometry(QRect(110,418,130,2))
        self.fib5_4.setFrameShape(QFrame.HLine)
        self.fib5_4.setFrameShadow(QFrame.Plain)
        self.fib5_4.setLineWidth(2)
        self.fib5_4.setFrameShape(QFrame.HLine)

        self.fib4_4 = QFrame(self.frame22,"fib4_4")
        self.fib4_4.setGeometry(QRect(130,380,2,140))
        self.fib4_4.setFrameShape(QFrame.VLine)
        self.fib4_4.setFrameShadow(QFrame.Plain)
        self.fib4_4.setLineWidth(2)
        self.fib4_4.setFrameShape(QFrame.VLine)

        self.fib3_4 = QFrame(self.frame22,"fib3_4")
        self.fib3_4.setGeometry(QRect(90,380,2,140))
        self.fib3_4.setFrameShape(QFrame.VLine)
        self.fib3_4.setFrameShadow(QFrame.Plain)
        self.fib3_4.setLineWidth(2)
        self.fib3_4.setFrameShape(QFrame.VLine)

        self.fiesFocus_2 = QLabel(self.frame22,"fiesFocus_2")
        self.fiesFocus_2.setGeometry(QRect(180,230,40,30))

        self.frame23 = QFrame(self.frame22,"frame23")
        self.frame23.setGeometry(QRect(30,150,140,231))
        self.frame23.setFrameShape(QFrame.StyledPanel)
        self.frame23.setFrameShadow(QFrame.Plain)

        self.frm_Fies = QFrame(self.frame23,"frm_Fies")
        self.frm_Fies.setGeometry(QRect(20,10,100,30))
        self.frm_Fies.setPaletteBackgroundColor(QColor(225,228,239))
        self.frm_Fies.setFrameShape(QFrame.StyledPanel)
        self.frm_Fies.setFrameShadow(QFrame.Plain)

        self.fies = QLabel(self.frm_Fies,"fies")
        self.fies.setGeometry(QRect(5,5,90,20))
        self.fies.setAlignment(QLabel.AlignCenter)

        self.fib1_5 = QFrame(self.frame23,"fib1_5")
        self.fib1_5.setGeometry(QRect(40,41,2,140))
        self.fib1_5.setFrameShape(QFrame.VLine)
        self.fib1_5.setFrameShadow(QFrame.Plain)
        self.fib1_5.setLineWidth(2)
        self.fib1_5.setFrameShape(QFrame.VLine)

        self.fib3_5 = QFrame(self.frame23,"fib3_5")
        self.fib3_5.setGeometry(QRect(60,40,2,140))
        self.fib3_5.setFrameShape(QFrame.VLine)
        self.fib3_5.setFrameShadow(QFrame.Plain)
        self.fib3_5.setLineWidth(2)
        self.fib3_5.setFrameShape(QFrame.VLine)

        self.fib5_6 = QFrame(self.frame23,"fib5_6")
        self.fib5_6.setGeometry(QRect(80,41,2,140))
        self.fib5_6.setFrameShape(QFrame.VLine)
        self.fib5_6.setFrameShadow(QFrame.Plain)
        self.fib5_6.setLineWidth(2)
        self.fib5_6.setFrameShape(QFrame.VLine)

        self.fib4_5 = QFrame(self.frame23,"fib4_5")
        self.fib4_5.setGeometry(QRect(100,41,2,140))
        self.fib4_5.setFrameShape(QFrame.VLine)
        self.fib4_5.setFrameShadow(QFrame.Plain)
        self.fib4_5.setLineWidth(2)
        self.fib4_5.setFrameShape(QFrame.VLine)

        self.frm_ccdShutter_2 = QFrame(self.frame23,"frm_ccdShutter_2")
        self.frm_ccdShutter_2.setGeometry(QRect(20,181,100,40))
        self.frm_ccdShutter_2.setFrameShape(QFrame.StyledPanel)
        self.frm_ccdShutter_2.setFrameShadow(QFrame.Plain)

        self.ccdShutter_2 = QLabel(self.frm_ccdShutter_2,"ccdShutter_2")
        self.ccdShutter_2.setGeometry(QRect(10,5,80,30))
        self.ccdShutter_2.setAlignment(QLabel.AlignCenter)

        self.frm_ExposureMeter = QFrame(self.frame22,"frm_ExposureMeter")
        self.frm_ExposureMeter.setGeometry(QRect(140,432,160,81))
        self.frm_ExposureMeter.setPaletteBackgroundColor(QColor(225,228,239))
        self.frm_ExposureMeter.setFrameShape(QFrame.StyledPanel)
        self.frm_ExposureMeter.setFrameShadow(QFrame.Plain)

        self.textLabel11_2_2 = QLabel(self.frm_ExposureMeter,"textLabel11_2_2")
        self.textLabel11_2_2.setGeometry(QRect(5,50,60,20))
        self.textLabel11_2_2.setAlignment(QLabel.WordBreak | QLabel.AlignBottom)

        self.textLabel11_2_3 = QLabel(self.frm_ExposureMeter,"textLabel11_2_3")
        self.textLabel11_2_3.setGeometry(QRect(5,5,140,20))

        self.textLabel11_2 = QLabel(self.frm_ExposureMeter,"textLabel11_2")
        self.textLabel11_2.setGeometry(QRect(5,30,60,20))
        self.textLabel11_2.setAlignment(QLabel.WordBreak | QLabel.AlignBottom)

        self.ExpMeterCur = QLabel(self.frm_ExposureMeter,"ExpMeterCur")
        self.ExpMeterCur.setGeometry(QRect(70,30,85,20))
        self.ExpMeterCur.setAlignment(QLabel.AlignBottom)

        self.ExpMeterAcc = QLabel(self.frm_ExposureMeter,"ExpMeterAcc")
        self.ExpMeterAcc.setGeometry(QRect(70,50,85,20))
        self.ExpMeterAcc.setAlignment(QLabel.AlignBottom)

        self.textLabel15 = QLabel(self.frame22,"textLabel15")
        self.textLabel15.setGeometry(QRect(190,40,110,30))

        self.textLabel15_2 = QLabel(self.frame22,"textLabel15_2")
        self.textLabel15_2.setGeometry(QRect(48,120,110,30))

        self.textLabel10 = QLabel(self.frame22,"textLabel10")
        self.textLabel10.setGeometry(QRect(30,30,140,30))

        self.textLabel11 = QLabel(self.frame22,"textLabel11")
        self.textLabel11.setGeometry(QRect(180,210,50,20))
        self.widgetStack.addWidget(self.diagramView,1)

        self.positionView = QWidget(self.widgetStack,"positionView")

        self.textLabel2_3 = QLabel(self.positionView,"textLabel2_3")
        self.textLabel2_3.setGeometry(QRect(29,313,190,23))

        self.textLabel5_2 = QLabel(self.positionView,"textLabel5_2")
        self.textLabel5_2.setGeometry(QRect(409,313,160,23))

        self.textLabel1_5 = QLabel(self.positionView,"textLabel1_5")
        self.textLabel1_5.setGeometry(QRect(30,20,130,23))

        self.textLabel5_2_2 = QLabel(self.positionView,"textLabel5_2_2")
        self.textLabel5_2_2.setGeometry(QRect(409,23,160,23))

        self.textLabel4_3 = QLabel(self.positionView,"textLabel4_3")
        self.textLabel4_3.setGeometry(QRect(30,50,280,220))
        self.textLabel4_3.setPaletteBackgroundColor(QColor(255,255,255))
        self.textLabel4_3.setFrameShape(QLabel.StyledPanel)
        self.textLabel4_3.setFrameShadow(QLabel.Plain)

        self.textLabel3_2 = QLabel(self.positionView,"textLabel3_2")
        self.textLabel3_2.setGeometry(QRect(30,340,280,220))
        self.textLabel3_2.setPaletteBackgroundColor(QColor(255,255,255))
        self.textLabel3_2.setFrameShape(QLabel.StyledPanel)
        self.textLabel3_2.setFrameShadow(QLabel.Plain)

        self.textLabel6_2 = QLabel(self.positionView,"textLabel6_2")
        self.textLabel6_2.setGeometry(QRect(410,340,280,220))
        self.textLabel6_2.setPaletteBackgroundColor(QColor(255,255,255))
        self.textLabel6_2.setFrameShape(QLabel.StyledPanel)
        self.textLabel6_2.setFrameShadow(QLabel.Plain)

        self.textLabel6_2_2 = QLabel(self.positionView,"textLabel6_2_2")
        self.textLabel6_2_2.setGeometry(QRect(410,50,280,220))
        self.textLabel6_2_2.setPaletteBackgroundColor(QColor(255,255,255))
        self.textLabel6_2_2.setFrameShape(QLabel.StyledPanel)
        self.textLabel6_2_2.setFrameShadow(QLabel.Plain)
        self.widgetStack.addWidget(self.positionView,2)

        self.ExposureView = QWidget(self.widgetStack,"ExposureView")

        self.ExposureMeterAcc = QwtPlot(self.ExposureView,"ExposureMeterAcc")
        self.ExposureMeterAcc.setGeometry(QRect(10,352,680,210))

        self.textLabel1_2_2 = QLabel(self.ExposureView,"textLabel1_2_2")
        self.textLabel1_2_2.setGeometry(QRect(10,30,690,40))
        self.textLabel1_2_2.setAlignment(QLabel.WordBreak | QLabel.AlignCenter)

        self.ExposureMeterCur = QwtPlot(self.ExposureView,"ExposureMeterCur")
        self.ExposureMeterCur.setGeometry(QRect(10,102,680,210))
        self.widgetStack.addWidget(self.ExposureView,3)
        MainFormLayout.addWidget(self.widgetStack)

        self.fileExitAction = QAction(self,"fileExitAction")
        self.viewTableAction = QAction(self,"viewTableAction")
        self.viewTableAction.setToggleAction(0)
        self.viewDiagramAction = QAction(self,"viewDiagramAction")
        self.viewDiagramAction.setToggleAction(0)
        self.viewPositionsAction = QAction(self,"viewPositionsAction")
        self.viewExposureAction = QAction(self,"viewExposureAction")




        self.MenuBar = QMenuBar(self,"MenuBar")

        pal = QPalette()
        cg = QColorGroup()
        cg.setColor(QColorGroup.Foreground,Qt.black)
        cg.setColor(QColorGroup.Button,QColor(221,223,228))
        cg.setColor(QColorGroup.Light,Qt.white)
        cg.setColor(QColorGroup.Midlight,QColor(238,239,241))
        cg.setColor(QColorGroup.Dark,QColor(110,111,114))
        cg.setColor(QColorGroup.Mid,QColor(147,149,152))
        cg.setColor(QColorGroup.Text,Qt.black)
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,Qt.black)
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(225,228,239))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,Qt.black)
        cg.setColor(QColorGroup.LinkVisited,Qt.black)
        pal.setActive(cg)
        cg.setColor(QColorGroup.Foreground,Qt.black)
        cg.setColor(QColorGroup.Button,QColor(221,223,228))
        cg.setColor(QColorGroup.Light,Qt.white)
        cg.setColor(QColorGroup.Midlight,QColor(254,254,255))
        cg.setColor(QColorGroup.Dark,QColor(110,111,114))
        cg.setColor(QColorGroup.Mid,QColor(147,149,152))
        cg.setColor(QColorGroup.Text,Qt.black)
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,Qt.black)
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(225,228,239))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,QColor(0,0,238))
        cg.setColor(QColorGroup.LinkVisited,QColor(82,24,139))
        pal.setInactive(cg)
        cg.setColor(QColorGroup.Foreground,QColor(128,128,128))
        cg.setColor(QColorGroup.Button,QColor(221,223,228))
        cg.setColor(QColorGroup.Light,Qt.white)
        cg.setColor(QColorGroup.Midlight,QColor(254,254,255))
        cg.setColor(QColorGroup.Dark,QColor(110,111,114))
        cg.setColor(QColorGroup.Mid,QColor(147,149,152))
        cg.setColor(QColorGroup.Text,QColor(128,128,128))
        cg.setColor(QColorGroup.BrightText,Qt.white)
        cg.setColor(QColorGroup.ButtonText,QColor(128,128,128))
        cg.setColor(QColorGroup.Base,Qt.white)
        cg.setColor(QColorGroup.Background,QColor(225,228,239))
        cg.setColor(QColorGroup.Shadow,Qt.black)
        cg.setColor(QColorGroup.Highlight,QColor(0,0,128))
        cg.setColor(QColorGroup.HighlightedText,Qt.white)
        cg.setColor(QColorGroup.Link,QColor(0,0,238))
        cg.setColor(QColorGroup.LinkVisited,QColor(82,24,139))
        pal.setDisabled(cg)
        self.MenuBar.setPalette(pal)
        self.MenuBar.setFrameShape(QMenuBar.StyledPanel)
        self.MenuBar.setFrameShadow(QMenuBar.Plain)

        self.fileMenu = QPopupMenu(self)
        self.fileMenu.insertSeparator()
        self.fileMenu.insertSeparator()
        self.fileExitAction.addTo(self.fileMenu)
        self.MenuBar.insertItem(QString(""),self.fileMenu,4)

        self.View = QPopupMenu(self)
        self.viewTableAction.addTo(self.View)
        self.viewDiagramAction.addTo(self.View)
        self.viewPositionsAction.addTo(self.View)
        self.viewExposureAction.addTo(self.View)
        self.MenuBar.insertItem(QString(""),self.View,5)


        self.languageChange()

        self.resize(QSize(730,670).expandedTo(self.minimumSizeHint()))
        self.clearWState(Qt.WState_Polished)

        self.connect(self.fileExitAction,SIGNAL("activated()"),self.close)
        self.connect(self.viewTableAction,SIGNAL("activated()"),self.showTable)
        self.connect(self.viewDiagramAction,SIGNAL("activated()"),self.showDiagram)
        self.connect(self.viewPositionsAction,SIGNAL("activated()"),self.showPositions)
        self.connect(self.viewExposureAction,SIGNAL("activated()"),self.showExposure)


    def languageChange(self):
        self.setCaption(self.__tr("FIES Status Display - FIESTA (v1.3)"))
        self.setIconText(self.__tr("FIESTA"))
        self.textLabel3.setText(self.__tr("<i>Science Fibers</i> (<font size=\"-1\">#1-4</font>)"))
        self.textLabel2.setText(self.__tr("<i>Calibration Fiber</i> (<font size=\"-1\">#5</font>)"))
        self.textLabel4.setText(self.__tr("<i>Telescope Status</i>"))
        self.pickoffMirrorLabel.setText(self.__tr("<b>Pickoff&nbsp;Mirror</b>"))
        self.guideProbeLabel.setText(self.__tr("<b>Vignetting</b>"))
        self.guideProbe.setText(self.__tr("0"))
        self.pickoffMirror.setText(self.__tr("0"))
        self.ccdFilterLabel.setText(self.__tr("<b>StanCam&nbsp;Filter</b>"))
        self.ccdFilter.setText(self.__tr("0"))
        self.fiberMaskLabel.setText(self.__tr("<b>Fiber&nbsp;Mask</b>"))
        self.fiberMask.setText(self.__tr("0"))
        self.fiberArmLabel.setText(self.__tr("<b>Fiber&nbsp;Arm</b>"))
        self.fiberLampsLabel.setText(self.__tr("<b>Fiber Lamps</b>"))
        self.fiberLamps.setText(self.__tr("0"))
        self.fiberArm.setText(self.__tr("0"))
        self.calShutterLabel.setText(self.__tr("<b>Cal. Shutter</b>"))
        self.calLamps.setText(self.__tr("0"))
        self.calShutter.setText(self.__tr("0"))
        self.calLampsLabel.setText(self.__tr("<b>Cal. Lamps</b>"))
        self.calMirror.setText(self.__tr("0"))
        self.calMirrorLabel.setText(self.__tr("<b>Lamp Selector</b>"))
        self.ccdShutterLabel.setText(self.__tr("<b>FIES Shutter</b>"))
        self.ccdShutter.setText(self.__tr("0"))
        self.fiesFocus.setText(self.__tr("0"))
        self.fiesFocusLabel.setText(self.__tr("<b>FIES Focus</b>"))
        self.textLabel1.setText(self.__tr("<i>Spectrograph</i>"))
        self.textLabel1_2.setText(self.__tr("<h1>FIES Status Display</h1>"))
        QToolTip.add(self.fib1_2,self.__tr("Fiber #1: Low Resolution"))
        QToolTip.add(self.fib1_1,self.__tr("Fiber #1: Low Resolution"))
        QToolTip.add(self.fib4_2,self.__tr("Fiber #4: High Resolution"))
        QToolTip.add(self.fib3_2,self.__tr("Fiber #3: Medium Resolution"))
        QToolTip.add(self.fib3_3,self.__tr("Fiber #3: Medium Resolution"))
        QToolTip.add(self.fib3_1,self.__tr("Fiber #3: Medium Resolution"))
        QToolTip.add(self.fib4_1,self.__tr("Fiber #4: High Resolution"))
        self.textLabel13_2.setText(self.__tr("<b>FIES Building</b>"))
        self.textLabel13.setText(self.__tr("<b>Telescope Adaptor</b>"))
        self.textLabel1_4.setText(self.__tr("<font size=\"-1\">1</font>"))
        self.stancam.setText(self.__tr("CCD"))
        self.textLabel5.setText(self.__tr("Filter"))
        self.fiberMask_2.setText(self.__tr("0"))
        self.fiberArm_2.setText(self.__tr("0"))
        QToolTip.add(self.frm_fiberLamps_2,self.__tr("Turns calibration lamp number n on or off. Valid options: [6-7]<p><font color=blue>Sequencer:&nbsp;lamp&nbsp;n&nbsp;'on'|'off'</font>"))
        self.fiberLamps_2.setText(self.__tr("0"))
        self.textLabel7.setText(self.__tr("Pickoff Mirror"))
        QToolTip.add(self.frm_fiberArm_2,self.__tr("Moves the calibration lamp arm to fiber n<p><font color=blue>Sequencer:&nbsp;arm&nbsp;n</font>"))
        QToolTip.add(self.frm_fiberMask_2,self.__tr("Moves the fiber mask to position n.<p><font color=blue>Sequencer:&nbsp;mask&nbsp;n</font>"))
        self.guideProbe_2.setText(self.__tr("0"))
        self.textLabel1_6.setText(self.__tr("Vignetting:"))
        self.textLabel2_2.setText(self.__tr("Fiber Mask"))
        QToolTip.add(self.frm_ccdFilter_2,self.__tr("Changes the STANCAM filter to the number specified.<p><font color=blue>Sequencer:&nbsp;ccd-filter&nbsp;n</font>"))
        self.ccdFilter_2.setText(self.__tr("0"))
        QToolTip.add(self.frm_pickoffMirror_2,self.__tr("Telescope pick-off mirror. Directs light to either FIES (split position), StanCam (ccd position) or Cass (park position).<p><font color=blue>Sequencer:&nbsp;camera-probe-split,camera-probe-ccd,camera-probe-park</font>"))
        self.pickoffMirror_2.setText(self.__tr("0"))
        self.textLabel4_2.setText(self.__tr("StanCam"))
        self.textLabel6.setText(self.__tr("Top Calib Unit"))
        self.textLabel1_3.setText(self.__tr("Fiber Arm"))
        QToolTip.add(self.frm_fiberHead_2,self.__tr("Fiber #1: Low Resolution<br>Fiber&nbsp;#3:&nbsp;Medium&nbsp;Resolution<br>Fiber #4: High Resolution"))
        self.fiberHead_2.setText(self.__tr("Fiberhead"))
        self.textLabel1_4_3.setText(self.__tr("<font size=\"-1\">3</font>"))
        self.textLabel1_4_4.setText(self.__tr("<font size=\"-1\">4</font>"))
        QToolTip.add(self.frm_calLamps_2,self.__tr("Turns calibration lamp number n on or off. Valid options: [1-4]<p><font color=blue>Sequencer:&nbsp;lamp&nbsp;n&nbsp;'on'|'off'</font>"))
        self.calLamps_2.setText(self.__tr("0"))
        QToolTip.add(self.frm_calMirror_2,self.__tr("Moves the lamp selector to calibration lamp 1-4. Not relevant for lamp 6 and 7.<p><font color=blue>Sequencer:&nbsp;calmove&nbsp;n</font>"))
        self.calMirror_2.setText(self.__tr("0"))
        QToolTip.add(self.frm_calShutter_2,self.__tr("Opens the calibration fiber shutter for nn deciseconds.<p><font color=blue>Sequencer:&nbsp;calshutter&nbsp;nn|'open'|'close'</font>"))
        self.calShutter_2.setText(self.__tr("0"))
        QToolTip.add(self.fib5_3,self.__tr("Fiber #5: Calibration"))
        QToolTip.add(self.fib1_4,self.__tr("Fiber #1: Low Resolution"))
        self.textLabel1_4_5_2.setText(self.__tr("<font size=\"-1\">4</font>"))
        self.textLabel1_4_5_4.setText(self.__tr("<font size=\"-1\">3</font>"))
        self.textLabel1_4_5.setText(self.__tr("<font size=\"-1\">1</font>"))
        self.textLabel1_4_5_5.setText(self.__tr("<font size=\"-1\">5</font>"))
        QToolTip.add(self.fib5_5,self.__tr("Fiber #5: Calibration"))
        QToolTip.add(self.fib5_4,self.__tr("Fiber #5: Calibration"))
        QToolTip.add(self.fib4_4,self.__tr("Fiber #4: High Resolution"))
        QToolTip.add(self.fib3_4,self.__tr("Fiber #3: Medium Resolution"))
        self.fiesFocus_2.setText(self.__tr("0"))
        self.fies.setText(self.__tr("CCD"))
        QToolTip.add(self.fib1_5,QString.null)
        QToolTip.add(self.frm_ccdShutter_2,self.__tr("Shutter at spectrograph entrance."))
        self.ccdShutter_2.setText(self.__tr("0"))
        self.textLabel11_2_2.setText(self.__tr("<i>Accum.</i>"))
        self.textLabel11_2_3.setText(self.__tr("Exposure Meter:"))
        self.textLabel11_2.setText(self.__tr("<i>Current</i>"))
        self.ExpMeterCur.setText(self.__tr("0"))
        self.ExpMeterAcc.setText(self.__tr("0"))
        self.textLabel15.setText(self.__tr("Lamp Selector"))
        self.textLabel15_2.setText(self.__tr("Spectrograph"))
        self.textLabel10.setText(self.__tr("Bottom Calib Unit"))
        self.textLabel11.setText(self.__tr("Focus"))
        self.textLabel2_3.setText(self.__tr("<b>MASK positions</b>"))
        self.textLabel5_2.setText(self.__tr("<b>Lamp Selector</b>"))
        self.textLabel1_5.setText(self.__tr("<b>ARM positions</b>"))
        self.textLabel5_2_2.setText(self.__tr("<b>Calibration Lamps</b>"))
        self.textLabel4_3.setText(self.__tr("1  	F1 LowRes Halogen\n"
"2 	F1 LowRes ThAr\n"
"3 	F2 MedRes Halogen(*)\n"
"4 	F2 MedRes ThAr(*)\n"
"5 	F3 MedRes Halogen\n"
"6 	F3 MedRes ThAr\n"
"7 	F4 HiRes Halogen\n"
"8 	F4 HiRes ThAr\n"
"\n"
"* Fiber 2 not available"))
        self.textLabel3_2.setText(self.__tr("1  	F2 MedRes(*) \n"
"2 	F3 MedRes\n"
"3 	F4 HiRes\n"
"4 	Closed\n"
"5 	F1 LowRes\n"
"6 	F1+F2 Low+MedRes(*)\n"
"7 	F2+F3 Med+MedRes(*)\n"
"8 	F3+F4 Med+HiRes\n"
"\n"
"* Fiber 2 not available"))
        self.textLabel6_2.setText(self.__tr("1  	Halogen\n"
"2 	Unavailable\n"
"3 	Unavailable\n"
"4 	ThAr"))
        self.textLabel6_2_2.setText(self.__tr("1  	Halogen     spectrograph\n"
"2 	Unavailable	 	 	\n"
"3 	Unavailable\n"
"4 	ThAr	     spectrograph\n"
"6	Halogen      telescope\n"
"7	ThAr	     telescope"))
        self.textLabel1_2_2.setText(self.__tr("<h1>FIES Exposure Meter</h1>"))
        self.fileExitAction.setText(self.__tr("Exit"))
        self.fileExitAction.setMenuText(self.__tr("E&xit"))
        self.fileExitAction.setAccel(self.__tr("Ctrl+X"))
        self.viewTableAction.setText(self.__tr("Table"))
        self.viewTableAction.setMenuText(self.__tr("&Table"))
        self.viewTableAction.setAccel(self.__tr("Ctrl+T"))
        self.viewDiagramAction.setText(self.__tr("Diagram"))
        self.viewDiagramAction.setMenuText(self.__tr("&Diagram"))
        self.viewDiagramAction.setAccel(self.__tr("Ctrl+D"))
        self.viewPositionsAction.setText(self.__tr("Information"))
        self.viewPositionsAction.setMenuText(self.__tr("&Information"))
        self.viewPositionsAction.setAccel(self.__tr("Ctrl+I"))
        self.viewExposureAction.setText(self.__tr("Exposure Meter"))
        self.viewExposureAction.setMenuText(self.__tr("&Exposure Meter"))
        self.viewExposureAction.setAccel(self.__tr("Ctrl+E"))
        if self.MenuBar.findItem(4):
            self.MenuBar.findItem(4).setText(self.__tr("&File"))
        if self.MenuBar.findItem(5):
            self.MenuBar.findItem(5).setText(self.__tr("&View"))


    def showDiagram(self):
        print "MainForm.showDiagram(): Not implemented yet"

    def showTable(self):
        print "MainForm.showTable(): Not implemented yet"

    def showPositions(self):
        print "MainForm.showPositions(): Not implemented yet"

    def showExposure(self):
        print "MainForm.showExposure(): Not implemented yet"

    def __tr(self,s,c = None):
        return qApp.translate("MainForm",s,c)

if __name__ == "__main__":
    a = QApplication(sys.argv)
    QObject.connect(a,SIGNAL("lastWindowClosed()"),a,SLOT("quit()"))
    w = MainForm()
    a.setMainWidget(w)
    w.show()
    a.exec_loop()
