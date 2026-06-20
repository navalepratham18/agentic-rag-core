import hashlib
import json
import logging
from src.cache.connection import redis_manager
from src.core.config import settings

logger = logging.getLogger(__name__)

class SemanticCache:
    def __init__(self):
        # Grabs the resilient connection pool we built earlier
        self.client = redis_manager.get_client()
        self.ttl = settings.CACHE_TTL_SECONDS

    def _generate_key(self, query: str) -> str:
        """
        Normalizes and hashes the query to create a deterministic Redis key.
        In a $0 local setup, we use exact-match hashing. 
        In production, you would replace this with vector embeddings for semantic matching.
        """
        normalized_query = query.lower().strip()
        query_hash = hashlib.sha256(normalized_query.encode()).hexdigest()
        return f"rag_cache:{query_hash}"

    def get(self, query: str) -> dict | None:
        """Retrieves a cached response if it exists."""
        if not self.client:
            return None # Fails gracefully if Redis is down
            
        key = self._generate_key(query)
        try:
            cached_data = self.client.get(key)
            if cached_data:
                logger.info(f"Cache HIT for query: '{query}'")
                return json.loads(cached_data)
            
            logger.info(f"Cache MISS for query: '{query}'")
            return None
        except Exception as e:
            logger.error(f"Redis GET failed. Bypassing cache. Error: {e}")
            return None

    def set(self, query: str, response: dict):
        """Stores a query-response pair in the cache with a TTL."""
        if not self.client:
            return
            
        key = self._generate_key(query)
        try:
            # setex sets the value and the expiration time in one atomic operation
            self.client.setex(
                name=key,
                time=self.ttl,
                value=json.dumps(response)
            )
            logger.info(f"Successfully cached response for query: '{query}'")
        except Exception as e:
            logger.error(f"Redis SET failed. Error: {e}")

# Instantiate a single global cache instance
semantic_cache = SemanticCache()