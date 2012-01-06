"""
Prepares a LaTex article for submission.

Performs the following actions:

    1. Strips out all comments (lines starting with %) from the LaTex file.
    2. Renames all figures as fig1, fig2, etc. and updates the tex file
    3. Converts (E)PS figures to PDFs for arXiv.org submission (optional), requires GhostScript
    4. Crops the PDF bounding boxes for arXiv.org submission (optional), requires GhostScript
    5. Compresses everything into a single tar ball.

Run::

    python prepareToSubmit.py [-t] [-x] [-m] [-o] -i <filename.tex>



:author: Sami-Matias Niemi
:contact: sammy@sammyniemi.com

:version: 0.2
:date: 6/JAN/2012
"""
import glob as g
import sys, os, shutil, re, logging, subprocess
from optparse import OptionParser


def processArgs(printHelp=False):
    """
    Processes command line arguments.

    :param printHelp: if True then execution is halted and help is printed to stout
    :type printHelp: boolean

    :return: parsed command line arguments
    :rtype: instance
    """
    parser = OptionParser()

    parser.add_option('-i', '--input',
                      dest='input',
                      help='Name of the latex file, for example, document.tex',
                      metavar='string')
    parser.add_option('-o', '--output',
                      dest='output',
                      help='Name of the output folder. Default is "submit"',
                      metavar='string')
    parser.add_option('-x', '--xiv',
                      dest='xiv',
                      default=False,
                      action='store_true',
                      help='Converts the figures to PDFs for arXiv.org submission',
                      metavar='boolean')
    parser.add_option('-m', '--margin',
                      dest='margin',
                      help='Size of the bounding box margin in case of arXiv.org submission. Default is 2.',
                      metavar='integer')

    if printHelp:
        parser.print_help()
    else:
        return parser.parse_args()


def setupLogger():
    """
    Sets up a basic logger.
    """
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)s %(levelname)s: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename='prepareToSubmit.log',
                        filemode='w')
    # define a Handler which writes INFO messages or higher to the sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    # tell the handler to use this format
    console.setFormatter(formatter)
    # add the handler to the root logger
    logging.getLogger('').addHandler(console)


def processTex(filename, outdir):
    """
    Process the given tex file:

      1. Remove all lines starting with %
      2. Find all figures and rename them as fig1., fig2. etc.

    :param filename: name of the tex file to be processed
    :type filename: string
    :param outdir: name of the output path
    :type outdir: string

    :return: names of new figures
    :rtype: dict
    """
    #output file handler
    fh = open(outdir + '/' + filename, 'w')

    #dictionary of files that need to be copied
    data = {}

    i = 1
    for line in open(filename, 'r').readlines():
        if not line.startswith('%'):
            if 'includegraphics' in line:
                search = re.search(r'\\includegraphics.*{(.*)}', line)
                tmp = search.group(1)
                path = os.path.dirname(tmp)
                file = os.path.basename(tmp)
                ext = os.path.splitext(file)
                newfile = 'fig' + str(i) + ext[1]

                newline = line.replace('{0:>s}/{1:>s}'.format(path, file), newfile)
                fh.write(newline)

                data[tmp] = newfile

                i += 1
            else:
                fh.write(line)

    fh.close()

    return data


def directorySize(directory):
    """
    Walks all the subdirections and files in the given directory and counts the cumulative sizes of files.

    :param directory: name of the root directory
    :type directory: string

    :return: cumulative size of a given directory in kB
    :rtype: float
    """
    fs = 0.
    for path, dirs, files in os.walk(directory):
        for file in files:
            name = os.path.join(path, file)
            fs += os.path.getsize(name)

    return fs / 1024.


def reduceFileSize(path, margin):
    """
    Uses GhostScript to convert the (E)PS files to PDFs.
    This often helps to reduce the file sizes.

    If the input image is PNG then does nothing.

    :param path: path of the submission folder
    :type path: string
    :param margin: size of the bounding box margin
    :type margin: int

    :return: mapping of file names that were compressed
    :rtype: dict
    """
    reducedFiles = {}

    #change the current working directory to the submit folder
    os.chdir(path)

    for file in files.itervalues():
        if 'png' not in file:
            sp = os.path.splitext(file)
            newfile = sp[0] + '.pdf'

            #converts the file to PDF
            if 'eps' in file:
                cmd = 'epstopdf {0:>s} {1:>s}'.format(file, newfile)
            else:
                cmd = 'ps2pdf {0:>s} {1:>s}'.format(file, newfile)
            logging.debug(cmd)
            try:
                subprocess.call(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            except:
                logging.error('Did not find GhostScript, cannot reduce file sizes...\n')
                os.chdir('../')
                break

            #crops the bounding box
            cmd = 'pdfcrop --margins {0:d} {1:>s} {2:>s}'.format(margin, newfile, newfile)
            logging.debug(cmd)
            try:
                subprocess.call(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            except:
                logging.error('Could not crop the bounding box of {0:>s}...\n'.format(newfile))

            #gets file sizes
            old = os.path.getsize(file) / 1024.
            new = os.path.getsize(newfile) / 1024.

            if new > 500.:
                logging.info('{0:>s} is larger than 500kB, '.format(file))

            #test size?
            if new < old:
                #the new file is smaller
                os.remove(file)
                logging.info('{0:>s} was reduced from {1:.2f} to {2:.2f} kB'.format(file, old, new))
                #now the fileformat is wrong in the text...
                reducedFiles[file] = newfile
            else:
                os.remove(newfile)

    #change the current working directory back
    os.chdir('../')

    return reducedFiles


def changeFilenames(reduced, path, input):
    """
    Changes the figure filenames in the tex files.

    :param reduced: mapping of the compressed and original file names
    :type reduced: dict
    :param path: path to the tex file
    :type path: string
    :param input: name of the tex file
    :type input: string

    :rtype: None
    """
    file = path + '/' + input
    data = open(file, 'r').readlines()
    os.remove(file)

    fh = open(file, 'w')
    for line in data:
        if 'includegraphics' in line:
            for key in reduced:
                if key in line:
                    new = line.replace(key, reduced[key])
                    fh.write(new)

                    logging.debug('Changed {0:>s} to {1:>s} '.format(line, new))
        else:
            fh.write(line)

    fh.close()


if __name__ == '__main__':
    opts, args = processArgs()

    if opts.input is None:
        processArgs(printHelp=True)
        sys.exit(-9)
    else:
        #set up the logger
        setupLogger()

    if opts.output is None:
        output = 'submit'
    else:
        output = opts.output

    logging.info('Processing %s LaTex file to %s folder\n' % (opts.input, output))

    #create a folder
    if not os.path.exists(output):
        os.makedirs(output)

    #copy TEX and BBL files to the submit directory
    shutil.copyfile(opts.input, output + '/' + opts.input)
    bbls = g.glob('*.bbl')
    if len(bbls) > 1:
        logging.warning('Found more than one .bbl file, this is confusing...\n')
    for bbl in bbls:
        shutil.copyfile(bbl, output + '/' + bbl)

    #process the tex file
    files = processTex(opts.input, output)

    #copy new figures to the submit directory
    for key, value in files.iteritems():
        shutil.copyfile(key, output + '/' + value)

    #test the size of the files in the directory
    logging.info('The new {0:>s} folder is about {1:.2f} kB\n'.format(output, directorySize(output)))

    #tries to reduce the file size by converting all PS files to PDFs if arXiv.org submission
    if opts.margin is None:
        margin = 2
    else:
        margin = int(opts.margin)

    reduced = reduceFileSize(output, margin)
    changeFilenames(reduced, output, opts.input)

    #tries to create a tar ball
    try:
        logging.info('Will create a tar ball using the following files:')
        subprocess.call('tar cvzf {0:>s}.tar.gz submit'.format(output), shell=True)
        logging.info('The tar ball is about {0:.2f} kB'.format(os.stat('{0:>s}.tar.gz'.format(output)).st_size / 1024.))
    except:
        logging.error('Did not find tar, cannot create a tar ball...')
        
