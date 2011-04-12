import fileinput as f
import glob as g

def findDMhaloes(files,
                 times,
                 columns):

    for file in files:
        print 'Processing: %s' % file
        for line in f.input(file):
            if not line.startswith('#'):
                tmp = line.split()
                for key in times:
                    if round(float(tmp[columns['scale']]), 4) == round(key, 4):
                        a = float(tmp[columns['mvir']])
                        b = float(tmp[columns['orig_mvir']])
                        c = float(tmp[columns['phantom']])
                        string = '%f %f %f\n' % (a, b, c)
                        filen = 'DMhaloes%s.txt' % (str(times[key]).replace('.', '_'))
                        out = open(filen, 'a')
                        out.write(string)
                        out.close()
         #just for testing
         #break

if __name__ == '__main__':
    #this is for Bolshoi's tree outputs
    #scale : redshift
    #times = {0.4984 : 1.0064,
    #         0.2464 : 3.0584,
    #         0.1983 : 4.0429,
    #         0.1323 : 6.5586,
    #         0.1084 : 8.2251,
    #         0.1623 : 5.1614,
    #         0.3303 : 2.0276}
   
    times = {0.9434 : 0.059995760017,
             0.9073 : 0.102171277417,
             0.8324 : 0.201345506968,
             0.7663 : 0.304971943103,
             0.7124 : 0.403705783268,
             0.6643 : 0.505343971097,
             0.6223 : 0.606941989394,
             0.5864 : 0.705320600273,
             0.5564 : 0.797268152408,
             0.5283 : 0.892863903085,
             0.4984 : 1.00642054575}

    files = g.glob('/Users/niemi/Desktop/Research/Bolshoi/bolshoi_isotrees/*.dat')
    
    columns = {'mvir' : 9,
               'orig_mvir' : 10,
               'phantom' : 8,
               'scale': 0
               }

    findDMhaloes(files,
                 times,
                 columns)
