"""
Unit tests for ReportCache class.
"""

import asyncio
import pytest
import pickle
import zlib
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta

from app.core.tax.report_cache import ReportCache, report_cache

# Test data
TEST_KEY = "test_key"
TEST_VALUE = {"test": "data", "number": 123, "nested": {"key": "value"}}
TEST_TAGS = ["tag1", "tag2"]
TEST_TTL = 300

class TestReportCache:
    """Test cases for ReportCache class."""
    
    @pytest.fixture(autouse=True)
    async def setup_and_teardown(self):
        """Set up and tear down for each test."""
        # Initialize with a mock Redis connection
        self.redis_mock = AsyncMock()
        self.report_cache = ReportCache()
        self.report_cache.redis = self.redis_mock
        self.report_cache._redis_initialized = True
        
        # Reset mocks before each test
        self.redis_mock.reset_mock()
        
        yield
        
        # Clean up after each test
        await self.report_cache.clear_all()
    
    async def test_initialize_success(self):
        """Test successful Redis initialization."""
        with patch('app.core.redis_utils.redis_manager.initialize') as mock_init, \
             patch('app.core.redis_utils.redis_manager.redis') as mock_redis:
            
            mock_redis.return_value = self.redis_mock
            
            cache = ReportCache()
            await cache.initialize()
            
            mock_init.assert_called_once()
            assert cache._redis_initialized is True
    
    async def test_generate_cache_key(self):
        """Test cache key generation."""
        key = self.report_cache._generate_cache_key(
            "test_prefix",
            param1="value1",
            param2=123,
            param3=["a", "b", "c"],
            param4={"nested": "value"}
        )
        
        # Key should be deterministic based on input parameters
        assert key.startswith("tax:report:test_prefix")
        assert "param1:value1" in key
        assert "param2:123" in key
        assert "param3:a:b:c" in key
        assert "param4:" in key
    
    async def test_serialize_compression(self):
        """Test serialization with compression."""
        # Create a large enough value to trigger compression
        large_value = {"data": "x" * 2000}
        
        # Serialize with compression
        serialized = self.report_cache._serialize(large_value)
        
        # Should be compressed (starts with b'1')
        assert serialized.startswith(b'1')
        
        # Deserialize should return original value
        deserialized = self.report_cache._deserialize(serialized)
        assert deserialized == large_value
    
    async def test_serialize_no_compression(self):
        """Test serialization without compression."""
        # Small value that shouldn't be compressed
        small_value = {"data": "small"}
        
        # Serialize without compression
        serialized = self.report_cache._serialize(small_value)
        
        # Should not be compressed (starts with b'0')
        assert serialized.startswith(b'0')
        
        # Deserialize should return original value
        deserialized = self.report_cache._deserialize(serialized)
        assert deserialized == small_value
    
    async def test_set_and_get(self):
        """Test setting and getting a value from cache."""
        # Mock Redis get to return our serialized value
        serialized = self.report_cache._serialize(TEST_VALUE)
        self.redis_mock.get.return_value = serialized
        
        # Test get with cached value
        result = await self.report_cache.get(TEST_KEY)
        assert result == TEST_VALUE
        self.redis_mock.get.assert_called_once_with(TEST_KEY)
        
        # Test get with no value
        self.redis_mock.get.return_value = None
        result = await self.report_cache.get("nonexistent_key")
        assert result is None
    
    async def test_set_with_ttl_and_tags(self):
        """Test setting a value with TTL and tags."""
        # Mock pipeline
        pipeline_mock = AsyncMock()
        self.redis_mock.pipeline.return_value.__aenter__.return_value = pipeline_mock
        
        # Call set with TTL and tags
        result = await self.report_cache.set(
            TEST_KEY, 
            TEST_VALUE, 
            ttl=TEST_TTL,
            tags=TEST_TAGS
        )
        
        # Should return True on success
        assert result is True
        
        # Should call pipeline with expected commands
        pipeline_mock.set.assert_called_once()
        pipeline_mock.sadd.assert_called()
        pipeline_mock.expire.assert_called()
        pipeline_mock.execute.assert_called_once()
    
    async def test_invalidate_by_tags(self):
        """Test invalidating cache entries by tags."""
        # Mock scan to return test keys
        self.redis_mock.scan.side_effect = [
            (b'0', [b'tax:report:key1', b'tax:report:key2']),
            (b'0', [])  # No more keys
        ]
        
        # Mock delete to return success
        self.redis_mock.delete.return_value = 1
        
        # Invalidate by tags
        count = await self.report_cache.invalidate_by_tags(["tag1", "tag2"])
        
        # Should return count of invalidated keys
        assert count > 0
        
        # Should call scan with the tag pattern
        self.redis_mock.scan.assert_called()
        
        # Should call delete for each key
        self.redis_mock.delete.assert_called()
    
    async def test_clear_all(self):
        """Test clearing all cache entries."""
        # Mock scan to return test keys
        self.redis_mock.scan.side_effect = [
            (b'0', [b'tax:report:key1', b'tax:report:key2']),
            (b'0', []),  # No more report keys
            (b'0', [b'tag:tag1', b'tag:tag2']),
            (b'0', [])   # No more tag keys
        ]
        
        # Mock delete to return success
        self.redis_mock.delete.return_value = 1
        
        # Clear all cache
        result = await self.report_cache.clear_all()
        
        # Should return True on success
        assert result is True
        
        # Should call scan to find all keys
        assert self.redis_mock.scan.call_count >= 2
        
        # Should call delete for keys in batches
        self.redis_mock.delete.assert_called()
    
    async def test_deserialize_invalid_data(self):
        """Test deserialization of invalid data."""
        # Test with None
        assert self.report_cache._deserialize(None) is None
        
        # Test with empty bytes
        assert self.report_cache._deserialize(b'') is None
        
        # Test with invalid compressed data
        assert self.report_cache._deserialize(b'1' + b'invalid') is None
        
        # Test with invalid pickle data
        assert self.report_cache._deserialize(b'0' + b'invalid') is None
    
    async def test_cache_decorator(self):
        """Test the @cached decorator."""
        # Create a test function with the decorator
        @report_cache.cached(ttl=300, key_prefix="test_func")
        async def test_func(arg1, arg2):
            return {"result": f"{arg1}-{arg2}"}
        
        # Mock the cache's get and set methods
        with patch.object(report_cache, 'get', new_callable=AsyncMock) as mock_get, \
             patch.object(report_cache, 'set', new_callable=AsyncMock) as mock_set:
            
            # First call - not in cache
            mock_get.return_value = None
            result = await test_func("value1", "value2")
            
            # Should call the function and cache the result
            assert result == {"result": "value1-value2"}
            mock_get.assert_called_once()
            mock_set.assert_called_once()
            
            # Reset mocks
            mock_get.reset_mock()
            mock_set.reset_mock()
            
            # Second call - return from cache
            mock_get.return_value = {"result": "cached"}
            result = await test_func("value1", "value2")
            
            # Should return from cache without calling set
            assert result == {"result": "cached"}
            mock_get.assert_called_once()
            mock_set.assert_not_called()
    
    async def test_cache_decorator_with_unless(self):
        """Test the @cached decorator with unless condition."""
        # Create a test function with the decorator and unless condition
        @report_cache.cached(
            ttl=300, 
            key_prefix="test_func",
            unless=lambda *args, **kwargs: kwargs.get("skip_cache", False)
        )
        async def test_func(arg1, skip_cache=False):
            return {"result": f"processed-{arg1}"}
        
        # Mock the cache's get and set methods
        with patch.object(report_cache, 'get', new_callable=AsyncMock) as mock_get, \
             patch.object(report_cache, 'set', new_callable=AsyncMock) as mock_set:
            
            # Call with skip_cache=True - should skip cache
            result = await test_func("test", skip_cache=True)
            
            # Should call the function and not use cache
            assert result == {"result": "processed-test"}
            mock_get.assert_not_called()
            mock_set.assert_not_called()
            
            # Call with skip_cache=False - should use cache
            mock_get.return_value = None
            await test_func("test", skip_cache=False)
            
            # Should try to get from cache and then set it
            mock_get.assert_called_once()
            mock_set.assert_called_once()
