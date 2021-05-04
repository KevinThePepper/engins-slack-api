import asyncio
import logging

from typing import Union

from slack import WebClient
from slack.errors import SlackApiError

from app.core.config import (
    SLACK_BOT_ID,
    SLACK_ADMIN_ID,
    SLACK_API_TOKEN,
    SLACK_DEFAULT_CHANNEL,
    SLACK_TAG
)
from app.models.slack.responses import BotsInfo, AuthTest, SlackError


class SlackClient(WebClient):
    """Asynchronous Slack web client.

    Args:
        AsyncWebClient (AsyncWebClient): The asynchronous web client provided by Slack.
    """

    __instance = None

    bot_id: str
    user_id: str
    app_id: str
    name: str
    deleted: bool
    logger: logging.Logger

    @staticmethod
    def instance():
        """A function to gives the ``get_instance`` method a friendly name.

        Returns:
            SlackClient: The ``SlackClient`` singleton instance.
        """
        return SlackClient.get_instance()

    @staticmethod
    def get_instance():
        """Returns the singleton instance of this client. If one does not exist, the constructor is invoked and
        the generated instance is returned.

        Returns:
            SlackClient: The ``SlackClient`` singleton instance.
        """
        if not SlackClient.__instance:
            SlackClient()
        return SlackClient.__instance

    def __init__(self, token: str = SLACK_API_TOKEN) -> None:
        """Gives this web client the required API token.

        Args:
            token (str): The Slack API token for the bot.
        """
        if SlackClient.__instance:
            raise Exception("SlackClient is a singleton class")

        SlackClient.__instance = self
        super().__init__(token=token, run_async=True)
        try:
            future: asyncio.Future = self.bots_info()
            loop = asyncio.get_event_loop()
            bots_info: BotsInfo = loop.run_until_complete(future)
            if "bot" in bots_info and bots_info.bot is not None:
                print(bots_info)
                self.bot_id = bots_info.bot.id
                self.user_id = bots_info.bot.user_id
                self.app_id = bots_info.bot.app_id
                self.name = bots_info.bot.name
                self.deleted = bots_info.bot.deleted
            else:
                self.bot_id = SLACK_BOT_ID
                self.user_id = SLACK_ADMIN_ID

            # if not set grab the user ID
            if not self.user_id or not self.bot_id:
                future: asyncio.Future = self.auth_test()
                auth_info: Union[AuthTest, SlackError] = loop.run_until_complete(future)
                if "user_id" in auth_info:
                    auth_info = AuthTest(**auth_info)
                    print("Auth info obtained: %s" % str(auth_info))
                    self.user_id = auth_info.user_id
                    self.bot_id = auth_info.bot_id

        except SlackApiError as e:
            self._assert_and_log_error(e)

        self.logger = logging.getLogger(SLACK_TAG)

    def _assert_and_log_error(self, error: SlackApiError) -> None:
        """Asserts a SlackApiError to validate it and raise the error. This is a helper function to be used by methods
        that have been overriden to throw errors.

        Args:
            error (SlackApiError): The error response from Slack.

        Raises:
            error: The error response from Slack will be raised again.
        """
        assert error.response["ok"] is False
        assert error.response["error"]
        self.logger.exception(error.response["error"])
        raise error

    def is_bot_user(self, _id: str) -> bool:
        """Determines if the passed user ID is the bot's ID.

        Args:
            _id (str): The user ID to check.

        Returns:
            bool: ``True`` if the user ID matches the bot ID.
        """
        return self.bot_id == _id

    def is_admin_user(self, _id: str) -> bool:
        """Determines if the passed user ID is the bot's admin ID.

        Args:
            _id (str): The user ID to check.

        Returns:
            bool: ``True`` if the user ID matches the admin ID.
        """
        return self.app_id == _id

    def is_app_user(self, _id: str) -> bool:
        """Determines if the passed user ID is the bot's admin ID.

        Args:
            _id (str): The user ID to check.

        Returns:
            bool: ``True`` if the user ID matches the admin ID.
        """
        return self.user_id == _id

    def is_user(self, _id: str) -> bool:
        """Determines if the user ID belongs to this bot client.

        Args:
            _id (str): The user ID to check.

        Returns:
            bool: ``True`` if the user ID matches the bot ID or the admin ID.
        """
        return self.is_bot_user(_id=_id) or self.is_admin_user(_id=_id) or self.is_app_user(_id=_id)

    async def post_message(self, text: str, channel: str = SLACK_DEFAULT_CHANNEL):
        """Posts a message to a channel.

        Args:
            text (str): The message to post.
            channel (str, optional): The channel to post the message to. Defaults to ``SLACK_DEFAULT_CHANNEL``.

        Raises:
            e (SlackApiError): Raised if the response's ``ok`` component is False.
        """
        future = self.chat_postMessage(channel=channel, text=text)
        try:
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(future)
            assert response["message"]["text"] == text
        except SlackApiError as e:
            self._assert_and_log_error(e)

    async def post_ephimeral(self, text: str, user: str, channel: str = SLACK_DEFAULT_CHANNEL):
        """Posts an ephimeral message on a channel to a specific user.

        Args:
            text (str): The message to post.
            user (str): The user to send the message to.
            channel (str, optional): The channel to post the message to. Defaults to ``SLACK_DEFAULT_CHANNEL``.

        Raises:
            e (SlackApiError): Raised if the response's ``ok`` component is False.
        """
        future = self.chat_postEphemeral(channel=channel, user=user, text=text)
        try:
            loop = asyncio.get_event_loop()
            response = loop.run_until_complete(future)
            assert response["message"]["text"] == text
        except SlackApiError as e:
            self._assert_and_log_error(e)
