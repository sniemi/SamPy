"""
Class to process emsao output and combine information to generate a velocity field.

Parses the input data and outputs reformatted data to a file.
Combines velocity information with the coordinate information
to generate a velocity field and outputs this information to
a comma separated ascii file.

Will also generate a plot showing the parsed velocities.
This plot is meant for quick visual inspection only. Note
that all three slices are in the same plot so the x axis
values are rather arbitrary.

:requires: NumPy
:requires: SamPy
:requires: matplotlib (for plotting)

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0.6
"""
import csv
import numpy as np
from matplotlib import pyplot as plt
import SamPy.smnIO.write as write
import SamPy.smnIO.read as read
import SamPy.sandbox.odict as o


class emsaoVelocity():
    """
    Class to parse emsao velocity information and to combine it with coordinate information.
    Can be used to generate a velocity field.
    """

    def __init__(self, file='emsao.log'):
        """
        Class constructor.

        :param file: file name of the emsao log file
        :type file: string
        """
        self.file = file


    def parseInformation(self):
        """
        Parses the file given in the class constructor for velocity information.
        Assumes that the input is in the emsao log file format.

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

        #dumps to a file
        write.cPickleDumpDictionary(out, 'velocity.pk')

        self.velocityInfo = out
        return self.velocityInfo


    def getValues(self, data=None):
        """
        Massages data to a different format that is easier to deal with and plot.

        :param data: input data if None taken from the parseInformation method
        :type data: ndarray

        :return: reformatted data
        :rtype: dictionary
        """
        if data == None:
            data = self.velocityInfo

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
        self.velocityInfo2 = out

        return self.velocityInfo2


    def combineVelocityCoordinates(self,
                                   vel='velocity.pk',
                                   coord='coordinates.pk'):
        """
        Combine velocity and coordinate information.
        Takes the data from pickled files.

        :param vel: pickled velocity information
        :type vel: string
        :param coord: pickled coordinate information
        :type coord: string
        """
        #load in data
        coords = read.cPickledData(coord)
        vel = read.cPickledData(vel)

        #output
        out = []
        #loop over all time and space...
        for file in coords.keys():
            for coordline in coords[file]:
                for velline in vel:
                    if velline[0] == file.replace('.fits', '') and int(velline[1]) == coordline[1]:
                        #this is match but need to test if there's any useful veocity info
                        if float(velline[2]) > 0.0 or float(velline[5]) > 0.0:
                            tmp = coordline + [float(velline[2]), float(velline[3]),
                                               float(velline[4]), float(velline[5]),
                                               float(velline[6]), float(velline[7]), file]
                            out.append(tmp)

        info = {'coordinates': coords,
                'velocities': vel,
                'data': out}

        self.velocityField = info
        write.cPickleDumpDictionary(self.velocityField, 'velocityField.pk')


    def generatePlot(self):
        """
        Makes a quick plot of parsed data for visualization.
        
        This plot is only so useful given that the x-axis is in pixels,
        thus the centre of the galaxy is not aligned for different slices.
        """
        data = self.velocityInfo2

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


    def output(self, outfile='velocityField.csv'):
        """
        Outputs data to a pickled file and to a comma separated ascii file.

        For ascii file, the method will combine the coordinate and velocity
        information. Will set velocities to -99.99 if did not find information.
        Note, however, that emsao sets velocities to 0.0 if it was not able
        to derive a velocity.

        :param outfile: name of the ascii output file
        :type outfile: string
        """
        fh = open(outfile, 'w')
        fh.write('#file x_coord y_crood ra dec combine_vel error cz emission_vel error ez\n')

        #combine information
        for file in sorted(self.velocityField['coordinates'].keys()):
            for line in self.velocityField['coordinates'][file]:
                found = False
                for x in self.velocityField['data']:
                    if line[1] == x[1] and x[12] == file:
                        #found velocity information
                        found = True
                        output = x[12] + ', ' + str(int(x[0])) + ', ' + str(x[1]) + ', ' + str(x[4]) + ', ' + str(x[5])
                        output += ', ' + str(x[6]) + ', ' + str(x[7]) + ', ' + str(x[8]) + ', ' + str(x[9])
                        output += ', ' + str(x[10]) + ', ' + str(x[11])
                        fh.write(output + '\n')
                        break
                if not found:
                    output = file +', 1, ' + str(line[1]) + ', ' + str(line[4]) + ', ' + str(line[5])
                    output += ', -99.99' * 6
                    fh.write(output + '\n')

        fh.close()


if __name__ == '__main__':
    velocity = emsaoVelocity()
    velocity.parseInformation()
    velocity.getValues()
    velocity.combineVelocityCoordinates()
    velocity.output()

    #make a plot
    velocity.generatePlot()