"""
Image transformation functions.

:requires: NumPy
:requires: SciPy.ndimage

:author: Sami-Matias Niemi
:contact: sniemi@unc.edu

:version: 0,1
"""
import numpy
from scipy.ndimage import interpolation

def homogeneous(xywIn):
    """
    Converts a 2xN or 3xN set of points to homogeneous coordinates.
        - for 2xN arrays, adds a row of ones
        - for 3xN arrays, divides all rows by the third row
    """
    if xywIn.shape[0] == 3:
        xywOut = numpy.zeros_like(xywIn)
        for i in range(3):
            xywOut[i, :] = xywIn[i, :] / xywIn[2, :]
    elif xywIn.shape[0] == 2:
        xywOut = numpy.vstack((xywIn, numpy.ones((1, xywIn.shape[1]), dtype=xywIn.dtype)))

    return xywOut


def Image(input, tform, output_range="same"):
    """
    Transform the input image using a 3x3 transform.  The array tform should
    specify the 3x3 transform from input to output coordinates, a forward
    mapping.  This matrix needs to have an inverse.
    
    output_range should be one of:
        "same" - match the range from the input image
        "auto" - determine a range by applying the transform to the corners of the input image
        ndarray - a 2x2 numpy array like [(x1, y1), (x2, y2)]
    """
    h, w = input.shape[0:2]

    # determine pixel coordinates of output image
    if output_range == "auto":
        pass
    elif type(output_range) == numpy.ndarray:
        pass
    else:
        yy, xx = numpy.mgrid[0:h, 0:w]

    # transform output pixel coordinates into input image coordinates
    xywOut = numpy.vstack((xx.flatten(), yy.flatten()))
    xywOut = homogeneous(xywOut)
    xywIn = numpy.dot(numpy.linalg.inv(tform), xywOut)
    xywIn = homogeneous(xywIn)

    # reshape input image coordinates
    xxIn = xywIn[0, :].reshape((h, w))
    yyIn = xywIn[1, :].reshape((h, w))

    # sample output image
    if input.ndim == 3:
        output = numpy.zeros((h, w, input.shape[2]), dtype=input.dtype)
        for d in range(input.shape[2]):
            output[..., d] = interpolation.map_coordinates(input[..., d], [yyIn, xxIn])
    else:
        output = interpolation.map_coordinates(input, [yyIn, xxIn])

    return output


def makeCenteredRotation(angle, center=(0, 0)):
    """
    Creates a 3x3 transform matrix for centered rotation.

    :param: angle, in degrees
    :param: center, a list [xcentre, ycentre]
    """
    # center
    Cf = numpy.array([[1, 0, -center[0]],
                      [0, 1, -center[1]],
                      [0, 0, 1]])
    Cb = numpy.linalg.inv(Cf)

    # rotate
    cost = numpy.cos(numpy.deg2rad(angle))
    sint = numpy.sin(numpy.deg2rad(angle))
    R = numpy.array([[cost, -sint, 0],
                     [sint, cost, 0],
                     [0, 0, 1]])

    # compose
    A = numpy.dot(R, Cf)
    A = numpy.dot(Cb, A)
    return A
