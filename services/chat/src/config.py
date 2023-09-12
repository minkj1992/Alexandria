from functools import lru_cache

from pydantic import BaseSettings


class Settings(BaseSettings):
    openai_api_key: str
    redis_host: str = "redis-stack"
    redis_port: int = 6379
    base_url: str
    serper_api_key: str

    class Config:
        env_file = ".env"

    @property
    def redis_url(self) -> str:
        return f"redis://@{self.redis_host}:{self.redis_port}/0"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
