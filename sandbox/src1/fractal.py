"""
draw a fractal tree using PIL, code adopted from:
http://www.math.union.edu/research/fractaltrees/
uses the Python Image Library (PIL) free from:
http://www.pythonware.com/products/pil/index.htm
"""

import os
import math

# needs Python Image Library (PIL)
from PIL import Image, ImageDraw

def fractal_tree(iter, origin, t, r, theta, dtheta):
    """
    returns a list of line begin/end coordinate tuples
    iter:     iteration number, stop when iter == 0
    origin:   x,y coordinates of the start of this branch
    t:        current trunk length
    r:        factor to contract the trunk each iteration
    theta:    starting orientation
    dtheta:   angle of the branch
    """
    if iter == 0:
        return []
    x0, y0 = origin
    x, y = x0 + t * math.cos(theta), y0 + t * math.sin(theta)
    lines = [((x0,y0), (x,y))]
    # recursive calls
    lines.extend(fractal_tree(iter-1, (x,y), t * r, r, theta + dtheta, dtheta))
    lines.extend(fractal_tree(iter-1, (x,y), t * r, r, theta - dtheta, dtheta))
    return lines

def draw_lines(lines, width=320, height=250):
    """draw and return the fractal tree image"""
    # create empty white image to draw on
    image1 = Image.new("RGB", (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(image1)
    for line in lines:
        draw.line(line, (0, 0, 0))
        #print line  # test
    return image1

# test the functions ...
if __name__ == '__main__':
    # angle to radian factor
    ang2rad = math.pi/180.0
    
    # experiment with number of iterations (try 4 to 16)
    iter = 14
    # experiment with trunk length (try 100)
    t = 120
    # experiment with factor to contract the trunk each iteration (try 0.65)
    r = 0.65
    # starting orientation (initial 90 deg)
    theta = 90.0 * ang2rad
    # experiment with angle of the branch (try 60 deg)
    dtheta = 60.0 * ang2rad
    # center of top
    origin = (200, 0)
    
    lines = fractal_tree(iter, origin, t, r, theta, dtheta)
    
    # change width and height as needed ...
    width = 400
    height = 300
    image1 = draw_lines(lines, width, height)
    
    # use PIL's show, internally saves a temporary bitmap file, then calls the default viewer
    # (the problem: these bitmap files are large and accumulate in one of the temp directories)
    #imgage1.show()
    
    # or ...

    # save as .png .jpg .gif or .bmp file
    # (the .png format gives the smallest file size)
    filename = "fractaltree.jpg"
    image1.save(filename)
    
    """
    # ... and view the saved file, works with Windows only
    # behaves like double-clicking on the saved file
    os.startfile(filename)
    """

    # another way to activate the default viewer associated with the image
    # might work on more platforms
    import webbrowser
    webbrowser.open(filename)
