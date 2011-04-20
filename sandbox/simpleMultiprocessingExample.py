from multiprocessing import Pool

def aFunction(x):
    return [[len(z), z] for z in x]

if __name__ == '__main__':
    #create a pool that has 8 workers
    pool = Pool(processes=8)
    d = ['test', 'word', 'should', 'have',
         'more', 'than', 'eight', 'words',
         'This', 'is', 'a', 'pretty', 'stupid',
         'example']
    #get the result asynchronously
    result = pool.apply_async(aFunction, [d])
    #print out the results
    print result.get()
