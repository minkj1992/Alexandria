from typing import List, Union

import redis.asyncio as redis
from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field

from src.infra.redis.connection import get_redis_connection
from src.services import book_service

router = APIRouter(prefix="/books", tags=["books"])


class CreateBookUrlRequest(BaseModel):
    name: str = Field(title="Book name")

    urls: List[str] = Field(title="학습할 사이트 urls")

    description: Union[str, None] = Field(
        title="Book description",
    )


class BookResponse(BaseModel):
    book_ulid: str


@router.get("/{pk}", status_code=200)
async def get_a_book(pk: str, response: Response):
    return await book_service.get_a_book(pk)


@router.post(
    "/urls",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=BookResponse,
)
async def create_a_book_with_urls(
    book_in: CreateBookUrlRequest, redis_conn=Depends(get_redis_connection)
):
    book_pk = await book_service.create_a_book(
        book_in.name,
        book_in.description,
    )

    vs = await book_service.create_a_book_chain(book_pk, book_in.urls)
    await book_service.create_a_book_chain_schema(redis_conn, book_pk, vs.schema)
    return BookResponse(book_ulid=book_pk)
