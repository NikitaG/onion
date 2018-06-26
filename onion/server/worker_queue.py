from collections import OrderedDict
from time import time

from onion import log


class WorkerQueue(object):
    def __init__(self):
        self.queue = OrderedDict()

    def ready(self, worker):
        self.queue.pop(worker.address, None)
        self.queue[worker.address] = worker

    def purge(self):
        """Look for & kill expired workers."""
        t = time()
        expired = []
        for address,worker in self.queue.items():
            if t > worker.expiry:  # Worker expired
                expired.append(address)
        for address in expired:
            log.debug("W: Idle worker expired: %s" % address)
            self.queue.pop(address, None)

    def next(self):
        address, _ = self.queue.popitem(False)
        return address

    def __len__(self):
        return len(self.queue)

