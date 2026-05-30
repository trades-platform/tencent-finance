import pytest
import pytest_asyncio
from tencent_finance import Client, AsyncClient


@pytest.fixture
def client():
    return Client()


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient() as c:
        yield c
