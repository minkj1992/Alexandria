from aredis_om.model import Field, HashModel
from pydantic import UUID4


class Room(HashModel):
    title: str
    prompt: str


MODELS = (
    Room,
)