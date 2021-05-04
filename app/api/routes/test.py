import logging

from fastapi import APIRouter
from starlette.status import HTTP_200_OK

from app.core.config import SLACK_TAG
from app.models.schemas.common import BaseResponse
from app.slack.client import SlackClient

router = APIRouter()
logger = logging.getLogger(SLACK_TAG)


@router.post(
    "",
    name="test:test",
    status_code=HTTP_200_OK,
    response_model=BaseResponse,
    response_description="Test successful",
    responses={200: {"description": "Test successful"}}
)
def test(payload) -> BaseResponse:
    client = SlackClient.get_instance()
    client.post_message("Test", "general")
    return BaseResponse(ok=True, message="test")
