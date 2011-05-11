import Queue
import random
import threading
import time

q = Queue.Queue()

# Console colors
RED = '\x1b[31m'
RESET = '\x1b[0m'

def producer(num_simulations=10):
    for simulation in range(num_simulations):
        simulation += 1
        print '%sPRODUCER%s: Starting simulation #%d' \
              % (RED, RESET, simulation)
        simulation_remaining = random.randint(1, 3) * 5
        while simulation_remaining > 0:
            print '%sPRODUCER%s: Working on product for simulation #%d ' \
                  '(%d seconds remaining)' \
                  % (RED, RESET, simulation, simulation_remaining)
            time.sleep(5)
            simulation_remaining -= 5
        print '%sPRODUCER%s: Simulation #%d done; putting result on queue' \
              % (RED, RESET, simulation)
        q.put(simulation)
    print '%sPRODUCER%s: Done all simulations; exiting' % (RED, RESET)


def consumer(timeout=15):
    while True:
        try:
            result = q.get(timeout=timeout)
        except Queue.Empty:
            print 'CONSUMER: Queue still empty after waiting %d seconds; ' \
                  'exiting' % timeout
            break
        print 'CONSUMER: Starting processing new result (%d)' % result
        simulation_remaining = random.randint(1, 3) * 5
        while simulation_remaining > 0:
            print 'CONSUMER: Processing result %d (%d seconds remaining)' \
                  % (result, simulation_remaining)
            time.sleep(5)
            simulation_remaining -= 5
        print 'CONSUMER: Processing result %d done.  Getting next result...' \
              % result
        q.task_done()


if __name__ == '__main__':
    producer_thread = threading.Thread(target=producer, args=(3,))
    consumer_thread = threading.Thread(target=consumer)
    producer_thread.daemon = True
    consumer_thread.daemon = True
    producer_thread.start()
    consumer_thread.start()
    producer_thread.join()
    consumer_thread.join()
    q.join()
