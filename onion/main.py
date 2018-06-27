"""
Sample Module
"""

from onion.server import Broker

def run_broker():
    """
    Running messaging broker
    """
    broker = Broker()
    broker.start()

if __name__ == "__main__":
    try:
        run_broker()
    except KeyboardInterrupt:
        pass
