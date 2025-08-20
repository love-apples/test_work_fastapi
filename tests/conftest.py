import os
import sys
import uuid
import pytest

from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager

ROOT = os.path.dirname(os.path.abspath(__file__ + "/.."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import app.app as app_module  # noqa


def _short_test_db_name(base: str) -> str:
    
    suffix = "_t_" + uuid.uuid4().hex[:6]
    max_len = 63
    trimmed_base = base[: max_len - len(suffix)]
    
    return trimmed_base + suffix


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client():
    app_module.cnf.mongo.NAME = _short_test_db_name(app_module.cnf.mongo.NAME)

    async with LifespanManager(app_module.app):
        transport = ASGITransport(app=app_module.app)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac

        motor_client = app_module.app.state.mongo_client
        await motor_client.drop_database(app_module.cnf.mongo.NAME)
