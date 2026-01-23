from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional


@dataclass
class CacheEntry:
    value: Any
    created: datetime
    ttl_seconds: int


class ServiceCache:
    def __init__(self, default_ttl_seconds: int = 600):
        self.default_ttl_seconds = default_ttl_seconds
        self._entries: Dict[str, CacheEntry] = {}


def cache_set(cache: ServiceCache, key: str, value: Any, ttl_seconds: Optional[int] = None) -> None:
    ttl = ttl_seconds if ttl_seconds is not None else cache.default_ttl_seconds
    cache._entries[key] = CacheEntry(value=value, created=datetime.now(), ttl_seconds=ttl)


def cache_get(cache: ServiceCache, key: str, ignore_expiry: bool = False):
    entry = cache._entries.get(key)
    if entry is None:
        return None
    if ignore_expiry:
        return entry.value
    if not is_cache_valid(cache, key):
        cache_invalidate(cache, key)
        return None
    return entry.value


def is_cache_valid(cache: ServiceCache, key: str) -> bool:
    entry = cache._entries.get(key)
    if entry is None:
        return False
    return datetime.now() - entry.created < timedelta(seconds=entry.ttl_seconds)


def cache_invalidate(cache: ServiceCache, key: str) -> None:
    if key in cache._entries:
        del cache._entries[key]
