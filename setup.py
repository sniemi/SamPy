from distutils.core import setup

setup(
    name='SamPy',
    version='0.1',
    author='Sami-Matias Niemi',
    author_email='sniemi@unc.edu',
    packages=['astronomy', 'boolshoi', 'candels', 'cos', 'cosmology',
              'cuda', 'dates', 'db', 'finance', 'fits', 'fitting',
              'focus', 'grisms', 'herschel', 'image', 'log', 'parsing',
              'pca', 'plot', 'resolve', 'sandbox', 'smakced', 'smnIO',
              'statistics', 'stis', 'wrapper'],
    license='LICENSE.txt',
    url='http://users.utu.fi/saniem/SamPy/',
    long_description=open('README.txt').read(),
)