import matplotlib
matplotlib.rc('text', usetex = True)
matplotlib.rc('xtick', labelsize=12) 
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rc('lines', markeredgewidth=2.0)
matplotlib.rcParams['lines.linewidth'] = 2.5
matplotlib.rcParams['legend.fontsize'] = 11
matplotlib.rcParams['legend.handlelength'] = 5
matplotlib.rcParams['font.size'] = 13
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
matplotlib.rcParams['legend.fancybox'] = True
matplotlib.use('PDF')

from matplotlib.ticker import MultipleLocator, FormatStrFormatter, NullFormatter, LogLocator
from matplotlib import cm
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
import matplotlib.collections as collections
import pylab as P
import numpy as N
import matplotlib.cm as cm

import pylab as P
import pyfits as PF
import wrapper as w
import IO
import time, glob
import numpy as N

def printSensitivity(data, dispersion, header, outfile):
    '''
    '''
    #effective area
    #area = const*sensitivity/(wave*dlam_dx)
    const = 2.998e10 * 6.626e-27 / 1.0e-8 #h*c*1.e-8 (to convert Ang to cm)
    ar = 45238.93416

    #printing
    wr = open(outfile, 'w')
    wr.write(header+'\n')

    wr2 = open(outfile[:-4]+'_forIHB.txt', 'w')
    wr2.write(header+'\n')


    result = []
    #loop over the data
    for wave, sens in data:
        area = const * sens / (wave * dispersion)
        result.append([wave, sens, area])
        a = sens * ar
        s = a * wave * dispersion / const
        wr.write('%5.1f%15.3e%15.3e%15.3e\n' % (wave, sens, s, a))
        if wave == data[0][0]: wr2.write('%5.0f%15.3e%15.1e%15.2e\n' % (wave, sens, s, a))
        if wave % 50 == 0.0: wr2.write('%5.0f%15.3e%15.1e%15.2e\n' % (wave, sens, s, a))
    wr.close()
    wr2.write('%5.0f%15.3e%15.1e%15.2e\n' % (wave, sens, s, a))
    wr2.close()
    
    return result

def findLatestFile(folder):
    date_file_list = []
    for f in glob.glob(folder):
        print "folder =", f
        # select the type of file, for instance *.jpg or all files *.*
        for file in glob.glob(f + '/*syn.fits'):
            # retrieves the stats for the current file as a tuple
            # (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
            # the tuple element mtime at index 8 is the last-modified-date
            stats = os.stat(file)
            # create tuple (year yyyy, month(1-12), day(1-31), hour(0-23), minute(0-59), second(0-59),
            # weekday(0-6, 0 is monday), Julian day(1-366), daylight flag(-1,0 or 1)) from seconds since epoch
            # note:  this tuple can be sorted properly by date and time
            lastmod_date = time.localtime(stats[8])
            #print image_file, lastmod_date   # test
            # create list of tuples ready for sorting by date
            date_file_tuple = lastmod_date, file
            date_file_list.append(date_file_tuple)
 
    #print date_file_list  # test
    date_file_list.sort()
    date_file_list.reverse()  # newest mod date now first
    return date_file_list

def throughputs(files):
    res = {}
    for file in files:
        print 'Reading file', file
        d = PF.open(file)[1].data
        w = d.field('WAVELENGTH')
        t = d.field('THROUGHPUT')
        mask = t > 0.0
        res[file] = [w[mask], t[mask]]
    return res

def fixThroughputs(data):
    ks = data.keys()
    ks.sort()

    wave = []
    th = []
    for k in ks:
        w, t = data[k]
        wave += w.tolist()
        th += t.tolist()

    result = zip(wave, th)
    #result.sort()

    nodub = {}
    for a, b in result:
        if nodub.has_key(a):
            nodub[a] = nodub.get(a, []) + [b]
        else:
            nodub[a] = [b]
    
    wave, th = [], []
    for x in nodub:
        wave.append(x)
        th.append(N.max(nodub[x]))

    result = zip(wave, th)
    result.sort()
    return result

def FUVsensitivity(G130, G160, G140, output):
    '''
    Plots FUV point-source sensitivities in units of 
    effective area and throughput. Used in Chapter 6
    of COS IHB, version 2.0.
    '''
    pad = 1
    
    ar = 45238.93416 #HST primary area in cm**2
    
    ax = P.subplot(111)
    ax2 = ax.twinx()

    ax2.plot([line[0] for line in G130][pad:-pad],
             [line[1] for line in G130][pad:-pad], 'b-', label='G130M', zorder = 2)
    ax2.plot([line[0] for line in G140][pad:-pad],
             [line[1] for line in G140][pad:-pad], 'r-', label='G140L')
    ax2.plot([line[0] for line in G160][pad:-pad],
             [line[1] for line in G160][pad:-pad], 'g-', label='G160M', zorder = 2)

    ax.plot([line[0] for line in G130][pad:-pad],
            [line[1]*ar for line in G130][pad:-pad], 'b-', label='G130M', lw = 3, zorder = 2)
    ax.plot([line[0] for line in G140][pad:-pad],
            [line[1]*ar for line in G140][pad:-pad], 'r-', label='G140L', lw = 3)
    ax.plot([line[0] for line in G160][pad:-pad],
            [line[1]*ar for line in G160][pad:-pad], 'g-', label='G160M', lw = 3, zorder = 2)
 
    s = [line[1] for line in G130 if line[0] > 1100. and line[0] < 2000.]

    ax.set_ylim(-0.0001, max(s)*1.05*ar)
    ax2.set_ylim(-0.0001, max(s)*1.05)

    ax.set_xlim(900., 2050.)
    ax2.set_xlim(900., 2050.)

    ax.set_xlabel('Wavelength (\AA)')
    ax.set_ylabel('Effective Area (cm$^{2}$)') 
    ax2.set_ylabel('Fractional Throughput') 
    
    xminorLocator = MultipleLocator(50)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)

    ax.yaxis.set_minor_locator(MultipleLocator(500/5))
    ax2.yaxis.set_minor_locator(MultipleLocator(0.01/5))

    ax.set_zorder(20)
    ax2.set_zorder(20)

    P.legend(shadow = True)
    P.savefig(output + '.pdf')
    P.close()

def NUVsensitivity(G185, G225, G285, G230, output):
    '''
    Plots NUV point-source sensitivities in units
    of effective area and throughput. Used in Chapter 6
    of COS IHB, version 2.0.
    '''
    ar = 45238.93416 #HST primary area in cm**2
    split = 3230
    every = 25
    pad = 1
    
    ax = P.subplot(111)
    #P.title('FUV point-source sensitivities')

    #take away the second order
    wave230 = N.array([line[0] for line in G230][::every])
    thru230 = N.array([line[1] for line in G230][::every])
    mask = wave230 < split

    ax2 = ax.twinx()

    ax2.plot([line[0] for line in G185][pad:-pad:every],
             [line[1] for line in G185][pad:-pad:every], 'b-', label='G185M')
    ax2.plot([line[0] for line in G225][pad:-pad:every],
             [line[1] for line in G225][pad:-pad:every], 'g-', label='G225M')
    ax2.plot([line[0] for line in G285][pad:-pad:every],
             [line[1] for line in G285][pad:-pad:every], 'r-', label='G285M')
    ax2.plot(wave230[mask], thru230[mask], 'm-', label='G230L')

    ax.plot([line[0] for line in G185][pad:-pad:every], 
            [line[1]*ar for line in G185][pad:-pad:every], 'b-', label='G185M', lw = 3)
    ax.plot([line[0] for line in G225][pad:-pad:every],
            [line[1]*ar for line in G225][pad:-pad:every], 'g-', label='G225M', lw = 3)
    ax.plot([line[0] for line in G285][pad:-pad:every],
            [line[1]*ar for line in G285][pad:-pad:every], 'r-', label='G285M', lw = 3)
    ax.plot(wave230[mask], thru230[mask]*ar, 'm-', label='G230L', lw = 3)

    ms = N.max(N.array([line[1] for line in G230]))
    ax.set_ylim(-0.0001, ms*1.05*ar)
    ax2.set_ylim(-0.0001, ms*1.05)

    ax.set_xlim(1400., 3300.)
    ax2.set_xlim(1400., 3300.)

    ax.set_xlabel('Wavelength (\AA)')
    ax.set_ylabel('Effective Area (cm$^{2}$)') 
    ax2.set_ylabel('Fractional Throughput') 
    
    xminorLocator = MultipleLocator(500/5)
    xminorFormattor = NullFormatter()
    ax.xaxis.set_minor_locator(xminorLocator)
    ax.xaxis.set_minor_formatter(xminorFormattor)

    ax.yaxis.set_minor_locator(MultipleLocator(100/5))
    ax2.yaxis.set_minor_locator(MultipleLocator(0.005/5))

    P.legend(shadow = True)
    P.savefig(output + '.pdf')
    P.close()

def multiplyThroughputs(data, ota_mirror, fuv_mirror = '/grp/hst/cdbs/comp/cos/cos_mirrora_005_syn.fits', NUV = False):
    ota = PF.open(ota_mirror)[1].data
    otaw = ota.field('WAVELENGTH')
    otat = ota.field('THROUGHPUT')

    waveto = N.array([line[0] for line in data])
    th = N.array([line[1] for line in data])
    #interpolated throughput
    otathroughput = N.interp(waveto, otaw, otat)
    #multiply throughputs together
    thout = th * otathroughput
    
#    if NUV:
        #MIRRORA needs to be taken into account as well
#        mirrora = PF.open(fuv_mirror)[1].data
#        mirroraw = mirrora.field('WAVELENGTH')
#        mirrorat = mirrora.field('THROUGHPUT')
        #interplotion
#        mth = N.interp(waveto, mirroraw, mirrorat)
        #multiply with the mirror a
#        thout *= mth

    return zip(waveto, thout)

def Chapeter15Sensitivity(data, boafile, dispersion, grating, title, output):
    '''
    Plots the point-source sensitivities for Chapter 15.
    '''
    pad = 1
    every = 20

    boaFactor = 100.
    
    wave = N.array([x[0] for x in data])
    thr = N.array([x[1] for x in data])
    #remove the second order
    if grating == 'G230':
        mask = wave < 3220
        wave = wave[mask]
        thr = thr[mask]
        
    #from throughput to sensitivi
    const = 2.998e10 * 6.626e-27 / 1.0e-8
    ar = 45238.93416
    sens = thr * ar * wave * dispersion / const

    boa = PF.open(boafile)[1].data
    boaw = boa.field('WAVELENGTH')
    boat = boa.field('THROUGHPUT')
    #interplotion
    boathmlply = N.interp(wave, boaw, boat)
    #multiply with the mirror a
    boasens = boathmlply * boaFactor * thr * (ar * wave * dispersion / const)
    if grating == 'G130':
        mask = wave < 1200
        boasens[mask] = 0.
   
    #plot
    ax1 = P.subplot(111)
    
    #P.title(title)
    
    ax1.set_xlabel('Wavelength (\AA)')
    ax1.set_ylabel('counts pixel$^{-1}$ s$^{-1}$ / (erg s$^{-1}$ cm$^{-2}$ \AA$^{-1}$)')      

    ax1.plot(wave[pad:-pad:every], sens[pad:-pad:every],
             'r-', label='PSA', lw = 3)
    if grating == 'G140':
        extra = 10
        ax1.plot(wave[pad:-pad:every], extra*sens[pad:-pad:every],
                 'r--', label='PSAx % i' % int(extra), lw = 3)

    ax1.plot(wave[pad:-pad:every], boasens[pad:-pad:every],
             'g--', label='BOA x %i' % int(boaFactor), lw = 3)

    ax1.legend(shadow = True, fancybox = True)

    if grating == 'G225':
        ax1.set_ylim(N.min(sens), N.max(sens)*1.13)
    else:
        ax1.set_ylim(N.min(sens), N.max(sens)*1.02)

    m = ax1.get_yticks()[1] - ax1.get_yticks()[0]
    yminorLocator = MultipleLocator(m/5)
    yminorFormattor = NullFormatter()
    ax1.yaxis.set_minor_locator(yminorLocator)
    ax1.yaxis.set_minor_formatter(yminorFormattor)      
    
    if grating == 'G140':
        P.xlim(900, 2150)
        xminorLocator = MultipleLocator(50)
        xminorFormattor = NullFormatter()
        ax1.xaxis.set_minor_locator(xminorLocator)
        ax1.xaxis.set_minor_formatter(xminorFormattor) 
    elif grating == 'G230':
        P.xlim(1400, 3300)
        xminorLocator = MultipleLocator(100)
        xminorFormattor = NullFormatter()
        ax1.xaxis.set_minor_locator(xminorLocator)
        ax1.xaxis.set_minor_formatter(xminorFormattor)
    elif grating == 'G130':
        P.xlim(1000, 1480)
        xminorLocator = MultipleLocator(25)
        xminorFormattor = NullFormatter()
        ax1.xaxis.set_minor_locator(xminorLocator)
        ax1.xaxis.set_minor_formatter(xminorFormattor)
    else:
        xminorLocator = MultipleLocator(25)
        xminorFormattor = NullFormatter()
        ax1.xaxis.set_minor_locator(xminorLocator)
        ax1.xaxis.set_minor_formatter(xminorFormattor)

    ax1.set_yticks(ax1.get_yticks()[1:]) #deletes the lowest y axis tick!
    
    P.savefig(output + '.pdf')
    P.close()

def Chapeter15SensitivityNewG130M(data, boafile, dispersion, grating, title, output):
    '''
    Plots the point-source sensitivities for Chapter 15.
    '''
    pad = 1
    every = 20

    boaFactor = 50.
    
    wave = N.array([x[0] for x in data])
    thr = N.array([x[1] for x in data])

    mask = wave < 1200
    wave = wave[mask]
    thr = thr[mask]

    #from throughput to sensitivi
    const = 2.998e10 * 6.626e-27 / 1.0e-8
    ar = 45238.93416
    sens = thr * ar * wave * dispersion / const

    boa = PF.open(boafile)[1].data
    boaw = boa.field('WAVELENGTH')
    boat = boa.field('THROUGHPUT')
    #interplotion
    boathmlply = N.interp(wave, boaw, boat)
    #multiply with the mirror a
    boasens = boathmlply * boaFactor * thr * (ar * wave * dispersion / const)
   
    #plot
    ax1 = P.subplot(111)
    
    #P.title(title)
    
    ax1.set_xlabel('Wavelength (\AA)')
    ax1.set_ylabel('counts pixel$^{-1}$ s$^{-1}$ / (erg s$^{-1}$ cm$^{-2}$ \AA$^{-1}$)')      

    ax1.semilogy(wave[pad:-pad:every], sens[pad:-pad:every],
             'r-', label='PSA', lw = 3)
    #ax1.semilogy(wave[pad:-pad:every], boasens[pad:-pad:every],
    #         'g--', label='BOA x %i' % int(boaFactor), lw = 3)

    ax1.legend(shadow = True, fancybox = True)

    ax1.set_ylim(N.min(sens), N.max(sens)*1.02)

    #m = ax1.get_yticks()[1] - ax1.get_yticks()[0]
    #yminorLocator = MultipleLocator(m/5)
    #yminorFormattor = NullFormatter()
    #ax1.yaxis.set_minor_locator(yminorLocator)
    #ax1.yaxis.set_minor_formatter(yminorFormattor)      
    
    P.xlim(900, 1190)
    xminorLocator = MultipleLocator((ax1.get_xticks()[1] - ax1.get_xticks()[0])/5)
    xminorFormattor = NullFormatter()
    ax1.xaxis.set_minor_locator(xminorLocator)
    ax1.xaxis.set_minor_formatter(xminorFormattor)

    ax1.set_yticks(ax1.get_yticks()[1:]) #deletes the lowest y axis tick!
    
    P.savefig(output + '.pdf')
    P.close()

def main():
    #constants
    FUVdispersionReferenceFile = 't9e1307kl_disp.fits' 
    NUVdispersionReferenceFile = 't9e1307ll_disp.fits'
    COSrefFiles = '/grp/hst/cdbs/lref/'
    outputfolder = './Graphics/'
    sd = './sensitivities/'
    sinp = '/grp/hst/cdbs/comp/cos/'
    ota_mirror = '/grp/hst/cdbs/comp/ota/hst_ota_007_syn.fits'
    boa = sinp + 'cos_boa_004_syn.fits'
    
    #reading
    read = IO.COSHBIO(COSrefFiles, 'temp.tmp')
    
    #reading in some data
    #Dispersion solutions for FUV.
    #These are needed for effective areas
    FUVd = read.FITSTable(FUVdispersionReferenceFile, 1)
    FUVtemp = PF.getdata('/grp/hst/cos/calibration/synphot_files/new_disp.fits')
    G130Mdisp = [x[5][1] for x in FUVd if x[0] == 'FUVA' and x[1] == 'G130M' and x[2] == 'PSA' and x[3] == 1309]
    G130MSdisp = [x[5][1] for x in FUVtemp if x[0] == 'FUVB' and x[1] == 'G130M' and x[2] == 'PSA' and x[3] == 1055]
    G160Mdisp = [x[5][1] for x in FUVd if x[0] == 'FUVA' and x[1] == 'G160M' and x[2] == 'PSA' and x[3] == 1600]
    G140Ldisp = [x[5][1] for x in FUVd if x[0] == 'FUVA' and x[1] == 'G140L' and x[2] == 'PSA' and x[3] == 1230]
    #Dispersion solution for NUV
    NUVd = read.FITSTable(NUVdispersionReferenceFile, 1)
    G185Mdisp = N.mean([x[5][1] for x in NUVd if x[1] == 'G185M' and x[2] == 'PSA'])
    G225Mdisp = N.mean([x[5][1] for x in NUVd if x[1] == 'G225M' and x[2] == 'PSA'])
    G285Mdisp = N.mean([x[5][1] for x in NUVd if x[1] == 'G285M' and x[2] == 'PSA'])
    G230Ldisp = N.mean([x[5][1] for x in NUVd if x[1] == 'G230L' and x[2] == 'PSA'])
    
    #read in sensitivities, synphot files have wavelength and throughput
    #find the last synphots for each grating
    #for g130m new modes must be taken into account
    g1 = glob.glob(sinp + 'cos_mcp_g130mc*_008_syn.fits')
    g1.append(sinp + 'cos_mcp_g130mc1055_001_syn.fits')
    g1.append(sinp + 'cos_mcp_g130mc1096_001_syn.fits')
    G130Ms = fixThroughputs(throughputs(g1))
    G140Ls = fixThroughputs(throughputs(glob.glob(sinp + 'cos_mcp_g140lc*_008_syn.fits')))
    G160Ms = fixThroughputs(throughputs(glob.glob(sinp + 'cos_mcp_g160mc*_008_syn.fits')))
    G185Ms = fixThroughputs(throughputs(glob.glob(sinp + 'cosncm3_g185mc*_006_syn.fits')))
    G225Ms = fixThroughputs(throughputs(glob.glob(sinp + 'cosncm3_g225mc*_006_syn.fits')))
    G230Ls = fixThroughputs(throughputs(glob.glob(sinp + 'cosncm3_g230lc*_006_syn.fits')))
    G285Ms = fixThroughputs(throughputs(glob.glob(sinp + 'cosncm3_g285mc*_006_syn.fits')))
    
    #take into acount all mirrors in the lightpath
    G130Msens = multiplyThroughputs(G130Ms, ota_mirror)
    G140Lsens = multiplyThroughputs(G140Ls, ota_mirror)
    G160Msens = multiplyThroughputs(G160Ms, ota_mirror)
    
    G185Msens = multiplyThroughputs(G185Ms, ota_mirror, NUV = True)
    G225Msens = multiplyThroughputs(G225Ms, ota_mirror, NUV = True)
    G285Msens = multiplyThroughputs(G285Ms, ota_mirror, NUV = True)
    G230Lsens = multiplyThroughputs(G230Ls, ota_mirror, NUV = True)
    
    #FUV files
    tmp = [(a, b) for a, b in G130Msens if a < 1201]
    hdr = ' Wavel   Throughput   Sensitivity   Effective Area'
    _tmp = printSensitivity(tmp, G130MSdisp[0], '#G130MS' + hdr, sd + 'G130MSsensitivity.txt')   
    G130 = printSensitivity(G130Msens, G130Mdisp[0], '#G130M' + hdr, sd + 'G130Msensitivity.txt')   
    G160 = printSensitivity(G160Msens, G160Mdisp[0], '#G160M' + hdr, sd + 'G160Msensitivity.txt')   
    G140 = printSensitivity(G140Lsens, G140Ldisp[0], '#G140L' + hdr, sd + 'G140Lsensitivity.txt')  
    #FUV plot
    FUVsensitivity(G130, G160, G140, outputfolder + 'FUVSensitivity')
    
    #NUV files
    G185 = printSensitivity(G185Msens, G185Mdisp, '#G185M' + hdr, sd + 'G185Msensitivity.txt')   
    G225 = printSensitivity(G225Msens, G225Mdisp, '#G225M' + hdr, sd + 'G225Msensitivity.txt')        
    G285 = printSensitivity(G285Msens, G285Mdisp, '#G285M' + hdr, sd + 'G285Msensitivity.txt')
    G230 = printSensitivity(G230Lsens, G230Ldisp, '#G230L' + hdr, sd + 'G230Lsensitivity.txt')
    #NUV plot
    NUVsensitivity(G185, G225, G285, G230, outputfolder +'NUVSensitivity')
    
    #individual plots
    #NUV
    Chapeter15Sensitivity(G185, boa, G185Mdisp, 'G185', 'G185M', outputfolder + 'G185Msensitivity')
    Chapeter15Sensitivity(G225, boa, G225Mdisp, 'G225', 'G225M', outputfolder + 'G225Msensitivity')
    Chapeter15Sensitivity(G285, boa, G285Mdisp, 'G285', 'G285M', outputfolder + 'G285Msensitivity')
    Chapeter15Sensitivity(G230, boa, G230Ldisp, 'G230', 'G230L', outputfolder + 'G230Lsensitivity')
    #FUV
    Chapeter15Sensitivity(G130, boa, G130Mdisp[0], 'G130', 'G130M', outputfolder + 'G130Msensitivity')
    Chapeter15Sensitivity(G160, boa, G160Mdisp[0], 'G160', 'G160M', outputfolder + 'G160Msensitivity')
    Chapeter15Sensitivity(G140, boa, G140Ldisp[0], 'G140', 'G140L', outputfolder + 'G140Lsensitivity')
    #new G130M modes
    Chapeter15SensitivityNewG130M(G130, boa, G130MSdisp[0], 
                                  'G130', 'G130MS',
                                  outputfolder + 'G130MSsensitivity')

if __name__ == '__main__':
    main()