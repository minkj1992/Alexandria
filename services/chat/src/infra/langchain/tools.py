from typing import Any

from langchain.agents import AgentExecutor, Tool, load_huggingface_tool, load_tools
from langchain.tools import BaseTool
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.vectorstores.base import VectorStore
from loguru import logger

from src.config import get_settings
from src.services.room_service import get_a_room_vector

serper_api_key = get_settings().serper_api_key
search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)


def get_tools(room_pk: str):
    return [
        build_tool(
            name="Minwook",
            description="useful for when you need to refer who is minwook je",
            room_pk=room_pk,
        ),
        *load_tools(["google-serper"]),
    ]


def build_tool(name: str, description: str, room_pk: str):
    class DynamicTool(BaseTool):
        verbose = True

        def _run(self, query: str) -> str:
            raise NotImplementedError("Does not support sync")

        async def _arun(self, query: str) -> list:
            vectorstore: VectorStore = await get_a_room_vector(room_pk=self.room_pk)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            docs = retriever.get_relevant_documents(query)
            return [doc.page_content for doc in docs]

    DynamicTool = type(
        "DynamicTool",
        (DynamicTool,),
        {"name": name, "description": description, "room_pk": room_pk},
    )

    return DynamicTool()


# class LangchainTool(BaseTool):
#     name = "Langchain"
#     description = (
#         "Useful for when you need to refer to LangChain's documentations about query"
#     )
#     verbose = True

#     def _run(
#         self,
#         query: str,
#     ) -> str:
#         raise NotImplementedError("Calculator does not support async")

#     async def _arun(
#         self,
#         query: str,
#     ) -> list:
#         langchain_vs: VectorStore = await get_a_room_vector(room_pk=langchain_index)
#         retriever = langchain_vs.as_retriever(search_kwargs={"k": 3})
#         docs = retriever.get_relevant_documents(query)
#         return [doc.page_content for doc in docs]
