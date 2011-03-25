import logging
import logging.handlers

__author__ = 'Sami-Matias Niemi'
__version__ = '0.3'


def setUpLogger(log_filename, loggername = 'logger'):
    '''
    Sets up a logger.
    @param log_filename: name of the file to save the log. 
    @param loggername: name of the logger 
    @return: logger instance
    '''
    # create logger
    logger = logging.getLogger(loggername)
    logger.setLevel(logging.DEBUG)
    # Add the log message handler to the logger
    handler = logging.handlers.RotatingFileHandler(log_filename)
                                                  #maxBytes=20, backupCount=5)
    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(module)s - %(funcName)s - %(levelname)s - %(message)s')    
    # add formatter to ch
    handler.setFormatter(formatter)
    # add handler to logger 
    logger.addHandler(handler)

    return logger


class SimpleLogger(object):
    '''
    A simple class to create a log file or print the information on screen.
    '''
    
    def __init__(self, filename, verbose = False):
        self.file = open(filename, 'w')
        self.verbose = verbose
    
    def write(self, text):
        '''
        Writes text either to file or screen.
        '''
        print >> self.file, text
        if self.verbose: print text