from collections.abc import AsyncIterator

import pytest
from dependency_injector import providers
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncEngine

from ups_kulka.container import Container
from ups_kulka.main import create_app

pytestmark = pytest.mark.integration


@pytest.fixture
def container(engine: AsyncEngine, clean_db: None) -> Container:
    container = Container()
    container.engine.override(providers.Object(engine))
    return container


@pytest.fixture
async def client(container: Container) -> AsyncIterator[AsyncClient]:
    app = create_app(container)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as http:
        yield http
