from typing import List

from aredis_om.model import HashModel, JsonModel


def get_redis_schema_key(pk: str) -> str:
    return f"schema:{pk}"


class Book(HashModel):
    name: str
    description: str


# 1:n = Room : Book
class Room(JsonModel):
    name: str
    prompt: str
    books: List[str]


MODELS = (
    Room,
    Book,
)
