"""
Sample Module
"""

from onion.server import Broker
from onion.backend import Worker
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
    worker = Worker()
    worker.run()

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


if __name__ == "__main__":
    try:
        if len(sys.argv) == 1 or len(sys.argv) == 2 and sys.argv[1] == 'broker':
            run_broker()
        if len(sys.argv) == 2 and sys.argv[1] == 'worker':
            run_worker()
        if len(sys.argv) == 2 and sys.argv[1] == 'client':
            run_client()
    except KeyboardInterrupt:
        pass
