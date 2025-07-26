import pytest
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestPerformance:
    """Performance tests for API endpoints"""
    
    def test_api_response_times(self):
        """Test API response times are under 200ms"""
        endpoints = [
            "/api/integration/financial-summary/1",
            "/api/accounts-payable/vendors",
            "/api/accounts-receivable/customers",
            "/api/cash-management/cash-position",
            "/api/budget/budgets"
        ]
        
        for endpoint in endpoints:
            start_time = time.time()
            response = client.get(endpoint)
            end_time = time.time()
            
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            assert response.status_code == 200
            assert response_time < 200, f"Endpoint {endpoint} took {response_time}ms (>200ms)"
    
    def test_concurrent_requests(self):
        """Test system handles concurrent requests"""
        def make_request():
            response = client.get("/api/integration/financial-summary/1")
            return response.status_code == 200
        
        # Test 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(results), "Some concurrent requests failed"
    
    def test_large_dataset_performance(self):
        """Test performance with large datasets"""
        # Test pagination performance
        response = client.get("/api/accounts-receivable/customers?limit=1000")
        
        start_time = time.time()
        data = response.json()
        end_time = time.time()
        
        processing_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert processing_time < 500, f"Large dataset processing took {processing_time}ms (>500ms)"
    
    def test_database_query_performance(self):
        """Test database query performance"""
        # Test complex reporting query
        start_time = time.time()
        response = client.get(
            "/api/integration/reports/executive-dashboard/1",
            params={
                "period_start": "2024-01-01",
                "period_end": "2024-12-31"
            }
        )
        end_time = time.time()
        
        query_time = (end_time - start_time) * 1000
        
        assert response.status_code == 200
        assert query_time < 1000, f"Complex query took {query_time}ms (>1000ms)"

class TestLoadTesting:
    """Load testing for system capacity"""
    
    def test_sustained_load(self):
        """Test system under sustained load"""
        def sustained_requests():
            success_count = 0
            for _ in range(50):  # 50 requests per thread
                try:
                    response = client.get("/api/integration/financial-summary/1")
                    if response.status_code == 200:
                        success_count += 1
                    time.sleep(0.1)  # 100ms between requests
                except Exception:
                    pass
            return success_count
        
        # Run 5 threads for sustained load
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(sustained_requests) for _ in range(5)]
            results = [future.result() for future in futures]
        
        total_requests = sum(results)
        success_rate = total_requests / 250  # 5 threads * 50 requests
        
        assert success_rate > 0.95, f"Success rate {success_rate} is below 95%"
    
    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Make 100 requests
        for _ in range(100):
            client.get("/api/integration/financial-summary/1")
        
        final_memory = process.memory_info().rss
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be less than 50MB
        assert memory_growth < 50 * 1024 * 1024, f"Memory grew by {memory_growth / 1024 / 1024}MB"

class TestSecurityPerformance:
    """Security-related performance tests"""
    
    def test_authentication_performance(self):
        """Test authentication doesn't significantly impact performance"""
        # Test without auth (should fail but quickly)
        start_time = time.time()
        response = client.get("/api/integration/financial-summary/1")
        end_time = time.time()
        
        auth_check_time = (end_time - start_time) * 1000
        
        # Authentication check should be fast even when failing
        assert auth_check_time < 50, f"Auth check took {auth_check_time}ms (>50ms)"
    
    def test_rate_limiting_performance(self):
        """Test rate limiting doesn't degrade performance"""
        # Make requests up to rate limit
        response_times = []
        
        for _ in range(10):
            start_time = time.time()
            client.get("/api/integration/financial-summary/1")
            end_time = time.time()
            
            response_times.append((end_time - start_time) * 1000)
        
        # Response times should remain consistent
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 200, f"Average response time {avg_response_time}ms under rate limiting"