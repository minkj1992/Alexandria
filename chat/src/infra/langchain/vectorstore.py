from typing import Iterable, List, Optional

import redis.asyncio as redis
from fastapi.concurrency import run_in_threadpool
from langchain.docstore.document import Document
from langchain.vectorstores.base import VectorStore
from langchain.vectorstores.redis import Redis as LangchainRedis
from loguru import logger

from src.config import get_settings
from src.infra.langchain.embeddings import get_embeddings

redis_url = get_settings().redis_url


async def from_docs(docs: List[Document], index_name: str) -> LangchainRedis:
    embedding = get_embeddings()
    return await run_in_threadpool(
        func=LangchainRedis.from_documents,
        documents=docs,
        embedding=embedding,
        index_name=index_name,
        redis_url=redis_url,
    )


# connection_pool
async def drop_vectorstore(index_name: str):
    return await run_in_threadpool(
        func=LangchainRedis.drop_index,
        index_name=index_name,
        delete_documents=True,
        redis_url=redis_url,
    )


async def get_or_create_session_vectorstore(session_id: str) -> VectorStore:
    try:
        return await get_vectorstore(session_id)
    except TypeError as e:
        pass
    except Exception as e:
        logger.error(e)
    return await from_docs([Document(page_content="")], session_id)


async def get_vectorstore(index_name: str, schema: dict = {}) -> VectorStore:
    embedding = get_embeddings()
    return await run_in_threadpool(
        func=LangchainRedis.from_existing_index,
        embedding=embedding,
        index_name=index_name,
        redis_url=redis_url,
        schema=schema,
    )


# or use retriever adocument
async def update_vectorstore(
    index_name: str, texts: Iterable[str], metadatas: Optional[List[dict]] = None
):
    vectorstore = await get_vectorstore(index_name)
    await run_in_threadpool(
        func=vectorstore.add_texts,
        texts=texts,
        metadatas=metadatas,
    )
