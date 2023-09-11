from functools import lru_cache

from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    redis_host: str = 'redis-stack'
    redis_port: int = 6379

    model_config = SettingsConfigDict(env_file=".env")

    @property
    def redis_url(self) -> str:
        return f'redis://@{self.redis_host}:{self.redis_port}/0'


@lru_cache()
def get_settings() -> Settings:
    return Settings()

