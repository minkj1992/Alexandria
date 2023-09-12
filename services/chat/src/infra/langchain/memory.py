from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import RedisChatMessageHistory

from config import get_settings

redis_url = get_settings().redis_url


def get_memory(session_id: str):
    chat_history_memory = RedisChatMessageHistory(
        url=redis_url,
        ttl=600,
        session_id=session_id,
    )
    return ConversationBufferMemory(
        memory_key="memory", chat_memory=chat_history_memory, return_messages=True
    )
