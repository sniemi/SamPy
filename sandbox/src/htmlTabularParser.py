'''
Created on Sep 2, 2009

@author: niemi
'''

import BeautifulSoup
import urllib2

url = 'http://www.stsci.edu/institute/org/ins/cos_stis/projects/UserSupport/BOP/cos_spec_limits.html'
url2 = 'http://www.stsci.edu/institute/org/ins/cos_stis/projects/UserSupport/BOP/cos_ima_limits.html'


g = open('html_table.txt','w')

#change this
data = urllib2.urlopen(url2).read()

data = data[data.find('<!-- start PAGE CONTENT -->'): data.find('<!-- end PAGE CONTENT -->')]
soup = BeautifulSoup.BeautifulSoup(data)

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
                g.write('    ')
            except: pass        
        for td in cols:
            try:
                g.write(td.find(text=True))
                g.write('    ')
            except: pass
        g.write("\n")

g.close()
