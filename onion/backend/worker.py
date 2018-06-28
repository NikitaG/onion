# pylint: disable=E1101

from time import time, sleep
from random import randint

from onion.exceptions import HeartbeatFailed
from onion.backend import WorkerMessageHandler

import zmq

from onion import constants, log


class Worker(object):
    def __init__(self, broker_address: str = "tcp://localhost:5552", auto_recovery: bool = True):
        self.running: bool = False
        self.auto_recovery: bool = auto_recovery

        self.broker_address: str = broker_address
        self.context: zmq.Context = zmq.Context(1)
        self.poller: zmq.Poller = zmq.Poller()

    def run(self):
        interval = constants.INTERVAL_INIT
        while True:
            self.run_handler()
            if not self.auto_recovery:
                raise Exception
            else:
                log.warning("Heartbeat failure, can't reach queue")
                log.info("Reconnecting in %0.2fs…", interval)
                sleep(interval)
                if interval < constants.INTERVAL_MAX:
                    interval *= 2

        return True

    def run_handler(self):
        worker = self._create_worker()

        try:
            handler = WorkerMessageHandler(worker)
            while True:
                socks = dict(self.poller.poll(constants.HEARTBEAT_INTERVAL * 1000))
                handler.loop(socks)
        except HeartbeatFailed:
            self._kill_worker(worker)

    def _create_worker(self)-> zmq.Socket:
        """Helper function that returns a new configured socket"""

        identity = b"%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))

        worker = self.context.socket(zmq.DEALER)  # DEALER
        worker.setsockopt(zmq.IDENTITY, identity)
        self.poller.register(worker, zmq.POLLIN)

        worker.connect(self.broker_address)
        worker.send(constants.RESPONSE_READY)

        log.debug("Worker created and bound, id: %s", str(identity))
        return worker

    def _kill_worker(self, worker):
        self.poller.unregister(worker)
        worker.setsockopt(zmq.LINGER, 0)
        worker.close()
