# cache.py
from functools import wraps
from cachetools import TTLCache
import asyncio

cache = TTLCache(maxsize=100, ttl=300)  # Cache up to 100 items for 5 minutes

def async_cache(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        key = str(args) + str(kwargs)
        if key in cache:
            return cache[key]
        result = await func(*args, **kwargs)
        cache[key] = result
        return result
    return wrapper