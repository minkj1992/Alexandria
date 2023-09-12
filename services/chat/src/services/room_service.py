import asyncio
from typing import List

import redis.asyncio as redis
from aredis_om.model import NotFoundError
from loguru import logger

from src.app.exceptions import BookNotFoundException, RoomNotFoundException
from src.domain.models import RoomDto
from src.infra.redis.models import Book, Room
from src.services import book_service


async def create_a_room(name: str, books: List[str], prompt: str) -> str:
    room = await Room(name=name, books=books, prompt=prompt).save()
    return room.pk


async def get_a_room(
    room_pk: str,
) -> Room:
    try:
        return await Room.get(pk=room_pk)
    except NotFoundError:
        raise RoomNotFoundException(room_pk=room_pk)


async def get_a_room_dto(
    room_pk: str,
) -> RoomDto:
    try:
        room = await Room.get(pk=room_pk)
    except NotFoundError:
        raise RoomNotFoundException(room_pk=room_pk)

    try:
        books = await asyncio.gather(
            *[book_service.get_a_book(pk) for pk in room.books]
        )

    except NotFoundError:
        raise BookNotFoundException(" ".join(room.books))

    return RoomDto(
        pk=room.pk,
        name=room.name,
        prompt=room.prompt,
        books=books,
    )
