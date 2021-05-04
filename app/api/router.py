from fastapi import APIRouter

from app.api.routes import test

api_router = APIRouter()
api_router.include_router(test.router, tags=["test"], prefix="/test")
