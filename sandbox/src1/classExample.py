class Square:
    def __init__(self, side):
        self.side = side
    def calculateArea(self):
        return self.side**2.
    def display(self):
        print "Area of square (side of %f) is %f" % (self.side, Square.calculateArea(self))

class Circle:
    def __init__(self, radius):
        self.radius = radius
    def calculateArea(self):
        import math
        return math.pi*(self.radius**2.)
    def display(self):
        print "Area of circle (radius of %f) is %f" % (self.radius, Circle.calculateArea(self))

class Sphere(Circle):
    def calculateVolume(self):
        import math
        return 4./3.*math.pi*(self.radius**3.)
    def calculateArea(self):
        import math
        return 4*math.pi*(self.radius**2.)
    def display(self):
        print "Area of sphere (radius of %f) is %f" % (self.radius, Sphere.calculateArea(self))
        print "Volume of sphere ( radius of %f) is %f" % (self.radius, Sphere.calculateVolume(self))
    
if __name__ == '__main__':

    list = [Circle(5), Circle(7), Square(9), Sphere(3), Square(12)]

    for shape in list:
        shape.display()
        #print "The area is: ", shape.calculateArea()
