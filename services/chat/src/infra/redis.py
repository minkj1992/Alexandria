import redis.asyncio as redis
from fastapi import FastAPI
from loguru import logger

from src.config import Settings


async def connect_to_redis(app: FastAPI, settings: Settings) -> None:
    logger.info(f"Connecting to Redis-stack")
    pool = redis.ConnectionPool(
        host=settings.redis_host, 
        port=settings.redis_port, 
        protocol=3,
    )
    app.state.redis = redis.Redis(connection_pool=pool, auto_close_connection_pool=False)
    logger.info("Connection established")


async def close_redis_connection(app: FastAPI) -> None:
    logger.info("Closing connection to database")

    await app.state.redis.close()
    await app.state.redis.connection_pool.disconnect()
    logger.info("Connection closed") 