# pylint: disable=E1101

from time import time
from typing import Callable

import zmq

from onion import constants, log
from onion.exceptions import HeartbeatFailed, InvalidMessage


class WorkerMessageHandler():
    def __init__(self, worker_func: Callable[..., bool], worker_socket: zmq.Socket):
        self.worker_socket: zmq.Socket = worker_socket
        self.worker_func: Callable[..., bool] = worker_func

        self.heartbeat_at: float = time()
        self.liveness: int = constants.HEARTBEAT_LIVENESS

    def loop(self):
        self._process_message()
        
    def _process_message(self):
        line = self.worker_socket.recv_string()
        self.worker_func(line)