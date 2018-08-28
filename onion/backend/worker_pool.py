from typing import Callable
import threading
from onion.backend import Worker


class WorkerPool():
    def __init__(self, worker_func: Callable[..., bool], broker_address: str = "tcp://localhost:5551", auto_recovery: bool = True, threads_number: int = 1):
        self.worker_func: Callable[..., bool] = worker_func
        self.threads_number: int = threads_number
        self.broker_address: str = broker_address
        self.auto_recovery: bool = auto_recovery

    def _start_worker(self):
        worker = Worker(self.worker_func, broker_address=self.broker_address, auto_recovery=self.auto_recovery)
        worker.run()

    def run(self):
        threads = []
        for i in range(self.threads_number):
            thread = threading.Thread(name="Worker-%d"%i, target=self._start_worker)
            thread.start()
            threads.append(thread)
        
        for x in threads:
            x.join()

