
import pytest
from aredis_om.model.model import NotFoundError
from fastapi import FastAPI

from src.infra.redis.models import Room

pytestmark = pytest.mark.asyncio


async def test_create_and_delete_a_room():
    expect = Room(
        title = "Test Room",
        prompt = "Test Prompt"
    )
    await expect.save()

    actual = await Room.get(expect.pk)
    assert actual == expect
    
    await Room.delete(expect.pk)
    with pytest.raises(NotFoundError):
        await Room.get(expect.pk)
