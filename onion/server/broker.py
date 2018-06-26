# pylint: disable=E1101
import sys
from collections import OrderedDict
from time import time

import zmq

from onion import constants, log
from onion.server import Worker, WorkerQueue


class Broker(object):
    def __init__(self, frontend_address="tcp://*:5551", backend_address="tcp://*:5552"):
        self.running: bool = False
        self.context: zmq.Context = zmq.Context(constants.BROKER_THREADS)
        self.frontend_address: str = frontend_address
        self.backend_address: str = backend_address
        self.frontend: zmq.Socket = None
        self.backend: zmq.Socket = None
        self.poll_workers: zmq.Poller = None
        self.poll_both: zmq.Poller = None
        self.workers: WorkerQueue = WorkerQueue()
        self.heartbeat_at: float = None
        self.msg_id: int = 0

        log.debug("Messaging broker created")

    def start(self):
        log.debug("Starting messaging broker: frontend at %s, backend at %s", self.frontend_address, self.backend_address)
        self.running = True

        self._create_routers()
        self._start_routing()

    def stop(self):
        self.running = False

    def _create_routers(self):
        self.frontend = self.context.socket(zmq.ROUTER)  # ROUTER
        self.backend = self.context.socket(zmq.ROUTER)  # ROUTER

    def _start_routing(self):
        self.frontend.bind(self.frontend_address)  # For clients
        self.backend.bind(self.backend_address)  # For workers

        self.poll_workers = zmq.Poller()
        self.poll_workers.register(self.backend, zmq.POLLIN)

        self.poll_both = zmq.Poller()
        self.poll_both.register(self.frontend, zmq.POLLIN)
        self.poll_both.register(self.backend, zmq.POLLIN)

        self.heartbeat_at = time() + constants.HEARTBEAT_INTERVAL

        while self.running:
            if not self._message_loop():
                return

    def _message_loop(self):
        if len(self.workers.queue) > 0:
            poller = self.poll_both
        else:
            poller = self.poll_workers

        socks = dict(poller.poll(constants.HEARTBEAT_INTERVAL * 1000))

        # Handle worker activity on backend
        if socks.get(self.backend) == zmq.POLLIN:
            # Use worker address for LRU routing
            frames = self.backend.recv_multipart()
            if not frames:
                log.error('Unable to receive any frames')
                return False

            address = frames[0]
            self.workers.ready(Worker(address))

            # Validate control message, or return reply to client
            msg = frames[1:]
            if len(msg) == 1:
                if msg[0] not in (constants.RESPONSE_READY, constants.RESPONSE_HEARTBEAT):
                    print("E: Invalid message from worker: %s" % msg)
            else:
                self.frontend.send_multipart(msg)

            # Send heartbeats to idle workers if it's time
            if time() >= self.heartbeat_at:
                for worker in self.workers.queue:
                    msg = [worker, constants.RESPONSE_HEARTBEAT]
                    self.backend.send_multipart(msg)
                self.heartbeat_at = time() + constants.HEARTBEAT_INTERVAL
        if socks.get(self.frontend) == zmq.POLLIN:
            frames = self.frontend.recv_multipart()
            if not frames:
                log.error('Unable to receive any frames')
                return False

            self.msg_id += 1
            frames.insert(2, self.msg_id.to_bytes(4, byteorder=sys.byteorder))
            self.frontend.send_multipart(
                frames[:3] + [constants.RESPONSE_DELIVERED])

            frames.insert(0, self.workers.next())
            self.backend.send_multipart(frames)
            # [ wid, cid, _, msgid, msg]

        self.workers.purge()
        return True
