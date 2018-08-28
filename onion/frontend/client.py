# pylint: disable=E1101
import zmq
import sys

from onion import log, constants
from time import time
from random import randint 


class Client(object):
    def __init__(self, server_address="tcp://localhost:5551", auto_recovery=True):
        self.server_address = server_address
        self.auto_recovery=auto_recovery
        self.context = zmq.Context(1)
        
        self.client = None
        # self.poll = zmq.Poller()

    def connect(self):
        if self.client:
            log.error("Client already connected to server.")
            return

        log.info("Connecting to server…")
        
        self.client = self.context.socket(zmq.PUSH)
        identity = b"%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
        log.info(str(identity))
    
        # self.client.setsockopt(zmq.IDENTITY, identity)
        
        self.client.bind(self.server_address)
        # self.poll.register(self.client, zmq.POLLIN)

    def disconnect(self, terminate=False):
        if not self.context:
            raise Exception("Client has been terminated.")

        if self.client:
            log.info("Disconnecting from server…")
            self.client.setsockopt(zmq.LINGER, 0)
            self.client.close()
            # self.poll.unregister(self.client)
            self.client = None

        if terminate:
            self.context.term()
            self.context = None
            log.info("Client terminated.")

    def send(self, message):
        if not self.client:
            raise Exception("Client isn't connected.")

        if type(message) == str:
            self.client.send_string(message)
        else:
            self.client.send(message)
        
