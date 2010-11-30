from distutils.core import setup, Extension

module1 = Extension('hello',
                    sources = ['HelloWorld.c'])

setup (name = 'PackageName',
       version = '1.0',
       description = 'This is a demo package',
       ext_modules = [module1])
