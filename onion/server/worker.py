from time import time
from onion import constants


class Worker(object):
    def __init__(self, address):
        self.address = address
        self.expiry = time() + constants.HEARTBEAT_INTERVAL * constants.HEARTBEAT_LIVENESS
