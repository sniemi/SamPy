from multiprocessing import Pool

def f(*x):
    tmp = [a*a*a for a in x]
    return tmp

if __name__ == '__main__':
    evlist = [11,111,1111,123456789]
    pool = Pool(processes = 4)              # start 4 worker processes
    result = pool.apply_async(f, evlist) 
    print result.get(timeout=1)
    print pool.map(f, range(10))
