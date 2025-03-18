import redis
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional
import os
from functools import wraps

class Cache:
    def __init__(self):
        """Initialize Redis connection."""
        self.redis_client = redis.Redis(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0)),
            decode_responses=True
        )
        
        # Default cache expiration (1 hour)
        self.default_expiry = timedelta(hours=1)
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve data from cache."""
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
    
    def set(self, key: str, value: Dict[str, Any], expiry: Optional[timedelta] = None) -> bool:
        """Store data in cache."""
        try:
            self.redis_client.setex(
                key,
                int((expiry or self.default_expiry).total_seconds()),
                json.dumps(value)
            )
            return True
        except Exception:
            return False
    
    def delete(self, key: str) -> bool:
        """Delete data from cache."""
        try:
            self.redis_client.delete(key)
            return True
        except Exception:
            return False
    
    def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        return bool(self.redis_client.exists(key))
    
    def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return len(keys)
        except Exception:
            return 0

def cache_result(expiry: Optional[timedelta] = None):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Initialize cache
            cache = Cache()
            
            # Try to get from cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # If not in cache, execute function
            result = func(*args, **kwargs)
            
            # Store in cache
            cache.set(cache_key, result, expiry)
            
            return result
        return wrapper
    return decorator

# Cache key patterns
ANALYSIS_KEY_PATTERN = "analysis:*"
REPORT_KEY_PATTERN = "report:*"
WEBHOOK_KEY_PATTERN = "webhook:*"
EXPORT_KEY_PATTERN = "export:*"

# Initialize global cache instance
cache = Cache() 