'''
Created on Dec 8, 2009

@author: niemi
'''
def RMS(data):
    return N.sqrt(N.mean(data)**2 + N.std(data)**2)

def CombineFlat(self, filelist):
    '''
    Combines created images to form a final flats.
    '''
    #hard coded value
    siglim = 5
    list = filelist
    
    nimage = len(list)

    #make zero arrays
    added_flux = N.zeros((1024, 1024))
    added_error = N.zeros((1024, 1024))
    added_dq = N.zeros((1024, 1024))
    weights = N.zeros((1024, 1024))
            
    fluxall = N.zeros((1024, 1024, nimage))
    errorall = N.zeros((1024, 1024, nimage))
    flagsall = N.zeros((1024, 1024, nimage))

    for i, file in enumerate(list):
        fh = PF.open(file)
        fluxin = fh[1].data
        errorin = fh[2].data
        flagsin = fh[3].data
        fh.close()
        
        if i > 1: flagsin[225:801, 180] = flagsin[225:801, 180] + 1024
        
        fluxall[:,:,i] = fluxin.copy()
        errorall[:,:,i] = errorin.copy()
        flagsall[:,:,i] = flagsin.copy()

    for ix in range(1024):
        for iy in range(1024):
            added_dq[iy, ix] = N.min(flagsall[iy, ix, :])
            ig = N.where((flagsall[iy, ix, :] == 0) & (errorall[iy, ix,:] > 0.0))
            if len(ig[0]) <= 0:
                added_flux[iy, ix] = 1.
                added_error[iy,ix] = 0.1
            elif len(ig[0]) <= 2:
                added_flux[iy,ix] = N.sum(fluxall[iy,ix,ig]/errorall[iy,ix,ig]**2)/N.sum(1./errorall[iy,ix,ig]**2)
                added_error[iy,ix] = N.sqrt(1./N.sum(1./errorall[iy,ix,ig]**2))
            else:
                center = N.median(fluxall[iy,ix,ig])
                std = N.max(errorall[iy,ix,ig])
                igg = N.where(N.abs(fluxall[iy,ix,ig] - center) < siglim*std)
                if len(igg[0]) >= 1:
                    cov = N.where(((flagsall[iy, ix, :] == 0) & (errorall[iy, ix,:] > 0.0)) & (N.abs(fluxall[iy,ix,:] - center) < siglim*std))
                    added_flux[iy,ix] = N.sum(fluxall[iy,ix,cov]/errorall[iy,ix,cov]**2)/N.sum(1./errorall[iy,ix,cov]**2)
                    added_error[iy,ix] = N.sqrt(1./N.sum(1./errorall[iy,ix,cov]**2))
                else:
                    added_flux[iy,ix] = center
                    added_error[iy,ix] = std
    
    #low and med res copies
    flat_l = added_flux.copy()
    flat_m = added_flux.copy()
    err_l = added_error.copy()
    err_m = added_error.copy()
    dq_l = added_dq.copy()
    dq_m = added_dq.copy()

    # flag and patch dust motes (dq=1024)                                                                                                                                  
    m_mote = N.ones((1024,1024), dtype = N.int)
    l_mote = N.ones((1024,1024), dtype = N.int)
    l_mote, xlcen, ylcen, radl = self._badspot(l_mote, 'G430L')
    m_mote, xmcen, ymcen, radm = self._badspot(m_mote, 'G430M')
    
    # since basic flats are from m mode data, have to also replace area covered by                                                                                         
    # m-mode motes with "good" l mode data to produce l mode pflat.                                                                                                        
    l_mote_ext = l_mote*m_mote

    # flag dust motes with 1024                                                                                                                                            
    dq_l[l_mote_ext == 0] = dq_l[l_mote_ext == 0] + 1024
    dq_m[m_mote == 0] = dq_m[m_mote == 0] + 1024

    # leave m-mode modes alone, but paste into l_mode motes from another file                                                                                                                                                                  
    templ_f = PF.open('/grp/hst/cdbs/oref/k2910262o_pfl.fits')[1].data
    templ_e = PF.open('/grp/hst/cdbs/oref/k2910262o_pfl.fits')[2].data
    l_mote_loc = N.where(l_mote_ext == 0)
    flat_l[l_mote_loc] = templ_f[l_mote_loc]
    err_l[l_mote_loc] = templ_e[l_mote_loc]

    # write individual extensions of low and high disp file
    templ = '/grp/hst/cdbs/oref/n491401ho_pfl.fits' #
    tempm = '/grp/hst/cdbs/oref/n491401ko_pfl.fits' #'n491401eo_pfl.fits'
    self._writeCombinedFits(flat_l, err_l, dq_l, headerl, templ, raws, self.output + 'coadd_comb_reject_l.fits')          
    self._writeCombinedFits(flat_m, err_m, dq_m, headerm, tempm, raws, self.output + 'coadd_comb_reject_m.fits')

    #make some extra plots
    self._plot50(flat_l, xlcen, ylcen, radl, 'coadd_comb_reject_l')
    self._plot50(flat_m, xmcen, ymcen, radm, 'coadd_comb_reject_m')
    
    #print out some information
    print '\nSTDEV of L-mode flat is %f' % N.std(flat_l)
    #print 'while the mean and the stardard error are %f and %f, respectively.' % (N.mean(flat_l),  Mstats.stderr(flat_l))
    print '\nSTDEV of M-mode flat is %f' % N.std(flat_m)
    #print 'while the mean and the stardard error are %f and %f, respectively.\n' % (N.mean(flat_m),  Mstats.stderr(flat_m))


if __name__ == '__main__':
    out = '../out/'
    #read in file lists
    cleanG1 = open('g430m_50ccd_gain1_crj.txt').readlines()
    cleanG4 = open('g430m_50ccd_gain4_crj.txt').readlines()
    
    sl0 = open('g430m_52x2_crj.txt').readlines()
    slm3 = open('g430m_52x2m3640_crj.txt').readlines()
    slp3 = open('g430m_52x2p3640_crj.txt').readlines()
    slm7 = open('g430m_52x2m7300_crj.txt').readlines()
    slp7 = open('g430m_52x2p7300_crj.txt').readlines()
    
    flat50G1 = out + 'ppG430M_50CCD_gain1_flat.fits'
    flat50G4 = out + 'ppG430M_50CCD_gain4_flat.fits'
    
    