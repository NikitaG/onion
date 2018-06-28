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
        self.poll = zmq.Poller()

    def connect(self):
        if self.client:
            log.error("Client already connected to server.")
            return

        log.info("Connecting to server…")
        
        self.client = self.context.socket(zmq.REQ)
        identity = b"%04X-%04X" % (randint(0, 0x10000), randint(0, 0x10000))
        log.info(str(identity))
    
        self.client.setsockopt(zmq.IDENTITY, identity)
    
        self.client.connect(self.server_address)
        self.poll.register(self.client, zmq.POLLIN)

    def disconnect(self, terminate=False):
        if not self.context:
            raise Exception("Client has been terminated.")

        if self.client:
            log.info("Disconnecting from server…")
            self.client.setsockopt(zmq.LINGER, 0)
            self.client.close()
            self.poll.unregister(self.client)
            self.client = None

        if terminate:
            self.context.term()
            self.context = None
            log.info("Client terminated.")

    def send(self, message):
        request = message.encode()
        log.debug("Sending (%s)", request)
        self.client.send(request)

        retries_left = constants.REQUEST_RETRIES
        while retries_left:
            socks = dict(self.poll.poll(constants.REQUEST_TIMEOUT))
            if socks.get(self.client) == zmq.POLLIN:
                frames = self.client.recv_multipart()
                reply = frames[1]
                msg_id = int.from_bytes(frames[0], byteorder=sys.byteorder)
                if not reply:
                    return False
                if reply == constants.RESPONSE_DELIVERED:
                    log.debug("Server delivered (%s)", msg_id)
                    return True
                if reply == constants.RESPONSE_OK:
                    log.debug("Server replied OK (%s)", msg_id)
                    return True
                else:
                    log.error("Malformed reply from server: %s" , reply)
                    return False

            else:
                retries_left -= 1
                if retries_left == 0 or not self.auto_recovery:
                    raise Exception("Unable to send message to server: No response from server.")
                
                log.warning("No response from server, retrying…")
                # Socket is confused. Close and remove it.
                log.debug("Reconnecting and resending (%s)", request)
                
                self.disconnect()
                self.connect()
                self.client.send(request)

