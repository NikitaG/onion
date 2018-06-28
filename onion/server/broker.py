# pylint: disable=E1101
import sys
from collections import OrderedDict
from time import time

import zmq

from onion import constants, log
from onion.server import Worker, WorkerQueue
from threading import Thread


class Broker(object):
    def __init__(self, frontend_address="tcp://*:5551", backend_address="tcp://*:5552"):
        self.running: bool = False

        self.workers: WorkerQueue = WorkerQueue()
        self.context: zmq.Context = zmq.Context(constants.BROKER_THREADS)
        self.frontend_address: str = frontend_address
        self.frontend: zmq.Socket = None
        self.backend_address: str = backend_address
        self.backend: zmq.Socket = None

        self.heartbeat_at: float = None
        self.msg_id: int = 0

        log.debug("Messaging broker created")

    def run(self):
        log.info("Starting messaging broker: frontend at %s, backend at %s", self.frontend_address, self.backend_address)
        
        self._create_routers()
        self._start_routing()

    def _create_routers(self):
        self.frontend = self.context.socket(zmq.ROUTER)  # ROUTER
        self.backend = self.context.socket(zmq.ROUTER)  # ROUTER

    def _start_routing(self):
        self.frontend.bind(self.frontend_address)  # For clients
        self.backend.bind(self.backend_address)  # For workers

        poll_workers = zmq.Poller()
        poll_workers.register(self.backend, zmq.POLLIN)

        poll_both = zmq.Poller()
        poll_both.register(self.frontend, zmq.POLLIN)
        poll_both.register(self.backend, zmq.POLLIN)

        self.heartbeat_at = time() + constants.HEARTBEAT_INTERVAL

        while True:
            if not self._message_loop(poll_workers, poll_both):
                return
        log.info("Finishing message broker.")

    def _message_loop(self, poll_workers, poll_both):
        if len(self.workers.queue) > 0:
            poller = poll_both
        else:
            poller = poll_workers

        socks = dict(poller.poll(constants.HEARTBEAT_INTERVAL * 1000))

        # Handle worker activity on backend
        if socks.get(self.backend) == zmq.POLLIN:
            self._process_backend_message()

        if socks.get(self.frontend) == zmq.POLLIN:
            self._process_frontend_message()

        self.workers.purge()
        return True

    def _process_backend_message(self):
        # Use worker address for LRU routing
        frames = self.backend.recv_multipart()
        if not frames:
            log.error('Unable to receive any frames')
            raise Exception()

        address = frames[0]
        if self.workers.ready(Worker(address)):
            pass
            # log.debug("New worker is connected: %s, workers ready: %d", address, len(self.workers))

        # Validate control message, or return reply to client
        msg = frames[1:]
        if len(msg) == 1:
            if msg[0] not in (constants.RESPONSE_READY, constants.RESPONSE_HEARTBEAT):
                log.error("Invalid message from worker: %s", msg)
        # else:
        #     self.frontend.send_multipart(msg)

        # Send heartbeats to idle workers if it's time
        if time() >= self.heartbeat_at:
            for worker in self.workers.queue:
                msg = [worker, constants.RESPONSE_HEARTBEAT]
                self.backend.send_multipart(msg)
            self.heartbeat_at = time() + constants.HEARTBEAT_INTERVAL

    def _process_frontend_message(self):
        frames = self.frontend.recv_multipart()
        if not frames:
            log.error('Unable to receive any frames')
            raise Exception()

        self.msg_id += 1
        frames.insert(2, self.msg_id.to_bytes(4, byteorder=sys.byteorder))
        self.frontend.send_multipart(
            frames[:3] + [constants.RESPONSE_DELIVERED])

        frames.insert(0, self.workers.next())
        self.backend.send_multipart(frames)