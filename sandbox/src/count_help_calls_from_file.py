import urllib2

def allindices(string, sub, offset=0):
    listindex = []
    i = string.find(sub, offset)
    while i >= 0:
        listindex.append(i)
        i = string.find(sub, i + 1)
    return listindex


out = {}

data = open('spec.rep_fixed').readlines()

for line in data:
    if line.startswith('<a href='):
        url = line.split('"')[1]
        f = urllib2.urlopen(url)
        urldata = f.read()
        f.close()
        strsearch = 'changed platform to'
        lind = allindices(urldata, strsearch)
        if len(lind) > 0:
            start = lind[-1]
            tmp = urldata[len(strsearch) + start:len(strsearch) + start+10]
            ins = tmp[1:tmp.find('<br')]
            if out.has_key(ins):
                out[ins] += 1
            else:
                out[ins] = 1
        else:
            print 'No platform change found for\n', url
        for line2 in urldata.split():
            if 'changed platform to' in line2:
                inst = line2.split()[-1]
                print inst
                


print out
