import matplotlib 
matplotlib.use('PDF')
matplotlib.rc('xtick', labelsize=16) 
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rc('lines', markeredgewidth=3.0)
matplotlib.rcParams['lines.linewidth'] = 2.5
matplotlib.rcParams['font.size'] = 16
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

    P.savefig('/Users/niemi/Desktop/CANDELS/CANDELS_FILTERS/CANDELSMockfilters.pdf')

def main2(color):
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
                if gr.has_key(camera):
                    gr[camera] += [[x, y, f]]
                else:
                    gr[camera] = [[x, y, f]]
  
    #make the figure
    fig = P.figure(figsize=(40,50))
    P.subplots_adjust(wspace = 0.0, hspace = 0.0)
    P.title('CANDELS Mock Catalogue Filter Transmittance Curves')
    for i in range(1, 11):
        axs = P.subplot(10, 1, i)

        for key in gr:
            for a, b, c in gr[key]:
                axs.plot(a, b, 'k-', alpha = 0.1)
                if ('WFC3' in key or 'ACS' == key or 'GALEX' in key) and i == 2:
                    axs.plot(a, b)
                if ('Hawk' in key) and i == 3:
                    axs.plot(a, b)     
               
                    
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

if __name__ == '__main__':
    
    color = ['DarkOliveGreen', 'Indigo', 'MediumPurple',
            'AntiqueWhite', 'DarkOrange', 'Red',
            'Aqua', 'Khaki', 'RosyBrown', 'Salmon',
            'AquaMarine', 'MediumSpringGreen',
            'LavenderBlush', 'SaddleBrown', 'DarkSeaGreen',
            'MediumVioletRed', 'DarkRed',
            'Black', 'MintCream', 'Blue', 'Yellow', 'Green',
            'Magenta']

    #main(color)
    main2(color)