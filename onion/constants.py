HEARTBEAT_LIVENESS = 3
HEARTBEAT_INTERVAL = 1

BROKER_THREADS = 1


INTERVAL_INIT = 1
INTERVAL_MAX = 32

REQUEST_TIMEOUT = 2500
REQUEST_RETRIES = 3

#  Paranoid Pirate Protocol constants
RESPONSE_READY = b"\x01"      # Signals worker is ready
RESPONSE_HEARTBEAT = b"\x02"  # Signals worker heartbeat
RESPONSE_DELIVERED = b"\x10"
RESPONSE_OK = b"\x11"
RESPONSE_FAILED = b"\x12"
