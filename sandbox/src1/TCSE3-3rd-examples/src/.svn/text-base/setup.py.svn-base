#!/usr/bin/env python
from distutils.core import setup, Extension
import os, glob

os.chdir('tools')
# all scripts in src/tools are executables (subst.py is also a module)
scripts = os.listdir(os.curdir)
for del_dir in 'scitools', 'CVS', '.svn', 'build':
    try:
        del scripts[scripts.index(del_dir)]
    except:
        pass
packages = ['scitools']
modules = ['subst']

setup(
    name='scitools',
    version='2.0',  # for 2nd edition of the book below
    description='Software for the book "Python Scripting for Computational Science" by H. P. Langtangen',
    author="H. P. Langtangen",
    author_email='hpl@simula.no',
    packages=packages,
    scripts=scripts,
    py_modules=modules,
    )
