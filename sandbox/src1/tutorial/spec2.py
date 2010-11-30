import numpy as n

class TransmissionFunction:
    '''Abstract Class representing a transmission function of wavelength
  
Unitless'''
    def __mul__(self, other):
        if isinstance(other, TransmissionFunction):
            return CompositeTransmissionFunction(self, other)
        if isinstance(other, SourceFunction):
            return CompositeSourceFunction(self, other, 'multiply')
        if type(other) in [type(1), type(1.)]:
            return CompositeTransmissionFunction(
               self, ConstTransmission(other))
        else:
            print "must be product of TransmissionFunction, SourceFunction or constant"
    def __rmul__(self, other):
        return self.__mul__(other)
   
class CompositeTransmissionFunction(TransmissionFunction):
    '''Transmission function that is a product of two other transmission functions'''
    def __init__(self, tran1, tran2):
        if (not isinstance(tran1, TransmissionFunction) or
            not isinstance(tran2, TransmissionFunction)):
            print "Arguments must be TransmissionFunctions"
            raise TypeError
        self.tran1 = tran1
        self.tran2 = tran2
    def __call__(self, wave):
        return self.tran1(wave) * self.tran2(wave)
  
class ConstTransmission(TransmissionFunction):
    def __init__(self, value):
        self.value = value
    def __call__(self, wave):
        return 0.*wave + self.value    
  
class GaussianAbsorption(TransmissionFunction):
    def __init__(self, center, width, depth):
        self.center = center
        self.width = width
        self.depth = depth
    def __call__(self, wave):
        return 1. - self.depth*n.exp(-(wave-self.center)**2/(2*self.width**2))          
  
class SourceFunction:    
    '''Abstract Class representing a source as a function of wavelength 
  
Units are assumed to be Flambda
'''
    def __add__(self, other):
        if not isinstance(other, SourceFunction):
            print "Can only add SourceFunctions"
            raise TypeError
        return CompositeSourceFunction(self, other, 'add')    
        # __radd__ not needed
    def __mul__(self, other):
        if type(other) in [type(1), type(1.)]:
            other = ConstTransmission(other)
        if not isinstance(other, TransmissionFunction):
            print 'Source functions can only be '+ \
                 'multiplied by Transmission Functions or constants'
            raise TypeError
        return CompositeSourceFunction(self, other, 'multiply')
    def __rmul__(self, other):
        return self.__mul__(other)

class CompositeSourceFunction(SourceFunction):
    '''Source function that is a binary composition of two other functions
''' 
    def __init__(self, source1, source2, operation):
        self.comp1 = source1
        self.comp2 = source2
        self.operation = operation
    def  __call__(self, wave):
        if self.operation == 'add':
            return self.comp1(wave) + self.comp2(wave)
        if self.operation == 'multiply':
            return self.comp1(wave) * self.comp2(wave)

class BlackBody(SourceFunction):
    def __init__(self, temperature):
        '''Temperature in degrees Kelvin'''
        self.temperature=temperature
    def __call__(self, wave):
        BBCONST =6.625e-34 * 3e8/(1.38e-23 * 1.e-10)
        exparg = BBCONST/(n.array(wave)*self.temperature)
        exparg[exparg>600] = 600. # to prevent overflows
        return 1.e21/(wave**5 * (n.exp(exparg)-1.))

  
class Gaussian(SourceFunction):
    def __init__(self, center, width):
        self.width=width
        self.center=center
    def __call__(self, wave):
        return n.exp(-(wave-self.center)**2/(2*self.width**2))
