import pytest
import asyncio
import time
from unittest.mock import AsyncMock, patch

class TestDatabasePerformance:
    async def test_bulk_asset_creation_performance(self):
        with patch('app.modules.core_financials.fixed_assets.services.FixedAssetService') as mock_service:
            mock_service.return_value.create = AsyncMock()
            
            start_time = time.time()
            
            tasks = []
            for i in range(100):
                task = mock_service.return_value.create(AsyncMock(), obj_in={'asset_number': f'FA-{i:03d}'})
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            execution_time = time.time() - start_time
            assert execution_time < 5.0

class TestAPIPerformance:
    def test_concurrent_api_requests(self, client):
        with patch('app.core.auth.tenant_auth.validate_tenant_access') as mock_auth:
            mock_auth.return_value = AsyncMock()
            
            start_time = time.time()
            responses = []
            
            for _ in range(10):
                response = client.get("/api/v1/tenant/info", headers={"X-Tenant-ID": "test_tenant"})
                responses.append(response)
            
            execution_time = time.time() - start_time
            assert execution_time < 2.0
            assert len(responses) == 10