from typing import Any

from fastapi import WebSocketDisconnect
from langchain.callbacks.base import AsyncCallbackHandler
from loguru import logger
from starlette.websockets import WebSocketDisconnect
from websockets import ConnectionClosed

from src.domain.models import ChatResponse


class StreamingLLMCallbackHandler(AsyncCallbackHandler):
    """Callback handler for streaming LLM responses."""

    def __init__(self, websocket):
        self.websocket = websocket

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        resp = ChatResponse(sender="Assistant", message=token, type="stream")
        try:
            await self.websocket.send_json(resp.dict())
        except (WebSocketDisconnect, ConnectionClosed):
            pass
        except Exception as ex:
            await logger.exception(ex)
