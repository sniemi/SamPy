import numpy as n

class SourceFunction:    
    '''Abstract Class representing a source as a function of wavelength

    
Units are assumed to be Flambda

'''
    def __add__(self, other):
        return CompositeSourceFunction(self, other, 'add')    
        # __radd__ not needed

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
            
class BlackBody(SourceFunction):
    def __init__(self, temperature):
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


