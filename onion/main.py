"""
Sample Module
"""

from onion.server import Broker
from onion.client import Worker
import sys

def run_broker():
    """
    Running messaging broker
    """
    broker = Broker()
    broker.start()

def run_worker():
    """
    Running messaging worker
    """
    worker = Worker()
    worker.run()

if __name__ == "__main__":
    try:
        if len(sys.argv) == 1 or len(sys.argv) == 2 and sys.argv[1] == 'broker':
            run_broker()
        if len(sys.argv) == 2 and sys.argv[1] == 'worker':
            run_worker()
    except KeyboardInterrupt:
        pass
