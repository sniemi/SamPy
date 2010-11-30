import fileinput as f
import glob as g

#NOTE: This is so stupidly written that one should redo!

def redshift_from_scale(scale):
    return 1./scale - 1

def scale_from_redshift(redshift):
    return 1 /(redshift + 1.)


#this is for Bolshoi's tree outputs
#scale : redshift
#times = {0.4984 : 1.0064,
#         0.2464 : 3.0584,
#         0.1983 : 4.0429,
#         0.1323 : 6.5586,
#         0.1084 : 8.2251,
#         0.1623 : 5.1614,
#         0.3303 : 2.0276}

times = {0.9943 : 0.0057}

files = g.glob('/Users/niemi/Desktop/Research/Bolshoi/bolshoi_isotrees/*.dat')

columns = {'mvir' : 9,
           'orig_mvir' : 10,
           'phantom' : 8,
           'scale': 0
           }

log = open('DMmfhalo.log', 'w')
#this is so stupidly done.
# key in times loop should be at the last if statement level!!!
for key in times:
    mvir = []
    orig_mvir = []
    phantom = []
    i = 0
    for file in files:
        i += 1
        for line in f.input(file):
            if not line.startswith('#'):
                tmp = line.split()
                if round(float(tmp[columns['scale']]),4) == round(key, 4):
                    mvir.append(float(tmp[columns['mvir']]))
                    orig_mvir.append(float(tmp[columns['orig_mvir']]))
                    phantom.append(float(tmp[columns['phantom']]))
         #just for testing
         #break

    log.write('Redshift = %f' % round(times[key], 4))
    log.write('%i files were processed...' % i)
    log.write('In total, %i dark matter haloes were found' % len(mvir))

    file ='DMhaloesz%.2f' % round(times[key], 4)
    op = file.replace('.', '_') + '.txt'

    out = open(op, 'w')
    for a, b, c in zip(mvir, orig_mvir, phantom):
        string = '%f %f %f\n' % (a, b, c)
        out.write(string)
    out.close()

    log.write('File %s has been written...\n\n\n' % op)

log.close()
