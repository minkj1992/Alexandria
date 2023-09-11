import redis.asyncio as redis
from fastapi import FastAPI, Request
from loguru import logger

from src.config import Settings
from src.infra.redis.models import MODELS


async def connect_to_redis(app: FastAPI, settings: Settings) -> None:
    logger.info(f"Connecting to Redis-stack")
    pool = redis.ConnectionPool(
        host=settings.redis_host, 
        port=settings.redis_port,
    )
    redis_impl = redis.Redis(connection_pool=pool, decode_responses = True, auto_close_connection_pool=False)
    app.state.redis = redis_impl
    logger.info("Connection established")


def set_conn_to_models(conn: redis.Redis):
    for m in MODELS:
        m.Meta.database = conn


async def close_redis_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")
    await app.state.redis.close()
    await app.state.redis.connection_pool.disconnect()
    logger.info("Connection closed")


def get_redis_connection(request: Request) -> redis.Redis:
    return request.app.state.redis