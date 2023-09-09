import pytest
from fastapi import FastAPI, Response
from httpx import AsyncClient
from loguru import logger
from starlette.status import HTTP_404_NOT_FOUND

pytestmark = pytest.mark.asyncio


async def test_wrong_path(app: FastAPI):
    async with AsyncClient(base_url="http://testserver", app=app) as client:
        response = await client.get("/wrong_path/")

    assert response.status_code == HTTP_404_NOT_FOUND

    error_data = response.json()
    logger.info(response)
    assert "errors" in error_data