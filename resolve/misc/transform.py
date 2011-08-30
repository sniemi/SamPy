"""
Transforms science data using IRAF.
Performs both linear and logarithmic transformations.
The script calls IRAF from the command line as follows::

  cl -0 < command_file.cl

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import glob as g
import os

def generateIRAFtransformCommand(data, low=5520, high=6820):
    """
    Creates an ascii file which lists all the IRAF commands
    required to make both linear and logarithmic transformations.
    
    :param: data, a dictionary holding the files to be transformed
            and the matching arc files.
    :param: low, minimum wavelength in angstroms
    :param: high, maximum wavelength in anstroms

    :return: None
    """
    #make the file with suitable commands
    lin = open('transformlin.cl', 'w')
    log = open('transformlog.cl', 'w')
    lin.write('images\nimmatch\nnoao\ntwodspec\nlongslit\n')
    log.write('images\nimmatch\nnoao\ntwodspec\nlongslit\n')
    for key, values in data.iteritems():
        cmd1 = 'transform %s lin%s fitnames="%s,%s" ' % (key, key, values[0], values[1])
        cmd1 += 'database="database" interp=linear x1=%i x2=%i ' % (low, high)
        cmd1 += 'dx=INDEF nx=INDEF xlog=no y1=INDEF y2=INDEF dy=INDEF ny=INDEF '
        cmd1 += 'ylog=no flux=yes logfile="STDOUT,logfile" mode="h"\n'
        cmd2 = 'transform %s log%s fitnames="%s,%s" ' % (key, key, values[0], values[1])
        cmd2 += 'database="database" interp=linear x1=%i x2=%i ' % (low, high)
        cmd2 += 'dx=INDEF nx=INDEF xlog=yes y1=INDEF y2=INDEF dy=INDEF ny=INDEF '
        cmd2 += 'ylog=no flux=yes logfile="STDOUT,logfile" mode="h"\n'
        lin.write(cmd1)
        log.write(cmd2)
        lin.write('hedit lin%s "comp1" "%s" add=yes delete=yes verify=no show=no update=yes\n' % (key, values[0]))
        lin.write('hedit lin%s "comp2" "%s" add=yes delete=yes verify=no show=no update=yes\n' % (key, values[1]))
        log.write('hedit log%s "comp1" "%s" add=yes delete=yes verify=no show=no update=yes\n' % (key, values[0]))
        log.write('hedit log%s "comp2" "%s" add=yes delete=yes verify=no show=no update=yes\n' % (key, values[1]))
    lin.write('logout\n')
    log.write('logout\n')
    lin.close()
    log.close()


def findArcs(scis, arcs):
    """
    Finds arc files that are related to the science files.
    This works only if the arc file has been named
    properly, as done by modifyArcs.py script.

    :param: scis, a list of science files
    :param: arcs, a slist of arc files

    :return: data, where science file names are keys and
             related arcs are values (a list)
    :rtype: a dictionary
    """
    #find arcs that match the science frames
    data = {}
    for sci in scis:
        tmp = sci.split('.')
        tm = []
        for arc in arcs:
            if tmp[0] in arc and tmp[1] in arc and tmp[2] in arc:
                tm.append(arc[:-5])
        if len(tm) == 2:
            data[sci] = tm
        else:
            print '\nCould not find arcs for:', sci
    return data


if __name__ == '__main__':
    #find all files
    scis = g.glob('ft*RS*slice*')
    arcs = g.glob('arc*.fits')

    data = findArcs(scis, arcs)
    generateIRAFtransformCommand(data)

    #run IRAF
    os.system('cl -o < transformlin.cl')
    os.system('cl -o < transformlog.cl')
