"""
Combines FITS images using the imcombine IRAF task.

The script calls IRAF from the command line as follows::

  cl -0 < command_file.cl

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import glob as g
import os


def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def writeCommand(data, outputfile, outfileid='lin'):
    """
    Writes an IRAF command file.

    :param: data,
    :param: outputfile, name of the output file
    :param: outfileid, id either lin or log

    :return: None
    """
    comp = data[0].split('.')
    tm = []
    fh = open(outputfile, 'w')
    fh.write('images\nimmatch\n')
    for i, file in enumerate(data):
        if i == 0:
            tm.append(file)
            continue

        tmp = file.split('.')
        if (tmp[1] == comp[1]) & (tmp[2] == comp[2]):
            tm.append(file)
        else:
            output = tmp[1] + tmp[2]
            fls = ''
            for x in tm:
                fls += x + ', '
            str = 'imcombine input="%s" output=%s%s ' % (fls[:-2], outfileid, output)
            str += 'combine=median reject=avsigclip scale=none lthresh=-1000\n\n'
            fh.write(str)
            tm = [file, ]
            comp = tmp

    fh.write('logout')
    fh.close()

    
if __name__ == '__main__':
    #lin files
    files = g.glob('str_lin*RS*.fits')

    #pprint.pprint(list(chunks(files, 9)))
    slice1 = files[::3]
    slice2 = files[1::3]
    slice3 = files[2::3]

    writeCommand(slice1, 'combine_commandslin1.cl')
    writeCommand(slice2, 'combine_commandslin2.cl')
    writeCommand(slice3, 'combine_commandslin3.cl')

    #call IRAF
    os.system('cl -o < combine_commandslin1.cl')
    os.system('cl -o < combine_commandslin2.cl')
    os.system('cl -o < combine_commandslin3.cl')


    #log files
    files = g.glob('str_log*RS*.fits')

    #pprint.pprint(list(chunks(files, 9)))
    slice1 = files[::3]
    slice2 = files[1::3]
    slice3 = files[2::3]

    writeCommand(slice1, 'combine_commandslog1.cl', outfileid='log')
    writeCommand(slice2, 'combine_commandslog2.cl', outfileid='log')
    writeCommand(slice3, 'combine_commandslog3.cl', outfileid='log')

    #call IRAF
    os.system('cl -o < combine_commandslog1.cl')
    os.system('cl -o < combine_commandslog2.cl')
    os.system('cl -o < combine_commandslog3.cl')
