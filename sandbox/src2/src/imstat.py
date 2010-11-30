#! /usr/bin/env python
import sys
from pyraf import iraf

def run_imstat(input):
    iraf.images()
    for image in input:
        iraf.imstat(image)

if __name__ == "__main__":
    run_imstat(sys.argv[1:])
