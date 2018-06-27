from collections import OrderedDict
from time import time

from onion import log


class WorkerQueue(object):
    def __init__(self):
        self.queue = OrderedDict()

    def ready(self, worker)->bool:
        """Add worker. Return True if worker is new, otherwise False """
        w = self.queue.pop(worker.address, None)
        self.queue[worker.address] = worker
        return w == None

    def purge(self):
        """Look for & kill expired workers."""
        t = time()
        expired = []
        for address,worker in self.queue.items():
            if t > worker.expiry:  # Worker expired
                expired.append(address)
        for address in expired:
            self.queue.pop(address, None)
            # log.debug("Idle worker expired: %s, workers ready: %d", address, len(self.queue))
            
    def next(self):
        address, _ = self.queue.popitem(False)
        return address

    def __len__(self):
        return len(self.queue)
