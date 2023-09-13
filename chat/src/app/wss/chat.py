from asyncio import Semaphore
from typing import Annotated

from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from langchain.callbacks.manager import AsyncCallbackManager
from loguru import logger
from pydantic import BaseModel
from src.app.utils import wss_close_ignore_exception
from src.config import get_settings
from src.domain.models import ChatResponse, RoomDto
from src.infra.langchain.agent import get_agent_executor
from src.infra.langchain.callbacks import StreamingLLMCallbackHandler
from src.services import room_service
from starlette.websockets import WebSocketDisconnect, WebSocketState
from ulid import ULID
from websockets import ConnectionClosed

chat_server = FastAPI()
chat_server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
templates = Jinja2Templates(directory="/src/templates")


@chat_server.get("/{room_pk}", description="Room의 데이터를 기반으로 랜더링될 채팅방 UI를 반환합니다.")
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


semaphore = Semaphore(10)


@chat_server.websocket("/{room_pk}")
async def chat(websocket: WebSocket, room_pk: str):
    async with semaphore:  # 동시 접속 제한
        room_dto: RoomDto = await room_service.get_a_room_dto(room_pk)
        session_id = str(ULID())

        callback_manager = AsyncCallbackManager(
            [StreamingLLMCallbackHandler(websocket)]
        )
        agent = get_agent_executor(session_id, room_dto, callback_manager)

        await websocket.accept()
        try:
            while websocket.client_state == WebSocketState.CONNECTED:
                # Receive and send back the client message
                client_msg = await websocket.receive_text()
                resp = ChatResponse(sender="Human", message=client_msg, type="stream")
                await websocket.send_json(resp.dict())

                await agent.arun(client_msg)

        except (WebSocketDisconnect, ConnectionClosed):
            logger.info("websocket disconnect")
        except Exception as e:
            logger.error(e)
            await wss_close_ignore_exception(websocket)
