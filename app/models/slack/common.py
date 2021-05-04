import validators

from pydantic import validator
from typing import List, Optional

from app.models.schemas.common import Model


class Profile(Model):
    avatar_hash: str
    status_text: str
    status_expiration: int
    real_name: str
    display_name: str
    real_name_normalized: str
    display_name_normalized: str
    email: str
    image: Optional[str]
    image_24: Optional[str]
    image_32: Optional[str]
    image_48: Optional[str]
    image_72: Optional[str]
    image_192: Optional[str]
    image_512: Optional[str]
    team: str

    @validator("image", pre=True)
    def split_str(cls, v):
        return cls.image_192

    @validator("email")
    def validate_email(cls, v):
        if validators.email(v) is not True:
            raise ValueError("email must be an Email address")
        return v

    @validator("image_24", "image_32", "image_48", "image_72", "image_192", "image_512")
    def validate_image_url(cls, v):
        if validators.url(v) is not True:
            raise ValueError("image must be a URL")
        return v


class User(Model):
    id: str
    email: Optional[str]
    is_admin: bool
    is_owner: bool
    is_primary_owner: bool
    is_restricted: bool
    is_ultra_restricted: bool
    is_bot: bool
    profile: Optional[Profile]


class SlackBase(Model):
    token: str


class SlackChallenge(SlackBase):
    challenge: str
    type: str


class SlackEnvelope(SlackBase):
    team_id: str
    api_app_id: str
    event: dict
    type: str
    authed_users: Optional[List[str]]
    event_id: str
    event_time: int


class SlackAction(SlackBase):
    class Config:
        extra = "allow"

    type: str

    actions: list = None
    api_app_id: str = None
    callback_id: str = None
    channel: dict = None
    container: dict = None
    hash: str = None
    is_cleared: bool = None
    message: dict = None
    response_url: str = None
    team: dict = None
    trigger_id: str = None
    user: dict = None
    view: dict = None


class SlackCommand(SlackBase):
    command: str
    response_url: str
    trigger_id: str
    user_id: str
    user_name: str
    team_id: str
    channel_id: str
    text: str
