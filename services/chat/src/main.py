import os

import uvicorn
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException

from src.app.handlers import http422_error_handler, http_error_handler
from src.app.http import greet
from src.app.wss.chat import chat_server
from src.config import get_settings


def get_application() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title='ChatServer')

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/chat", chat_server)

    routers = [
        greet.router,
    ]
    for router in routers:
        app.include_router(router)

    app.add_exception_handler(HTTPException, http_error_handler)
    app.add_exception_handler(RequestValidationError, http422_error_handler)
    return app

app = get_application()


