"""
Handles events from the events API
Full list here: https://api.slack.com/events
"""
import logging

from app.slack.hooks import events
from typing import Any, Callable, Dict, List, Optional

from app.core.config import SLACK_TAG
from app.models.slack.events import (
    AppHomeOpenedPayload,
    AppMentionPayload,
    BasePayload,
    ChannelCreatedPayload,
    MessageAppHomePayload,
    MessageChannelPayload,
    MessageGroupsPayload,
    TeamJoinPayload
)
from app.slack.events.structures import CustomEvent, EventTypes
from app.slack.events.custom import (
    hello
)

logger = logging.getLogger(SLACK_TAG)

# all custom events
# must either be methods that accept a payload as a parameter or
# a class that extends the CustomEvent class
custom_events = [
    hello
]


def _get_custom_events_list(event_type: str) -> List[CustomEvent]:
    """Helper method for generating a list of events from the custom event list that match the specified event type.

    Args:
        event_type (str): The event type.

    Raises:
        AttributeError: If the event type is not a known event type (does not exist in ``EventTypes`` class).

    Returns:
        List[CustomEvent]: A list of all custom events matching the event type.
    """
    if not EventTypes.exists(event_type):
        raise AttributeError(f"event_type must be a value in EventTypes: {event_type}")

    return [e.Event() for e in custom_events if issubclass(e.Event, CustomEvent) and e.Event.event_type == event_type]


# separate the custom events into lists
# separation is done prior to event calls for shorter throughput
app_mention_events: List[CustomEvent] = _get_custom_events_list(event_type=EventTypes.APP_MENTION)
app_home_opened_events: List[CustomEvent] = _get_custom_events_list(event_type=EventTypes.APP_HOME_OPENED)
message_app_home_events: List[CustomEvent] = _get_custom_events_list(event_type=EventTypes.MESSAGE_APP_HOME)
team_join_events: List[CustomEvent] = _get_custom_events_list(event_type=EventTypes.TEAM_JOIN)


async def _invoke_custom_events(payload: BasePayload, events: Optional[List[CustomEvent]] = None) -> None:
    """Invokes a list of custom events.

    Args:
        events (Optional[List[CustomEvent]], optional): The list of custom events. These events must be either methods
            or classes that extends the ``CustomEvent`` class. Defaults to None.
    """
    print(f"Triggering {len(events)} events")
    for event in events:
        try:
            logger.debug("Running custom event %s" % event.name)
            await event(payload=payload)
        except Exception as e:
            logger.exception(e)


async def handle_app_mention(payload: Dict[Any, Any]):
    """When the bot is mentioned.

    Args:
        payload (AppMentionPayload): A payload with the event information.
    """
    await _invoke_custom_events(payload=AppMentionPayload(**payload), events=app_mention_events)


@events.on(EventTypes.APP_HOME_OPENED)
def handle_app_home_opened(payload: AppHomeOpenedPayload):
    """User clicked into your App Home.

    Args:
        payload (AppHomeOpenedPayload): A payload with the event information.
    """
    _invoke_custom_events(payload=payload, events=app_home_opened_events)
    logger.debug(payload)


@events.on(EventTypes.MESSAGE_APP_HOME)
def handle_app_home_message(payload: MessageAppHomePayload):
    """A user sent a message to your Slack app.

    Args:
        payload (MessageAppHomePayload): A payload with the event information.
    """
    logger.debug(payload)


@events.on(EventTypes.MESSAGE_CHANNELS)
def handle_message_channel(payload: MessageChannelPayload):
    """A message was posted to a channel.

    Args:
        payload (MessageChannelPayload): A payload with the event information.
    """
    logger.debug(payload)


@events.on(EventTypes.MESSAGE_GROUPS)
def handle_message_private_channel(payload: MessageGroupsPayload):
    """A message was posted to a private channel.

    Args:
        payload (MessageGroupsPayload): A payload with the event information.
    """
    logger.debug(payload)


@events.on(EventTypes.CHANNEL_CREATED)
def handle_channel_created(payload: ChannelCreatedPayload):
    """A channel was created.

    Args:
        payload (ChannelCreatedPayload): A payload with the event information.
    """
    logger.debug(payload)


def handle_team_join(payload: TeamJoinPayload):
    """A new member has joined.

    Args:
        payload (TeamJoinPayload): A payload with the event information.
    """
    _invoke_custom_events(payload=payload, events=team_join_events)
    logger.debug(payload)


event_mapping: Dict[str, Callable[[BasePayload], None]] = {
    EventTypes.APP_MENTION: handle_app_mention,
    EventTypes.APP_HOME_OPENED: handle_app_home_opened,
    EventTypes.MESSAGE_APP_HOME: handle_app_home_message,
    EventTypes.MESSAGE_CHANNELS: handle_message_channel,
    EventTypes.MESSAGE_GROUPS: handle_message_private_channel,
    EventTypes.CHANNEL_CREATED: handle_channel_created,
    EventTypes.TEAM_JOIN: handle_team_join
}
