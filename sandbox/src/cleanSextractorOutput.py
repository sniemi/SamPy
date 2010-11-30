#######################################################
#Extremely simple script that can be used to clean
#Sextractor output file. Finds all objects that were
#not flagged by the source extraction and writes these
#objects to a new file. Does not edit object data in
#any other way.
#The flag column should be changed accordingly if ran
#to an arbitrary file.
#######################################################

import sys
mydir = '/Users/niemi/Desktop/Python/STScI/'
sys.path.append(mydir)
import IO

__author__ = 'Sami-Matias Niemi'
__version__ = "1.0"

filename = 'test.cat'
flagcolm = 2

data = IO.readFile(filename)

results = [line for line in data if line[flagcolm] == '0']

IO.writeToFile(results, '', 'stars.cat', separator = ' ')
