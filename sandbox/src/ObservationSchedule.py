'''
ABOUT:
         This script can be used to parse instrument specific
         observations from SMS messages. It can also be used to
         generate memory dump schedule from the SMS. 
         
         The script can automatically email generated schedules
         to a given email address.

USAGE:   
         python ObservationSchedule.py [flags]
         where flags can be following
         -v : verbose mode on
         -s sms_number e.g. 09299
         -i instrument_name e.g. STIS
         -d dump_file e.g. 092297e3 
         -o output_file 
         -e email address e.g. niemi@stsci.edu
         
         E.g python ObservationSchedule.py -i STIS -s 09229 -d 092297e3 

DEPENDS:
         Python 2.5 (no 3.0 compatible)

EXITSTA:  
          0: No errors
         -9: No command line flags given

HISTORY:
         Aug 17 2009: Initial Version 0.1
         Nov 20 2009: Version 0.2 (added email sending option)

@author: Sami-Matias Niemi (niemi@stsci.edu) for STScI
'''

__author__ = 'Sami-Matias Niemi'
__version__ = '0.2'


def process_args(just_print_help = False):
    from optparse import OptionParser
    
    usage = 'usage: %prog [options]'
    desc = 'This script can be used to parse instrument specific observations from SMS messages.'
    
    parser = OptionParser(usage = usage, version='%prog ' + __version__, description = desc)
         
    parser.add_option('-v', '--verbose', action='store_true', dest='verbose',
                      help='Verbose mode on. Will print info to stout.')
    parser.add_option('-s', '--sms', dest='sms', 
                      help='SMS file to be processed, e.g. 09229', 
                      metavar='string')
    parser.add_option('-i', '--instrument', dest='instrument', 
                      help='Instrument, O = STIS, L = COS, J = ACS, I = WFC3.', 
                      metavar='string')
    parser.add_option('-d', '--dump', dest='dump',
                      help='Memory dump file e.g. 092297e3.')
    parser.add_option('-o', '--output', dest='output',
                      help='Name of the output file.')
    parser.add_option('-e', '--email', dest='email',
                      help='Email address to send the attachments.')
    if just_print_help:
        parser.print_help()
    else:
        return parser.parse_args()

def checkZeroArguments(opts):
    for x in opts.__dict__:
        if opts.__dict__[x] is not None:
            return True
    return False

def DaystoDates(input):
    '''
    '''
    import datetime
    
    year = datetime.datetime.today().year 
    
    result = []
    for line in input:
        start = datetime.datetime.strptime(str(year) + line[1], '%Y%j')
        end = datetime.datetime.strptime(str(year) + line[3], '%Y%j')
        result.append([line[0],start.isoformat()[5:-9],line[2],end.isoformat()[5:-9],line[4]])
    return result

def DaystoDates2(input):
    '''
    '''
    import datetime
    
    year = datetime.datetime.today().year 
    
    result = []
    for line in input:
        try:
            start = datetime.datetime.strptime(str(year) + line[5].split(':')[0], '%Y%j')
            end = datetime.datetime.strptime(str(year) + line[7].split(':')[0], '%Y%j')
            result.append([line[0][0:5],
                           line[1],
                           line[2],
                           line[3],
                           line[4],
                           start.isoformat()[5:-9] + ' ' + line[5][-8:],
                           end.isoformat()[5:-9]  + ' ' + line[7][-8:],
                           line[8]])
        except:
            print 'A problem on line:', line
    return result


def fixDumps(input):
    
    result=[]
    prop = input[0][0]
    startd = input[0][1]
    startt = input[0][2]
    for line in input:
        if line[0] == prop:
            endd = line[3]
            endt = line[4]
        else:
            result.append([prop, startd, startt, endd, endt])
            prop = line[0]
            startd = line[1]
            startt = line[2]
            endd = line[3]
            endt = line[4]

    #last one is special
    result.append([prop, startd, startt, endd, endt])
    
    return result

def findTitle(input):
    import urllib2
    
    maxLenght = 50
    
    for line in input:
        url = 'http://www.stsci.edu/observing/phase2-public/' + line[0] + '.apt'
        try:
            urldata = urllib2.urlopen(url).read()
        except:
            urldata = '\n<Title>NA</Title>\ntmp'
        for data in urldata.split('\n'):
            if '<Title>' in data:
                start = data.find('<Title>')
                stop = data.find('</Title>')
                title = data[start+len('<Title>'):stop]
                break
        if len(title) > maxLenght:
            title = title[0:maxLenght]
        else:
            title = title + (maxLenght-len(title))*' '
        line[0] = line[0] + ' ' + title
    
    return input
    
def SendEmail(instrument, sms, files, mailto):
    '''
    This function sends an email to mailto address and attaches
    all files in files list to the message.
    '''
    import commands, os
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    
    svr_addr = 'smtp.stsci.edu'
    email_to = mailto.split(',')
    
    email_from = commands.getoutput('whoami') + '@stsci.edu'
    mailcc = email_from

    #Subject
    txt_subject = '%s observation schedules from SMS %s' % (instrument, sms)
    
    # Email header
    msg = MIMEMultipart()
    msg['Subject'] = txt_subject
    msg['From'] = email_from
    msg['To'] = mailto
    msg['Cc'] = mailcc
    
    txt_body = 'Dear Recipient,\n\n Attached are %s observation schedules generated from SMS %s.\n' % (instrument, sms)
    txt_body += '\n\n Cheers,\nSami\n\n\n (This email has been automatically generated by ObservationSchedule.py)\n\n'
    
    # Put email body in email
    msg.attach(MIMEText(txt_body))

    # Add attachment
    for file in files:
        fp = open(file)
        atth = MIMEText(fp.read())
        fp.close()
        atth.add_header('Content-Disposition', 'attachment', filename=file)
        msg.attach(atth)    

    s = smtplib.SMTP(svr_addr)
    s.sendmail(email_from, email_to, msg.as_string())
    s.quit()    


if __name__ == '__main__':    
    '''
    Main program. 
    '''
    import sys
    import urllib2
    
    #define constants
    smsurl = 'http://www.stsci.edu/spss/'
    gaps = '.gaps'
    insts = {'O' : 'STIS',
             'L' : 'COS',
             'J' : 'ACS',
             'I' : 'WFC3'
             }
    
    #command line arguments
    opts, args = process_args()
    
    #process zero arguments
    if checkZeroArguments(opts) == False:
        process_args(True)
        sys.exit(-9)
        
    if opts.verbose is True: verbose = True
    else: verbose = False
    
     #search string
    if opts.sms is None:
        sms = '09229'
        file = smsurl + opts.sms + gaps
        print 'You did not specify SMS file. Will use %s with full address %s.' % (sms, file)
    else:
        sms = opts.sms
        file = smsurl + sms + gaps
        if verbose: print 'The full address to parse is %s.' % file
        
    if opts.instrument is None:
        instrument = 'O'
        if verbose: print 'Instrument was not specified, will use STIS.'
    else:
        if opts.instrument != 'O' or \
           opts.instrument != 'L' or \
           opts.instrument != 'J' or \
           opts.instrument != 'I':
            for key in insts:
                if opts.instrument == insts[key]:
                    instrument = key                  
        else:
            instrument = opts.instrument
        if verbose: print 'Instrument %s was chosen...' % insts[instrument]

    if opts.output is None:
        outfile = '%sObs%s.txt' % (insts[instrument], sms)
        print 'You did not specify output file, will use default %s.' % outfile
    else:
        outfile = opts.output

    if opts.dump is not None:
        dumpurl = smsurl + opts.dump + '.rdo'
        timeurl = smsurl + opts.dump + '-spb.cal'
        dumpdata = urllib2.urlopen(dumpurl).read()
        timedata = urllib2.urlopen(timeurl).read()
    
    #gets data
    smsdata = urllib2.urlopen(file).read()
        
    #find observations
    outd = []
    summary = []
    for line in smsdata.split('\n'):
        try:
            if line.split()[2].startswith(instrument):
                if verbose:
                    print 'Found line "%s" for instrument %s.' % (line, instrument)
                outd.append(line.split())
            if line.strip().startswith('Number of'):
                if 'STIS' in line and instrument == 'O':
                    if verbose: print line
                    summary.append(line)
                if 'COS' in line and instrument == 'L':
                    if verbose: print line
                    summary.append(line)
                if 'ACS' in line and instrument == 'J':
                    if verbose: print line
                    summary.append(line)
                if 'WFC' in line and instrument == 'I':
                    if verbose: print line
                    summary.append(line)
        except: pass

    outdata = findTitle(DaystoDates2(outd))
    #outdata.sort(lambda x, y: cmp(x[0], y[0]))
    

    #generates the output
    hd0 = '#%s observations during SMS %s\n' % (insts[instrument], sms)
    header = '\n#Proposal' + 49*' ' + 'Pri   Obs  Start time (UT)     End time (UT)       GAP\n'
    
    fh = open(outfile, 'w')
    fhcal = open(outfile[:-4] + 'CalibOnly.txt', 'w')
    
    fh.write(hd0)
    fhcal.write('#%s calibration observations during SMS %s' % (insts[instrument], sms))
    fhcal.write(header)
    for line in summary:
        fh.write('#' + line +' (estimated internal real)\n')
    fh.write(header)
    for line in outdata:
        if line[3] == 'CA': fhcal.write('%50s%4s%6s%17s  -%17s%13s\n' % (line[0], line[1], line[3], line[5], line[6], line[7]))
        out =  '%50s%4s%6s%17s  -%17s%13s\n'% (line[0], line[1], line[3], line[5], line[6], line[7])
        fh.write(out)
    fh.close()
    fhcal.close()
    
    files = [outfile, outfile[:-4] + 'CalibOnly.txt']
    
    if opts.dump is not None:
        import datetime
        
        year = datetime.datetime.today().year 
        
        dumpout = []
        for line in dumpdata.split('\n'):
            try:
                if line.split()[7] == insts[instrument]:
                   id = line.split()[5][0:3]
                   for timeline in timedata.split('\n'):
                       if id in timeline:
                           proposal = timeline[timeline.find(id)-6:timeline.find(id)-1]
                           tmp = line.split()
                           dumpout.append([proposal, tmp[0], tmp[1], tmp[2], tmp[3]])
                           break
            except:
                pass
            
        dumps = findTitle(DaystoDates(fixDumps(dumpout)))
        
        of = outfile[:-4] + 'DumpSchedule.txt'
        fh = open(of, 'w')
        hd0 = '#%s memory dumps during SMS %s\n' % (insts[instrument], sms)
        fh.write(hd0)
        fh.write('# Proposal' + 50*' ' + 'Start time (UT)      Stop time (UT)\n')
        for line in dumps:
            out = '%40s%9s%10s%10s%10s\n' % (line[0],line[1],line[2],line[3],line[4])
            fh.write(out)
        fh.close()
        
        files.append(of)
    
    if opts.email is not None:
        SendEmail(insts[instrument], sms, files, opts.email)
        print 'An email has been send to %s' % opts.email
    
    print '%s script finished' % sys.argv[0]
