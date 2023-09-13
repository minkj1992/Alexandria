from typing import List, Union

import redis.asyncio as redis
from fastapi import APIRouter, Depends, Response, status
from pydantic import BaseModel, Field
from src.domain.consts import MAX_CRAWL_DEPTH
from src.infra.redis.connection import get_redis_connection
from src.services import book_service

router = APIRouter(prefix="/books", tags=["books"])


@router.get("/{pk}", status_code=200, description="Book을 반환합니다.")
async def get_a_book(pk: str, response: Response):
    return await book_service.get_a_book(pk)


class CreateBookUrlRequest(BaseModel):
    name: str = Field(title="Book name")

    urls: List[str] = Field(title="학습할 사이트 urls")

    description: Union[str, None] = Field(
        title="Book description",
        description="채팅방에서 OpenaiAgent가 사용자의 발화에 따라 어떤 Book을 사용할지 참고하는 메타데이터."
    )

    max_depth: int = Field(title="max crawl depth", default=MAX_CRAWL_DEPTH)


class BookResponse(BaseModel):
    book_ulid: str


@router.post(
    "/urls",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=BookResponse,
    description="Book을 생성합니다, 이떄 주어진 url들을 크롤링 하여 vectorstore를 생성하며, book과 index_schema를 생성합니다."
)
async def create_a_book_with_urls(
    book_in: CreateBookUrlRequest, redis_conn=Depends(get_redis_connection)
):
    book_pk = await book_service.create_a_book(
        book_in.name,
        book_in.description,
    )

    vs = await book_service.create_a_book_chain(
        book_pk, book_in.urls, book_in.max_depth
    )
    await book_service.create_a_book_chain_schema(redis_conn, book_pk, vs.schema)
    return BookResponse(book_ulid=book_pk)
