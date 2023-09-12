from aredis_om.model import HashModel
from pydantic import UUID4


def get_redis_schema_key(pk: str) -> str:
    return f"schema:{pk}"


class Room(HashModel):
    title: str
    prompt: str


MODELS = (Room,)
