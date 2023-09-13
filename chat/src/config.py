import os
from functools import lru_cache

from pydantic import BaseSettings as S

_PHASE = os.getenv("PHASE").lower()


class BaseSettings(S):
    openai_api_key: str
    redis_host: str = "redis-stack"
    redis_port: int = 6379
    base_url: str
    serper_api_key: str

    @property
    def redis_url(self) -> str:
        return f"redis://@{self.redis_host}:{self.redis_port}/0"


class ProdSettings(BaseSettings):
    class Config:
        env_file = ".env"


class TestSettings(BaseSettings):
    class Config:
        env_file = ".env.test"


@lru_cache()
def get_settings() -> BaseSettings:
    if _PHASE == "test":
        return TestSettings()
    return ProdSettings()
