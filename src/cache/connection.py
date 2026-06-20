import redis
import logging
from src.core.config import settings

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisManager:
    def __init__(self):
        self.url = settings.REDIS_URL
        self.client = None
        self._connect()

    def _connect(self):
        """Attempts to establish a connection to Redis with graceful failure."""
        try:
            self.client = redis.from_url(
                self.url, 
                decode_responses=True,
                socket_timeout=2.0, # Don't hang the app if Redis is unresponsive
                socket_connect_timeout=2.0
            )
            # Ping forces a network check; from_url is lazy and won't fail until a query is made
            self.client.ping()
            logger.info(f"Successfully connected to Redis at {self.url}")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis. Running in Cache-Bypass mode. Error: {e}")
            self.client = None

    def get_client(self):
        """Returns the Redis client, or None if the connection failed."""
        return self.client

# Instantiate a single global connection pool
redis_manager = RedisManager()