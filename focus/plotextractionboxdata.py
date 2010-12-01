'''
@author: Sami-Matias Niemi
'''
import matplotlib
matplotlib.rc('text', usetex = False)
matplotlib.rc('xtick', labelsize=12) 
matplotlib.rc('axes', linewidth=1.2)
matplotlib.rc('lines', markeredgewidth=2.0)
matplotlib.rcParams['lines.linewidth'] = 1.8
matplotlib.rcParams['legend.fontsize'] = 9
matplotlib.rcParams['legend.handlelength'] = 2
matplotlib.rcParams['font.size'] = 12
matplotlib.rcParams['xtick.major.size'] = 5
matplotlib.rcParams['ytick.major.size'] = 5
matplotlib.use('PDF')
#matplotlib.use('Agg')
from matplotlib.dates import DateFormatter
import pylab as P
import dates.julians
import datetime as D

__author__ = 'Sami-Matias Niemi'
__version__ = '0.9'

def parse_data(file, mjd = 2, focus = 6):
    #output dictionary
    out = {}
    #read the file
    data = open(file, 'r').readlines()
    
    for line in data:
        if line.startswith('#'):
            value = line.split()[0][1:]
        if line.startswith('i'):
            tmp = line.split()
            if out.has_key(value):
                out[value] += [[tmp[mjd], tmp[focus]]]
            else:
                out[value] = [[tmp[mjd], tmp[focus],]]
    return out

def read_breathing(file):
    out = []
    data = open(file, 'r').readlines()
    for line in data:
        if not line.startswith('J'):
            tmp = line.split()
            out.append([tmp[0], tmp[6]])
    return out

def plot_extractionbox_comparison(data, breathing, outdir):
    #data time formatter
    dfrm = DateFormatter('%H:%M')
    
    #get dat
    d = parse_data(data)

    #get breathing values
    br = read_breathing(breathing)

    markers = ['bo', 'rD', 'ys']

    fig = P.figure()
    ax = fig.add_subplot(111)
    P.title('Extraction size comparison for WFC3 data')
    
    #plot breathing
    x = [D.datetime(*dates.julians.fromJulian(float(a))[:6]) for a, b in br]
    y = [float(b)+0.2 for a, b in br]
    ax.plot_date(x, y, 'g-', label = 'Breathing Model')
    
    #plot data
    for key, m in zip(d, markers):
        values = d[key]
        x = [D.datetime(*dates.julians.fromJulian(float(a))[:6]) for a, b in values]
        y = [float(b) for a, b in values]
        ax.plot_date(x, y, m, label = '%s pixels' % key, ms = 8)
       
    ax.xaxis.set_major_formatter(dfrm)   
    
    date = x[0].strftime('%A %d. %B %Y')   
    
    P.legend(shadow = True, fancybox = True, numpoints = 1)
    P.ylabel('Defocus (microns in SM)')
    P.xlabel(date)
    P.ylim(-1, 7)
    P.savefig(outdir + 'extractions.pdf')

if __name__ == '__main__':
    
    data = '/Users/niemi/Desktop/Focus/extraction_boxes/diff_extractions.txt'
    breathing = '/Users/niemi/Desktop/Focus/extraction_boxes/breathing.txt'
    output = '/Users/niemi/Desktop/Focus/extraction_boxes/'
    
    plot_extractionbox_comparison(data, breathing, output)