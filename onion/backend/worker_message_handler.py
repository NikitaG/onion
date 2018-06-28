# pylint: disable=E1101

from time import time

import zmq

from onion import constants, log
from onion.exceptions import HeartbeatFailed, InvalidMessage


class WorkerMessageHandler():
    def __init__(self, worker_socket: zmq.Socket):
        self.worker_socket = worker_socket

        self.heartbeat_at: float = time()
        self.liveness: int = constants.HEARTBEAT_LIVENESS

    def loop(self, socks):
        # Handle worker activity on backend
        if socks.get(self.worker_socket) == zmq.POLLIN:
            self._process_message()
        else:
            self.liveness -= 1
            if not self.liveness:
                raise HeartbeatFailed()
        if time() > self.heartbeat_at:
            self.heartbeat_at = time() + constants.HEARTBEAT_INTERVAL
            #   print("I: Worker heartbeat")
            self.worker_socket.send(constants.RESPONSE_HEARTBEAT)

    def _process_message(self):
        #  Get message
        #  - 3-part envelope + content -> request
        #  - 1-part HEARTBEAT -> heartbeat
        frames = self.worker_socket.recv_multipart()
        if not frames:
            raise InvalidMessage  # Interrupted

        if len(frames) == 4:
            self.worker_socket.send_multipart(frames[:3]+[constants.RESPONSE_OK])
            self.liveness = constants.HEARTBEAT_LIVENESS
            # time.sleep(1)  # Do some heavy work
        elif len(frames) == 1 and frames[0] == constants.RESPONSE_HEARTBEAT:
            # print("I: Queue heartbeat")
            self.liveness = constants.HEARTBEAT_LIVENESS
        else:
            log.error("Invalid message: %s", frames)
