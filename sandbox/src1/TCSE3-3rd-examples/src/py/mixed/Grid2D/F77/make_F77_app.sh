#!/bin/sh -x
# compile the gridloop.f file as a stand-alone application:

g77 -O -o tmp.app gridloop.f

echo we make a test run:
timer.py ./tmp.app
