import os
import numpy as N
#Sami's repository
import db.sqlite as sq
    
if __name__ == '__main__':
    #find the home directory, because the output is to dropbox 
    #and my user name is not always the same, this hack is required.
    hm = os.getenv('HOME')
    #constants
    #path = hm + '/Dropbox/Research/Herschel/runs/reds_zero/'
    path = hm + '/Research/Herschel/runs/big_volume/'
    db = 'sams.db'

    mergetimelimit = 0.25

#    print 'Calculating merger statistics from:'
#    print path + db
#    print 'with mergetimelimit =', mergetimelimit
#
#    query2 = '''select galprop.tmerge, galprop.tmajmerge
#                from FIR, galprop where
#                galprop.mstar > 10.0 and
#                FIR.z >= 2.0 and
#                FIR.z < 4.0 and
#                FIR.spire250_obs < 1e6 and
#                FIR.gal_id = galprop.gal_id and
#                FIR.halo_id = galprop.halo_id
#                '''
#    #get data, massive galaxies
#    data = sq.get_data_sqliteSMNfunctions(path, db, query2)
#    tmerge = data[:,0]
#    tmajor = data[:,1]
#    #masks
#    nomergeMask = tmerge < 0.0
#    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
#    majorsMask2 = (tmajor > mergetimelimit)
#    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) & \
#                  (majorsMask == False) & (majorsMask2 == False)
#    mergersMask2 = (nomergeMask == False) & (majorsMask == False) & \
#                   (mergersMask == False) & (majorsMask2 == False)
#    #the fraction of no mergers?
#    nm2 = len(tmerge[tmerge < 0.0]) / float(len(tmerge)) * 100.
#    nm3 = len(tmajor[tmajor < 0.0]) / float(len(tmajor)) * 100.
#    nm4 = len(tmajor[majorsMask]) / float(len(tmajor)) * 100.
#    #print out some statistics
#    print 'Number of galaxies and Poisson error:', len(tmerge), N.sqrt(len(tmerge))
#    print 'Mean tmerge of M_star > 10**10 galaxies', N.mean(tmerge[tmerge > 0.0])
#    print 'Max tmerge of M_star > 10**10 galaxies', N.max(tmerge[tmerge > 0.0])
#    print 'Fraction of M_star > 10**10 have experienced a merger', 100.-nm2
#    print 'Fraction of M_star > 10**10 have experienced a major merger', 100.-nm3
#    print 'Fraction of M_star > 10**10 who have experienced their major merger within mergetimlimit', nm4
#    print

###############################################################################
        
    query2 = '''select galprop.tmerge, galprop.tmajmerge
                from FIR, galprop where
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.spire250_obs < 1e6 and
                FIR.spire250_obs > 1e-40 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                '''
    #get data
    data = sq.get_data_sqliteSMNfunctions(path, db, query2)
    tmerge = data[:,0]
    tmajor = data[:,1]
    #masks
    nomergeMask = tmerge < 0.0
    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
    majorsMask2 = (tmajor > mergetimelimit)
    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) & \
                  (majorsMask == False) & (majorsMask2 == False)
    mergersMask2 = (nomergeMask == False) & (majorsMask == False) & \
                   (mergersMask == False) & (majorsMask2 == False)
    #the fraction of no mergers?
    nm2 = len(tmerge[tmerge < 0.0]) / float(len(tmerge)) * 100.
    nm3 = len(tmajor[tmajor < 0.0]) / float(len(tmajor)) * 100.
    nm4 = len(tmajor[majorsMask]) / float(len(tmajor)) * 100.
    #print out some statistics
    print 'Number of galaxies and Poisson error:', len(tmerge), N.sqrt(len(tmerge))
    print 'Mean tmerge of all galaxies', N.mean(tmerge[tmerge > 0.0])
    print 'Max tmerge of all galaxies', N.max(tmerge[tmerge > 0.0])
    print 'Fraction of all galaxies that have experienced a merger', 100.-nm2
    print 'Fraction of all galaxies that have experienced a major merger', 100.-nm3
    print 'Fraction of all galaxies that who have experienced their major merger within mergetimlimit', nm4
    print
    
    import sys; sys.exit()

###############################################################################
        
    query2 = '''select galprop.tmerge, galprop.tmajmerge
                from FIR, galprop where
                FIR.spire250_obs > 20e-3 and
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.spire250_obs < 1e6 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                '''
    #get data, S_250 > 20 mJy
    data = sq.get_data_sqliteSMNfunctions(path, db, query2)
    tmerge = data[:,0]
    tmajor = data[:,1]
    #masks
    nomergeMask = tmerge < 0.0
    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
    majorsMask2 = (tmajor > mergetimelimit)
    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) & \
                  (majorsMask == False) & (majorsMask2 == False)
    mergersMask2 = (nomergeMask == False) & (majorsMask == False) & \
                   (mergersMask == False) & (majorsMask2 == False)
    #the fraction of no mergers?
    nm2 = len(tmerge[tmerge < 0.0]) / float(len(tmerge)) * 100.
    nm3 = len(tmajor[tmajor < 0.0]) / float(len(tmajor)) * 100.
    nm4 = len(tmajor[majorsMask]) / float(len(tmajor)) * 100.
    #print out some statistics
    print 'Number of galaxies and Poisson error:', len(tmerge), N.sqrt(len(tmerge))
    print 'Mean tmerge of S_250 > 20 mJy galaxies', N.mean(tmerge[tmerge > 0.0])
    print 'Max tmerge of S_250 > 20 mJy galaxies', N.max(tmerge[tmerge > 0.0])
    print 'Fraction of S_250 > 20 mJy have experienced a merger', 100.-nm2
    print 'Fraction of S_250 > 20 mJy have experienced a major merger', 100.-nm3
    print 'Fraction of S_250 > 20 mJy who have experienced their major merger within mergetimlimit', nm4
    print

###############################################################################
    query2 = '''select galprop.tmerge, galprop.tmajmerge
                from FIR, galprop where
                FIR.spire250_obs > 5e-3 and
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.spire250_obs < 1e6 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                '''
    #get data, S_250 > 5 mJy
    data = sq.get_data_sqliteSMNfunctions(path, db, query2)
    tmerge = data[:,0]
    tmajor = data[:,1]
    #masks
    nomergeMask = tmerge < 0.0
    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
    majorsMask2 = (tmajor > mergetimelimit)
    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) & \
                  (majorsMask == False) & (majorsMask2 == False)
    mergersMask2 = (nomergeMask == False) & (majorsMask == False) & \
                   (mergersMask == False) & (majorsMask2 == False)
    #the fraction of no mergers?
    nm2 = len(tmerge[tmerge < 0.0]) / float(len(tmerge)) * 100.
    nm3 = len(tmajor[tmajor < 0.0]) / float(len(tmajor)) * 100.
    nm4 = len(tmajor[majorsMask]) / float(len(tmajor)) * 100.
    #print out some statistics
    print 'Number of galaxies and Poisson error:', len(tmerge), N.sqrt(len(tmerge))
    print 'Mean tmerge of S_250 > 5 mJy galaxies', N.mean(tmerge[tmerge > 0.0])
    print 'Max tmerge of S_250 > 5 mJy galaxies', N.max(tmerge[tmerge > 0.0])
    print 'Fraction of S_250 > 5 mJy have experienced a merger', 100.-nm2
    print 'Fraction of S_250 > 5 mJy have experienced a major merger', 100.-nm3
    print 'Fraction of S_250 > 5 mJy who have experienced their major merger within mergetimlimit', nm4
    print

###############################################################################
    query2 = '''select galprop.tmerge, galprop.tmajmerge
                from FIR, galprop where
                FIR.pacs160_obs > 10e-3 and
                FIR.z >= 2.0 and
                FIR.z < 4.0 and
                FIR.spire250_obs < 1e6 and
                FIR.gal_id = galprop.gal_id and
                FIR.halo_id = galprop.halo_id
                '''
    #get data
    data = sq.get_data_sqliteSMNfunctions(path, db, query2)
    tmerge = data[:,0]
    tmajor = data[:,1]
    #masks
    nomergeMask = tmerge < 0.0
    majorsMask = (tmajor > 0.0) & (tmajor <= mergetimelimit)
    majorsMask2 = (tmajor > mergetimelimit)
    mergersMask = (tmerge > 0.0) & (tmerge <= mergetimelimit) & \
                  (majorsMask == False) & (majorsMask2 == False)
    mergersMask2 = (nomergeMask == False) & (majorsMask == False) & \
                   (mergersMask == False) & (majorsMask2 == False)
    #the fraction of no mergers?
    nm2 = len(tmerge[tmerge < 0.0]) / float(len(tmerge)) * 100.
    nm3 = len(tmajor[tmajor < 0.0]) / float(len(tmajor)) * 100.
    nm4 = len(tmajor[majorsMask]) / float(len(tmajor)) * 100.
    #print out some statistics
    print 'Number of galaxies and Poisson error:', len(tmerge), N.sqrt(len(tmerge))
    print 'Mean tmerge of PACS S_160 > 10 mJy galaxies', N.mean(tmerge[tmerge > 0.0])
    print 'Max tmerge of PACS S_160 > 10 mJy galaxies', N.max(tmerge[tmerge > 0.0])
    print 'Fraction of PACS S_160 > 10 mJy have experienced a merger', 100.-nm2
    print 'Fraction of PACS S_160 > 10 mJy have experienced a major merger', 100.-nm3
    print 'Fraction of PACS S_160 > 10 mJy who have experienced their major merger within mergetimlimit', nm4
