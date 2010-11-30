'''
Created on Feb 15, 2010

@author: Sami-Matias Niemi
'''

class HSTInstruments():
    def __init__(self, instrument, exposures, usage):
        '''
        Constructor
        '''
        self.instrument = instrument
        self.exposures = exposures
        self.usage = usage

    def display(self):
        frm = (self.instrument, self.exposures, self.usage)
        print 'Weighted usage of %s is %.0f while the current usage is %s' % frm
    
    def __add__(self, x):
        if 'increasing' in self.usage: tmp = self.usage
        elif 'increasing' in x.usage : tmp = x.usage
        else: tmp = 'unknown'
        return HSTInstruments(self.instrument + ' and ' + x.instrument + ' in parrallel',
                              (self.exposures + x.exposures)**2 / x.exposures,
                              tmp)
    
    def __mul__(self, x):
        print 'Such a weird choice trying to multiply...'
        return HSTInstruments('INVALID', 0, 'NONE')
    
if __name__ == '__main__':
    
    s = HSTInstruments('COS', 500, 'increasing')
    a = HSTInstruments('NICMOS', 700, 'non-existing')
    m = HSTInstruments('STIS', 1000, 'slowing down')
    
    print '0'
    a.display()
    add = s + a
    print '1'
    add.display()
    print '2'
    multi = s * a 
    multi.display()
    print '3'
    wrd = (m + a) + (s + m)
    wrd.display()