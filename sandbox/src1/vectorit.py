
class Vectors:
    def __init__(self, a, b):
        self.a = a; self.b = b

    def dotProduct(self):
        return self.a[0]*self.b[0] + self.a[1]*self.b[1] + self.a[2]*self.b[2]

    def crossProduct(self):
        return ((self.a[1]*self.b[2]-self.a[2]*self.b[1]),
               (self.a[0]*self.b[2]-self.a[2]*self.b[0]),
               (self.a[0]*self.b[1]-self.a[1]*self.b[0]))


if (__name__ == '__main__'):
    r = (1,2,3)
    d = (2,-1,1)

    vec = Vectors(r,d)
    print "%s dot %s = %f" % (r,d,vec.dotProduct())
    print
    print "%s x %s = %s" % (r,d,vec.crossProduct())
