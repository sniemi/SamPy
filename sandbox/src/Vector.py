'''
Operator overloading example class.

Created on Feb 16, 2010

@author: Sami-Matias Niemi
'''
class Vector:
    def __init__(self, data):
        self.data = data
    
    def __repr__(self):
        print 'I am vector:'
        return repr(self.data)

    def __add__(self, v2):
        return Vector(map(lambda x, y: x+y, self.data, v2.data))

    def __sub__(self, v2):
        return Vector(map(lambda x, y: x-y, self.data, v2.data))

    def __div__(self, v2):
        return Vector(map(lambda x, y: x/y, self.data, v2.data))

    def __mul__(self, v2):
        return Vector(map(lambda x, y: x*y, self.data, v2.data))

if __name__ == '__main__':
    a = Vector([1, 2, 3])
    b = Vector([-1, 2, -1])
    print '1'
    print a #__repr__
    c = a + b
    print '2'
    print c
    d = (a - b) * Vector([-1, -1, -1])
    print '3'
    print d