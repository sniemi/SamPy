import cprimes
import math
import multiprocessing
import Queue
import threading
import timeit

CPU_COUNT = multiprocessing.cpu_count()

def isprime(n):
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    maximum = int(math.ceil(math.sqrt(n)))
    i = 3
    while i <= maximum:
        if n % i == 0:
            return False
        i += 2
    return True

def sum_primes(n):
    return sum(x for x in xrange(2, n) if isprime(x))

def single_threaded_test():
    for n in xrange(100000, 5000000, 100000):
        sum_primes(n)

def multi_threaded_test():
    def do_work(work_queue):
        while True:
            try:
                n = work_queue.get(block=False)
                sum_primes(n)
            except Queue.Empty:
                break

    q = Queue.Queue()
    for n in xrange(100000, 5000000, 100000):
        q.put(n)

    threads = [threading.Thread(target=do_work, args=(q,))
               for x in range(CPU_COUNT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def multi_process_test():
    def do_work(work_queue):
        while True:
            try:
                n = work_queue.get(block=False)
                sum_primes(n)
            except Queue.Empty:
                break

    q = multiprocessing.Queue()
    for n in xrange(100000, 5000000, 100000):
        q.put(n)

    threads = [multiprocessing.Process(target=do_work, args=(q,))
               for x in range(CPU_COUNT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def single_threaded_with_c_code_test():
    for n in xrange(100000, 5000000, 100000):
        cprimes.sum_primes(n)

def multi_threaded_with_c_code_test():
    def do_work(work_queue):
        while True:
            try:
                n = work_queue.get(block=False)
                cprimes.sum_primes(n)
            except Queue.Empty:
                break

    q = Queue.Queue()
    for n in xrange(100000, 5000000, 100000):
        q.put(n)

    threads = [threading.Thread(target=do_work, args=(q,))
               for x in range(CPU_COUNT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

def multi_process_with_c_code_test():
    def do_work(work_queue):
        while True:
            try:
                n = work_queue.get(block=False)
                cprimes.sum_primes(n)
            except Queue.Empty:
                break

    q = multiprocessing.Queue()
    for n in xrange(100000, 5000000, 100000):
        q.put(n)

    threads = [multiprocessing.Process(target=do_work, args=(q,))
               for x in range(CPU_COUNT)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()


if __name__ == '__main__':
    #tests = ["single_threaded_test()", "multi_threaded_test()",
    #         "multi_process_test()", "single_threaded_with_c_code_test()",
    #         "multi_threaded_with_c_code_test()",
    #         "multi_process_with_c_code_test()"]
    tests = ["single_threaded_with_c_code_test()",
    "multi_threaded_with_c_code_test()"]
    for t in tests:
        timer = timeit.Timer(t, setup="from primes import %s" % t[:-2])
        print t, ('%0.2f' % (timer.timeit(number=1) / 60)), 'minutes'
