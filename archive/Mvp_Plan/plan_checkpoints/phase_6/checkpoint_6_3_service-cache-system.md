# Checkpoint 6.3: Service Cache System

#### Checkpoint 6.3: Service Cache System
**Generic caching for all services.**

**Tasks:**
1. Create `src/ai_radio/services/cache.py`
2. Generic cache with expiration
3. Used by weather and other services

**Tests First:**
```python
# tests/services/test_cache.py
"""Tests for service cache."""
import pytest
from datetime import datetime, timedelta
from src.ai_radio. services.cache import (
    ServiceCache,
    cache_get,
    cache_set,
    cache_invalidate,
    is_cache_valid,
)


class TestServiceCache:
    """Test generic caching."""
    
    def test_set_and_get(self):
        """Must be able to set and get values."""
        cache = ServiceCache()
        cache_set(cache, "key", "value")
        assert cache_get(cache, "key") == "value"
    
    def test_get_missing_returns_none(self):
        """Getting missing key must return None."""
        cache = ServiceCache()
        assert cache_get(cache, "nonexistent") is None
    
    def test_cache_expires(self):
        """Cached values must expire."""
        cache = ServiceCache(default_ttl_seconds=60)
        cache_set(cache, "key", "value")
        
        # Simulate time passing
        cache._entries["key"]. created = datetime.now() - timedelta(seconds=120)
        
        assert cache_get(cache, "key") is None
    
    def test_invalidate_removes_entry(self):
        """Invalidating must remove entry."""
        cache = ServiceCache()
        cache_set(cache, "key", "value")
        cache_invalidate(cache, "key")
        assert cache_get(cache, "key") is None
```

**Success Criteria:**
- [x] All cache tests pass
- [x] Generic cache works for any data
- [x] Expiration works correctly

**Git Commit:** `feat(services): add service cache`
