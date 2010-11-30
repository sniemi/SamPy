if __name__ == '__main__':
    from MSdata import *
    import numpy as N
    import sys

    data = []

    #ID
    datar = N.loadtxt("EllipticalsT4.out", comments = "#", usecols=(0,1,9), dtype=long)
    #lets get rid off the subhaloes
    indices = N.where(datar[:,2] == 0)
    idlist = datar[indices]
    
    study = len(idlist[:,0])
    
    splitvalue = 25
    merger = 0
    tmp = 0
    
    print '\nIn total %i galaxies found from the file...' % len(datar[:,0])
    print 'However, only %i galaxies will be studied...' % study
    
    safety = open('identitytime.safety' ,'w')
    
    for id in idlist:
        print '\nChecking halo %s with last progenitor Id of %s (%4.1f per cent done)' % (id[0], id[1], (100.*float(tmp)/float(study)))
        if id[0] != id[1]: 
            sql = """
    select D.galaxyId,
        P1.redshift as p1_reds,
        P2.snapnum as p2_snap,
        D.mag_b as d_mag_b,
        D.mag_bbulge as d_mag_bBulge,
        D.sfr as d_sfr,
        P1.mag_b as p1_mag_b,
        P2.mag_b as p2_mag_b,
        D.stellarMass as d_STmass,
        P1.stellarMass as p1_STmass,
        P2.stellarMass as p2_STmass,
        P1.bulgeMass as p1_bulgeMass,
        P1.mvir as p1_mvir,
        P2.bulgeMAss as p2_bulgeMass,
        P2.mvir as p2_mvir
    from MPAgalaxies..DeLucia2006a P1,
        MPAgalaxies..DeLucia2006a P2,
        MPAgalaxies..DeLucia2006a D
    where P1.SNAPNUM=P2.SNAPNUM
        and P1.galaxyId between %s and %s
        and P2.galaxyId between %s and %s
        and P1.descendantId = D.galaxyId
        and P2.descendantId = D.galaxyId
        and P1.descendantId = P2.descendantId
        and P1.galaxyId < P2.galaxyId
        and P1.stellarMass >= .2*D.stellarMass
        and P2.stellarMass >= .2*D.stellarMass
    order by P1.redshift""" % (id[0], id[1], id[0], id[1])
            #Px are progenitors
            
            #equal size: and P2.stellarMass / P1.stellarMass > 0.5 or even 0.55?
            
            MS = MillenniumData(sql)
            res, cin, cer = MS.fetchdata()   
            
            onlygalaxies = MS.dataonly(res, splitvalue)
            header = onlygalaxies[0]        
     
            if cer.find("ERROR") != -1: 
                print 'Something wrong with the SQL part. Will print out the error:\n'
                print cer
                print '\nWill save the data collected so far to dump.file...'
                r = open('dump.file','w')
                r.write('#' + header + '\n')
                for line in data:
                    r.write(line + '\n')
                r.close()
                sys.exit(-99)
                 
            mergers = len(onlygalaxies)-1
            print 'Found %i major merger(s)...' % mergers
            tmp += 1
    
            if mergers > 0:
                #this will save all number data
                #data.append(onlygalaxies[1:])
                #we only need the latest event!
                data.append(onlygalaxies[1])
                merger += 1
                safety.write(onlygalaxies[1] + '\n')
                safety.flush()
    
    safety.close()
    
    outputfile = 'identitytime.file'
    r = open(outputfile, 'w')
    r.write('#' + header + '\n')
    try: 
        for line in data:
            r.write(line + '\n')
    finally:
        r.close()
    
    print '\n%i field ellipticals were studied.' % study
    print '%i (should be same as %i) of them had major mergers!' % (merger, len(data))
    print 'meaning %4.3f per cent...' % (100.*float(merger)/float(study))

