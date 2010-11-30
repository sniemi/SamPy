def ngaussSlow(n):
    import random
    return [random.gauss(0,1) for i in range(n)] 

r = ngaussSlow(10) 
print r

#####################################
def splitter(fname):
    import os
    dirname, basename = os.path.split(fname)
    return dirname, basename

f = '/some/path/case2.data_source'
import os
moviefile = os.path.basename(os.path.splitext(f)[0] + '.mpg') 

print moviefile

####################################
