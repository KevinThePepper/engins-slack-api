from typing import Any

from app.models.slack.events import AppMentionPayload
from app.slack.events.structures import CustomEvent, EventTypes


class Event(CustomEvent):
    """Custom event class that simply print "Hello!" to the channel.

    Args:
        CustomEvent ([type]): [description]
    """
    name = "hello"
    event_type = EventTypes.APP_MENTION

    async def __call__(self, payload: AppMentionPayload, **kwargs) -> Any:
        if not self.client.is_user(payload.event.user):
            channel = payload.event.channel
            bot_info = await self.client.bots_info()
            await self.client.post_message(channel=channel, text=str(bot_info))
