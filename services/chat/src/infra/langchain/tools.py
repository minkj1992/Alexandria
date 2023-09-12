from typing import Any, List

from langchain.agents import AgentExecutor, Tool, load_huggingface_tool, load_tools
from langchain.tools import BaseTool
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.vectorstores.base import VectorStore

from src.config import get_settings
from src.domain.models import RoomDto
from src.services.book_service import get_a_book_vector

serper_api_key = get_settings().serper_api_key
search = GoogleSerperAPIWrapper(serper_api_key=serper_api_key)


def get_tools(room_dto: RoomDto):
    return [
        *[
            build_tool(
                name=book.name,
                description=book.description,
                book_pk=book.pk,
            )
            for book in room_dto.books
        ],
        *load_tools(["google-serper"]),
    ]


def build_tool(name: str, description: str, book_pk: str):
    class DynamicTool(BaseTool):
        verbose = True

        def _run(self, query: str) -> str:
            raise NotImplementedError("Does not support sync")

        async def _arun(self, query: str) -> list:
            vectorstore: VectorStore = await get_a_book_vector(book_pk=self.book_pk)
            retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
            docs = retriever.get_relevant_documents(query)
            return [doc.page_content for doc in docs]

    DynamicTool = type(
        "DynamicTool",
        (DynamicTool,),
        {"name": name, "description": description, "book_pk": book_pk},
    )

    return DynamicTool()
