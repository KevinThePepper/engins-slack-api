import logging

from logging.config import dictConfig
from typing import Callable

from fastapi import FastAPI

from app.core.config import LOGGING

logger = logging.getLogger("uvicorn")


def create_start_app_handler(app: FastAPI) -> Callable:  # type: ignore
    async def start_app() -> None:
        dictConfig(LOGGING)
        logger.info("Set up logging dict config")

    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:  # type: ignore
    async def stop_app() -> None:
        logger.info("Closing app...")

    return stop_app
