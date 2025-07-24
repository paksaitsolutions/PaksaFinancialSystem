import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from app.main import app
from app.core.db.tenant_middleware import set_tenant_context

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    engine = create_async_engine(TEST_DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession)
    async with async_session() as session:
        yield session

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def test_tenant():
    tenant_id = "test_tenant_123"
    set_tenant_context(tenant_id)
    return tenant_id