
from typing import Iterable, List, Optional

import redis.asyncio as redis
from fastapi.concurrency import run_in_threadpool
from langchain.docstore.document import Document
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores.redis import Redis as LangchainRedis

from src.config import get_settings

redis_url = get_settings().redis_url

async def from_docs(docs: List[Document], index_name:str) -> LangchainRedis:
    embedding = OpenAIEmbeddings(chunk_size=500)
    return await run_in_threadpool(
        func=LangchainRedis.from_documents,
        documents = docs,
        embedding = embedding,
        index_name = index_name,
        redis_url = redis_url
    )


async def drop_vectorstore(index_name:str):
    return await run_in_threadpool(
        func=LangchainRedis.drop_index,
        index_name=index_name,
        delete_documents=True,
        redis_url=redis_url
    )


async def get_vectorstore(index_name:str):
    embedding = OpenAIEmbeddings(chunk_size=500)
    return await run_in_threadpool(
        func=LangchainRedis.from_existing_index,
        embedding=embedding,
        index_name=index_name,
        redis_url=redis_url
    )


# or use retriever adocument
async def update_vectorstore(index_name:str, texts: Iterable[str], metadatas: Optional[List[dict]] = None):
    vectorstore = await get_vectorstore(index_name)
    await run_in_threadpool(
        func=vectorstore.add_texts,
        texts=texts,
        metadatas=metadatas,
    )
