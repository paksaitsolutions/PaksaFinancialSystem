"""
Caching utilities for tax reporting.

This module provides efficient caching mechanisms for tax reporting data,
including compression, invalidation strategies, and cache warming.
"""

import json
import zlib
import pickle
from typing import Any, Dict, Optional, List, Callable, TypeVar, Union
from datetime import datetime, timedelta
import hashlib
import logging
from functools import wraps

import aioredis
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.redis_utils import redis_manager

logger = logging.getLogger(__name__)

T = TypeVar('T')

class ReportCache:
    """Enhanced caching for tax reports with compression and invalidation."""
    
    def __init__(self):
        self.redis = None
        self._redis_initialized = False
        self.compress_threshold = 1024  # Compress objects larger than 1KB
        self.default_ttl = 3600  # 1 hour default TTL
        
    async def initialize(self):
        """Initialize the Redis connection if not already done."""
        if not self._redis_initialized and settings.REDIS_URL:
            try:
                await redis_manager.initialize()
                self.redis = await redis_manager.redis()
                self._redis_initialized = True
                logger.info("ReportCache Redis connection initialized")
            except Exception as e:
                logger.error(f"Failed to initialize ReportCache Redis: {e}")
                self._redis_initialized = False
    
    def _generate_cache_key(self, prefix: str, **kwargs) -> str:
        """Generate a consistent cache key from function arguments."""
        key_parts = [f"tax:report:{prefix}"]
        
        for k, v in sorted(kwargs.items()):
            if v is None:
                continue
                
            if isinstance(v, (str, int, float, bool)):
                key_parts.append(f"{k}:{v}")
            elif isinstance(v, (list, tuple, set)):
                key_parts.append(f"{k}:{':'.join(str(i) for i in sorted(v))}")
            elif isinstance(v, dict):
                key_parts.append(f"{k}:{self._dict_hash(v)}")
            elif hasattr(v, 'isoformat'):  # Handle date/datetime
                key_parts.append(f"{k}:{v.isoformat()}")
            else:
                key_parts.append(f"{k}:{str(v)}")
                
        return ":".join(str(part) for part in key_parts)
    
    def _dict_hash(self, dictionary: Dict[str, Any]) -> str:
        """Generate a hash for a dictionary."""
        return hashlib.md5(json.dumps(dictionary, sort_keys=True).encode()).hexdigest()
    
    def _serialize(self, value: Any) -> bytes:
        """Serialize a value, with compression for large objects."""
        try:
            serialized = pickle.dumps(value, protocol=pickle.HIGHEST_PROTOCOL)
            
            # Compress if over threshold
            if len(serialized) > self.compress_threshold:
                compressed = zlib.compress(serialized)
                # Only use compression if it actually saves space
                if len(compressed) < len(serialized):
                    return b'1' + compressed  # Prefix with 1 to indicate compressed
            
            return b'0' + serialized  # Prefix with 0 for uncompressed
            
        except (pickle.PicklingError, TypeError) as e:
            logger.error(f"Failed to serialize value for cache: {e}")
            raise ValueError(f"Could not serialize value: {e}")
    
    def _deserialize(self, value: bytes) -> Any:
        """Deserialize a value, handling compression if needed."""
        if not value:
            return None
            
        try:
            # Check compression flag
            if value[0] == 49:  # b'1' - compressed
                return pickle.loads(zlib.decompress(value[1:]))
            elif value[0] == 48:  # b'0' - uncompressed
                return pickle.loads(value[1:])
            else:
                # Backward compatibility for old format
                return pickle.loads(value)
                
        except (pickle.UnpicklingError, zlib.error, EOFError) as e:
            logger.error(f"Failed to deserialize cached value: {e}")
            return None
    
    async def get(self, key: str) -> Any:
        """Get a value from the cache."""
        if not self._redis_initialized:
            return None
            
        try:
            value = await self.redis.get(key)
            if value is not None:
                return self._deserialize(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> bool:
        """
        Set a value in the cache with optional TTL and tags.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (defaults to self.default_ttl)
            tags: List of tags for invalidation
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self._redis_initialized:
            return False
            
        try:
            serialized = self._serialize(value)
            ttl = ttl if ttl is not None else self.default_ttl
            
            # Use pipeline for atomic operations
            async with await self.redis.pipeline() as pipe:
                await pipe.set(key, serialized, ex=ttl)
                
                # Store tag associations if provided
                if tags:
                    tag_key = f"{key}:tags"
                    await pipe.sadd(tag_key, *tags)
                    await pipe.expire(tag_key, ttl)
                    
                    # Store reverse mapping from tags to keys
                    for tag in tags:
                        tag_members_key = f"tag:{tag}"
                        await pipe.sadd(tag_members_key, key)
                        await pipe.expire(tag_members_key, ttl)
                
                await pipe.execute()
                
            return True
            
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def invalidate_by_tags(self, tags: List[str]) -> int:
        """
        Invalidate all cache entries with the given tags.
        
        Args:
            tags: List of tags to invalidate
            
        Returns:
            int: Number of cache entries invalidated
        """
        if not self._redis_initialized or not tags:
            return 0
            
        try:
            count = 0
            
            for tag in tags:
                tag_members_key = f"tag:{tag}"
                
                # Get all keys with this tag
                cursor = b'0'
                while cursor:
                    cursor, keys = await self.redis.scan(
                        cursor=cursor or b'0',
                        match=f"tax:report:*{tag}*",
                        count=100
                    )
                    
                    if keys:
                        # Delete the keys and their tag associations
                        await self.redis.delete(*keys)
                        for key in keys:
                            await self.redis.delete(f"{key}:tags")
                        count += len(keys)
                
                # Clean up the tag index
                await self.redis.delete(tag_members_key)
                
            return count
            
        except Exception as e:
            logger.error(f"Error invalidating cache by tags {tags}: {e}")
            return 0
    
    async def clear_all(self) -> bool:
        """Clear all tax report cache entries."""
        if not self._redis_initialized:
            return False
            
        try:
            # Find all tax report keys
            cursor = b'0'
            keys_to_delete = []
            
            while cursor is not None:
                cursor, keys = await self.redis.scan(
                    cursor=cursor or b'0',
                    match="tax:report:*",
                    count=1000
                )
                if keys:
                    keys_to_delete.extend(keys)
            
            # Delete in batches to avoid blocking Redis
            if keys_to_delete:
                for i in range(0, len(keys_to_delete), 1000):
                    batch = keys_to_delete[i:i+1000]
                    await self.redis.delete(*batch)
            
            # Also clean up tag indexes
            cursor = b'0'
            tag_keys = []
            
            while cursor is not None:
                cursor, keys = await self.redis.scan(
                    cursor=cursor or b'0',
                    match="tag:*",
                    count=1000
                )
                if keys:
                    tag_keys.extend(keys)
            
            if tag_keys:
                for i in range(0, len(tag_keys), 1000):
                    batch = tag_keys[i:i+1000]
                    await self.redis.delete(*batch)
            
            return True
            
        except Exception as e:
            logger.error(f"Error clearing tax report cache: {e}")
            return False

# Singleton instance
report_cache = ReportCache()

def cached(
    ttl: int = 3600,
    key_prefix: Optional[str] = None,
    tags: Optional[List[str]] = None,
    unless: Optional[Callable[..., bool]] = None
):
    """
    Decorator to cache function results with TTL and tags.
    
    Args:
        ttl: Time to live in seconds
        key_prefix: Optional prefix for cache keys
        tags: List of tags for invalidation
        unless: Callable that returns True to skip caching
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Skip caching if unless condition is met
            if unless and unless(*args, **kwargs):
                return await func(*args, **kwargs)
                
            # Initialize cache if needed
            if not report_cache._redis_initialized:
                await report_cache.initialize()
                
            # Generate cache key
            cache_key = key_prefix or f"{func.__module__}:{func.__name__}"
            cache_key = report_cache._generate_cache_key(cache_key, **kwargs)
            
            # Try to get from cache
            cached_result = await report_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
                
            # Call the function if not in cache
            result = await func(*args, **kwargs)
            
            # Cache the result
            if result is not None:
                await report_cache.set(cache_key, result, ttl=ttl, tags=tags)
                
            return result
            
        return wrapper
        
    return decorator
