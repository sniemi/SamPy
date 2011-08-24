"""
Pulls out data from the SMAKCED wiki page
and parses it into a NumPy array, which is
easy to sort and manipulate.

:requires: NumPy
:requires: BeautifulSoup

:date: Created on Mar 26, 2010

:version: 0.1

:author: Sami-Matias Niemi
"""
import urllib2, csv
import numpy as N
from parsing.BeautifulSoup import BeautifulSoup

__author__ = 'Sami-Matias Niemi'
__version__ = '0.1'

class Smakced():
    """
    A Class related to SMAKCED collaboration wiki page.
    """

    def __init__(self, url, table):
        """
        Constructor

        :param: url: url address of the page
        :type url: string
        :param: table: name of the table
        :type table: string
        """
        self.url = url
        self.table = table
        self.address = self.url + self.table

    def getData(self):
        """
        Retrieve data from the SMAKCED web page.
        
        :return: retrieved raw data
        """
        hand = urllib2.urlopen(self.address)
        data = hand.readlines()
        hand.close()
        return data

    def parseTable(self, data):
        """
        Parses html table data using BeautifulSoup.
        Note that table number has been hard coded.
        The SMAKCED wiki page returns several "tables".
        
        :param: data: data that has been retrieved with the getData method

        :return: array containing table entries
        """
        tablenumber = 3
        result = []
        soup = BeautifulSoup(''.join(data))
        t = soup.findAll('table')
        table = t[tablenumber]
        rows = table.findAll('tr')
        for tr in rows:
            line = []
            cols = tr.findAll('td')
            hdr = tr.findAll('th')
            for th in hdr:
                tmp = str(th.find(text=True))
                x = tmp.replace('&nbsp;', '')
                line.append(x)
            for td in cols:
                tmp = str(td.find(text=True))
                x = tmp.replace('&nbsp;', '')
                line.append(x)
            result.append(line)
        return result

    def writeToFile(self, data, output):
        """
        Writes an html page that contains tables to a file in ascii format.
        Uses BeautifulSoup for parsing tables.
        
        :note: This method is untested.
        
        :param: data: data that has been retrieved with the getData method
        :param: output: name of the output file
        """
        g = open(output, 'w')
        soup = BeautifulSoup(''.join(data))
        t = soup.findAll('table')
        for table in t:
            g.write('\nNew Table:\n')
            rows = table.findAll('tr')
            for tr in rows:
                cols = tr.findAll('td')
                hdr = tr.findAll('th')
                for th in hdr:
                    try:
                        g.write(th.find(text=True))
                        g.write(',')
                    except: pass
                for td in cols:
                    try:
                        g.write(td.find(text=True))
                        g.write(',')
                    except: pass
                g.write("\n")
        g.close()

if __name__ == '__main__':
    """
    Run when the script is run from the command line.
    """
    #table address
    smackedurl = 'http://smakced.pbworks.com'
    tableName1 = '/Virgo1'

    #class instance
    SM1 = Smakced(smackedurl, tableName1)
    #download data
    data = SM1.getData()
    #parse table
    table = SM1.parseTable(data)
    #to a Numpy array
    dt = N.array(table)

    #data limitations, only objects that are marked
    #to be observed at NOT2010 i.e. SMN targets
    mask = dt[:, 6] == 'NOT2010'

    #output my targets to a file
    output = open('SMNTargets.txt', 'w')
    dump = csv.writer(output)
    dump.writerow(dt[0])
    dump.writerows(dt[mask])
    output.close()

    #make NOT TCS compatible object list file
    output = open('NOTobjectlist.txt', 'w')
    for line in dt[mask]:
        str = 'VCC' + line[0].split()[0] + ' ' + line[8].replace(' ', ':')
        str += ' ' + line[9].replace(' ', ':')
        str += ' 2000 0 0 ' + line[13]
        output.write(str + '\n')
    output.close()

    #make a file that can be pasted to the visibility plot software
    output = open('visibility_plot.txt', 'w')
    for line in dt[mask]:
        str = 'VCC' + line[0].split()[0] + ' ' + line[8] + ' ' + line[9]
        output.write(str + '\n')
    output.close()

    print 'All done...'