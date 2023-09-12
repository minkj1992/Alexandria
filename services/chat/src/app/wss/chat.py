import asyncio
from typing import Annotated

import openai
from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from langchain.callbacks.manager import AsyncCallbackManager
from loguru import logger
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect, WebSocketState
from websockets import ConnectionClosed

from src.config import get_settings
from src.domain.models import ChatResponse, RoomDto
from src.infra.langchain.agent import get_agent_executor
from src.infra.langchain.callbacks import StreamingLLMCallbackHandler
from src.services import book_service, room_service

chat_server = FastAPI()
chat_server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="/src/templates")


@chat_server.get("/{room_pk}")
async def get(
    request: Request, room_pk: str, settings: Annotated[dict, Depends(get_settings)]
):
    room = await room_service.get_a_room(room_pk)
    return templates.TemplateResponse(
        "chat.html",
        {
            "request": request,
            "room_name": room.name,
            "base_url": settings.base_url,
            "room_pk": room_pk,
        },
    )


class ChatRequest(BaseModel):
    message: str


@chat_server.websocket("/{room_pk}")
async def chat(websocket: WebSocket, room_pk: str):
    room_dto: RoomDto = await room_service.get_a_room_dto(room_pk)

    callback_manager = AsyncCallbackManager([StreamingLLMCallbackHandler(websocket)])
    agent = get_agent_executor(room_dto, callback_manager)

    await websocket.accept()
    try:
        while websocket.client_state == WebSocketState.CONNECTED:
            # Receive and send back the client message
            client_msg = await websocket.receive_text()

            resp = ChatResponse(sender="Human", message=client_msg, type="stream")
            await websocket.send_json(resp.dict())

            # 1. Send Chat start message
            start_resp = ChatResponse(sender="Assistant", message="", type="start")
            await websocket.send_json(start_resp.dict())
            # 2. Generate Chat Response
            await agent.arun(client_msg)

            # 3. Send Chat start message
            end_resp = ChatResponse(sender="Assistant", message="", type="end")
            await websocket.send_json(end_resp.dict())
    except (WebSocketDisconnect, ConnectionClosed):
        logger.info("websocket disconnect")
