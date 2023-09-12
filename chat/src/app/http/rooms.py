from typing import List

from fastapi import APIRouter, Response, status
from pydantic import BaseModel, Field

from src.domain.prompts import BASE_SYS_PROMPT
from src.services import room_service

router = APIRouter(prefix="/rooms", tags=["rooms"])


class CreateRoomRequest(BaseModel):
    name: str = Field(title="Room name")

    books: List[str] = Field(title="Room에 포함시킬 book pk 리스트")

    prompt: str = Field(
        default=BASE_SYS_PROMPT,
        title="Room Prompt",
    )


class RoomResponse(BaseModel):
    room_pk: str


@router.get("/{pk}", status_code=200)
async def get_a_room(pk: str, response: Response):
    return await room_service.get_a_room(pk)


@router.post(
    "/",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=RoomResponse,
)
async def create_a_room(room_in: CreateRoomRequest):
    room_pk = await room_service.create_a_room(
        room_in.name,
        room_in.books,
        room_in.prompt,
    )
    return RoomResponse(room_pk=room_pk)
