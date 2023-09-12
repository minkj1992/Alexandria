import asyncio
from typing import Any, List

from langchain.agents import AgentExecutor, Tool, load_huggingface_tool, load_tools
from langchain.tools import BaseTool
from langchain.utilities import GoogleSerperAPIWrapper
from langchain.vectorstores.base import VectorStore
from loguru import logger

from infra.huggingface.loader import load_bart_pipe, load_t5_small_pipe
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
        TranslationTool(),
        SummarizationTool(),
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


# t5-small: useful for translations involving English, French, Romanian, and German.
class TranslationTool(BaseTool):
    name = "translate_en_to_fr"
    description = "useful for changing English sentences into French."
    verbose = True

    pipe = load_t5_small_pipe()
    fallback_msg = "rien n'a été renvoyé"

    def _run(self, en_text: str) -> str:
        # i.g. [{'translation_text': 'traduire cette déclaration'}]
        result = self.pipe(en_text)
        try:
            translation_text = result[0].get("translation_text", self.fallback_msg)
        except IndexError:
            return self.fallback_msg
        return translation_text

    async def _arun(self, en_text: str) -> list:
        loop = asyncio.get_event_loop()
        translation = await loop.run_in_executor(None, self._run, en_text)
        return translation


class SummarizationTool(BaseTool):
    name = "summarization"
    description = "useful for tasks requiring summarization."
    verbose = True

    fallback_msg = "Cannot summarize."
    pipe = load_bart_pipe()

    def _run(self, text: str) -> str:
        result = self.pipe(text)
        try:
            summarized_text = result[0].get("summary_text", self.fallback_msg)
            return summarized_text
        except IndexError:
            return self.fallback_msg

    async def _arun(self, text: str) -> list:
        loop = asyncio.get_event_loop()
        summarized = await loop.run_in_executor(None, self._run, text)
        return summarized
