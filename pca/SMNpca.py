"""
This Python module contains principle component analysis (PCA).

It is SMN's adaptation and no guarantees for correct results
are made. So do not complain to me if it does not work ;-)

:requires: NumPy
:requires: matplotlib

:author: Sami-Matias Niemi
:contact: niemi@stsci.edu

:date: 14/11/08 Initial Version
:version: 0.1a
"""
__author__ = 'Sami-Matias Niemi'
__version__ = "0.1a"

class SMNpca():
    """
    This class calculates the principle component analysis (PCA).

    First PC is direction of the maximum variance from origin. Subsequent PCs are orthogonal
    to 1st PC and describe maximum residual variance. Eigenvector cells are coefficients of 
    the corresponding principal component.

    Data input must be a matrix where rows are dimensions/variables and columns
    are measurements/observations.
    
    Optional argument stdnorm refers to standard deviation normalisation.
    A PCA without dividing by the standard deviation is an eigenanalysis of the covariance matrix, 
    and a PCA in which you divide by the standard deviation is an eigenanalysis of the correlation matrix.

    Output is...
    """

    def __init__(self, inputMatrix, stdnorm=False):
        self.data = inputMatrix
        self.stdnorm = stdnorm

    def doPCA(self):
        import numpy as N
        import numpy.linalg as NA

        orgdata = N.transpose(self.data)

        #Removes mean from the orignal data
        avg = N.mean(orgdata, axis=0)
        if self.stdnorm:
            data = (orgdata - avg) / N.std(orgdata, axis=0)
        else:
            data = orgdata - avg

        #Calculates the covariance matrix
        #For 2dim:
        #If the non-diagonal elements in the covariance matrix are positive, 
        #we should expect that both the x and y variable increase together.
        self.cov = N.cov(N.transpose(N.mat(data)))

        #We could calculate the singular value decomposition, but not in this adaptation...
        #U, S_values, V_trans = NA.svd(data)

        #Calculates eigenvalues and eigenvectors
        self.evaltrue, self.evecorg = NA.eig(N.mat(self.cov))
        #I am not sure if this should be abs or evaltrue.real?
        #Depends if eigenvalues can have imaginary part in PCA...
        self.evalorg = N.transpose(N.mat(N.abs(self.evaltrue)))
        #temp = NA.eig(N.mat(cov))

        #sort eigenvectors by eigenvalues
        order = (N.argsort(self.evaltrue)[::-1])
        self.evec = N.take(self.evecorg, order, 1)
        self.eval = N.take(self.evaltrue, order)
        #This sorting is obsolete and actually gave wrong results...
        #tmp = []
        #for val, vec in zip(temp[0], temp[1]):
        #    tmp.append([val.real, vec])
        #Gives the components in order of significance:
        #sorted = sorted(tmp, cmp = lambda x,y: (-1 if x[0] < y[0] else (1 if x[0] > y[0] else 0)), reverse = True)

        #Lets get the feature vector:
        self.featurevec = N.mat(self.evec)

        #the eigenvector with the highest eigenvalue is the principle component of the data set:
        self.maxfeaturevec = self.featurevec[0][:]

        #New Data sets
        self.maxnewdata = N.mat(self.maxfeaturevec) * N.transpose(N.mat(data))
        self.newdata = self.featurevec * N.transpose(N.mat(data))

        return self.newdata

    def evectors(self):
        return self.evec

    def evalues(self):
        return self.eval

    def principleComponent(self):
        return self.maxfeaturevec

    def featureMatrix(self):
        return self.featurevec

    def DisplayAxisVariation(self):
        if self.stdnorm:
            dim = N.sum(self.eval)
            perc = self.eval / dim * 100.
            i = 0
            print
            for p in perc:
                i += 1
                #How much axis explains of the variation in the entire data set
                print 'PCA Axis %i: %4.2f per cent' % (i, p)

    def DisplayCov(self):
        print '\nCovariance matrix:\n', self.cov

    def DisplayEigenvalues(self):
        print '\nEigenvalues:\n', self.evalorg

    def DisplayEigenvectors(self):
        print '\nEigenvectors:\n', self.evecorg

    def DisplayFeatureMatrix(self):
        print '\nFeature matrix:\n', self.featurevec

    def DisplayNewData(self):
        print '\nFinal Data Transposed:\n', N.transpose(N.mat(self.newdata))

    def DisplayMajorComponentData(self):
        print '\nMajor Component Data Transposed:\n', N.transpose(N.mat(self.maxnewdata))

    def Cov(self):
        return self.cov

    def Eigenvalues(self):
        return self.evalorg

    def Eigenvectors(self):
        return self.evecorg

    def FeatureMatrix(self):
        return self.featurevec

    def MajorComponentData(self):
        return N.transpose(N.mat(self.maxnewdata))

    def VisualisePCAtoFileIn2D(self, data, filename):
        import pylab as P
        import numpy as N

        newdata = N.array(data)

        P.scatter(newdata[0, :], newdata[1, :])
        P.axhline(0.)
        P.axvline(0.)
        P.xlabel('PC 1')
        P.ylabel('PC 2')
        P.savefig(filename)

    def VisualisePCAtoFileIn3D(self, data, filename):
        import pylab as P
        import numpy as N

        newdata = N.array(data)
        P.scatter(newdata[0, :], newdata[1, :], s=newdata[2, :] * 4.)
        P.axhline(0.)
        P.axvline(0.)
        P.xlabel('PC 1')
        P.ylabel('PC 2')
        P.title('Size corresponds to PC3')
        P.savefig(filename)

if __name__ == '__main__':
    #This can be used for testing purposes
    import numpy as N

    #2 dimensional data
    x = [2.5, 0.5, 2.2, 1.9, 3.1, 2.3, 2.0, 1.0, 1.5, 1.1]
    y = [2.4, 0.7, 2.9, 2.2, 3.0, 2.7, 1.6, 1.1, 1.6, 0.9]
    orgdata = N.array([x, y])

    #3 dimensional data
    #x = [2.5,0.5,2.2,1.9,3.1,2.3,2.0,1.0,1.5,1.1]
    #y = [2.4,0.7,2.9,2.2,3.0,2.7,1.6,1.1,1.6,0.9]
    #z = [1.2,3.4,1.2,5.6,3.0,0.1,3.7,3.3,2.2,2.2]
    #orgdata = N.array([x , y, z])

    PCA = SMNpca(orgdata, stdnorm=False)
    newdata = PCA.doPCA()

    PCA.DisplayCov()
    PCA.DisplayMajorComponentData()
    PCA.DisplayFeatureMatrix()
    PCA.DisplayNewData()
    PCA.VisualisePCAtoFileIn2D(newdata, 'test')
