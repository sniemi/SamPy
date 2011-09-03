"""
This file contains MillenniumData -class. It can be used  to fetch data from the Millennium Simulation database.

File also contains a small example.

:author: Sami-Matias Niemi (sami@not.iac.es)!
"""
import os

class MillenniumData():
    """
    This class was designed to fetch data from the Millennium Simulation database.
    Input for the constructor is SQL query to be performed. Syntax must be valid
    SQL.  
    """

    def __init__(self, sql):
        self.user = 'sniemi'
        self.passwd = 'XB48D682'
        self.url = 'http://www.g-vo.org/MyMillennium?action=doQuery&SQL='
        self.cookies = '--cookies=on --keep-session-cookies --save-cookies=cookie.txt --load-cookies=cookie.txt'
        self.sql = sql

    def fetchdata(self):
        command = 'wget --http-user=%s --http-passwd=%s %s -O - \"%s%s\"'\
        % (self.user, self.passwd, self.cookies, self.url, self.sql)
        cin, cout, cerr = os.popen3(command)
        res = ''.join(cout.readlines())
        cerrr = ''.join(cerr.readlines())
        return res, cin, cerrr

    def savetofile(self, data, filename):
        output = open(filename, 'a')
        output.write(data)
        output.close()

    def savetofileseparated(self, data, filename, separator):
        output = open(filename, 'a')
        for line in data:
            output.write(line.replace(',', separator))
        output.close()

    def dataonly(self, data, splitvalue):
        temp = []
        for line in data.split():
            if len(line) > splitvalue: temp.append(line)
        return temp

    def iterateGalaxies(self, galaxies):
        for galaxy in galaxies: yield galaxy

if __name__ == '__main__':
    sql = """select *
             from DGalaxies..Bower2006a
                 where snapnum=63
                   and ix between 5 and 6
                   and iy between 5 and 6
                   and iz between 5 and 6"""

    outputfile = 'msdata.file'
    outputspace = 'msdataspacesep.file'
    outputlog = 'msdata.log'
    separator = ' '
    splitvalue = 25

    MS = MillenniumData(sql)
    res, cin, cer = MS.fetchdata()
    MS.savetofile(res, outputfile)
    MS.savetofile(cer, outputlog)
    MS.savetofileseparated(res, outputspace, separator)
    onlygalaxies = MS.dataonly(res, splitvalue)

    iter = MS.iterateGalaxies(onlygalaxies)
    header = iter.next()

    print "The header of the retrieved data:"
    print header
    print

    while True:
        try:
            temp = iter.next().split(',')[52]
        except StopIteration:
            break
        print "r_SDSS_Obs: " + temp

    print '\n%i characters were retrieved and saved to a file %s\n' % (len(res), outputfile)
