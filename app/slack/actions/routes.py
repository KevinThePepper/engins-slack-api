import logging
from slackers.hooks import actions

logger = logging.getLogger()


@actions.on("block_actions")
def block_actions_pipeline(payload):
    logger.debug(payload)
