import pytest
from aredis_om.model.model import NotFoundError
from fastapi import FastAPI

from src.infra.redis.models import Book

pytestmark = pytest.mark.asyncio


async def test_create_and_delete_a_book():
    expect = Book(name="Test Book", description="Test desc")
    await expect.save()

    actual = await Book.get(expect.pk)
    assert actual == expect

    await Book.delete(expect.pk)
    with pytest.raises(NotFoundError):
        await Book.get(expect.pk)
