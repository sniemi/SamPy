import matplotlib 
matplotlib.use('PDF')
#matplotlib.use('Agg')
matplotlib.rc('xtick', labelsize=18) 
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rc('lines', markeredgewidth=3.0)
matplotlib.rcParams['lines.linewidth'] = 2.8
matplotlib.rcParams['font.size'] = 18
matplotlib.rcParams['xtick.major.size'] = 10
matplotlib.rcParams['xtick.labelsize'] = 'large'
matplotlib.rcParams['ytick.major.size'] = 10
matplotlib.rcParams['ytick.labelsize'] = 'large'
matplotlib.rcParams['legend.fontsize'] = 11
import matplotlib.transforms 
from mpl_toolkits.axes_grid.inset_locator import inset_axes
from mpl_toolkits.axes_grid.inset_locator import mark_inset

import pylab as P
import glob as g
import numpy as N

class InsetPosition(object): 
    def __init__(self, parent, lbwh): 
        self.parent = parent 
        self.lbwh = lbwh # position of the inset axes in the 
                          # normalized coordinate of the parent axes 

    def __call__(self, ax, renderer): 
        bbox_parent = self.parent.get_position(original=False) 
        trans = matplotlib.transforms.BboxTransformTo(bbox_parent) 
        bbox_inset = matplotlib.transforms.Bbox.from_bounds(*self.lbwh) 
        bb = matplotlib.transforms.TransformedBbox(bbox_inset, trans) 
        return bb 

def read_data(filename):
    x = []
    y = []
    fh = open(filename, 'r')
    while True:
        try:
            a = fh.next()
        except:
            break
        if a.startswith('#'):
            continue
        try:
            tmp = a.split()
            if '.filter' in filename:
                x.append(float(tmp[0]))
                y.append(float(tmp[1]))
            else:
                x.append(float(tmp[1]))
                y.append(float(tmp[2]))
        except:
            pass
    return N.array(x), N.array(y)

def main(color):
    #grouped data
    gr = {}
    #all filters
    all_folders = g.glob('/Users/niemi/Desktop/CANDELS/CANDELS_FILTERS/*')
    
    #collect data    
    for i, folder in enumerate(all_folders):
        camera = folder.split('/')[6]
        print camera
    
        files = g.glob(folder + '/*.dat')
        files += g.glob(folder + '/*.fil')
        files += g.glob(folder + '/*.filter')
    
        for f in files:
            x, y = read_data(f)
            if 'PACS' in f or 'SPIRE' in f or 'SCUBA' in f:
                x *= 10000
            if len(y[y > 1.]) > 1:
                print 'Normalizing ', camera
                y /= 100.
            if not ('WFC2' in f or 'UVIS2' in f):
                gr[f] = [x, y, f]
    
    #make the figure
    fig = P.figure(figsize=(40,50))
    P.subplots_adjust(wspace = 0.0, hspace = 0.0)
    P.title('CANDELS Mock Catalogue Filter Transmittance Curves')
    for i in range(1, 11):
        axs = P.subplot(10, 1, i)
        #inset
        if i > 1 and i < 9:
            axins = inset_axes(axs, width = 8, height = 1)
                                    #xstar, ystar, xsize, ysize
            ip = InsetPosition(axs, [0.4, 0.1, 0.3, 0.88]) 
            axins.set_axes_locator(ip) 

        j = 0
        for key in gr:
            x = gr[key][0]
            y = gr[key][1]
            axs.plot(x, y, 'k-', alpha = 0.1)
            #coloured plots           
            if N.min(x) <= 3000 and i == 1:
                tmp1 = gr[key][2].split('/')
                tmp2 = tmp1[7]
                name =  tmp1[6] + ' ' + tmp2[:tmp2.rfind('.')] 
                axs.plot(x, y, c = color[j], label = name, lw = 4.5)
                j += 1
            if N.min(x) <= 3500 and N.min(x) > 3000 and i == 2:
                tmp1 = gr[key][2].split('/')
                tmp2 = tmp1[7]
                name =  tmp1[6] + ' ' + tmp2[:tmp2.rfind('.')] 
                axs.plot(x, y, c = color[j], label = name, lw = 4.5)
                axins.plot(x, y*0.85, c = color[j], lw = 4.5)
                axins.set_yticks([])
                axins.set_xlim(3000, 7500)                
                j += 1
            if N.min(x) <= 4000 and N.min(x) > 3500 and i == 3:
                tmp1 = gr[key][2].split('/')
                tmp2 = tmp1[7]
                name =  tmp1[6] + ' ' + tmp2[:tmp2.rfind('.')] 
                axs.plot(x, y, c = color[j], label = name, lw = 4.5)
                axins.plot(x, y*0.85, c = color[j], lw = 4.5)
                axins.set_yticks([])
                axins.set_xlim(3500, 5800)                
                j += 1
            if N.min(x) <= 5000 and N.min(x) > 4000 and i == 4:
                tmp1 = gr[key][2].split('/')
                tmp2 = tmp1[7]
                name =  tmp1[6] + ' ' + tmp2[:tmp2.rfind('.')] 
                axs.plot(x, y, c = color[j], label = name, lw = 4.5)
                axins.plot(x, y*0.85, c = color[j], lw = 4.5)
                axins.set_yticks([])
                axins.set_xlim(4400, 11000)                
                j += 1
            if N.min(x) <= 6000 and N.min(x) > 5000 and i == 5:
                tmp1 = gr[key][2].split('/')
                tmp2 = tmp1[7]
                name =  tmp1[6] + ' ' + tmp2[:tmp2.rfind('.')] 
                axs.plot(x, y, c = color[j], label = name, lw = 4.5)
                axins.plot(x, y*0.85, c = color[j], lw = 4.5)
                axins.set_yticks([])
                axins.set_xlim(5000, 10000)
                j += 1
            if N.min(x) <= 9000 and N.min(x) > 6000 and i == 6:
                tmp1 = gr[key][2].split('/')
                tmp2 = tmp1[7]
                name =  tmp1[6] + ' ' + tmp2[:tmp2.rfind('.')] 
                axs.plot(x, y, c = color[j], label = name, lw = 4.5)
                axins.plot(x, y*0.85, c = color[j], lw = 4)
                axins.set_yticks([])
                axins.set_xlim(6500, 13000)
                j += 1          
            if N.min(x) <= 13000 and N.min(x) > 9000 and i == 7:
                tmp1 = gr[key][2].split('/')
                tmp2 = tmp1[7]
                name =  tmp1[6] + ' ' + tmp2[:tmp2.rfind('.')] 
                axs.plot(x, y, c = color[j], label = name, lw = 4.5)
                axins.plot(x, y*0.85, c = color[j], lw = 4.5)
                axins.set_yticks([])
                axins.set_xlim(9400, 18200)
                j += 1     
            if N.min(x) <= 25000 and N.min(x) > 13000 and i == 8:
                tmp1 = gr[key][2].split('/')
                tmp2 = tmp1[7]
                name =  tmp1[6] + ' ' + tmp2[:tmp2.rfind('.')] 
                axs.plot(x, y, c = color[j], label = name, lw = 4.5)
                axins.plot(x, y*0.85, c = color[j], lw = 4.5)
                axins.set_yticks([])
                axins.set_xlim(13500, 26000)
                j += 1            
            if N.min(x) <= 100000 and N.min(x) > 25000 and i == 9:
                tmp1 = gr[key][2].split('/')
                tmp2 = tmp1[7]
                name =  tmp1[6] + ' ' + tmp2[:tmp2.rfind('.')] 
                axs.plot(x, y, c = color[j], label = name, lw = 4.5)
                j += 1
            if N.min(x) > 1e5 and i == 10:
                tmp1 = gr[key][2].split('/')
                tmp2 = tmp1[7]
                name =  tmp1[6] + ' ' + tmp2[:tmp2.rfind('.')]
                if not 'SCUBA' in name:
                    axs.plot(x, y, c = color[j], label = name, lw = 4.5)
                    j += 1
                    
                    
        axs.set_xlim(1000, 10**7)
        axs.set_ylim(0.01, 1.05)
        axs.set_xscale('log')
        axs.set_ylabel('Normalized Transmission')
        if i == 10: 
            axs.set_xlabel('Wavelength [Angstrom]')
        else:
            axs.set_xticklabels([])

        axs.legend(fancybox = True, shadow = True)

    P.savefig('/Users/niemi/Desktop/CANDELS/CANDELS_FILTERS/CANDELSMockfilters2.pdf')

def main2(color, size = 'x-large'):
    #grouped data
    gr = {}
    #all filters
    all_folders = g.glob('/Users/niemi/Desktop/CANDELS/CANDELS_FILTERS/*')
    
    #collect data    
    for i, folder in enumerate(all_folders):
        camera = folder.split('/')[6]

        files = g.glob(folder + '/*.dat')
        files += g.glob(folder + '/*.fil')
        files += g.glob(folder + '/*.filter')
    
        for f in files:
            x, y = read_data(f)
            if 'PACS' in f or 'SPIRE' in f or 'SCUBA' in f:
                x *= 10000
            if len(y[y > 1.]) > 1:
                print 'Normalizing ', camera
                y /= 100.
            if 'SuprimeCAM' in folder:
                if '_subaru' in f:
                    if gr.has_key(camera):
                        gr[camera] += [[x, y, f]]
                    else:
                        gr[camera] = [[x, y, f]]
            else:
                if not ('UVIS2' in f or 'WFC2' in f):
                    if gr.has_key(camera):
                        gr[camera] += [[x, y, f]]
                    else:
                        gr[camera] = [[x, y, f]]            
  
    #make the figure
    fig = P.figure(figsize=(40,50))
    P.subplots_adjust(wspace = 0.0, hspace = 0.0)
    P.title('CANDELS Mock Catalogue Filter Transmittance Curves')
    for i in range(1, 10):
        axs = P.subplot(9, 1, i)
        inst = []
        j = 0
        for key in gr:
            for a, b, c in gr[key]:
                axs.plot(a, b, 'k-', alpha = 0.1)
                if ('2MASS' in key or 'CFHT' in key) and i == 1:
                    axs.plot(a, b, c = color[j])
                    mask = b == N.max(b)
                    tmp1 = c.split('/')
                    tmp2 = tmp1[7]
                    name = tmp2[:tmp2.rfind('.')]
                    if tmp1[6] not in inst:
                        inst.append(tmp1[6])
                    if '2MASS' in key: name = name.replace('band', '')
                    if 'ACS' in key: name = name.replace('.WFC1', '')
                    if 'galex' in name: name = name.replace('galex_', '')
                    if '2mass' in name: name = name.replace('_2mass', '')
                    if 'Mega' in name: name = name.replace('Mega', '')
                    if '_new' in name: name = name.replace('_new', '')
                    if name in ['u', 'g', 'r', 'i2', 'z'] :
                        multi = 1.15
                    else:
                        multi = 1.02
                    axs.annotate(name, (a[mask][0], multi*b[mask][0]), color = color[j],
                                 ha = 'center', size = size)
                    j += 1
                if ('GALEX' in key or 'ACS' in key) and i and ('PACS' not in key) and i == 2:
                    axs.plot(a, b, c = color[j])
                    mask = b == N.max(b)
                    tmp1 = c.split('/')
                    tmp2 = tmp1[7]
                    name = tmp2[:tmp2.rfind('.')]
                    if tmp1[6] not in inst:
                        inst.append(tmp1[6])
                    if '2MASS' in key: name = name.replace('band', '')
                    if 'ACS' in key: name = name.replace('.WFC1', '')
                    if 'galex' in name: name = name.replace('galex_', '')
                    if '2mass' in name: name = name.replace('_2mass', '')
                    if '814' in name:
                        multi = 1.5
                    elif '606' in name:
                        multi = 1.25
                    else:
                        multi = 1.02
                    axs.annotate(name, (a[mask][0], multi*b[mask][0]), color = color[j],
                                 ha = 'center', size = size)
                    j += 1
                if ('WFC3' in key or 'Johnson' in key) and i == 3:
                    axs.plot(a, b, c = color[j])
                    mask = b == N.max(b)
                    tmp1 = c.split('/')
                    tmp2 = tmp1[7]
                    name = tmp2[:tmp2.rfind('.')]
                    if tmp1[6] not in inst:
                        inst.append(tmp1[6])
                    if 'Johnson' in name: name = name.replace('Johnson_', '')
                    if 'filter' in name: name = name.replace('filter', '')
                    if 'UVIS' in name: name = name.replace('.UVIS1', '')
                    if 'IR' in name: name = name.replace('.IR', '')
                    if '160' in name:
                        multi = 1.35
                    elif '098' in name:
                        multi = 1.25
                    elif '125' in name:
                        multi = 1.2
                    else:
                        multi = 1.02
                    axs.annotate(name, (a[mask][0], multi*b[mask][0]), color = color[j],
                                 ha = 'center', size = size)
                    j += 1
                if ('DEEP' in key or 'LBC' in key) and i == 4:
                    if not 'hawa' in c:
                        axs.plot(a, b, c = color[j])
                        mask = b == N.max(b)
                        tmp1 = c.split('/')
                        tmp2 = tmp1[7]
                        name = tmp2[:tmp2.rfind('.')]
                        m = 1.015
                        if tmp1[6] not in inst:
                            inst.append(tmp1[6])
                        if 'deep' in name: name = name.replace('deep_', '')
                        if 'LBC' in name:
                            name = 'LBC/U'
                            m = 1.1
                        axs.annotate(name, (a[mask][0], m*b[mask][0]), color = color[j],
                                     ha = 'center', size = size)
                        j += 1
                if ('MUSYC' in key) and i == 5:
                    axs.plot(a, b, c = color[j])
                    mask = b == N.max(b)
                    tmp1 = c.split('/')
                    tmp2 = tmp1[7]
                    if tmp1[6] not in inst:
                        inst.append(tmp1[6])
                    name = tmp2[:tmp2.rfind('.')].replace('ecdfs.', '')
                    name = name.replace('.filt', '') 
                    if 'U' == name:
                        m = 0.8
                    else:
                        m = 1
                    axs.annotate(name, (m * a[mask][0], 1.05*b[mask][0]), color = color[j],
                                 ha = 'center', size = size)
                    j += 1
                if ('NEWFIRM' in key or 'SDSS' in key) and i == 6:
                    axs.plot(a, b, c = color[j])
                    mask = b == N.max(b)
                    tmp1 = c.split('/')
                    tmp2 = tmp1[7]
                    if tmp1[6] not in inst:
                        inst.append(tmp1[6])
                    name = tmp2[:tmp2.rfind('.')]
                    multi = 1.05
                    if 'sdss' in name:
                        multi = 1.2
                        name = name.replace('sdss_', '')

                    axs.annotate(name, (a[mask][0], multi*b[mask][0]), color = color[j],
                                 ha = 'center', size = size)
                    j += 1
                if ('PACS' in key or 'SPIRE' in key or 'IRAC' in key or 'MIPS' in key or 'Suprime' in key or 'UKIRT' in key) and i == 7:
                    axs.plot(a, b, c = color[j])
                    mask = b == N.max(b)
                    tmp1 = c.split('/')
                    tmp2 = tmp1[7]
                    if tmp1[6] not in inst:
                        inst.append(tmp1[6])
                    name = tmp2[:tmp2.rfind('.')]
                    if 'subaru' in name: name = name.replace('_subaru', '')
                    if 'irac' in name: name = name.replace('irac_', '')
                    if 'mips' in name: name = name.replace('mips_', '')
                    if 'filter' in name: name = name.replace('_filter', '')
                    if '200' in name: name = name.replace('_2004.2008', '')
                    multi = 1.02
                    m = 1.
                    if 'UKIRT' in key:
                        multi = 1.2
                    if '5.8' in name:
                        m = 1.1
                    if '350' in name:
                        multi = 1.35
                    axs.annotate(name, (m*a[mask][0], multi*b[mask][0]), color = color[j],
                                 ha = 'center', size = size)
                    j += 1     
                if ('VISTA' in key or 'VIMOS' in key) and i == 8:
                    axs.plot(a, b, c = color[j])
                    mask = b == N.max(b)
                    tmp1 = c.split('/')
                    tmp2 = tmp1[7]
                    if tmp1[6] not in inst:
                        inst.append(tmp1[6])
                    name = tmp2[:tmp2.rfind('.')]
                    if 'VISTA' in name: name = name.replace('VISTA_', '')
                    if 'VISTA' in key: name = name.replace('band', '')
                    if 'vimos' in name: name = name.replace('_vimos', '')
                    axs.annotate(name, (a[mask][0], 1.05*b[mask][0]), color = color[j],
                                 ha = 'center', size = size)
                    j += 1
                if ('MOSAIC' in key or 'Hawk' in key) and i == 9:
                    axs.plot(a, b, c = color[j])
                    axs.plot(a, b, c = color[j])
                    mask = b == N.max(b)
                    tmp1 = c.split('/')
                    tmp2 = tmp1[7]
                    if tmp1[6] not in inst:
                        inst.append(tmp1[6])
                    name =  tmp2[:tmp2.rfind('.')].replace('band', '')
                    if 'Hawk' in name: name = name.replace('HawkI_', '')
                    if 'mosaic' in name:
                        name = name.replace('_mosaic_tot','')
                    m = 1.05
                    if 'kp' in name:
                        m = 1.8
                    if 'U' in name:
                        name = name.upper().replace('_', '@')
                    axs.annotate(name, (a[mask][0], m*b[mask][0]), color = color[j],
                                 ha = 'center', size = size)
                    j += 1
            
        if len(inst) > 0:
            str = ''
            inst.reverse()
            if 'GALEX' in inst:
                inst = ['GALEX', 'ACS']
            if 'VIMOS' in inst:
                inst = ['VIMOS', 'VISTA']
            if 'MOSAIC' in inst:
                inst = ['MOSAIC', 'Hawk-I']
            if '2MASS' in inst:
                inst = ['CFHTLS', '2MASS']
            for x in inst:
                str += x + ', '
            if 'IRAC' in str:
                str = 'SuprimeCAM, UKIRT, IRAC\nMIPS, PACS, SPIRE  '
            axs.annotate(str[:-2], (0.02, 0.92), xycoords = 'axes fraction',
                         size = 'large', va = 'top')
             
        axs.set_xlim(1000, 10**7)
        axs.set_ylim(0.01, 1.1)
        axs.set_xscale('log')
        axs.set_ylabel('Normalized Transmission')
        if i == 9: 
            axs.set_xlabel('Wavelength [Angstrom]')
        else:
            axs.set_xticklabels([])
            
    note = 'Note: there are two types of normalizations in the image.'\
            +' Some curves show the filter transmission, while others' \
            +' show the total system throughput. Please see the table for more information.'
    P.annotate(note, (0.5, 0.05), xycoords = 'figure fraction',
               size = 'large', ha = 'center')

    P.savefig('/Users/niemi/Desktop/CANDELS/CANDELS_FILTERS/CANDELSMockfilters.pdf')

if __name__ == '__main__':
    
    color = ['DarkOliveGreen', 'Indigo', 'MediumPurple',
            'DarkOrange', 'Red', 'Magenta', 'Blue',
            'Aqua', 'Khaki', 'RosyBrown', 'Salmon', 'Green',
            'AquaMarine', 'SaddleBrown', 'DarkSeaGreen',  
            'MediumVioletRed', 'DarkRed', 'MediumSpringGreen',
            'Black', 'MintCream',  'Yellow',
            'AntiqueWhite', 'LavenderBlush']

    #main(color)
    main2(color)
    
    print 'All done...'