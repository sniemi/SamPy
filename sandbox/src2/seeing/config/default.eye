# Default configuration file for EyE 1.3.0
# EB 2007-01-17
#
#-------------------------------- Retina -------------------------------------
 
RETINA_NAME            default.ret     # File containing retina weights
RETINA_SIZE            5,5             # Retina size: <size> or <width>,<height>
 
#---------------------------- Neural Network ---------------------------------
 
LEARNING_TYPE          NEW             # NONE, NEW, RESUME or RESTART
LEARNING_RATE          0.1, 50.0       # <learn rate> or
                                       # <learn rate>,<max. learn rate>
NN_SIZE                12,8,1          # Neurons per layer (max. 3 layers)
NPASSES                100             # Nb of passes through the training set
BUFFER_MAXSIZE         200000          # Max.number of different patterns used
 
#--------------------------- Background subtraction ---------------------------
 
SUBTRACT_BACK          Y               # Subtract sky background (Y/N)?
                                       # (all or for each image)
                                       # (all or for each image)
                                       # (all or for each image)
BACK_SIZE              128             # Background mesh size (pixels)
                                       # (all or for each image)
BACK_FILTERSIZE        3               # Background map filter range (meshes)
                                       # (all or for each image)
 
#------------------------------ Check Image ----------------------------------
 
CHECKIMAGE_TYPE        NONE            # may be one of NONE, or HISTOGRAM
CHECKIMAGE_NAME        check.fits      # Filename for the check-image
 
#------------------------------ Miscellaneous ---------------------------------
 
FRAME_LIMITS           -1              # xmin, ymin, xmax, ymax of rectangular
                                       # area to use (-1 is the whole frame)
VERBOSE_TYPE           NORMAL          # "QUIET","NORMAL" or "FULL"
NTHREADS               1               # 1 single thread
