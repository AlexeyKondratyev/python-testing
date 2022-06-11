
import redis
import logging
from time import sleep
from random import uniform


CONN_TIMEOUT = 0.5 #connection timeout
REQ_TIMEOUT = 2 #request timeout
CONNS_ATTEMPTS = 5
BACKOFF_FACTOR = 2


logging.basicConfig(level=logging.DEBUG)


def sleep_betw_attempts(attempt):
    sleep_betw_attempts = format(uniform(BACKOFF_FACTOR, BACKOFF_FACTOR * 2 ** attempt), ".2f")
    logging.debug(f"sleeping {sleep_betw_attempts} seconds")
    return sleep(float(sleep_betw_attempts))

def conns_retries(func):
        def _wrapper(*args, **kwargs):
            for attempt in range(1, CONNS_ATTEMPTS+1):
                logging.debug(f"trying to connect with attempt {attempt}")
                try:
                    func(*args, **kwargs)
                except Exception as e:
                    logging.error(f"connection error{e}")
            sleep_betw_attempts(attempt)
        return _wrapper
    
def cache(func):
    def wrapper_cache(*args, **kwargs):
        cache_key = args + tuple(kwargs.items())
        if cache_key not in wrapper_cache.cache:
            wrapper_cache.cache[cache_key] = func(*args, **kwargs)
        return wrapper_cache.cache[cache_key]
    wrapper_cache.cache = dict()
    return wrapper_cache


class RedisCache():
    # socket_connect_timeout - timeout for socket connection
    # socket_timeout - timeout for reading/writing to the socket
    def __init__(self, host='localhost', 
                 port=6379, db=0, 
                 socket_connect_timeout=CONNS_ATTEMPTS,
                 socket_timeout = REQ_TIMEOUT,
                 connect=True):
        self.host = host
        self.port = port
        self.db = db
        self.socket_timeout = socket_timeout
        self.socket_connect_timeout = socket_connect_timeout
        if connect:
            self.connect()
    
    def connect(self):
        logging.debug(f"connect to{self.host}:{self.port}")
        self.storage = redis.Redis(
            host=self.host,
            port=self.port,
            db=self.db,
            socket_timeout=self.socket_timeout,
            socket_connect_timeout=self.socket_connect_timeout
        )

    @conns_retries
    def get(self, key):
        logging.debug(f"get key:{key} value")
        return self.storage.get(key)

    @conns_retries
    def set(self, key, value):
        logging.debug(f"set key:{key} value:{value}")
        return self.storage.set(key, value)

    @cache
    @conns_retries
    def cache_get(self, key):
        logging.debug(f"get cached key:{key} value")
        return self.storage.get(key)

    @cache
    @conns_retries
    def cache_set(self, key, score, time_store):
        logging.debug(f"set cached key:{key} score:{score} time_store:{time_store}")
        return self.storage.set(key, score, time_store)

