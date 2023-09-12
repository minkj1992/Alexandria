from typing import List, Union

import redis.asyncio as redis
from fastapi import APIRouter, Depends, Response, status
from loguru import logger
from pydantic import BaseModel, Field

from src.infra.redis.connection import get_redis_connection
from src.services import room_service

router = APIRouter(prefix="/rooms", tags=["rooms"])


class CreateRoomUrlRequest(BaseModel):
    title: str = Field(title="챗봇명")

    urls: List[str] = Field(
        title="챗봇이 학습할 사이트들", description="POST /pages에서 url들을 추출하여 전달하면 된다."
    )

    prompt: Union[str, None] = Field(
        title="챗봇이 QA할 prompt",
    )


class RoomResponse(BaseModel):
    room_ulid: str


@router.get("/{pk}", status_code=200)
async def get_a_room(pk: str, response: Response):
    return await room_service.get_a_room(pk)


@router.post(
    "/urls",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=RoomResponse,
)
async def create_a_room_with_urls(
    room_in: CreateRoomUrlRequest, redis_conn=Depends(get_redis_connection)
):
    room_pk = await room_service.create_a_room(
        room_in.title,
        room_in.prompt,
    )

    vs = await room_service.create_a_room_chain(room_pk, room_in.urls)
    await room_service.create_a_room_chain_schema(redis_conn, room_pk, vs.schema)

    room_schema = await room_service.get_a_room_chain_schema(
        room_pk,
        redis_conn,
    )
    return RoomResponse(room_ulid=room_pk)
