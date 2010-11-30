#! /usr/bin/env python
'''
This script can be used to generate an html page from the
ARuser monthly help desk report.

Created on Mar 2, 2010

@author: Sami-Matias Niemi (niemi@stsci.edu)
@version: 0.1
'''

def fixLines(data):
    '''
    Loops over the given data and adds html links
    for each suitable line. Will also calculate how
    many help calls were handled and compares it to
    the number recorded in the file. Will use  the 
    smaller number.
    '''
    out = ''
    cnt = 0
    format = ['%20s',
              '%20s',
              '%20s',
              '%4s',
              '%10s',
              '%25s',
              '%25s']
    html = '<a href=\"http://www.stsci.edu/institute/itsd/ARSystem/RemedyAlternateSearch?CALL=%s&ReviewRequests=Display+Call&DisplayCallNumber=1\">'
    for line in data:
        tmp = line.split()
        if len(tmp) > 0 and 'CNSHD' in tmp[0]:
            cnt += 1
            number = tmp[0][tmp[0].find('D')+1 : ]
            out += html % number
            out += tmp[0]
            out += '</a>'
            out += line[tmp[0].find('D') + len(number) + 2: -1]
            out += '\n'
        if 'Number of calls' in line:
            numb = int(line.split()[6])
            if cnt != numb:
                print 'Something weird in the number of calls...'
                print cnt, numb
                print 'Will use the smaller'
            if cnt < numb:
                out += line.replace('%i' % numb, '%i' % cnt)
            else:
                out += line
      
    return out

def subMonth(d):
    '''
    Takes away one month from the given date.
    '''
    year, month = d.year, d.month
    if month == 1:
        year -= 1
        month = 12
    else:
        month -= 1
    try:
        return d.replace(year = year, month = month)
    except ValueError:
        return d.replace(day = 1) - datetime.timedelta(1)

def findDate():
    '''
    Finds out the current date and then subtracts
    one month away from it. Thus, assumes that the script
    is being run few days (at least less than month) from
    the reporting date.
    '''
    import datetime
    return subMonth(datetime.date.today())
            
if __name__ == '__main__':
    '''
    The main program starts here.
    '''
    import sys
    
    try:
        data = open(sys.argv[1]).readlines()
    except:
        print 'Problem while reading file %s' % sys.argv[1]
        sys.exit(-9)
    
    date = findDate()
    
    tmp = fixLines(data)
    tmp2 = '<p><b>\nSpectrographs Calls for %s\n</b></p>\n<pre>\n' % date.strftime('%B %Y')
    output = tmp2 + '\n' + tmp + '\n</pre>\n'
    
    fh = open(sys.argv[1] + '_fixed', 'w')
    for line in output.split('\n'):
        fh.write(line.strip()+'\n')
        if '<a href' in line: fh.write('\n')
    fh.close()
    
        
    
        
    
    