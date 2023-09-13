import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY

pytestmark = pytest.mark.asyncio


async def test_wrong_path_error(app: FastAPI):
    async with AsyncClient(base_url="http://testserver", app=app) as client:
        response = await client.get("/wrong_path/")

    assert response.status_code == HTTP_404_NOT_FOUND

    error_data = response.json()
    assert "errors" in error_data


async def test_validation_error(app: FastAPI):
    @app.get("/wrong_path/{param}")
    def _(param: int) -> None:  # pragma: no cover
        pass

    async with AsyncClient(base_url="http://testserver", app=app) as client:
        response = await client.get("/wrong_path/asd")

    assert response.status_code == HTTP_422_UNPROCESSABLE_ENTITY

    error_data = response.json()
    assert "errors" in error_data
