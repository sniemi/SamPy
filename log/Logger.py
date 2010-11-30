'''
 A simple class to create a log file or print the information on screen.

@author: Sami-Matias Niemi
'''

__author__ = 'Sami-Matias Niemi'
__version__ = '0.2'

class Logger(object):
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