#! /usr/bin/env python
'''
.

ABOUT:
 

USAGE:   


DEPENDS:
         Python 2.5 or 2.6 (not version 3.x compatible)

EXITSTA:  
         0: No errors

AUTHOR :
         Sami-Matias Niemi, for STScI

HISTORY:
         May 15 2009: Initial Version

@author: Sami-Matias Niemi
'''

__author__ = 'Sami-Matias Niemi'
__version__ = '0.9'


#Processes command line arguments
def process_args(just_print_help = False):
    from optparse import OptionParser
    
    usage = 'usage: %prog [options]'
    desc = 'This script can be used to ...'
    
    parser = OptionParser(usage = usage, version='%prog ' + __version__, description = desc)
         
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      help="Verbose mode on.")
    parser.add_option("-i", "--input", dest="smsfile", 
                      help='''User define string that is used to find text files to be processed.
                              User must specify any wild cards in this string e.g. "*SMS.txt".''', 
                      metavar="string")
    parser.add_option('-d', '--debug', action='store_true', dest='debug',
                      help='debugging mode on.')
    parser.add_option('-t', '--text', action='store_true', dest='savetext',
                      help='Will output all text entries to ParsedText.ascii')
    if just_print_help:
        parser.print_help()
    else:
        return parser.parse_args()

def checkZeroArguments(opts):
    for x in opts.__dict__:
        if opts.__dict__[x] is not None:
            return True
    return False

def testSTD(filename):
    for line in open(filename, 'r'):
        if len(line) != 71: return False
    return True

def getKey(data):
    return data[12:16]

def parseCalendar(string):
    '''
    Parses calendar string and returns a tuple.
    '''
    import re
    
    cal_regex = '([0-9]+)Y([0-9]+)D([0-9]+)H([0-9]+)M([.0-9]+)S'

    subs = re.search(cal_regex, string)
    
    if int(sub.group(1)) > 50 and int(sub.group(1)) < 100:
        year = '19'+sub.group(1)
    else:
        year = '20'+sub.group(1) 
    day = sub.group(2)
    hour = sub.group(3)
    minute = sub.group(4)
    second = sub.group(5)
    
    return year, day, hour, minute, second


#keys
def SMS(pos, line, file):
    '''
    SMSHDR parser
    '''
#SMS0001   :SMSHDR,SMS_ID(JRHW00A_),CALENDAR(01Y302D13H54M25.000S)  ;;
#           ,CREATED(01Y302D13H54M25.000S),PDB_ID(JFLT200)           ;;
#           ,START=1995Y129D00H00M00.000S,END=1995Y130D00H25M56.000S ;;
#           ;SMSTIME=1995.129:00:00:00.000                                         
    
    #tests the line with the key
    for x in line.strip().split()[1].split(','):
        if x.find('SMS_ID') > -1: SMS_ID = insideParenthesis(x)
        if x.find('CALENDAR') > -1: CALENDARRaw = insideParenthesis(x)
        if x.find('CREATED') > -1: CREATEDRaw = insideParenthesis(x)
        if x.find('PDB_ID') > -1: PDB_ID = insideParenthesis(x)
        
    iterator = fileIterator(file) 
    
    p = 0
    for l in iterator:
        if p == pos:
            while 1:
                newline = iterator.next()
                if newline.strip().startswith('SMS') or newline.strip().startswith('9V2'): break
                else:
                    for x in newline.strip().split()[0].split(','):
                        if x.find('CALENDAR') > -1: CALENDARRaw = insideParenthesis(x)
                        if x.find('SMS_ID') > -1: SMS_ID = insideParenthesis(x)
                        if x.find('CREATED') > -1: CREATEDRaw = insideParenthesis(x)
                        if x.find('PDB_ID') > -1: PDB_ID = insideParenthesis(x)
        if p > pos : break
        p += 1
     
    try:
        CALENDAR = parseCalendar(CALENDARRaw)
    except:
        CALENDAR = CALENDARRaw
        
    try:
        CREATED = parseCalendar(CREATEDRaw)
    except:
        CREATED = CREATEDRaw
    
    return SMS_ID, CALENDAR, CREATED, PDB_ID

def GROUP(pos, line, file, debug):
    '''
    Group parser.
    '''
    result = {}
    cmd = []
    commandFound = False

    if debug: print 'GROUP function called:'
        
    iterator = fileIterator(file) 
    
    first = True
    p = 0
    for l in iterator:
        if p == pos:
            while 1:
                newline = iterator.next()
                if first:
                    result['GROUP'] = line.strip().split()[1].split(',')[1]
                    for x in line.strip().split()[1].split(','):
                        if x.find('FUNC') > -1: result['FUNC'] = insideParenthesis(x)
                        if x.find('TIME') > -1 and x.find('SMSTIME') == -1:
                            tmp = insideParenthesis2('TIME=', line)
                            if tmp == False:
                                tline = line.replace(';;', '').strip() + newline.replace(';;', '').strip()
                                tmp2 = insideParenthesis2('TIME=', tline)
                                if tmp2 == False:
                                    result['TIME'] = afterEqual(x)
                                else:
                                    result['TIME'] = tmp2
                            else:
                                result['TIME'] = tmp
                        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
                        if x.find('CMD') > -1:
                            cmd.append(line.replace(';;', '').strip())
                            commandFound = True
                        if x.find('SAFETY') > -1: result['SAFETY'] = insideParenthesis(x)                    
                first = False
                if newline.strip().startswith('SMS') or newline.strip().startswith('9V2'): break
                else:
                    for x in newline.strip().split()[0].split(','):
                        if x.find('FUNC') > -1: result['FUNC'] = insideParenthesis(x)
                        if x.find('TIME') > -1 and x.find('SMSTIME') == -1:
                            tmp = insideParenthesis2('TIME=', line)
                            if tmp == False:
                                tline = line.replace(';;', '').strip() + newline.replace(';;', '').strip()
                                tmp2 = insideParenthesis2('TIME=', tline)
                                if tmp2 == False:
                                    result['TIME'] = afterEqual(x)
                                else:
                                    result['TIME'] = tmp2
                            else:
                                result['TIME'] = tmp                      
                        if x.find('CMD') > -1:
                            cmd.append(newline.replace(';;', '').strip())
                            commandFound = True
                        if x.find('SAFETY') > -1: result['SAFETY'] = insideParenthesis(x)
                        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
                        if x.find('BEGINDATA') > -1:
                            tmp = []
                            while 1:
                                nl = iterator.next()
                                if nl.find('ENDDATA') > -1:
                                    result['DATA'] = tmp
                                    break
                                tmp.append(nl.strip())
        
        p += 1 
        if p > pos : break
    
    if commandFound: result['CMD'] = cmd
    
    return result

def CPMARK(pos, line, file, debug):
    '''
    CPMARK parser.
    '''
    
    result = {}
    
    if debug: print 'CPMARK function called:'
    
    for x in line.strip().split()[1].split(','):
        if x.find('CPID') > -1: result['CIPD'] = insideParenthesis(x)    
        if x.find('VECTOR') > -1: result['VECTOR'] = insideParenthesis(x)
        if x.find('ADR') > -1: result['ADR'] = insideParenthesis(x)
        if x.find('TIME') > -1 and x.find('SMSTIME') == -1: result['TIME'] = afterEqual(x)
        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
        
    iterator = fileIterator(file) 
    
    p = 0
    for l in iterator:
        if p == pos:
            while 1:
                newline = iterator.next()
                if newline.strip().startswith('SMS') or newline.strip().startswith('9V2'): break
                else:
                    for x in newline.strip().split()[0].split(','):
                        if x.find('CPID') > -1: result['CIPD'] = insideParenthesis(x)    
                        if x.find('VECTOR') > -1: result['VECTOR'] = insideParenthesis(x)
                        if x.find('ADR') > -1: result['ADR'] = insideParenthesis(x)
                        if x.find('TIME') > -1 and x.find('SMSTIME') == -1: result['TIME'] = afterEqual(x)
                        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
        p += 1 
        if p > pos : break    
            
    return result

def SLEW(pos, line, file, debug):
    '''
    SLEW parser.
    '''
    result = {} 

    if debug: print 'SLEW function called:'
    
    for x in line.strip().split()[1].split(','):
        if x.find('APER_EID') > -1: result['APER_EID'] = insideParenthesis(x)
        if x.find('CPNAME') > -1: result['CPNAME'] = insideParenthesis(x) 
        if x.find('END_DEC') > -1: result['END_DEC'] = insideParenthesis(x)
        if x.find('END_PA') > -1: result['END_PA'] = insideParenthesis(x)
        if x.find('END_RA') > -1: result['END_RA'] = insideParenthesis(x)
        if x.find('TYPE') > -1: result['TYPE'] = insideParenthesis(x)
        if x.find('START') > -1: result['START'] = insideParenthesis2('START=', line)
        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)

    iterator = fileIterator(file) 

    p = 0
    for l in iterator:
        if p == pos:
            while 1:
                newline = iterator.next()
                if newline.strip().startswith('SMS') or newline.strip().startswith('9V2'): break
                else:
                    for x in newline.strip().split()[0].split(','):
                        if x.find('APER_EID') > -1: result['APER_EID'] = insideParenthesis(x)
                        if x.find('CPNAME') > -1: result['CPNAME'] = insideParenthesis(x) 
                        if x.find('END_DEC') > -1: result['END_DEC'] = insideParenthesis(x)
                        if x.find('END_PA') > -1: result['END_PA'] = insideParenthesis(x)
                        if x.find('END_RA') > -1: result['END_RA'] = insideParenthesis(x)
                        if x.find('TYPE') > -1: result['TYPE'] = insideParenthesis(x)
                        if x.find('START') > -1: result['START'] = insideParenthesis2('START=', newline)
                        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
        p += 1 
        if p > pos : break         
    
    return result    
    

def TABLE(pos, line, file, debug):
    '''
    TABLE parser.
    
    :TABLE,LOSM,GRATING(G185M),LAMBDA(1850),OFFSET(0)        ;;
           ,TIME=(ORB,99950,EASCNCR,04H25M12.000S)                  ;;
           ;SMSTIME=2008.221:11:07:13.000                             
 9V20601B  :TABLE,LAPER,APERTURE(PSA),DET(FUV),TIME=(ORB,99950      ;;
           ,EASCNCR,04H27M40.000S)           
    
    '''
    result = {}

    if debug: print 'TABLE function called:'

    iterator = fileIterator(file) 

    first = True
    p = 0
    for l in iterator:
        if p == pos:
            while 1:
                newline = iterator.next()
                result['TABLE'] = line.strip().split()[1].split(',')[1]
                if first:
                    for x in line.strip().split()[1].split(','):
                        if x.find('DEFAULT') > -1: result['DEFAULT'] = x
                        if x.find('TIME') > -1 and x.find('SMSTIME') == -1:
                            tmp = insideParenthesis2('TIME=', line)
                            if tmp == False:
                                tline = line.replace(';;', '').strip() + newline.replace(';;', '').strip()
                                result['TIME'] = insideParenthesis2('TIME=', tline)
                            else:
                                result['TIME'] = tmp
                        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
                
                first = False
                if newline.strip().startswith('SMS') or newline.strip().startswith('9V2'): break
                else:
                    for x in newline.strip().split()[0].split(','):
                        if x.find('DEFAULT') > -1: result['DEFAULT'] = x
                        if x.find('TIME') > -1 and x.find('SMSTIME') == -1:                        
                            tmp = insideParenthesis2('TIME=', newline)
                            if tmp == False:
                                tline = newline.replace(';;', '').strip() + iterator.next().replace(';;', '').strip()
                                result['TIME'] = insideParenthesis2('TIME=', tline)
                            else:
                                result['TIME'] = tmp
                        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
        p += 1 
        if p > pos : break         
    
    return result

def AUTO(pos, line, file, debug):
    '''
    AUTO parser.
    '''
    result = {}
    first = True
    
    if debug: print 'AUTO function called:'
    
    iterator = fileIterator(file) 

    p = 0
    for l in iterator:
        if p == pos:
            while 1:
                newline = iterator.next()
                if first:
                    for x in line.strip().split()[1].split(','):
                        if x.find('EVENT') > -1: result['EVENT'] = insideParenthesis(x)
                        if x.find('STATE') > -1: result['STATE']= insideParenthesis(x)
                        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
                        if x.find('TIME') > -1 and x.find('SMSTIME') == -1: result['TIME'] = afterEqual(x.replace(';;', '').strip())
                first = False
                                
                if newline.strip().startswith('SMS') or newline.strip().startswith('9V2'): break
                else:
                    for x in newline.strip().split()[0].split(','):
                        if x.find('EVENT') > -1: result['EVENT'] = insideParenthesis(x)
                        if x.find('STATE') > -1: result['STATE']= insideParenthesis(x)
                        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
                        if x.find('TIME') > -1 and x.find('SMSTIME') == -1: result['TIME'] = afterEqual(x.replace(';;', '').strip())
        
        p += 1 
        if p > pos : break      
    
    return result

def GSACQ(pos, line, file, debug):
    '''
    GSAQC parser.
    '''
    result = {}
    
    if debug: print 'GASCQ function called:'
    
    for x in line.strip().split()[1].split(','):
        if x.find('ASTID') > -1: result['ASTID'] = insideParenthesis(x)
        if x.find('CENTER') > -1: result['CENTER'] = insideParenthesis(x)
        if x.find('CPNAME') > -1: result['CPNAME'] = insideParenthesis(x)
        if x.find('GS11DEC') > -1: result['GS11DEC'] = insideParenthesis(x)
        if x.find('GS11FGS') > -1: result['GS11FGS'] = insideParenthesis(x)
        if x.find('GS11ID') > -1: result['GS11ID'] = insideParenthesis(x)
        if x.find('GS11MAG') > -1: result['GS11MAG'] = insideParenthesis(x)
        if x.find('GS11RA') > -1: result['GS11RA'] = insideParenthesis(x)
        if x.find('GS11RAD') > -1: result['GS11RAD'] = insideParenthesis(x)
        if x.find('GS1DOM') > -1: result['GS1DOM'] = insideParenthesis(x)
        if x.find('GS21DEC') > -1: result['GS21DEC'] = insideParenthesis(x)
        if x.find('GS21FGS') > -1: result['GS21FGS'] = insideParenthesis(x)
        if x.find('GS21ID') > -1: result['GS21ID'] = insideParenthesis(x)
        if x.find('GS21MAG') > -1: result['GS21MAG'] = insideParenthesis(x)
        if x.find('GS21RA') > -1: result['GS21RA'] = insideParenthesis(x)
        if x.find('GS21RADA') > -1: result['GS21RAD'] = insideParenthesis(x)
        if x.find('NOSLEW') > -1: result['NOSLEW'] = x
        if x.find('NUM_PAIR') > -1: result['NUM_PAIR'] = insideParenthesis(x)
        if x.find('ACQTYPE') > -1: result['ACQTYPE'] = insideParenthesis(x)
        if x.find('FHSTBIAS') > -1: result['FHSTBIAS'] = insideParenthesis(x)
        if x.find('GS11AVG') > -1: result['GS11AVG'] = insideParenthesis(x)
        if x.find('GS11FT') > -1: result['GS11FT'] = insideParenthesis(x)
        if x.find('GS11K1X') > -1: result['GS11K1X'] = insideParenthesis(x)
        if x.find('GS11K1Y') > -1: result['GS11K1Y'] = insideParenthesis(x)
        if x.find('GS11K3X') > -1: result['GS11K3X'] = insideParenthesis(x)
        if x.find('GS11K3Y') > -1: result['GS11K3Y'] = insideParenthesis(x)
        if x.find('GS11ML') > -1: result['GS11ML'] = insideParenthesis(x)
        if x.find('GS21AVG') > -1: result['GS21AVG'] = insideParenthesis(x)
        if x.find('GS21FT') > -1: result['GS21FT'] = insideParenthesis(x)
        if x.find('GS21K1X') > -1: result['GS21K1X'] = insideParenthesis(x)
        if x.find('GS21K1Y') > -1: result['GS21K1Y'] = insideParenthesis(x)
        if x.find('GS21K3X') > -1: result['GS21K3X'] = insideParenthesis(x)
        if x.find('GS21K3Y') > -1: result['GS21K3Y'] = insideParenthesis(x)
        if x.find('GS21ML') > -1: result['GS21ML'] = insideParenthesis(x)
        if x.find('PLNTPRLX') > -1: result['PLNTPRLX'] = insideParenthesis(x)
        if x.find('RCHVM') > -1: result['RCHVM'] = insideParenthesis(x)
        if x.find('TARGETAQ') > -1: result['TARGETAQ'] = insideParenthesis(x)
        if x.find('WHICHACQ') > -1: result['WHICHACQ'] = insideParenthesis(x)
        if x.find('END') > -1: result['END'] = insideParenthesis(x)
        if x.find('START') > -1: result['START'] = insideParenthesis(x)
        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)

    iterator = fileIterator(file) 

    p = 0
    for l in iterator:
        if p == pos:
            while 1:
                newline = iterator.next()
                if newline.strip().startswith('SMS') or newline.strip().startswith('9V2'): break
                else:
                    for x in newline.strip().split()[0].split(','):
                        if x.find('ASTID') > -1: result['ASTID'] = insideParenthesis(x)
                        if x.find('CENTER') > -1: result['CENTER'] = insideParenthesis(x)
                        if x.find('CPNAME') > -1: result['CPNAME'] = insideParenthesis(x)
                        if x.find('GS11DEC') > -1: result['GS11DEC'] = insideParenthesis(x)
                        if x.find('GS11FGS') > -1: result['GS11FGS'] = insideParenthesis(x)
                        if x.find('GS11ID') > -1: result['GS11ID'] = insideParenthesis(x)
                        if x.find('GS11MAG') > -1: result['GS11MAG'] = insideParenthesis(x)
                        if x.find('GS11RA') > -1: result['GS11RA'] = insideParenthesis(x)
                        if x.find('GS11RAD') > -1: result['GS11RAD'] = insideParenthesis(x)
                        if x.find('GS1DOM') > -1: result['GS1DOM'] = insideParenthesis(x)
                        if x.find('GS21DEC') > -1: result['GS21DEC'] = insideParenthesis(x)
                        if x.find('GS21FGS') > -1: result['GS21FGS'] = insideParenthesis(x)
                        if x.find('GS21ID') > -1: result['GS21ID'] = insideParenthesis(x)
                        if x.find('GS21MAG') > -1: result['GS21MAG'] = insideParenthesis(x)
                        if x.find('GS21RA') > -1: result['GS21RA'] = insideParenthesis(x)
                        if x.find('GS21RADA') > -1: result['GS21RAD'] = insideParenthesis(x)
                        if x.find('NOSLEW') > -1: result['NOSLEW'] = x
                        if x.find('NUM_PAIR') > -1: result['NUM_PAIR'] = insideParenthesis(x)
                        if x.find('ACQTYPE') > -1: result['ACQTYPE'] = insideParenthesis(x)
                        if x.find('FHSTBIAS') > -1: result['FHSTBIAS'] = insideParenthesis(x)
                        if x.find('GS11AVG') > -1: result['GS11AVG'] = insideParenthesis(x)
                        if x.find('GS11FT') > -1: result['GS11FT'] = insideParenthesis(x)
                        if x.find('GS11K1X') > -1: result['GS11K1X'] = insideParenthesis(x)
                        if x.find('GS11K1Y') > -1: result['GS11K1Y'] = insideParenthesis(x)
                        if x.find('GS11K3X') > -1: result['GS11K3X'] = insideParenthesis(x)
                        if x.find('GS11K3Y') > -1: result['GS11K3Y'] = insideParenthesis(x)
                        if x.find('GS11ML') > -1: result['GS11ML'] = insideParenthesis(x)
                        if x.find('GS21AVG') > -1: result['GS21AVG'] = insideParenthesis(x)
                        if x.find('GS21FT') > -1: result['GS21FT'] = insideParenthesis(x)
                        if x.find('GS21K1X') > -1: result['GS21K1X'] = insideParenthesis(x)
                        if x.find('GS21K1Y') > -1: result['GS21K1Y'] = insideParenthesis(x)
                        if x.find('GS21K3X') > -1: result['GS21K3X'] = insideParenthesis(x)
                        if x.find('GS21K3Y') > -1: result['GS21K3Y'] = insideParenthesis(x)
                        if x.find('GS21ML') > -1: result['GS21ML'] = insideParenthesis(x)
                        if x.find('PLNTPRLX') > -1: result['PLNTPRLX'] = insideParenthesis(x)
                        if x.find('RCHVM') > -1: result['RCHVM'] = insideParenthesis(x)
                        if x.find('TARGETAQ') > -1: result['TARGETAQ'] = insideParenthesis(x)
                        if x.find('WHICHACQ') > -1: result['WHICHACQ'] = insideParenthesis(x)
                        if x.find('END') > -1: result['END'] = insideParenthesis(x)
                        if x.find('START') > -1: result['START'] = insideParenthesis(x)
                        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
        p += 1 
        if p > pos : break      
    
    return result


def CP22(pos, line, file, debug):
    '''
    CP224 parser.
    '''
    result = {}
    
    if debug: print 'CP22 function called:'
    
    result['CP224'] = line.strip().split()[1].split(',')[1]
    
    for x in line.strip().split()[1].split(','):
        if x.find('CPID') > -1: result['CPID'] = insideParenthesis(x)
        if x.find('TIME') > -1 and x.find('SMSTIME') == -1: result['TIME'] = afterEqual(x)
        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)

    iterator = fileIterator(file) 

    p = 0
    for l in iterator:
        if p == pos:
            while 1:
                newline = iterator.next()
                if newline.strip().startswith('SMS') or newline.strip().startswith('9V2'): break
                else:
                    for x in newline.strip().split()[0].split(','):
                        if x.find('CPID') > -1: result['CPID'] = insideParenthesis(x)
                        if x.find('TIME') > -1 and x.find('SMSTIME') == -1: result['TIME'] = afterEqual(x)
                        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
        p += 1 
        if p > pos : break      
    
    return result
       
def RTS(pos, line, file, debug):
    '''
    RTS parser.
    '''  
    result = {}
    cmd = []
    rtsdata = []
    commandFound = False
    dataFound = False
    
    if debug: print 'RTS function called:'

    result['RTS'] = line.strip().split()[1].split(',')[1]

    for x in line.strip().split()[1].split(','):
        if x.find('INDEX') > -1: result['INDEX'] = insideParenthesis(x)
        if x.find('RTSID') > -1: result['RTSID'] = insideParenthesis(x)
        if x.find('PROPTCEW') > -1: result['PROPTCEW'] = insideParenthesis(x)
        if x.find('PROPTCP') > -1: result['PROPTCP'] = insideParenthesis(x)
        if x.find('PROPTHP') > -1: result['PROPTHP'] = insideParenthesis(x)
        if x.find('PROPTWH') > -1: result['PROPTWH'] = insideParenthesis(x)
        if x.find('SETPT6S') > -1: result['SETPT6sv'] = insideParenthesis(x)
        if x.find('SETPTCEW') > -1: result['SETPTCEW'] = insideParenthesis(x)
        if x.find('SETPTCP') > -1: result['SETPTCP'] = insideParenthesis(x)
        if x.find('SETPTHP') > -1: result['SETPTHP'] = insideParenthesis(x)
        if x.find('SETPTWH') > -1: result['SETPTWH'] = insideParenthesis(x)
        if x.find('SETPTXCP') > -1: result['SETPTXCP'] = insideParenthesis(x)
        if x.find('SETPTXCW') > -1: result['SETPTXCW'] = insideParenthesis(x)
        if x.find('SETPTXHP') > -1: result['SETPTXHP'] = insideParenthesis(x)
        if x.find('SETPTXWH') > -1: result['SETPTXWH'] = insideParenthesis(x)
        if x.find('LOADBY') > -1: result['LOADBY'] = afterEqual(x)
        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
        if x.find('DUMPTIME') > -1: result['DUMPTIME'] = insideParenthesis(x)
        if x.find('OWNER') > -1: result['OWNER'] = insideParenthesis(x)
        if x.find('CMD') > -1: 
            cmd.append(line.replace(';;', '').strip())
            commandFound = True

    iterator = fileIterator(file) 
    
    p = 0
    for l in iterator:
        if p == pos:
            while 1:
                newline = iterator.next()
                if newline.strip().startswith('SMS') or newline.strip().startswith('9V2'): break
                else:
                    for x in newline.strip().split()[0].split(','):
                        if x.find('INDEX') > -1: result['INDEX'] = insideParenthesis(x)
                        if x.find('RTSID') > -1: result['RTSID'] = insideParenthesis(x)
                        if x.find('PROPTCEW') > -1: result['PROPTCEW'] = insideParenthesis(x)
                        if x.find('PROPTCP') > -1: result['PROPTCP'] = insideParenthesis(x)
                        if x.find('PROPTHP') > -1: result['PROPTHP'] = insideParenthesis(x)
                        if x.find('PROPTWH') > -1: result['PROPTWH'] = insideParenthesis(x)
                        if x.find('SETPT6S') > -1: result['SETPT6s'] = insideParenthesis(x)
                        if x.find('SETPTCEW') > -1: result['SETPTCEW'] = insideParenthesis(x)
                        if x.find('SETPTCP') > -1: result['SETPTCP'] = insideParenthesis(x)
                        if x.find('SETPTHP') > -1: result['SETPTHP'] = insideParenthesis(x)
                        if x.find('SETPTWH') > -1: result['SETPTWH'] = insideParenthesis(x)
                        if x.find('SETPTXCP') > -1: result['SETPTXCP'] = insideParenthesis(x)
                        if x.find('SETPTXCW') > -1: result['SETPTXCW'] = insideParenthesis(x)
                        if x.find('SETPTXHP') > -1: result['SETPTXHP'] = insideParenthesis(x)
                        if x.find('SETPTXWH') > -1: result['SETPTXWH'] = insideParenthesis(x)
                        if x.find('LOADBY') > -1: result['LOADBY'] = afterEqual(x)
                        if x.find('SMSTIME') > -1: result['SMSTIME'] = afterEqual(x)
                        if x.find('DUMPTIME') > -1: result['DUMPTIME'] = insideParenthesis(x)
                        if x.find('OWNER') > -1: result['OWNER'] = insideParenthesis(x)
                        if x.find('BEGINDATA') > -1:
                            dataFound = True
                            while 1:
                                nl = iterator.next()
                                if nl.strip().startswith('ENDDATA'): break
                                rtsdata.append(nl.replace(';;','').strip())
                        if x.find('CMD') > -1:
                            cmd.append(newline.replace(';;', '').strip())    
                            commandFound = True
        if p > pos : break
        p += 1
    
    if commandFound: result['CMD'] = cmd
    if dataFound: result['BEGINDATA'] = rtsdata
    
    return result

def TEXT(pos, line, file, debug, savetext):
    '''
    TEXT parser. Seems to be working!
    '''
    
    if savetext:
        out = open('ParsedText.ascii', 'a')
    
    iterator = fileIterator(file) 
    p = 0
    if debug:
        print 'TEXT function called:'
        print pos, line.strip()
    for l in iterator:
        if p == pos:
            linenumber = p + 1
            if savetext: out.write(l)
            while 1:
                newline = iterator.next()
                if newline.strip().startswith('SMS') or newline.strip().startswith('9V2'): break
                else:
                    if savetext: out.write(newline)
                    if debug: print linenumber, newline.strip()
                    linenumber += 1
        if p > pos : break
        p += 1
    
    if savetext: out.close()

#def keyError():
#    print 'ERROR: no matching action found...'
    

def fileIterator(filename):
    '''
    File iterator.
    '''
    for line in open(filename, 'r'):
        yield line

def insideParenthesis(string):
    '''
    Returns the string that was found inside parenthesis.
    '''
    try:
        start = string.find('(')
        stop = string.find(')')
        result = string[start+1:stop]
    except:
        pass
    return result

def insideParenthesis2(before, string):
    '''
    Returns the string that was found inside parenthesis followed the "before" string.
    E.g. TIME=(Mon,1,1,2001) -> before = "TIME=" and the function will return
    string "Mon,1,1,2001".
    '''
    try:
        string = string.replace(';;', '').strip()
        start = string.find(before + '(')
        stop = string[start:].find(')')
        if stop == -1: return False
        tmp = string[start:]
        result = tmp[len(before)+1:stop]
    except:
        pass
    return result

def afterEqual(string):
    '''
    Return the string that follow "=" character.
    '''
    try:
        start = string.find('=')
        result = string[start+1:]
    except:
        pass
    
    return result


if __name__    == '__main__':
    import glob
    import sys
    
    #command line arguments
    (opts, args) = process_args()
    
    #process zero arguments
    if checkZeroArguments(opts) == False:
        process_args(True)
        sys.exit(-9)
    
     #search string
    if opts.smsfile is None:
        print 'You have to specify an input file(s)!'
        sys.exit(-9)
    
    if opts.verbose is True: verbose = True
    else: verbose = False
    
    if opts.debug is True: debug = True
    else: debug = False
    
    if opts.savetext is True: savetext = True
    else: savetext = False
    
    #searches the files    
    smsfiles = glob.glob(opts.smsfile)
    
    #defines a dictionary that holds keys
    #keydict = {'SMSH' : SMS,
    #           'TEXT' : TEXT
    #           }
    
    #main loop begin
    for smsfile in smsfiles:      
        #tests if the file is according to standard...  
        if testSTD(smsfile) == False:
            #not standard
            print 'SMS file does not follow standards...'
            sys.exit(-9)
        
        for pos, line in enumerate(open(smsfile, 'r').readlines()):  
            if line.strip().startswith('SMS'):
                if debug: print '\n'
                #new key, get key
                key = getKey(line)
       
                #takes action for the key
                #tmp = keydict.get(key, keyError)()
                #if tmp == False: break            
                
                if key == 'SMSH':
                    smsdata = SMS(pos, line.strip(), smsfile)
                    if debug: print pos+1, smsdata
                if key == 'GROU':
                    grdata = GROUP(pos, line.strip(), smsfile, debug)
                    if debug: print pos+1, grdata
                if key == 'AUTO':
                    autodata = AUTO(pos, line.strip(), smsfile, debug)
                    if debug: print pos+1, autodata
                if key == 'TEXT':
                    TEXT(pos, line, smsfile, debug, savetext)
                if key == 'RTS,':
                    rtsdata = RTS(pos, line.strip(), smsfile, debug)
                    if debug: print pos+1, rtsdata
                if key == 'RTSC':
                    if debug: print pos+1, 'RTSC'
                if key == 'RTSE':
                    if debug: print pos+1, 'RTSE'
                if key == 'GSAC':
                    gsacdata = GSACQ(pos, line, smsfile, debug)
                    if debug: print  gsacdata
                if key == 'CPMA':
                    cpmarkdata = CPMARK(pos, line.strip(), smsfile, debug)
                    if debug: print pos+1, cpmarkdata
                if key == 'TABL':
                    tabledata = TABLE(pos, line, smsfile, debug)
                    if debug: print pos+1, tabledata
                if key == 'CP22':
                    cp22data = CP22(pos, line, smsfile, debug)
                    if debug: print pos+1, cp22data
                if key == 'SLEW':
                    slewdata = SLEW(pos, line, smsfile, debug)
                    if debug: print pos+1, slewdata
   
            if line.strip().startswith('9V2'):
                if debug: print pos+1, '9V2'
                
                keyV = getKey(line)

                if keyV == 'TEXT':
                    TEXT(pos, line, smsfile, debug, savetext)                
                                
   
        # OPEN Observation list file? (smsdata + .potr)

    
    #write .rev
    
    #write .act
