import os
import numpy as N
#Sami's repository
import db.sqlite as sq
    
if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    path = hm + '/Dropbox/Research/Herschel/runs/reds_zero/'
    db = 'sams.db'

    query2 = '''select galprop.mstar, galprop.tmerge
                from FIR, galprop where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.spire250_obs > 20e-3 and
                FIR.spire250_obs < 1e6
                '''
    #get data, S_250 > 5 mJy
    data = sq.get_data_sqliteSMNfunctions(path, db, query2)
    xd2 = data[:,0]
    yd2 = data[:,1]

    #the fraction of no mergers?
    nm2 = len(yd2[yd2 < 0.0]) / float(len(yd2)) * 100.

    #print out some statistics
    print len(yd2)
    print 'Mean tmerge of SPIRE detected galaxies', N.mean(yd2[yd2 > 0.0])
    print
    print 'Max tmerge of SPIRE detected galaxies', N.max(yd2[yd2 > 0.0])
    print
    print 'Fraction of SPIRE that have experienced a merger', 100.-nm2

######################
    query2 = '''select galprop.mstar, galprop.tmerge
                from FIR, galprop where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id and
                FIR.pacs160_obs > 10e-3 and
                FIR.spire250_obs < 1e6
                '''
    #get data, S_250 > 5 mJy
    data = sq.get_data_sqliteSMNfunctions(path, db, query2)
    xd2 = data[:,0]
    yd2 = data[:,1]

    #the fraction of no mergers?
    nm2 = len(yd2[yd2 < 0.0]) / float(len(yd2)) * 100.

    #print out some statistics
    print len(yd2)
    print 'Mean tmerge of PACS detected galaxies', N.mean(yd2[yd2 > 0.0])
    print
    print 'Max tmerge of PACS detected galaxies', N.max(yd2[yd2 > 0.0])
    print
    print 'Fraction of PACS that have experienced a merger', 100.-nm2
