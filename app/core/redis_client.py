# @Version :1.0
# @Author  : Mingyue
# @File    : redis_client.py
# @Time    : 12/03/2026 20:09
"""
Redis client singleton for caching and Celery broker.
"""
import redis
from typing import Optional

from app.core.config import config

_redis_client: Optional[redis.Redis] = None


def get_redis() -> redis.Redis:
    """Get or create Redis client singleton."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            config.REDIS_URL,
            decode_responses=True,
        )
    return _redis_client


def ping() -> bool:
    """Check Redis connection."""
    try:
        return get_redis().ping()
    except redis.ConnectionError:
        return False
