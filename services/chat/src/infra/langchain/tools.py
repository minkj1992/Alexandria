from typing import Any

from langchain.agents import AgentExecutor, Tool, load_tools
from langchain.tools import BaseTool
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.vectorstores.base import VectorStore

from src.config import get_settings
from src.services.room_service import get_a_room_vector

# langchain_index = "01HA0VEYFHG80TAFR2RY9G87EN"
langchain_index = "01HA3QTXMC00TS02WAVS7BV4J0"
serper_api_key = get_settings().serper_api_key
search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)


def get_tools():
    return [
        LangchainTool(),
        *load_tools(["google-serper"]),
    ]


class LangchainTool(BaseTool):
    name = "Langchain"
    description = (
        "Useful for when you need to refer to LangChain's documentations about query"
    )
    verbose = True

    def _run(
        self,
        query: str,
    ) -> str:
        raise NotImplementedError("Calculator does not support async")

    async def _arun(
        self,
        query: str,
    ) -> list:
        langchain_vs: VectorStore = await get_a_room_vector(room_pk=langchain_index)
        retriever = langchain_vs.as_retriever(search_kwargs={"k": 3})
        docs = retriever.get_relevant_documents(query)
        return [doc.page_content for doc in docs]
