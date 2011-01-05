'''
This script works as a wrapper to create plots for the COS instrument handbook.
Boolean variables in the main program can be set to False to limit the number
of plots.

Calculation of zodiacal and earth shine background requires the use of local
fits files (Zodi.fits and earthshine.fits). If these files cannot be found
the S/N ration related plots of chapter 15 cannot be done.

This wrapper should always be accompanied with plotting.py which contains
a plotting class. This class holds all the plotting functions and is required
for running this wrapper.

@note: This wrapper superseeds wrapper.py

@author: Sami-Matias Niemi (niemi@stsci.edu) for STScI
'''
__author__ = 'Sami-Matias Niemi'
__version__ = '1.6'

import numpy as N
import pyfits as PF
import math, sys

def calculateSTMAGlim(global_limit, grating, sensitivity, gain = 1, NUV = False):
    '''
    A fugdge factor of 96% for encircled energy fraction is being used.
    These integration times are so short that we can ignore everything
    else but source counts.
    '''
    fudge = 0.96 #this is aperture transmission and encircled energy fraction
    #countrate = sensitivity * flux / gain * fudge
    limit = global_limit / 15000. * 1.1
    flux = limit * gain / (sensitivity * fudge)
    if NUV: flux *= 6.*2
    stlim = fluxToSTMag(flux)
    print 'STMAG brightness limit is %4.2f for %s' % (stlim, grating)
    return stlim

def getDispersion(segment, grating, cenwave, fppos, fileData):
    '''
    Return dispersion relation of a given configuration.
    '''  
    for line in fileData:
        if line[0].strip() == segment.strip() and \
           line[1].strip() == grating.strip() and \
           line[2].strip() == 'PSA' and \
           line[3] == cenwave: #and  \
           #line[4] == fppos:
           return line[5]
           break
    
    return [-1.0,]

def getZodiacalBackground(wavelength, width):
    '''
    Returns the Zodiacal light background value at given wavelength range.
    Note: Uses hard coded file Zodi.fits, which must be present in the folder
    this function is called!
    '''
    try:
        zodidata = PF.open(localFolder + 'Zodi.fits')[1].data
    except:
        print 'No Zodi.fits file found from your working directory!'
        print 'Cannot get an estimate for zodiacal light background... will exit!'
        sys.exit()
    
    try:
        return N.mean([y for x, y in zodidata if x > wavelength - width and x < wavelength + width])
    except:
        return 22.7e-10

def getEarthShineBackground(wavelength, width):
    '''
    Returns the Earth Shine background value at given wavelength range.
    Note: Uses hard coded file earthshine.fits, which must be present in the folder
    this function is called!
    '''
    try:
        earthdata = PF.open(localFolder + 'earthshine.fits')[1].data
    except:
        print 'No earthshine.fits file found from your working directory!'
        print 'Cannot get an estimate for earth shine background... will exit!'
        sys.exit()        
    
    try:
        return N.mean([y for x, y in earthdata if x > wavelength - width and x < wavelength + width])
    except:
        return 50.0e-10

def signalToNoise(sensitivity, flux, time, Npix, Bsky, Bdet, gain = 1.):
    '''
    Calculates signal to noise ratio when following variables are given:
    sensitivity, flux, exposure time, number of pixels, sky backgound, detector background, and gain.
    For photon counters gain = 1. Number of pixels is used for the background calculations while the
    sensitivity is used for calculating the total number of counts. 
    '''
    counts = sensitivity * flux / gain
    up = counts * time
    down = (counts * time) + (Npix * (Bsky + Bdet) * time)
    SNR = up * down**(-1./2.)
    return SNR

def signalToNoisePerResel(sensitivity, flux, time, resel, Bsky, Bdet, gain = 1.):
    '''
    Calculates signal to noise ratio using total counts in resolution element.
    Input:
    sensitivity, flux, time, resel, Bsky, Bdet, gain = 1.
    Returns:
    Signal-to-noise ratio, source counts, source noise, dark current counts, sky, background, total noise
    '''
    counts = sensitivity * flux * resel / gain
    up = counts * time
    dark = Bdet * time * resel
    sky = Bsky * time * resel
    down = (counts * time) + (resel * (Bsky + Bdet) * time)
    SNR = up * down**(-1./2.)
    
    return SNR, up, math.sqrt(up), dark, sky, dark + sky, math.sqrt(dark) + math.sqrt(sky) + math.sqrt(up)

def selectSensitivity(wavelength, sensitivity, requiredWave, width):
    '''
    Returns:
    Mean of the sensitivity within required wavelength region.
    '''
    return N.mean([y for x, y in zip (wavelength, sensitivity) if x > requiredWave - width and x < requiredWave + width])

def fluxToSTMag(flux):
    '''
    Returns:
    NumPy array of ST magnitudes
    '''
    return -2.5*N.log10(N.array(flux)/3.63e-9)

def STMagToFlux(STMag):
    '''
    Returns:
    NumPy array of fluxes.
    '''
    return 10.**(N.array(STMag)/-2.5)*3.63e-9

def FUVSensitivityDataMod(data):
    '''
    Modifies the table containing FUV sensitivity data. Goes through the table and
    pulls out wavelength and sensitivity information. Goes through both sides (A and B).
    For the latter channel checks that the wavelength is not 50A, which is inside the gap.
    Makes sure that the saved wavelengths are not smaller than the first recorded  wavelength
    of the side A.
    The function could be made faster with array manipulations rather than looping
    through the data.
    '''
    result = []
    for x, y in zip(data[0][4], data[0][5]):
        result.append([x, y])
    for i, j in zip(data[1][4], data[1][5]):
        if i != 50. and i < result[0][0]:
            result.append([i, j])
    result.sort()
    return result

def NUVSensitivityDataMod(data, smoothing, median = True):
    '''
    Manipulates NUV sensitivity data. Pulls out all central wavelengths for all three
    stripes. Arranges the data with ascending wavelength.
    '''
    result = [[x, y] for x, y in zip(data[0][4], data[0][5])]
    for i in range(len(data)-1):
        result += ([x,y] for x, y in zip(data[i+1][4], data[i+1][5]))
    result.sort()
    return NUVSensitivityDataMod2(result, smoothing, median)

def NUVSensitivityDataMod2(data, stepsize, Median = True):
    '''
    Manipulates NUV sensitivity data. Finds either the min flux 
    value with given wavelength or takes the median of fluxes
    at given wavelength. 
    '''
    result = []
    wave = int(data[0][0])
    flux = [data[0][1],]
    result.append([data[0][0], data[0][1]])
    for wave1, flux1 in data:
        if wave1 < wave + stepsize and wave1 > wave - stepsize:
            if Median:
                flux.append(flux1)
        else:
            if Median:
                result.append([wave1, N.median(flux)])
            else:
                result.append([wave1, N.min(flux)])
            flux = [flux1,]
            wave = int(wave1) + stepsize
    result.append([data[-1][0], data[-1][1]])
    return result

def collapseSpectrumY(imagedata, yline, width):
    '''
    Collapses the spectrum in y (spatial for FUV) direction and 
    sums pixels over.
    @param yline: gives the center point of the spectrum.
    @param width: gives the number of (plus and minus) pixels summed 
    over in spatial direction.
    @note: This could be done easier with numpy.sum()
    '''
    collapsed = imagedata[yline, :]
    for i in range(width):
        collapsed += imagedata[yline-i-1, :] + imagedata[yline+i+1, :]
    return collapsed

def collapseSpectrumX(imagedata, xline, width):
    '''
    Collapses the spectrum in x (COS dispersion) direction and 
    sums pixels over.
    @param xline: gives the center point of the spectrum.
    @param width: gives the number of (plus and minus) pixels summed 
    over in dispersion direction.
    @note: This could be done easier with numpy.sum()
    '''
    collapsed = imagedata[:, xline]
    for i in range(width):
        collapsed += imagedata[:,xline-i-1] + imagedata[:,xline+i+1]
    return collapsed

def setCoordinatesImagingData(imagedata, x = -1, y = -1):
    '''
    Sets coordinates to imaging data.
    @return:  x, y, value found from image data
    '''
    result = []
    j = y
    for column in imagedata:
        j += 1
        i = x
        for value in column:
            i += 1
            result.append([i, j, value])
    return result
    
def printOutSensitivity(data, dispersion, header, outfile, stepsize = 50):
    '''
    '''
    #effective area
    #area = const*sensitivity/(wave*dlam_dx)
    const = 2.998e10 * 6.626e-27 / 1.0e-8 #h*c*1.e-8 (to convert Ang to cm)

    #printing
    wr = open(outfile, 'w')
    wr.write(header+'\n')
    tmp = NUVSensitivityDataMod(data, 0.55)
    
    #first row
    w0 = tmp[0][0]
    s0 = tmp[0][1]
    area = const * s0 / (w0 * dispersion)
    wr.write('%5i%15.3e%15.3e\n' % (int(tmp[0][0]), tmp[0][1], area))
    
    result = []
    #loop over the data
    for wave, sens in tmp:
        if int(wave) % 8 == 0:
            result.append([wave, const * sens / (wave * dispersion)])
        if int(wave) % stepsize == 0:
            area = const * sens / (wave * dispersion)
            wr.write('%5i%15.3e%15.3e\n' % (int(wave), sens, area))
    
    #last row
    wr.write('%5i%15.3e%15.3e\n' % (int(tmp[-1][0]), tmp[-1][1], const*tmp[-1][1] / (tmp[-1][0]*dispersion)))
    wr.close()
    
    return result
    
if __name__ == '__main__':    
    '''
    Main program. All plotting related lines; constants, 
    creation of instances, reading data, data manipulation
    and finally plotting. Each plot has been isolated by a
    comment block.
    '''
    import sys    
    import os
    import IO
    import Logger as L
    import plotting as P
    import numpy as N
    import glob
    import synphotSensitivity as ss

    #sets some files
    #change these when new reference files come available!
    FUVsensitivityReferenceFile = 'u4t18348l_phot.fits'
    NUVsensitivityReferenceFile = 't9h1220sl_phot.fits'
    FUVflatReferenceFile = 'n9n20182l_flat.fits'
    NUVflatReferenceFile = 's7g1700tl_flat.fits'
    FUVdispersionReferenceFile = 'u6s1320ql_disp.fits' #'t9e1307kl_disp.fits' 
    NUVdispersionReferenceFile = 'u1t1616pl_disp.fits' #'t9e1307ll_disp.fits'
    
    #Other hard coded filenames.
    #Change if necessary!
    FIG71Data = 'FIG71.data'
    PSFdataFile = 'laa701a8q_flt.fits'  #GROUND: 'psf.fits'
   
    #/cdbs/comp/cos -files
    #change when new comes available
    MirrorAImagingSensFile = 'fullthruAtab.fits' #GROUND: 'cos_mirrora_004_syn.fits'
    BOATransmissionFile = 'cos_boa_004_syn.fits'

    #Spatial profile plot files
    G130MASP = 'la9r01d7q_corrtag_a.fits'
    G130MBSP = 'la9r01d7q_corrtag_b.fits'

    #sets paths, works from NFS mount Macs or Solaris and Linux boxes
    COSrefFiles = '/grp/hst/cdbs/lref/'
    COScomFiles = '/grp/hst/cdbs/comp/cos/'
    localFolder = './data/'
    outputfolder = 'Graphics'
    sd = './sensitivities/'

    try: os.mkdir(outputfolder)
    except: pass
    outputfolder = './' + outputfolder + '/'

    #local = True
    computedPhot = True
    #referenceFiles = True
    #PSFs = True
    Chapter13 = True
    #LSF = True
    #SpatialProfiles = True

    #set booleans for different plots; False -> not plotted    
    local = False
    #computedPhot = False
    referenceFiles = False
    PSFs = False
    #Chapter13 = False
    SpatialProfiles = False
    LSF = False

    #hard coded COS geocoronal average intensity background values
    geo1216 = 3.05e-13
    geo1302 = 2.85e-14
    geo1356 = 2.50e-15
    geo2417 = 1.50e-15
    #hard coded COS dark values per pixel
    #For latest values, see:
    #http://www.stsci.edu/hst/observatory/etcs/etc_user_guide/1_ref_9_background.html
    # @todo: one could automize this part so that the latest dark would be parsed
    darkFUV = 0.0000022 #OLD: 3.*7.2e-7
    darkNUV = 3.0e-4 #OLD: (11./34.)*2.1e-4
    #ETC box height
    SNbox = 47 #FUV
    SNboxNUV = 8

    #If set to False, output will be save to a file rather than presented on screen
    verbose = True
    debug = True

    #sets constants
    FEFU = 10.**-15.
    FUVresel = 6.
    NUVresel = 3.
    
    # smoothing factor (wave - sm < x < wave + sm) for sensitivity plots
    smoothing = 5.
    g230lsm = 25.

    #creates plotting and reading instances
    plot = P.Plotting('.pdf')
    log = L.Logger('Plotting.output', verbose)
    if referenceFiles or Chapter13: read = IO.COSHBIO(COSrefFiles, 'temp.tmp')
    if computedPhot: readcom = IO.COSHBIO(COScomFiles, 'tempcom.tmp')
    if local: readlocal = IO.COSHBIO(localFolder, 'templocal.tmp')
    if PSFs: readPSF = IO.COSHBIO(localFolder, 'tempPSF.tmp')

    #Begins plotting...
    if referenceFiles:
        log.write('Starting to create plots based on reference files...\n')
########################################################################################
        #Dispersion solutions for FUV.
        #These are needed for effective areas
        FUVd = read.FITSTable(FUVdispersionReferenceFile, 1)
        G130Mdisp = [x[5][1] for x in FUVd if x[0] == 'FUVA' and x[1] == 'G130M' and x[2] == 'PSA' and x[3] == 1309]
        G160Mdisp = [x[5][1] for x in FUVd if x[0] == 'FUVA' and x[1] == 'G160M' and x[2] == 'PSA' and x[3] == 1600]
        G140Ldisp = [x[5][1] for x in FUVd if x[0] == 'FUVA' and x[1] == 'G140L' and x[2] == 'PSA' and x[3] == 1230]
########################################################################################        
        #Fig 5.2, page 40
        #Only for default central wavelengths
        #reads data, manipulates variable names and plots the figure
        FUVsensData = read.FITSTable(FUVsensitivityReferenceFile, 1)
    
        #All central wavelengths are default except for G140L (default 1230)   
        G130Msens = [line for line in FUVsensData if line[1].strip() == 'G130M' and 
                     line[2] == 1309 and line[3].strip() == 'PSA']
        G160Msens = [line for line in FUVsensData if line[1].strip() == 'G160M' and
                     line[2] == 1600 and line[3].strip() == 'PSA']
        G140Lsens = [line for line in FUVsensData if line[1].strip() == 'G140L' and
                     line[2] == 1105 and line[3].strip() == 'PSA']
        
        G130M = FUVSensitivityDataMod(G130Msens)
        G140L = FUVSensitivityDataMod(G140Lsens)
        G160M = FUVSensitivityDataMod(G160Msens)

        #Effective Area 
        #Prints out the FUV sensitivity files
        G130 = printOutSensitivity(G130Msens, G130Mdisp[0], '#G130M wave sens Aeff', sd + 'G130Msensitivity.txt')   
        G160 = printOutSensitivity(G160Msens, G160Mdisp[0], '#G160M wave sens Aeff', sd + 'G160Msensitivity.txt')   
        G140 = printOutSensitivity(G140Lsens, G140Ldisp[0], '#G140L wave sens Aeff', sd + 'G140Lsensitivity.txt')   
     
        #OLD sensitivity plot
        plot.FUVsensitivityOLD([pair[0] for pair in G130M], [FEFU*FUVresel*pair[1] for pair in G130M], 
                            [pair[0] for pair in G140L], [FEFU*FUVresel*pair[1] for pair in G140L], 
                            [pair[0] for pair in G160M], [FEFU*FUVresel*pair[1] for pair in G160M],
                            outputfolder + 'FUVSensitivityOLD')

        #new sensitivity plot with effective area
        plot.FUVsensitivity(G130, G160, G140, outputfolder + 'FUVSensitivity')


########################################################################################
        #A new fig, same as 5.2 but through BOA
        #reads data, manipulates variable names and plots the figure
        #FUVsensData = read.FITSTable(FUVsensitivityReferenceFile, 1)
    
        #All central wavelengths are default except for G140L (default 1230)   
        G130MBsens = [line for line in FUVsensData if line[1].strip() == 'G130M' and 
                     line[2] == 1309 and line[3].strip() == 'BOA']
        G160MBsens = [line for line in FUVsensData if line[1].strip() == 'G160M' and
                     line[2] == 1600 and line[3].strip() == 'BOA']
        G140LBsens = [line for line in FUVsensData if line[1].strip() == 'G140L' and
                     line[2] == 1105 and line[3].strip() == 'BOA']
        
        G130MB = FUVSensitivityDataMod(G130MBsens)
        G140LB = FUVSensitivityDataMod(G140LBsens)
        G160MB = FUVSensitivityDataMod(G160MBsens)
     
        plot.FUVsensitivityBOA([pair[0] for pair in G130MB], [FEFU*FUVresel*pair[1] for pair in G130MB], 
                               [pair[0] for pair in G140LB], [FEFU*FUVresel*pair[1] for pair in G140LB], 
                               [pair[0] for pair in G160MB], [FEFU*FUVresel*pair[1] for pair in G160MB],
                               outputfolder +'FUVBOASensitivity')

#########################################################################################
        #Dispersion solution for NUV
        #These are needed for effective area plots
        NUVd = read.FITSTable(NUVdispersionReferenceFile, 1)
        G185Mdisp = N.mean([x[5][1] for x in NUVd if x[1] == 'G185M' and x[2] == 'PSA'])
        G225Mdisp = N.mean([x[5][1] for x in NUVd if x[1] == 'G225M' and x[2] == 'PSA'])
        G285Mdisp = N.mean([x[5][1] for x in NUVd if x[1] == 'G285M' and x[2] == 'PSA'])
        G230Ldisp = N.mean([x[5][1] for x in NUVd if x[1] == 'G230L' and x[2] == 'PSA'])
#########################################################################################
        #Fig 5.3, page 41
        #reads data, manipulates data and plots the figure
        NUVsensData = read.FITSTable(NUVsensitivityReferenceFile, 1)
    
        G185Msens = [line for line in NUVsensData if line[1].strip() == 'G185M' and 
                     line[3].strip() == 'PSA']
        G225Msens = [line for line in NUVsensData if line[1].strip() == 'G225M' and 
                     line[3].strip() == 'PSA']
        G285Msens = [line for line in NUVsensData if line[1].strip() == 'G285M' and 
                     line[3].strip() == 'PSA']
        
        G230Lsens = [line for line in NUVsensData if line[1].strip() == 'G230L' and 
                     line[3].strip() == 'PSA' and line[0].strip() != 'NUVC']
    
        #CHANGED!
        #G230L = NUVSensitivityDataMod(G230Lsens, smoothing+g230lsm, median = False)
        G230L = NUVSensitivityDataMod(G230Lsens, smoothing+0)
        G185M = NUVSensitivityDataMod(G185Msens, smoothing+8)
        G225M = NUVSensitivityDataMod(G225Msens, smoothing+6)
        G285M = NUVSensitivityDataMod(G285Msens, smoothing+15)

        #Prints out the NUV sensitivity files
        G185 = printOutSensitivity(G185Msens, G185Mdisp, '#G185M wave sens Aeff', sd + 'G185Msensitivity.txt')   
        G225 = printOutSensitivity(G225Msens, G225Mdisp, '#G225M wave sens Aeff', sd + 'G225Msensitivity.txt')        
        G285 = printOutSensitivity(G285Msens, G285Mdisp, '#G285M wave sens Aeff', sd + 'G285Msensitivity.txt')
        G230 = printOutSensitivity(G230Lsens, G230Ldisp, '#G230L wave sens Aeff', sd + 'G230Lsensitivity.txt')
    
        #new sensitivity plot
        plot.NUVsensitivity(G185, G225, G285, G230, outputfolder +'NUVSensitivity')
    
        #OLD sensitivity plot
        plot.NUVsensitivityM([pair[0] for pair in G185M], [FEFU*NUVresel*pair[1] for pair in G185M], 
                             [pair[0] for pair in G225M], [FEFU*NUVresel*pair[1] for pair in G225M], 
                             [pair[0] for pair in G285M], [FEFU*NUVresel*pair[1] for pair in G285M],
                             outputfolder +'NUVSensitivityOLD')
   
##########################################################################################
        #Fig 5.4, page 42        
        plot.NUVsensitivityG230L([pair[0] for pair in G230L], [FEFU*NUVresel*pair[1] for pair in G230L], 
                                 outputfolder + 'NUVSensitivityG230L')

#########################################################################################    
        #Fig 5.5, page 53
        smoothFUV = True
        smoothingFUV = (500,)
        yline = 100
        FUVflat = read.FITSImage(FUVflatReferenceFile, 1)
        datay = FUVflat[yline, :]
        plot.FUVFlatField(range(len(datay)), datay, yline, outputfolder +'FUVXDLFlat', 
                          smooth = smoothFUV, smoothing = smoothingFUV)

#########################################################################################    
        #Fig 5.6, page 53
        smoothNUV = True
        smoothingNUV = (40,)
        yline = 430
        NUVflat = read.FITSImage(NUVflatReferenceFile, 1)
        datay = NUVflat[yline, :]
        plot.NUVFlatField(range(len(datay)), datay, yline, outputfolder +'NUVMAMAFlat',
                          smooth = smoothNUV, smoothing = smoothingNUV)

#########################################################################################
    
    if Chapter13:
        log.write('Starting to create Chapter 15 (see also synphotSensitivity.py) related plots..\n')
#########################################################################################
        #Chapter 13 plots
        #if referenceFiles == False: FUVsensData = read.FITSTable(FUVsensitivityReferenceFile, 1)
        #Run the sensitivity module
        ss.main()
        
        sensitivity = {}
        #G130M Wavel   Throughput   Sensitivity   Effective Area
        dt ={'names': ('wavelength', 'throughput', 'sensitivity', 'eff'),
             'formats': ('i4', 'f4', 'f4', 'f4')}        
        for file in glob.glob('./sensitivities/*sensitivity.txt'):
            grating = file[16:21]
            data = N.loadtxt(file, comments = '#', dtype = dt)
            sensitivity[grating] = data
        
        #FUV sensitivites and wavelengths
        G130Mw = sensitivity['G130M']['wavelength']
        G130Ms = sensitivity['G130M']['sensitivity']
        G160Mw = sensitivity['G160M']['wavelength']
        G160Ms = sensitivity['G160M']['sensitivity']
        G140Lw = sensitivity['G140L']['wavelength']
        G140Ls = sensitivity['G140L']['sensitivity']
        
        ###########
        ####FUV####
        ###########
        #G130Ms = [line for line in FUVsensData if line[1].strip() == 'G130M' and 
        #         line[2] == 1309 and line[3].strip() == 'PSA']
        #G130MBs = [line for line in FUVsensData if line[1].strip() == 'G130M' and 
        #          line[2] == 1309 and line[3].strip() == 'BOA']
          
        #OLD method
        #G130M = FUVSensitivityDataMod(G130Ms)
        #G130MB = FUVSensitivityDataMod(G130MBs)
        #plot.Chapeter13Plots([pair[0] for pair in G130M], 
        #                     [pair[1] for pair in G130M],
        #                     [pair[0] for pair in G130MB], 
        #                     [pair[1] for pair in G130MB],
        #                     'G130M, CENWAVE = 1309 \AA',
        #                     outputfolder + 'G130Msensitivity')
        
        #plot.Chapeter13Sensitivity(G130Ms, G130MBs, 'G130M, CENWAVE = 1309 \AA', outputfolder + 'G130Msensitivity')
        #plot.Chapeter13SensitivityNew(G130Ms, G130MBs, G130Mdisp[0],
        #                              'G130M, CENWAVE = 1309 \AA', outputfolder + 'G130MsensitivityNEW')
        
        #G130Mw = [line for line in FUVsensData if line[1].strip() == 'G130M' and 
        #          line[3].strip() == 'PSA']
               
        #plot.Chapter13Wavelength(G130Mw,
        #                         15,
        #                         'Wavelength Ranges for the G130M Grating Setting',
        #                         outputfolder + 'G130MWaveOLD')
        
        G130MSNRdata = []
        wv = 1310
        width = 2.0
        times = [1., 10., 100., 1000., 10000.]
        fluxes = STMagToFlux([x*0.2 for x in range(150)])
        
        G130Msens = selectSensitivity(G130Mw, G130Ms, wv, width)
        if debug: print 'G130M sensitivity %f at %i' % (G130Msens, wv)
        
        skyG130M = getZodiacalBackground(wv, width) + getEarthShineBackground(wv, width) + geo1302
        
        for time in times:
            tmp = []
            for flux in fluxes: 
                tmpSN = signalToNoisePerResel(G130Msens, flux, time, FUVresel, skyG130M, darkFUV*SNbox)
                tmp.append([flux, tmpSN])
            
            G130MSNRdata.append([time, tmp])
        
        plot.Chapter13SNPlot(G130MSNRdata,
                             calculateSTMAGlim(15000., 'G130M', G130Msens),
                             'G130M', str(wv), outputfolder + 'G130MSNR')
              
        #G130M short new modes!
        G130MSSNRdata = []
        wv = 1030
        width = 2.0
        times = [1., 10., 100., 1000., 10000.]
        fluxes = STMagToFlux([x*0.2 for x in range(150)])
        
        G130MSsens = selectSensitivity(G130Mw, G130Ms, wv, width)
        if debug: print 'G130MS sensitivity %f at %i' % (G130MSsens, wv)
        
        skyG130MS = getZodiacalBackground(wv, width) + getEarthShineBackground(wv, width) + geo1302
        
        for time in times:
            tmp = []
            for flux in fluxes: 
                tmpSN = signalToNoisePerResel(G130MSsens, flux, time, FUVresel, skyG130MS, darkFUV*SNbox)
                tmp.append([flux, tmpSN])
            
            G130MSSNRdata.append([time, tmp])
        
        plot.Chapter13SNPlot(G130MSSNRdata,
                             calculateSTMAGlim(15000., 'G130M', G130MSsens),
                             'G130M', str(wv), outputfolder + 'G130MSSNR')        
    
        ##########
        #G160Ms = [line for line in FUVsensData if line[1].strip() == 'G160M' and 
        #         line[2] == 1600 and line[3].strip() == 'PSA']
        #G160MBs = [line for line in FUVsensData if line[1].strip() == 'G160M' and 
        #          line[2] == 1600 and line[3].strip() == 'BOA']
        
        #Old method
        #G160M = FUVSensitivityDataMod(G160Ms)
        #G160MB = FUVSensitivityDataMod(G160MBs)
        #plot.Chapeter13Plots([pair[0] for pair in G160M], 
        #                     [pair[1] for pair in G160M],
        #                     [pair[0] for pair in G160MB], 
        #                     [pair[1] for pair in G160MB],
        #                     'G160M, CENWAVE = 1600 \AA',
        #                     outputfolder +  'G160Msensitivity')
        #plot.Chapeter13Sensitivity(G160Ms, G160MBs, 'G160M, CENWAVE = 1600 \AA', outputfolder +  'G160Msensitivity')

        #G160Mw = [line for line in FUVsensData if line[1].strip() == 'G160M' and 
        #          line[3].strip() == 'PSA']
        #plot.Chapter13Wavelength(G160Mw,
        #                         20,
        #                         'Wavelength Ranges for the G160M Grating Setting',
        #                         outputfolder + 'G160MWaveOLD')
        
        G160MSNRdata = []
        wv = 1610
        G160Msens = selectSensitivity(G160Mw, G160Ms, wv, width)
        if debug: print 'G160M sensitivity %f at %i' % (G160Msens, wv)
        
        skyG160M = getZodiacalBackground(wv, width) + getEarthShineBackground(wv, width) + geo1356
        
        for time in times:
            tmp = []
            for flux in fluxes: 
                tmpSN = signalToNoisePerResel(G160Msens, flux, time, FUVresel, skyG160M, darkFUV*SNbox)
                tmp.append([flux, tmpSN])
            
            G160MSNRdata.append([time, tmp])
        
        plot.Chapter13SNPlot(G160MSNRdata,
                             calculateSTMAGlim(15000., 'G160M', G160Msens),
                             'G160M', str(wv), outputfolder + 'G160MSNR')

        
        ########
        #G140Ls = [line for line in FUVsensData if line[1].strip() == 'G140L' and 
        #         line[2] == 1230 and line[3].strip() == 'PSA']
        #G140LBs = [line for line in FUVsensData if line[1].strip() == 'G140L' and 
        #          line[2] == 1230 and line[3].strip() == 'BOA']

        #Old method
        #G140L = FUVSensitivityDataMod(G140Ls)
        #G140LB = FUVSensitivityDataMod(G140LBs)
        #plot.Chapeter13Plots([pair[0] for pair in G140L], 
        #                     [pair[1] for pair in G140L],
        #                     [pair[0] for pair in G140LB], 
        #                     [pair[1] for pair in G140LB],
        #                     'G140L, CENWAVE = 1230 \AA',
        #                     outputfolder + 'G140Lsensitivity', True)
        #plot.Chapeter13Sensitivity(G140Ls, G140LBs, 'G140L, CENWAVE = 1230 \AA', outputfolder + 'G140Lsensitivity', True)

        #G140Lw = [line for line in FUVsensData if line[1].strip() == 'G140L' and 
        #          line[3].strip() == 'PSA']
        #plot.Chapter13Wavelength(G140Lw,
        #                         55,
        #                         'Wavelength Ranges for the G140L Grating Setting',
        #                         outputfolder + 'G140LWaveOLD', True)
        
        G140LSNRdata = []
        wv = 1230
        G140Lsens = selectSensitivity(G140Lw, G140Ls, wv, width)
        if debug: print 'G140L sensitivity %f at %i' % (G140Lsens, wv)
        
        skyG140L = getZodiacalBackground(wv, width) + getEarthShineBackground(wv, width) + geo1216
        
        for time in times:
            tmp = []
            for flux in fluxes: 
                tmpSN = signalToNoisePerResel(G140Lsens, flux, time, FUVresel, skyG140L, darkFUV*SNbox)
                tmp.append([flux, tmpSN])
            
            G140LSNRdata.append([time, tmp])
        
        plot.Chapter13SNPlot(G140LSNRdata,
                             calculateSTMAGlim(15000., 'G140L', G140Lsens),
                             'G140L', str(wv), outputfolder + 'G140LSNR')

        #New wavelength plots
        dt ={'names': ('grating', 'central', 'segment', 'fp-pos', 'start', 'stop'),
             'formats': ('S6', 'i4', 'S4', 'i4', 'f4', 'f4')}
        gratings = ['G130MS', 'G130M', 'G160M', 'G140L']
        FUVWaves = N.loadtxt(localFolder + 'FUVWaves.txt', comments = '#', dtype = dt)

        for grating in gratings:
            data = FUVWaves[FUVWaves['grating'] == grating]
            print 'Grating', grating
            print 'Data', data
            plot.Chapter13Waves(data, grating, outputfolder + grating + 'Wave')

        ###########
        ####NUV####
        ###########
        #if referenceFiles == False:
        #    NUVsensData = read.FITSTable(NUVsensitivityReferenceFile, 1)
        #    G185Msens = [line for line in NUVsensData if line[1].strip() == 'G185M' and 
        #                 line[3].strip() == 'PSA']
        #    G225Msens = [line for line in NUVsensData if line[1].strip() == 'G225M' and 
        #                 line[3].strip() == 'PSA']
        #    G285Msens = [line for line in NUVsensData if line[1].strip() == 'G285M' and 
        #                 line[3].strip() == 'PSA']
        #    G230Lsens = [line for line in NUVsensData if line[1].strip() == 'G230L' and 
        #                 line[3].strip() == 'PSA' and line[0].strip() != 'NUVC']
        #        #CHANGED G230L added stripe not C
        #    
        #    G185M = NUVSensitivityDataMod(G185Msens, smoothing+14)
        #    G225M = NUVSensitivityDataMod(G225Msens, smoothing+5)
        #    G285M = NUVSensitivityDataMod(G285Msens, smoothing+14)
        #    G230L = NUVSensitivityDataMod(G230Lsens, smoothing+g230lsm, median = False)
        
        #G185MBsens = [line for line in NUVsensData if line[1].strip() == 'G185M' and 
        #              line[3].strip() == 'BOA']
        #G225MBsens = [line for line in NUVsensData if line[1].strip() == 'G225M' and 
        #              line[3].strip() == 'BOA']
        #G285MBsens = [line for line in NUVsensData if line[1].strip() == 'G285M' and 
        #              line[3].strip() == 'BOA']
        #G230LBsens = [line for line in NUVsensData if line[1].strip() == 'G230L' and 
        #              line[3].strip() == 'BOA' and line[0].strip() != 'NUVC']    

        #G185MB = NUVSensitivityDataMod(G185MBsens, smoothing+14)
        #G225MB = NUVSensitivityDataMod(G225MBsens, smoothing+5)
        #G285MB = NUVSensitivityDataMod(G285MBsens, smoothing+14)
        #G230LB = NUVSensitivityDataMod(G230LBsens, smoothing+30)
        #G230LB = NUVSensitivityDataMod(G230LBsens, smoothing+g230lsm, median = False)
        
        G185Mw = sensitivity['G185M']['wavelength']
        G185Ms = sensitivity['G185M']['sensitivity']
        G225Mw = sensitivity['G225M']['wavelength']
        G225Ms = sensitivity['G225M']['sensitivity']
        G285Mw = sensitivity['G285M']['wavelength']
        G285Ms = sensitivity['G285M']['sensitivity']
        G230Lw = sensitivity['G230L']['wavelength']
        G230Ls = sensitivity['G230L']['sensitivity']                
                     
        #plot.Chapeter13Plots([pair[0] for pair in G185M], 
        #                     [pair[1] for pair in G185M],
        #                     [pair[0] for pair in G185MB], 
        #                     [pair[1] for pair in G185MB],
        #                     'G185M',
        #                     outputfolder + 'G185Msensitivity')
        
        #plot.Chapeter13Plots([pair[0] for pair in G285M], 
        #                     [pair[1] for pair in G285M],
        #                     [pair[0] for pair in G285MB], 
        #                     [pair[1] for pair in G285MB],
        #                     'G285M',
        #                     outputfolder + 'G285Msensitivity')
        
        #plot.Chapeter13Plots([pair[0] for pair in G225M], 
        #                     [pair[1] for pair in G225M],
        #                     [pair[0] for pair in G225MB], 
        #                     [pair[1] for pair in G225MB],
        #                     'G225M',
        #                     outputfolder + 'G225Msensitivity')
        
        #plot.Chapeter13Plots([pair[0] for pair in G230L if pair[0] < 3240], 
        #                     [pair[1] for pair in G230L if pair[0] < 3240],
        #                     [pair[0] for pair in G230LB if pair[0] < 3240], 
        #                     [pair[1] for pair in G230LB if pair[0] < 3240],
        #                     'G230L',
        #                     outputfolder + 'G230Lsensitivity')
       
        # WAVELENGTH PLOTS
        NUVd = read.FITSTable(NUVdispersionReferenceFile, 1)
        d = [(x[0], x[1], x[3], x[5]) for x in NUVd if x[2] == 'PSA']
        plot.Chapter13WavelengthNUVNew(d, outputfolder)
        #plot.Chapter13WavelengthNUV(G185Msens,
        #                            18,
        #                            'Wavelength Ranges for the G185M Grating Setting',
        #                            outputfolder + 'G185MWave')

        #plot.Chapter13WavelengthNUV(G285Msens,
        #                            30,
        #                            'Wavelength Ranges for the G285M Grating Setting',
        #                            outputfolder + 'G285MWave')
 
        #plot.Chapter13WavelengthNUV(G225Msens,
        #                            18,
        #                            'Wavelength Ranges for the G225M Grating Setting',
        #                            outputfolder + 'G225MWave')
        
        #G230Lsens = [line for line in NUVsensData if line[1].strip() == 'G230L' and 
        #             line[3].strip() == 'PSA']
 
        #plot.Chapter13WavelengthNUV(G230Lsens,
        #                            15,
        #                            'Wavelength Ranges for the G230L Grating Setting',
        #                            outputfolder + 'G230LWave')
        
        G185MSNRdata = []
        wv = 1851
        #note that we are limited to stripe B, so change this accordingly is wv above is changed
        #G185Msens = [line for line in NUVsensData if line[1].strip() == 'G185M' and 
        #             line[2] == 1850 and line[3].strip() == 'PSA' and line[0].strip() == 'NUVB']
        
        G185Ms = selectSensitivity(G185Mw, G185Ms, wv, width)
        if debug: print 'G185M sensitivity %f at %i' % (G185Ms, wv)
        
        skyG185M = getZodiacalBackground(wv, width) + getEarthShineBackground(wv, width) + geo1356
        skyG185M = 8.809e-9 #taken from ETC 17.4_test as the other method gave very wrong solution?
        
        for time in times:
            tmp = []
            for flux in fluxes: 
                tmpSN = signalToNoisePerResel(G185Ms, flux, time, NUVresel, skyG185M, darkNUV*SNboxNUV)
                tmp.append([flux, tmpSN])
            
            G185MSNRdata.append([time, tmp])
        
        plot.Chapter13SNPlot(G185MSNRdata,
                             calculateSTMAGlim(30000., 'G185M', G185Ms, NUV = True),
                             'G185M', str(wv), outputfolder + 'G185MSNR', FUV = False)

        ####################
        G225MSNRdata = []
        wv = 2251
        #note that we are limited to stripe B, so change this accordingly is wv above is changed
        #G225Msens = [line for line in NUVsensData if line[1].strip() == 'G225M' and 
        #             line[2] == 2250 and line[3].strip() == 'PSA' and line[0].strip() == 'NUVB']
        
        G225Ms = selectSensitivity(G225Mw, G225Ms, wv, width)
        if debug: print 'G225M sensitivity %f at %i' % (G225Ms, wv)
        
        skyG225M = getZodiacalBackground(wv, width) + getEarthShineBackground(wv, width) + geo2417
        skyG225M = 1.395e-7 #taken from ETC 17.4_test..
        
        for time in times:
            tmp = []
            for flux in fluxes: 
                tmpSN = signalToNoisePerResel(G225Ms, flux, time, NUVresel, skyG225M, darkNUV*SNboxNUV)
                tmp.append([flux, tmpSN])
            
            G225MSNRdata.append([time, tmp])
        
        plot.Chapter13SNPlot(G225MSNRdata,
                             calculateSTMAGlim(30000., 'G225M', G225Ms, NUV = True),
                             'G225M', str(wv), outputfolder + 'G225MSNR', FUV = False)

        ####################
        G285MSNRdata = []
        wv = 2851
        #note that we are limited to stripe B, so change this accordingly is wv above is changed
        #G285Msens = [line for line in NUVsensData if line[1].strip() == 'G285M' and 
        #             line[2] == 2850 and line[3].strip() == 'PSA' and line[0].strip() == 'NUVB']
        
        G285Ms = selectSensitivity(G285Mw, G285Ms, wv, width)
        if debug: print 'G285M sensitivity %f at %i' % (G285Ms, wv)
        
        skyG285M = getZodiacalBackground(wv, width) + getEarthShineBackground(wv, width) + geo2417
        skyG285M = 2.318e-7 #taken from ETC 17.4_test...
        
        for time in times:
            tmp = []
            for flux in fluxes: 
                tmpSN = signalToNoisePerResel(G285Ms, flux, time, NUVresel, skyG285M, darkNUV*SNboxNUV)
                tmp.append([flux, tmpSN])
            
            G285MSNRdata.append([time, tmp])
        
        plot.Chapter13SNPlot(G285MSNRdata,
                             calculateSTMAGlim(30000., 'G285M', G285Ms, NUV = True),
                             'G285M', str(wv), outputfolder + 'G285MSNR', FUV = False)         

        ####################
        G230LSNRdata = []
        wv = 3001
        #note that we are limited to stripe B, so change this accordingly is wv above is changed
        #G230Lsens = [line for line in NUVsensData if line[1].strip() == 'G230L' and 
        #             line[2] == 3000 and line[3].strip() == 'PSA' and line[0].strip() == 'NUVB']
        
        G230Ls = selectSensitivity(G230Lw, G230Ls, wv, width)
        if debug: print 'G230L sensitivity %f at %i' % (G230Ls, wv)
        
        skyG230L = getZodiacalBackground(wv, width) + getEarthShineBackground(wv, width) + geo2417
        skyG230L = 4.891e-6 #taken from ETC 17.4_test...
        
        for time in times:
            tmp = []
            for flux in fluxes: 
                tmpSN = signalToNoisePerResel(G230Ls, flux, time, NUVresel, skyG230L, darkNUV*SNboxNUV)
                tmp.append([flux, tmpSN])
            
            G230LSNRdata.append([time, tmp])

        plot.Chapter13SNPlot(G230LSNRdata,
                             calculateSTMAGlim(30000., 'G230L', G230Ls, NUV = True),
                             'G230L', str(wv), outputfolder + 'G230LSNR', FUV = False)         
#########################################################################################
        #Spatial profiles
    if SpatialProfiles:
        dispData = read.FITSTable(FUVdispersionReferenceFile, 1)
        
        xvalues = (2005, 8005, 14005)
        width = 5
        ymin = 460
        ymax = 520
        
        #G130A
        G130MAimage = readlocal.FITSTable(G130MASP, 1)
        G130MAhdr = readlocal.Header(G130MASP, 0)
        G130MAhdr1 = readlocal.Header(G130MASP, 1)
        G130MAdisp = getDispersion(G130MAhdr['SEGMENT'],
                                   G130MAhdr['OPT_ELEM'],
                                   G130MAhdr['CENWAVE'],
                                   G130MAhdr['FPPOS'],
                                   dispData)
        plot.SpatialProfileFUV(G130MAimage,
                               G130MAdisp,
                               xvalues,
                               width,
                               ymin,
                               ymax,
                               G130MAhdr1['SP_LOC_A'],
                               G130MAhdr1['SP_HGT'],
                               'G130M Spatial Profile Segment A',
                               outputfolder + 'G130MSpatialProfile')

        #G130MBimage = readlocal.FITSTable(G130MBSP, 1)

        
#########################################################################################
    if LSF:
        #LSF plots       
        #read data with Numpy
        G130LSF = N.loadtxt(localFolder + 'G130MLSFdata.txt', comments='#')
        G140LSF = N.loadtxt(localFolder + 'G140LLSFdata.txt', comments='#')
        G160LSF = N.loadtxt(localFolder + 'G160MLSFdata.txt', comments='#')
        NUVLSF = N.loadtxt(localFolder + 'NUVLSFdata.txt', comments='#')

        #G130M LSF
        G130LSFwaves = ['1150','1200','1250','1300','1350','1400','1450']
        plot.LSFcomparison(G130LSF, G130LSFwaves, 'LSF of G130M', outputfolder + 'G130LSFComparison')

        #G140L LSF 
        G140LSFwaves = ['1250','1300','1350','1400','1450','1500','1550','1600','1650','1700','1750','1800']
        plot.LSFcomparison(G140LSF, G140LSFwaves, 'LSF of G140L', outputfolder + 'G140LSFComparison')

        #G160M LSF
        G160LSFwaves = '1450,1500,1550,1600,1650,1700,1750'.split(',')
        plot.LSFcomparison(G160LSF, G160LSFwaves, 'LSF of G160M', outputfolder + 'G160LSFComparison')
        
        #NUV LSF
        NUVLSFwaves = '1700           1800           1900           2000           2100           2200           2300           2400           2500           2600           2700           2800           2900           3000           3100           3200'.split()
        plot.LSFcomparison(NUVLSF, NUVLSFwaves, 'LSF of NUV Gratings', outputfolder + 'NUVLSFComparison')
#########################################################################################
        #Dispersed-light acquisition plots
        #Fig. 8.9, COS IHB, version 2.0, draft 1
        dt ={'names': ('grating', 'flux', 'time'),'formats': ('S5', 'f4', 'f4')}
        gratings = ['G130M', 'G160M', 'G140L', 'G185M', 'G225M', 'G285M', 'G230L']
        DAcq = N.loadtxt(localFolder + 'DispAcqData.txt', comments = '#', dtype = dt)
        
        plot.DispersedLightAcquisitionTimes(DAcq, gratings, outputfolder + 'DispLightAcq')
#########################################################################################

    if computedPhot:
        log.write('Starting to create plots that are based on computed values...\n')
##########################################################################################        
        #Figure 3.4, page 14
        extension = 1
        every = 60  #1 = every point is plotted
        
        data = readcom.FITSTable(BOATransmissionFile, extension)
    
        wave = [triplet[0] for triplet in data]
        throughput = [triplet[1] for triplet in data] 
        
        plot.BOATransmission(wave, throughput, every, outputfolder +'BOATransmission')
        
##########################################################################################        
        #Fig. 7..3, page 72 (COS IHB, version 1.0)  
        AcqImageData = [
                        [[5, 1, 0.1, 0.01, 0.009], [1.7377, 8.6892, 86.9775, 878.3045, 977.0638], 'r-', 'PSA + MIRRORA'],
                        [[50, 10, 1, 0.1], [2.0759, 10.3806, 103.9461, 1053.4850], 'b-', 'PSA + MIRRORB'],
                        [[1000, 400, 4], [ 3.9282, 9.8206, 983.5532], 'g-', 'BOA + MIRRORA'],
                        [[10000, 5000,1000,100, 40], [4.5177, 9.0355,45.1802,452.0930,1131.4448], 'k-', 'BOA + MIRRORB']
                        ]

        plot.AcqImageExposureTimes(AcqImageData, outputfolder + 'ACQImageExposureTime')
        

    if local:
        log.write('Starting to create plots that are based on files on local folder...\n')
##########################################################################################     
        #Fig 6.1, page 61        
        #data = readcom.FITSTable(MirrorAImagingSensFile, 1)
        data = readlocal.FITSTable(MirrorAImagingSensFile, 1)
        
        wave = [triplet[0] for triplet in data]
        throughput = [triplet[1] for triplet in data] 
        
        plot.NUVPSAImagingSensitivity(wave, throughput, outputfolder +'NUVImagingSensitivity')
               
#########################################################################################
        #Example routine to make plots 7.4 to 7.7, change files and plotting functions
        imagedata = readlocal.FITSImage('l61h2904r_06334222945_flt.fits', 1 )
        xline = 595
        counts = imagedata[:, xline]
    
        plot.PSAMMIRRORANUVImaging(range(len(counts)), counts, outputfolder +'NUVImagingPSA')
    
#########################################################################################
        #Example for Fig 4.2 p 29, filename and exposure time should be changed
        file = 'l61h0000r_06336164728'
        exptime = float(readlocal.HeaderKeyword(file + '_flt_b.fits', 1, 'EXPTIME'))
        imagedata = readlocal.FITSImage(file + '_flt_b.fits', 1)
    
        #specdata = readlocal.FITSTable(file + '_x1d.fits', 1)
        #wave = specdata[0][3]
        #counts = specdata[0][4]
        #plot.COSFUVSpectrum(imagedata, wave, counts, 'COSFUVSpectrum')
        
        yline = 520
        width = 5
        collapsed = collapseSpectrumY(imagedata, yline, width) 
            
        plot.COSFUVSpectrum(imagedata, range(len(collapsed)), 
                            collapsed, exptime, outputfolder +'COSFUVSpectrum')
    
##########################################################################################
        #Example of Fig 13.3 on page 138
        #Filename etc. should be changed for real data
        #Use wavelength rather than pixels for the proper plot
        file =  'l61h0102r_06337015153_flt_a.fits'
    
        imagedata = readlocal.FITSImage(file, 1)
        collapsed = collapseSpectrumY(imagedata, 476, 6)
        
        plot.WavecalSpecPSA(range(len(collapsed)), 
                            collapsed, outputfolder +'WavecalSpecFUVPSA')
    
##########################################################################################
        #Example of Fig. 5.1 on page 39  
        #File should be changed...
        file = 'l61h0102r_06337015153_flt_a.fits'
        
        imagedata = readlocal.FITSImage(file, 1)
        collapsed = collapseSpectrumY(imagedata, 476, 6)
        
        plot.ScatteredLight(range(len(collapsed)), 
                            collapsed, outputfolder +'ScatteredLightFUV')
        
##########################################################################################
        #Fig. 7.4 page 73 of COS IHB (version 1.0)        
        file = 'laa702acq_flt.fits'
        data = readlocal.FITSImage(file, 1)
        
        yline = 440
        exptime = 60.
        xmin = 260
        xmax = 350
        ydata = data[yline,xmin:xmax]*exptime
        
        plot.MIRRORB(range(xmin,xmax), ydata, outputfolder +'MIRRORBProfile')
                
##########################################################################################
        #Fig. 7.5
        file = 'laa702b7q_flt.fits'
        data = readlocal.FITSImage(file, 1)
        
        exptime = 80.
        yline = 287
        xline = 527
        xmin = 510
        xmax = 550
       
        #straight plot
        ydata = data[yline,xmin:xmax]*exptime
        plot.BOAprofile(range(xmin, xmax), ydata, outputfolder +'BOAProfile')

        #collapsed and summed over
        ydata = collapseSpectrumY(data, yline, 2)*exptime/5.  
        plot.BOAprofile(range(xmin, xmax), ydata[xmin:xmax], outputfolder +'BOAProfile2')

        
##########################################################################################        
        #Fig. 7.6 & 7.7
        file = 'laa702c9q_flt.fits'
        data = readlocal.FITSImage(file, 1)
       
        exptime = 2630.
        xcen =  304 #304
        wid = 50
        ycen = 447 #447
        
        dataxy = data[ycen,xcen-wid:xcen+wid]*exptime
        datayy = data[ycen-wid:ycen+wid,xcen]*exptime
        
        plot.BOAMIRRORprofile(range(xcen-wid, xcen+wid), dataxy, 
                              range(ycen-wid, ycen+wid), datayy,
                              outputfolder +'BOAMIRRORBProfile')

        #collapsed
        dataxy = collapseSpectrumY(data, ycen, 1)[xcen-wid:xcen+wid]*exptime/3. #_x
        datayy = collapseSpectrumX(data, xcen, 1)[ycen-wid:ycen+wid]*exptime/3. #_y
        
        plot.BOAMIRRORprofile(range(xcen-wid, xcen+wid), dataxy, 
                              range(ycen-wid, ycen+wid), datayy,
                              outputfolder +'BOAMIRRORBProfile2')

##########################################################################################
    if PSFs:
        log.write('Starting to create PSF plots that are based on files on local folder...\n')
##########################################################################################
        #Fig 6.3 on page 63
        extension = 1
        imagedata = readPSF.FITSImage(PSFdataFile, extension)

        yline = 280

        plot.NUVImageProfile(range(len(imagedata[yline, :])), 
                             imagedata[yline, :], outputfolder +'NUVImageProfile')
        
##########################################################################################
        #Fig 6.2 on page 63
        centrex = 486
        centrey = 280
        displacement = 8
        xmin = centrex - displacement
        xmax = centrex + displacement
        ymin = centrey - displacement
        ymax = centrey + displacement
        
        datay = N.arange(ymin, ymax)
        datax = N.arange(xmin, xmax)
   
        #note the reversed order!
        dataz = imagedata[ymin:ymax, xmin:xmax]

        plot.PSF(datax, datay, dataz, outputfolder +'COSImagingPSF')
        
##########################################################################################        
        #Fig 6.2 on page 62
        #Calls and IDL routine to do the 3D plotting
        #filenames etc. should be edited inside the IDL routine
        log.write('Running IDL for PSF plots...\n')
        import subprocess
        try:
            subprocess.Popen('idl psfplotting.pro', shell=True, executable = 'tcsh').wait()
        except:
            log.write('Error encountered while calling IDL...\n')
            sys.exit(-99)
            

##########################################################################################
        #Fig 7.1 on page 69
        
        reads = open(localFolder + FIG71Data, 'r').readlines()
        alldata = []
        for line in reads:
            if line.startswith('#') is False:
                alldata.append(line.split())
        
        datax = [float(line[0]) for line in alldata]
        datay = [float(line[1]) for line in alldata]
        
        plot.PSARelativeTransmission(datax, datay, outputfolder +'RelativeTransmission')
        
##########################################################################################
    log.write('\nPlotting program ends...\n')
    