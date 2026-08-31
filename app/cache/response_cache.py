import hashlib
import time
from typing import Optional


class ResponseCache:
    def __init__(self, ttl_seconds: int = 300):
        self.ttl = ttl_seconds
        self._cache: dict[str, dict] = {}
        self._hits = 0
        self._misses = 0

    # Create a cache key from the normalized query.
    # For a Redis/Valkey cache, this is a very common approach.
    def _make_key(self, query: str) -> str:
        # .strip -> Removes whitespace from the beginning and end
        normalized_query = query.lower().strip()
        # .hexdigest -> result is always 64 hexadecimal characters
        return hashlib.sha256(normalized_query.encode()).hexdigest()

    def GetCache(self, query: str) -> Optional[str]:
        cache_key = self._make_key(query)

        if cache_key in self._cache:
            entry = self._cache[cache_key]

            if time.time() - entry["timestamp"] < self.ttl:
                self._hits += 1
                return entry["response"]
            else: 
                del self._cache[cache_key]

        self._misses += 1
        return None

    def SetCache(self, query: str, response: str) -> None:
        cache_key = self._make_key(query)

        self._cache[cache_key] = {
            "response": response,
            "timestamp": time.time(),
            "query": query
        }

    @property
    def stats(self) -> dict:
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        return {
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.1%}",
            "cached_entries": len(self._cache)
        }

