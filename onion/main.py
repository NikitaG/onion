"""
Sample Module
"""

from onion.server import Broker
from onion.backend import Worker, WorkerPool
from onion.frontend import Client
import sys
import time

def run_broker():
    """
    Running messaging broker
    """
    broker = Broker()
    broker.run()

def run_worker():
    """
    Running messaging worker
    """
    def work(*args):
        #time.sleep(0.1)
        print(*args)
        return True
    worker = Worker(work)
    worker.run()
    
def run_workers(threads_number: int = 1):
    """
    Running messaging worker
    """
    def work(*args):
        print("MSG", *args)
        time.sleep(0.1)
        return True
    workerpool = WorkerPool(work, threads_number=threads_number)
    workerpool.run()

def run_client():
    """
    Running messaging worker
    """
    client = Client()
    client.connect()
   
    s = time.time()
    i = 0
    while(time.time() - s < 1):
        i += 1
        client.send("Test %d" % i)
    print(i)
    client.disconnect()


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1 or len(sys.argv) == 2 and sys.argv[1] == 'broker':
            run_broker()
        elif len(sys.argv) == 2 and sys.argv[1] == 'worker':
            run_worker()
        elif len(sys.argv) == 3 and sys.argv[1] == 'workers':
            run_workers(int(sys.argv[2]))
        elif len(sys.argv) == 2 and sys.argv[1] == 'client':
            run_client()
    except KeyboardInterrupt:
        pass
