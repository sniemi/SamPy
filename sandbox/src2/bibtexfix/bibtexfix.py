#!/sw/bin/python

import sys

#abbfolder = '/Users/Sammy/Documents/workspace/Python/bibtexfix/'
#abbfile =  'abb.file'

input = sys.argv[1]

#abbdata = open(abbfile, 'r')
#abbdict = {}

#out1 = open(abbfile +'_fix', 'a')

#for line in abbdata.readlines():
#    linedata = line.split()
#    temp = ''
#    for comp in linedata[1:]:
#        temp += (comp + ' ')
#    out1.write(temp +'\t' + linedata[0] + '\n')
#    abbdict[linedata[0]] = temp

#out1.close()
#print abbdict

#abbdata.close()

data = open(input, 'r').readlines()
output = open(input + '_fix', 'a')

for line in data:
    if 'local-url =' in line:
        print 'local-url removed'
    elif 'uri =' in line:
        print 'uri removed'
    elif 'rating =' in line:
        print 'rating removed'
    elif 'read =' in line:
        print 'read removed'
    elif 'abstract =' in line:
        print 'abstract removed'
    elif 'date-added =' in line:
        print 'date-added removed'
    elif 'date-modified =' in line:
        print 'date-modified removed'
    else:
        output.write(line)
   
output.close()
