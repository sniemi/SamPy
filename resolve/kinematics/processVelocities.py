"""
Class to process emsao output. Will parse the input data and output reformatted data to a file.
Will also generate a plot showing the velocities for pixels.

:requires: NumPy
:requires: matplotlib (for plotting)

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.1
"""
import csv
import numpy as np
from matplotlib import pyplot as plt
import SamPy.smnIO.write as write
import SamPy.sandbox.odict as o


class emsaoVelocity():
    """
    Class to parse emsao velocity information.
    """

    def __init__(self, file='emsao.log'):
        self.file = file


    def parseInformation(self):
        """
        Parses the file for velocity information.

        :return: velocity information
        :rtype: dictionary
        """
        out = []
        #read in data and loop over it
        data = open(self.file, 'r').readlines()
        for line in data:
            if len(line) > 1:
                tmp = line.split()
                if line.startswith('File:'):
                    file = tmp[1]
                    pixel = tmp[2]
                if line.startswith('Object:'):
                    object = tmp[1]
                if line.startswith('Combined'):
                    cvel = tmp[3]
                    cvelerr = tmp[5]
                    cz = tmp[8]
                if line.startswith('Emission'):
                    evel = tmp[3]
                    evelerr = tmp[5]
                    ez = tmp[8]
            else:
                out.append([file, pixel, cvel, cvelerr, cz, evel, evelerr, ez, object])
        return out


    def getValues(self, data):
        """
        Massages data to a different format that is easier to plot.

        :param data: input data (from parseInformation method)
        :type data: dictionary

        :return: reformatted data
        :rtype: dictionary
        """
        file = []
        pix = []
        cvel = []
        cvelerr = []
        evel = []
        evelerr = []
        for line in data:
            file.append(line[0])
            pix.append(int(line[1]))
            cvel.append(float(line[2]))
            cvelerr.append(float(line[3]))
            evel.append(float(line[5]))
            evelerr.append(float(line[6]))

        out = o.OrderedDict()
        out['file'] = file
        out['pixels'] = np.asarray(pix)
        out['cvelocities'] = np.asarray(cvel)
        out['cerrors'] = np.asarray(cvelerr)
        out['evelocities'] = np.asarray(evel)
        out['eerrors'] = np.asarray(evelerr)

        #dump to a pickled file
        write.cPickleDumpDictionary(out, 'tmpDict.pk')

        return out


    def generatePlot(self, data):
        """
        Makes a quick plot of parsed data for visualization.

        :param data: data to be plotted
        :type data: dictionary
        """
        minim = np.min(data['evelocities'][data['evelocities'] > 0]) * 0.99
        maxim = np.max(data['evelocities']) * 1.01

        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.errorbar(data['pixels'], data['cvelocities'], yerr=data['cerrors'],
                    marker='o', ms=4, ls='None', label='Combined Velocities')
        ax.errorbar(data['pixels'], data['evelocities'], yerr=data['eerrors'],
                    marker='s', ms=4, ls='None', label='Emission Velocities')
        ax.set_ylim(minim, maxim)
        ax.set_xlabel('Pixels')
        ax.set_ylabel('Velocity [km/s]')
        plt.legend(shadow=True, fancybox=True, numpoints=1)
        plt.savefig('velocity.pdf')


    def output(self, data, outfile='velocity.csv'):
        """
        Outputs data to two different files, one ascii and another pickled.

        :param data: data to be outputted
        :type data: dictionary
        :param outfile: name of the output file
        :type outfile: string
        """
        write.cPickleDumpDictionary(data, 'velocity.pk')

        fh = open(outfile, 'a')
        writer = csv.writer(fh)
        writer.writerows(data)
        fh.close()


if __name__ == '__main__':
    velocity = emsaoVelocity()
    info = velocity.parseInformation()
    velocity.output(info)

    #make a plot
    data = velocity.getValues(info)
    velocity.generatePlot(data)