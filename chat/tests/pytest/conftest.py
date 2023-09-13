
import random

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI
from httpx import AsyncClient

from src.config import get_settings
from src.infra.redis.connection import connect_to_redis
from src.infra.redis.models import MODELS


@pytest.fixture(scope='session')
def app() -> FastAPI:
    from src.main import get_application
    return get_application('ChatTestServer')


@pytest.fixture(scope='session')
async def initialized_app(app: FastAPI) -> FastAPI:
    async with LifespanManager(app):
        settings = get_settings()
        await connect_to_redis(app, settings)
        for m in MODELS:
            m.Meta.database = app.state.redis
        yield app


@pytest.fixture
async def client(initialized_app: FastAPI) -> AsyncClient:
    async with AsyncClient(
        app=initialized_app,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client

