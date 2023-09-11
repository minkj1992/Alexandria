from typing import List

import redis.asyncio as redis
from aredis_om.model import NotFoundError
from loguru import logger

from src.app.exceptions import RoomNotFoundException
from src.infra.langchain import vectorstore
from src.infra.langchain.loader import get_docs_from_urls
from src.infra.redis.models import Room


async def create_a_room(title: str, prompt: str) -> str:
    room = await Room(title=title, prompt=prompt).save()
    return room.pk


async def create_a_room_chain(room_pk: str, urls: List[str]):
    docs = await get_docs_from_urls(urls)
    await vectorstore.from_docs(docs, index_name=room_pk)
    return room_pk


async def get_a_room(room_pk: str) -> Room:
    try:
        room = await Room.get(pk=room_pk)
    except NotFoundError:
        raise RoomNotFoundException(room_pk=room_pk)
    except Exception as err:
        logger.exception(err)
        return None
    return room


async def get_a_room_chain(room_pk: str):
    room = await get_a_room(room_pk)
    vectorstore = await redis.get_vectorstore(room_pk)
