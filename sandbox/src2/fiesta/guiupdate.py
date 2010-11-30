from Qwt5.anynumpy import *

def updateExposure(form, fies, tcs):

    """
    Update the guide errors
    """

    form.timerLabel.setText(str(tcs['ut']))    


    # Update the Current Counts plot
    emc = form.ExposureMeterCur
    emc.x = concatenate((emc.x[1:], emc.x[:1]), 1)

    emc.counter = emc.counter + 1 
    if emc.counter == 10:
     emc.x[-1] = int((fies['counts'] - emc.lastcounts)/10)
     emc.lastcounts = fies['counts']
     emc.counter = 0 
    else:
     emc.x[-1] = emc.x[-2]

    emc.CountPlot.setData(emc.t, emc.x)
    emc.setTitle("Current Counts:  %.4g" % emc.x[-1])
    emc.replot()

    # Update the Accumulated Counts plot
    ema = form.ExposureMeterAcc
    ema.x = concatenate((ema.x[1:], ema.x[:1]), 1)
    ema.x[-1] = fies['counts'] 
    ema.CountPlot.setData(ema.t, ema.x)
    ema.setTitle("Accumulated Counts: %.4g" % fies['counts'])
    ema.replot()

def updateTable(form, fies, tcs):

    """
    Updates the text fields in the FIES status table with
    values passed to this function in dictionaries.
    """

    # We use the str() method to ensure the text field
    # actually recieves a string.

    form.timerLabel.setText(str(tcs['ut']))    

    form.fiesFocus.setText(str(fies['fiesfocus']))
    form.ccdShutter.setText(str(fies['ccdshutter']))

    form.calMirror.setText(str(fies['calmirror']))
    form.calShutter.setText(str(fies['calshutter']))
    form.calLamps.setText(str(fies['callamps']))

    form.fiberMask.setText(str(fies['fibermask']))
    form.fiberArm.setText(str(fies['fiberarm']))       
    form.fiberLamps.setText(str(fies['fiberlamps']))

    form.guideProbe.setText(str(tcs['vignetting']))
    form.pickoffMirror.setText(str(tcs['pickoffmirror']))
    form.ccdFilter.setText(str(tcs['ccdfilter'] + ':' + tcs['ccdfiltername']))

def updateDiagram(form, fies, tcs):

    """
    Updates the FIES Diagram according to the status values 
    passed to the function
    """

    from qt import Qt
    from qt import QColor
    import string    
    
    # Update tabular values

    form.timerLabel.setText(str(tcs['ut']))

    cur_counts = form.ExposureMeterCur.x[-1]
    form.ExpMeterCur.setText("%.2g" % cur_counts)
    form.ExpMeterAcc.setText("%.2g" % fies['counts'])

    form.fiesFocus_2.setText(str(fies['fiesfocus']))
    form.ccdShutter_2.setText(str(fies['ccdshutter']))

    form.calMirror_2.setText(str(fies['calmirror']))
    form.calShutter_2.setText(str(fies['calshutter']))
    form.calLamps_2.setText(str(fies['callamps']))

    form.fiberMask_2.setText(str(fies['fibermask']))
    form.fiberArm_2.setText(str(fies['fiberarm']))       
    form.fiberLamps_2.setText(str(fies['fiberlamps']))
    
    form.guideProbe_2.setText(str(tcs['vignetting']))
    form.ccdFilter_2.setText(str(tcs['ccdfilter'] + ':' + tcs['ccdfiltername']))
    

    ######################################################################
    #
    # Show current lightpath(s).
    #
    # Basically, you follow the lightpath from lightsource to CCD, evaluating 
    # whether light is passed or not at every node (component). The most 
    # complicated lightpath to draw is centered on the Arm/Mask mechanisms.
    # To understand the logic in the code below, think of the following
    # qualitative description of whats going on: 
    # If the pickoff mirror is directing light to the FIES, without arm and
    # mask mechanisms the telescope beam will flood all fibers in the fiber 
    # head. Both arm and mask will block for some of that light.
    # The arm will always block one of the fibers; Calibration light
    # will go through the arm and into the fiber. Not only does the arm
    # block one of the fibers from the telescope beam - the arm is fine
    # adjusted to only let either Halogen or ThAR light through from the
    # calibration unit. If the halogen lamp is turned on, but the arm is
    # set on ThAr, no light will go through.
    # The mask sits underneith the arm and blocks light from entering 2,3
    # or all 4 fibers in the fiber head.
    #
    ######################################################################


    # Define some default colors 
    # Calibration fiber colors are determined further down

    HALOGEN     = QColor(255, 220, 20) 
    THAR        = Qt.magenta
    LAMP_ERROR  = QColor(255, 0, 0)

    TELBEAM_ON  = QColor(0, 255, 0)

    BEAM_OFF    = Qt.white    
    FIB_OFF     = Qt.black
    
    MASK_ON     = Qt.black
    MASK_OFF    = Qt.white 

 
    ### PICKOFF MIRROR ###
    

    # Turn telescope beam on (always on)
    form.b_telescope.setPaletteForegroundColor(TELBEAM_ON)   

    if (tcs['pickoffmirror'] == "Park"):
        # light goes nowhere
        form.frm_ccdFilter_2.b_tel = False
        form.frm_fiberArm_2.b_tel = False
    elif (tcs['pickoffmirror'] == "FIES"):
        # light is directed to FIES
        form.frm_ccdFilter_2.b_tel = False
        form.frm_fiberArm_2.b_tel = True     
    else: # (tcs['pickoffmirror'] == "StanCam")
        # light is directed to stancam
        form.frm_ccdFilter_2.b_tel = True
        form.frm_fiberArm_2.b_tel = False
    
    form.pickoffMirror_2.setText(str(tcs['pickoffmirror']))
        
    ### STANCAM FILTER ###

    if (form.frm_ccdFilter_2.b_tel):
        form.b_stancam.setPaletteForegroundColor(TELBEAM_ON)   
        form.frm_stancam.b_tel = True
    else:
        form.b_stancam.setPaletteForegroundColor(BEAM_OFF)  
        form.frm_stancam.b_tel = False
        
    ### STANCAM CCD ###
    if (form.frm_stancam.b_tel):
        form.b_stancam_2.setPaletteForegroundColor(TELBEAM_ON)
    else:
        form.b_stancam_2.setPaletteForegroundColor(BEAM_OFF)


    ### FIBER CALIBRATION LAMPS (Telescope Adaptor) ###
    
    if (fies['fiberlamps'] != "Lamps Off"):

    # Define calibration beam color, depending on lamp(s) on
        if (fies['fiberlamps'] == "Halogen"):
            CALFIB_ON = HALOGEN
        elif (fies['fiberlamps'] == "ThAr"): 
            CALFIB_ON = THAR
        else:
            # More than one lamp is on, NOT GOOD - SHOW Error
            CALFIB_ON = LAMP_ERROR

        form.frm_fiberLamps_2.setPaletteBackgroundColor(CALFIB_ON)
        form.frm_fiberArm_2.b_cal = True
    else:
        # No light reaches the fiberArm unit from the calibration unit 
        form.frm_fiberLamps_2.setPaletteBackgroundColor(BEAM_OFF)   
        form.frm_fiberArm_2.b_cal = False
        CALFIB_ON = BEAM_OFF       

    ### FIBER ARM ### 

    # beam from telescope
    if (form.frm_fiberArm_2.b_tel):
        # Set mask_beam and pickup_beam to Telescope
        (pickup_beam1,mask_beam1) = (TELBEAM_ON, TELBEAM_ON)
        (pickup_beam2,mask_beam2) = (TELBEAM_ON, TELBEAM_ON)
        (pickup_beam3,mask_beam3) = (TELBEAM_ON, TELBEAM_ON)
        (pickup_beam4,mask_beam4) = (TELBEAM_ON, TELBEAM_ON)
    else:
        # Set mask_beam and pickup_beam to Off
        (pickup_beam1,mask_beam1) = (BEAM_OFF, BEAM_OFF)
        (pickup_beam2,mask_beam2) = (BEAM_OFF, BEAM_OFF)
        (pickup_beam3,mask_beam3) = (BEAM_OFF, BEAM_OFF)
        (pickup_beam4,mask_beam4) = (BEAM_OFF, BEAM_OFF)

    # armpos 1: Fiber 1, Halogen
    if (fies['armpos'] == 1):        
        # Components of the fiberarm that will be drawn
        (ae,as1,as2,as3,as4,a1,a2,a3,a4) = (1,1,1,1,1,1,0,0,0)    

        # Draw Halogen Arm
        armcol = (BEAM_OFF, HALOGEN)

        # Calibration lamp is set to ThAR, so no light will 
        # go through the arm: Turn off this beam 
        if (CALFIB_ON == THAR):
            mask_beam1 = BEAM_OFF
        # Calibration lamp is either Halogen or halogen+thar, in which
        # case light will pass through the arm. Set the beam
        # color to be the one of the calibration unit 
        else:
            mask_beam1 = CALFIB_ON
        
    # armpos 2: Fiber 1, ThAr
    if (fies['armpos'] == 2):        
        (ae,as1,as2,as3,as4,a1,a2,a3,a4) = (1,1,1,1,1,1,0,0,0)    
        armcol = (BEAM_OFF, THAR)
        if (CALFIB_ON == HALOGEN):
            mask_beam1 = BEAM_OFF
        else:
            mask_beam1 = CALFIB_ON

    # armpos 3: Fiber 2, Halogen
    if (fies['armpos'] == 3):
        (ae,as1,as2,as3,as4,a1,a2,a3,a4) = (1,0,1,1,1,0,1,0,0)
        armcol = (BEAM_OFF, HALOGEN)
        if (CALFIB_ON == THAR):
            mask_beam2 = BEAM_OFF
        else:
            mask_beam2 = CALFIB_ON

    # armpos 4: Fiber 2, ThAr
    if (fies['armpos'] == 4):
        (ae,as1,as2,as3,as4,a1,a2,a3,a4) = (1,0,1,1,1,0,1,0,0)
        armcol = (BEAM_OFF, THAR)
        if (CALFIB_ON == HALOGEN):
            mask_beam2 = BEAM_OFF
        else:
            mask_beam2 = CALFIB_ON

    # armpos 5: Fiber 3, Halogen
    if (fies['armpos'] == 5):
        (ae,as1,as2,as3,as4,a1,a2,a3,a4) = (1,0,0,1,1,0,0,1,0)
        armcol = (BEAM_OFF, HALOGEN)
        if (CALFIB_ON == THAR):
            mask_beam3 = BEAM_OFF
        else:
            mask_beam3 = CALFIB_ON

    # armpos 6: Fiber 3, ThAr
    if (fies['armpos'] == 6):
        (ae,as1,as2,as3,as4,a1,a2,a3,a4) = (1,0,0,1,1,0,0,1,0)
        armcol = (BEAM_OFF, THAR)
        if (CALFIB_ON == HALOGEN):
            mask_beam3 = BEAM_OFF
        else:
            mask_beam3 = CALFIB_ON

    # armpos 7: Fiber 4, Halogen
    if (fies['armpos'] == 7):
        (ae,as1,as2,as3,as4,a1,a2,a3,a4) = (1,0,0,0,1,0,0,0,1)
        armcol = (BEAM_OFF, HALOGEN)
        if (CALFIB_ON == THAR):
            mask_beam4 = BEAM_OFF
        else:
            mask_beam4 = CALFIB_ON

    # armpos 8: Fiber 4, ThAr
    if (fies['armpos'] == 8):
        (ae,as1,as2,as3,as4,a1,a2,a3,a4) = (1,0,0,0,1,0,0,0,1)
        armcol = (BEAM_OFF, THAR) 
        if (CALFIB_ON == HALOGEN):
            mask_beam4 = BEAM_OFF
        else:
            mask_beam4 = CALFIB_ON

    # armpos 0: Moving
    if (fies['armpos'] == 0):
        (ae,as1,as2,as3,as4,a1,a2,a3,a4) = (0,0,0,0,0,0,0,0,0) 
        armcol = (BEAM_OFF, THAR)   
        # Set all beams to off while arm is moving
        (mask_beam1,mask_beam2,mask_beam3,mask_beam4) = \
                (BEAM_OFF,BEAM_OFF,BEAM_OFF,BEAM_OFF)
        
    # The calibration unit is turned on
    if (form.frm_fiberArm_2.b_cal):
        form.b_cal_fibarm.setPaletteForegroundColor(CALFIB_ON)
    # Beam is off, the arm will be drawn in 'off' state
    else:
        form.b_cal_fibarm.setPaletteForegroundColor(BEAM_OFF)
        armcol = (BEAM_OFF,FIB_OFF)

    # Show the arm mechanism
    form.arm_entry.setPaletteForegroundColor(armcol[ae])
    form.armsec1.setPaletteForegroundColor(armcol[as1])
    form.armsec2.setPaletteForegroundColor(armcol[as2])
    form.armsec3.setPaletteForegroundColor(armcol[as3])
    form.armsec4.setPaletteForegroundColor(armcol[as4])
    form.arm1.setPaletteForegroundColor(armcol[a1])
    form.arm2.setPaletteForegroundColor(armcol[a2])
    form.arm3.setPaletteForegroundColor(armcol[a3])
    form.arm4.setPaletteForegroundColor(armcol[a4])
        
    ### FIBER MASK ###
        
    
    # The mask lets light pass through 0, 1 or 2 fibers depending
    # on mask position.
    

    # maskpos 1: Fiber 2
    if (fies['maskpos'] == 1):
        (pickup_beam1,pickup_beam3,pickup_beam4) = \
            (BEAM_OFF,BEAM_OFF,BEAM_OFF)
        (beam1,beam2,beam3,beam4) = \
            (BEAM_OFF,mask_beam2,BEAM_OFF,BEAM_OFF)
        (fib_beam1,fib_beam2,fib_beam3,fib_beam4) = \
            (FIB_OFF,beam2,FIB_OFF,FIB_OFF)
        (maskpos1,maskpos2,maskpos3,maskpos4) = \
            (MASK_OFF,MASK_ON,MASK_OFF,MASK_OFF)
    
    # maskpos 2: Fiber 3
    if (fies['maskpos'] == 2):
        (pickup_beam1,pickup_beam2,pickup_beam4) = \
            (BEAM_OFF,BEAM_OFF,BEAM_OFF)        
        (beam1,beam2,beam3,beam4) = \
            (BEAM_OFF,BEAM_OFF,mask_beam3,BEAM_OFF)
        (fib_beam1,fib_beam2,fib_beam3,fib_beam4) = \
            (FIB_OFF,FIB_OFF,beam3,FIB_OFF)
        (maskpos1,maskpos2,maskpos3,maskpos4) = \
            (MASK_OFF,MASK_OFF,MASK_ON,MASK_OFF)

    # maskpos 3: Fiber 4
    if (fies['maskpos'] == 3):
        (pickup_beam1,pickup_beam2,pickup_beam3) = \
            (BEAM_OFF,BEAM_OFF,BEAM_OFF)
        (beam1,beam2,beam3,beam4) = \
            (BEAM_OFF,BEAM_OFF,BEAM_OFF,mask_beam4)
        (fib_beam1,fib_beam2,fib_beam3,fib_beam4) = \
            (FIB_OFF,FIB_OFF,FIB_OFF,beam4)
        (maskpos1,maskpos2,maskpos3,maskpos4) = \
            (MASK_OFF,MASK_OFF,MASK_OFF,MASK_ON)

    # maskpos 4: Fibers Closed
    if (fies['maskpos'] == 4):
        (pickup_beam1,pickup_beam2,pickup_beam3,pickup_beam4) = \
            (BEAM_OFF,BEAM_OFF,BEAM_OFF,BEAM_OFF)
        (beam1,beam2,beam3,beam4) = \
            (BEAM_OFF,BEAM_OFF,BEAM_OFF,BEAM_OFF)
        (fib_beam1,fib_beam2,fib_beam3,fib_beam4) = \
            (FIB_OFF,FIB_OFF,FIB_OFF,FIB_OFF)
        (maskpos1,maskpos2,maskpos3,maskpos4) = \
            (MASK_OFF,MASK_OFF,MASK_OFF,MASK_OFF)

    # maskpos 5: Fiber 1
    if (fies['maskpos'] == 5):
        (pickup_beam2,pickup_beam3,pickup_beam4) = \
            (BEAM_OFF,BEAM_OFF,BEAM_OFF)
        (beam1,beam2,beam3,beam4) = \
            (mask_beam1,BEAM_OFF,BEAM_OFF,BEAM_OFF)
        (fib_beam1,fib_beam2,fib_beam3,fib_beam4) = \
            (beam1,FIB_OFF,FIB_OFF,FIB_OFF)
        (maskpos1,maskpos2,maskpos3,maskpos4) = \
            (MASK_ON,MASK_OFF,MASK_OFF,MASK_OFF)


    # maskpos 6: Fibers 1+2
    if (fies['maskpos'] == 6):
        (pickup_beam3,pickup_beam4) = \
            (BEAM_OFF,BEAM_OFF)
        (beam1,beam2,beam3,beam4) = \
            (mask_beam1,mask_beam2,BEAM_OFF,BEAM_OFF)
        (fib_beam1,fib_beam2,fib_beam3,fib_beam4) = \
            (beam1,beam2,FIB_OFF,FIB_OFF)
        (maskpos1,maskpos2,maskpos3,maskpos4) = \
            (MASK_ON,MASK_ON,MASK_OFF,MASK_OFF)

    # maskpos 7: Fibers 2+3
    if (fies['maskpos'] == 7):
        (pickup_beam1,pickup_beam4) = \
            (BEAM_OFF,BEAM_OFF)
        (beam1,beam2,beam3,beam4) = \
            (BEAM_OFF,mask_beam2,mask_beam3,BEAM_OFF)
        (fib_beam1,fib_beam2,fib_beam3,fib_beam4) = \
            (FIB_OFF,beam2,beam3,FIB_OFF)
        (maskpos1,maskpos2,maskpos3,maskpos4) = \
            (MASK_OFF,MASK_ON,MASK_ON,MASK_OFF)

    # maskpos 8: Fibers 3+4
    if (fies['maskpos'] == 8):
        (pickup_beam1,pickup_beam2) = \
            (BEAM_OFF,BEAM_OFF)
        (beam1,beam2,beam3,beam4) = \
            (BEAM_OFF,BEAM_OFF,mask_beam3,mask_beam4)
        (fib_beam1,fib_beam2,fib_beam3,fib_beam4) = \
            (FIB_OFF,FIB_OFF,beam3,beam4)
        (maskpos1,maskpos2,maskpos3,maskpos4) = \
            (MASK_OFF,MASK_OFF,MASK_ON,MASK_ON)

   # Show lightpaths arriving to the arm from pickup mirror

    form.beam1_0.setPaletteForegroundColor(pickup_beam1)
    form.beam2_0.setPaletteForegroundColor(pickup_beam2)
    form.beam3_0.setPaletteForegroundColor(pickup_beam3)
    form.beam4_0.setPaletteForegroundColor(pickup_beam4)

    # Show lightpaths arriving to the mask from arm

    form.beam1_1.setPaletteForegroundColor(beam1)
    form.beam2_1.setPaletteForegroundColor(beam2)
    form.beam3_1.setPaletteForegroundColor(beam3)
    form.beam4_1.setPaletteForegroundColor(beam4)

    # Show mask positions
    
    form.mask1.setPaletteForegroundColor(maskpos1)
    form.mask2.setPaletteForegroundColor(maskpos2)
    form.mask3.setPaletteForegroundColor(maskpos3)
    form.mask4.setPaletteForegroundColor(maskpos4)

    # Show lightpaths arriving to the fiberhead from mask

    form.beam1_2.setPaletteForegroundColor(beam1)
    form.beam2_2.setPaletteForegroundColor(beam2)
    form.beam3_2.setPaletteForegroundColor(beam3)
    form.beam4_2.setPaletteForegroundColor(beam4)


    ### FIBER HEAD ###


    # Convert BEAMS_OFF beams to FIB_OFF beams, basically
    # to show inactive fibers as black instead of white.
    # (This is a bad hack!)
    if (fib_beam1 == BEAM_OFF):
        fib_beam1 = FIB_OFF
    if (fib_beam2 == BEAM_OFF):
        fib_beam2 = FIB_OFF
    if (fib_beam3 == BEAM_OFF):
        fib_beam3 = FIB_OFF
    if (fib_beam4 == BEAM_OFF):
        fib_beam4 = FIB_OFF
    
    form.fib1_1.setPaletteForegroundColor(fib_beam1)
    form.fib1_2.setPaletteForegroundColor(fib_beam1)
    form.fib1_3.setPaletteForegroundColor(fib_beam1)
    form.fib1_4.setPaletteForegroundColor(fib_beam1)
    if (fies['ccdshutter'] == "Open"): 
        form.fib1_5.setPaletteForegroundColor(beam1)
    else:
        form.fib1_5.setPaletteForegroundColor(BEAM_OFF)

    # FIBER 2 IS NO LONGER AVAILABLE - DO NOT DRAW	
    #form.fib2_1.setPaletteForegroundColor(fib_beam2)
    #form.fib2_2.setPaletteForegroundColor(fib_beam2)
    #form.fib2_3.setPaletteForegroundColor(fib_beam2)
    #form.fib2_4.setPaletteForegroundColor(fib_beam2)
    #if (fies['ccdshutter'] == "Open"): 
    #    form.fib2_5.setPaletteForegroundColor(beam2)
    #else:
    #    form.fib2_5.setPaletteForegroundColor(BEAM_OFF)

    form.fib3_1.setPaletteForegroundColor(fib_beam3)
    form.fib3_2.setPaletteForegroundColor(fib_beam3)
    form.fib3_3.setPaletteForegroundColor(fib_beam3)
    form.fib3_4.setPaletteForegroundColor(fib_beam3)
    if (fies['ccdshutter'] == "Open"): 
        form.fib3_5.setPaletteForegroundColor(beam3)
    else:
        form.fib3_5.setPaletteForegroundColor(BEAM_OFF)

    form.fib4_1.setPaletteForegroundColor(fib_beam4)
    form.fib4_2.setPaletteForegroundColor(fib_beam4)
    form.fib4_3.setPaletteForegroundColor(fib_beam4)
    form.fib4_4.setPaletteForegroundColor(fib_beam4)
    if (fies['ccdshutter'] == "Open"): 
        form.fib4_5.setPaletteForegroundColor(beam4)
    else:
        form.fib4_5.setPaletteForegroundColor(BEAM_OFF)


    ### FIES CALIBRATION LAMPS ###

    if (fies['callamps'] != "Lamps Off"):
        # Lamp(s) are on, show bg color and set 'incoming fiberlight=on'
        # on next node: Lamp Selector (calMirror)

        # Define calibration fiber color, depending on lamp(s) on
        if (fies['callamps'] == "Halogen"):
            CALFIB_ON = HALOGEN
        elif (fies['callamps'] == "ThAr"): 
            CALFIB_ON = THAR
        else:
            # More than one lamp is on, NOT GOOD - SHOW RED
            CALFIB_ON = LAMP_ERROR

        form.frm_calLamps_2.setPaletteBackgroundColor(CALFIB_ON)
        form.frm_calMirror_2.b_cal = True
    else:
        # incoming fiberlight=off on Lamp Selector node
        form.frm_calLamps_2.setPaletteBackgroundColor(Qt.white)   
        form.frm_calMirror_2.b_cal = False

    ### LAMP SELECTOR ###

    if (form.frm_calMirror_2.b_cal):

        # Light is recieved from cal lamps, turn on fiber (beam)
        form.fib5_1.setPaletteForegroundColor(CALFIB_ON)
 
        if (fies['callamps'].find(fies['calmirror']) != -1):    
            #Lamp selector set to a lamp currently on, so light
            # will pass on to the calibration shutter
            form.frm_calShutter_2.b_cal = True
        else:
            # lamp selector shutting of light from cal unit!
            # light reaches no further
            form.frm_calShutter_2.b_cal = False
    else:
        # No light is reached from callamps, turn off fiber (beam) and
        # set incoming beamlight=off on shutter
        form.fib5_1.setPaletteForegroundColor(BEAM_OFF)
        form.frm_calShutter_2.b_cal = False

    ### CALIBRATION SHUTTER ###

    if (form.frm_calShutter_2.b_cal):

        # Light is recieved from lamp selector, turn on fiber(beam)
        form.fib5_2.setPaletteForegroundColor(CALFIB_ON)

        if (fies['calshutter'] == "Open"):
            # Shutter is open, light will pass to the CCD shutter
            form.frm_ccdShutter_2.b_cal = True
        else:
            # Shutter is closed, light reaches no further
            form.frm_ccdShutter_2.b_cal = False
    else:
        # No light is reached from lamp selector
        form.fib5_2.setPaletteForegroundColor(BEAM_OFF)
        form.frm_ccdShutter_2.b_cal = False

    ### FIES SHUTTER & CCD ###

    if (form.frm_ccdShutter_2.b_cal):

        # Light is recieved through cal shutter, turn on fiber
        form.fib5_3.setPaletteForegroundColor(CALFIB_ON)
        form.fib5_4.setPaletteForegroundColor(CALFIB_ON)
        form.fib5_5.setPaletteForegroundColor(CALFIB_ON)
        if (fies['ccdshutter'] == "Open"):
            # CCD shutter is open, light will pass to the CCD
            form.fib5_6.setPaletteForegroundColor(CALFIB_ON)
        else:
            # CCD shutter closed, light reaches no further
            form.fib5_6.setPaletteForegroundColor(BEAM_OFF)
    else:
        # No light comes through the calibration shutter
        form.fib5_3.setPaletteForegroundColor(FIB_OFF)
        form.fib5_4.setPaletteForegroundColor(FIB_OFF)
        form.fib5_5.setPaletteForegroundColor(FIB_OFF)
        form.fib5_6.setPaletteForegroundColor(BEAM_OFF)
