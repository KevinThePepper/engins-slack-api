import logging

from slackers.hooks import commands

from app.core.config import SLACK_TAG
from app.slack.client import SlackClient


logger = logging.getLogger(SLACK_TAG)
client = SlackClient.get_instance()


@commands.on("test")
def handle_test_command(payload):
    print(payload)
    client.post_message(text="hello", channel="general")
