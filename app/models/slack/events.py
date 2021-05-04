from typing import Any, Dict, Optional, List

from app.models.slack.common import User
from app.models.schemas.common import Model


class BaseEventPayload(Model):
    type: str
    channel: str
    user: str
    text: Optional[str]
    ts: str
    event_ts: str


class ChannelTypeEventPayload(BaseEventPayload):
    channel_type: str


class ChannelGroupEventPayload(BaseEventPayload):
    channel_group: str


class BasePayload(Model):
    token: str
    team_id: str
    api_app_id: str
    event: Optional[BaseEventPayload]
    type: str = "event_callback"
    event_id: str
    event_time: int
    authed_teams: Optional[List[str]]


class AppMentionPayload(BasePayload):
    event: BaseEventPayload


class AppHomeOpenedViewPayload(Model):
    id: str
    team_id: str
    type: str
    blocks: List[Dict[Any, Any]]
    private_metadata: str
    callback_id: str
    state: Dict[Any, Any]
    hash: str
    clear_on_close: bool
    notify_on_close: bool
    root_view_id: str
    app_id: str
    external_id: str
    app_installed_team_id: str
    bot_id: str


class AppHomeOpenedEventPayload(BaseEventPayload):
    tab: str
    view: AppHomeOpenedViewPayload


class ChannelCreatedChannelPayload(Model):
    id: str
    name: str
    created: int
    creator: str


class ChannelCreatedEventPayload(BaseEventPayload):
    type: str
    channel: ChannelCreatedChannelPayload


class ChannelCreatedPayload(BasePayload):
    event: ChannelCreatedEventPayload


class AppHomeOpenedPayload(BasePayload):
    event: AppHomeOpenedEventPayload


class MessageGroupsPayload(BasePayload):
    event: ChannelGroupEventPayload


class MessageAppHomePayload(BasePayload):
    event: ChannelTypeEventPayload


class MessageChannelPayload(BasePayload):
    event: ChannelTypeEventPayload


class TeamJoinEventPayload(Model):
    type: str
    user: User


class TeamJoinPayload(BasePayload):
    event: TeamJoinEventPayload
