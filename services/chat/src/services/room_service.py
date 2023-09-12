import json
from typing import List, Optional

import redis.asyncio as redis
from aredis_om.model import NotFoundError
from langchain.vectorstores.base import VectorStore
from loguru import logger

from src.app.exceptions import RoomNotFoundException
from src.config import get_settings
from src.infra.langchain import vectorstore
from src.infra.langchain.loader import get_docs_from_urls
from src.infra.redis.connection import get_redis_connection_from_url
from src.infra.redis.models import Room, get_redis_schema_key


async def create_a_room(title: str, prompt: str) -> str:
    room = await Room(title=title, prompt=prompt).save()
    return room.pk


async def create_a_room_chain(room_pk: str, urls: List[str]):
    docs = await get_docs_from_urls(urls)
    return await vectorstore.from_docs(docs, index_name=room_pk)


async def get_a_room_chain_schema(
    room_pk: str, redis_conn: Optional[redis.Redis] = None
) -> dict:
    if not redis_conn:
        redis_conn = get_redis_connection_from_url()

    schema_key = get_redis_schema_key(room_pk)
    schema = await redis_conn.get(schema_key)
    return json.loads(schema)


async def create_a_room_chain_schema(
    redis_conn: redis.Redis, room_pk: str, schema: dict
):
    schema_key = get_redis_schema_key(room_pk)
    schema = json.dumps(schema)
    logger.info(schema)
    await redis_conn.set(schema_key, schema)


async def get_a_room(room_pk: str) -> Room:
    try:
        room = await Room.get(pk=room_pk)
    except NotFoundError:
        raise RoomNotFoundException(room_pk=room_pk)
    except Exception as err:
        logger.exception(err)
        return None
    return room


async def get_a_room_vector(room_pk: str) -> VectorStore:
    schema = await get_a_room_chain_schema(room_pk)
    try:
        vs = await vectorstore.get_vectorstore(room_pk, schema)

    except Exception as err:
        logger.exception(err)
        return None
    return vs
