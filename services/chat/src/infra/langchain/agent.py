from typing import List

from langchain.agents import AgentExecutor
from langchain.agents.openai_functions_agent.agent_token_buffer_memory import (
    AgentTokenBufferMemory,
)
from langchain.agents.openai_functions_agent.base import OpenAIFunctionsAgent
from langchain.callbacks.manager import AsyncCallbackManager
from langchain.chat_models import ChatOpenAI
from langchain.prompts import MessagesPlaceholder
from langchain.schema.messages import SystemMessage
from loguru import logger

from src.domain.models import RoomDto
from src.infra.langchain.memory import get_memory
from src.infra.langchain.tools import get_tools


def get_agent_executor(
    room_dto: RoomDto,
    callback_manager: AsyncCallbackManager,
) -> AgentExecutor:
    llm = ChatOpenAI(
        model="gpt-3.5-turbo-16k",
        streaming=True,
        temperature=0,
        callback_manager=callback_manager,
    )

    prompt = OpenAIFunctionsAgent.create_prompt(
        system_message=SystemMessage(content=room_dto.prompt),
        extra_prompt_messages=[MessagesPlaceholder(variable_name="memory")],
    )

    tools = get_tools(room_dto)
    agent = OpenAIFunctionsAgent(llm=llm, tools=tools, prompt=prompt)
    return AgentExecutor(
        agent=agent,
        tools=tools,
        memory=get_memory(room_dto.pk),
        verbose=True,
    )
