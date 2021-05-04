"""
Defines custom structures for Slack events.
"""
import abc

from typing import Any, Dict, Optional, Union

from app.slack.client import SlackClient
from app.models.slack.events import BasePayload
from app.slack.common import IAction


class EventTypes:
    APP_MENTION: str = "app_mention"
    APP_HOME_OPENED: str = "app_home_created"
    MESSAGE_APP_HOME: str = "message.app_home"
    MESSAGE_CHANNELS: str = "message.channels"
    MESSAGE_GROUPS: str = "message.groups"
    CHANNEL_CREATED: str = "channel_created"
    TEAM_JOIN: str = "team_join"

    @staticmethod
    def exists(value: str):
        return value in [v for k, v in vars(EventTypes).items() if not k.startswith("_")]


class CustomEvent(IAction, metaclass=abc.ABCMeta):
    event_type: str = None

    def __init__(self, event_type: str = None) -> None:
        if event_type and not EventTypes.exists(event_type):
            raise AttributeError(f"event_type must be a name from EventTypesEnum: {event_type}")

        if not self.event_type and event_type:
            self.event_type = event_type
        self.client = SlackClient.get_instance()

    @abc.abstractmethod
    def __call__(self, payload: Optional[Union[Dict, BasePayload]] = None, **kwargs) -> Any:
        raise NotImplementedError("subclasses must implement the __call__ method")

    def post_call(self) -> None:
        pass


class CustomJsonEvent(CustomEvent):
    pass
