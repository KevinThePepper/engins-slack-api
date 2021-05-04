import pydantic
import validators

from pydantic import validator
from typing import Optional

from app.models.schemas.common import Model


def url_validator(url: str) -> str:
    if not validators.url(url):
        raise ValueError("Must be url: %s" % url)
    return url


class BaseSlackResponse(Model):
    ok: bool


class SlackError(BaseSlackResponse):
    ok: bool = False
    error: str


class BotIcons(Model):
    image_36: str
    image_48: str
    image_72: str

    @validator("image_36", "image_48", "image_72", pre=True)
    def validate_image_url(cls, v):
        return url_validator(url=v)


class Bot(Model):
    id: str
    deleted: bool
    name: str
    updated: int
    app_id: str
    user_id: str
    icons: Optional[BotIcons]


class BotsInfo(BaseSlackResponse):
    bot: Optional[Bot]


class AuthTest(BaseSlackResponse):
    url: str
    team: str
    user: str
    team_id: str
    user_id: str
    bot_id: Optional[str]
    is_enterprise_install: Optional[bool]

    @validator("url", pre=True)
    def url_validate(cls, v):
        return url_validator(url=v)
