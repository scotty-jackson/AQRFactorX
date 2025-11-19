"""
Redis caching utilities
"""
import os
import json
import redis
from functools import wraps
from typing import Optional, Any
import hashlib

# Redis client
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

try:
    redis_client = redis.from_url(REDIS_URL, decode_responses=True)
    redis_client.ping()
    CACHE_ENABLED = True
except:
    redis_client = None
    CACHE_ENABLED = False


def cache_key(*args, **kwargs) -> str:
    """Generate cache key from arguments"""
    key_data = f"{args}_{kwargs}"
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: int = 3600, prefix: str = ""):
    """
    Decorator to cache function results in Redis

    Args:
        ttl: Time to live in seconds (default 1 hour)
        prefix: Prefix for cache key
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not CACHE_ENABLED:
                return func(*args, **kwargs)

            # Generate cache key
            key = f"{prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"

            # Try to get from cache
            try:
                cached_result = redis_client.get(key)
                if cached_result:
                    return json.loads(cached_result)
            except Exception:
                pass  # If cache fails, continue to execute function

            # Execute function
            result = func(*args, **kwargs)

            # Store in cache
            try:
                redis_client.setex(key, ttl, json.dumps(result))
            except Exception:
                pass  # If caching fails, just return result

            return result

        return wrapper
    return decorator


def clear_cache_pattern(pattern: str):
    """Clear all cache keys matching a pattern"""
    if not CACHE_ENABLED:
        return

    try:
        keys = redis_client.keys(pattern)
        if keys:
            redis_client.delete(*keys)
    except Exception:
        pass


def clear_all_cache():
    """Clear all cache"""
    if not CACHE_ENABLED:
        return

    try:
        redis_client.flushdb()
    except Exception:
        pass
