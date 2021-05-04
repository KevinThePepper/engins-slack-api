import logging
from typing import List

from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret

API_TAG = "api"
API_PREFIX = f"/{API_TAG}"
SLACK_TAG = "slack"
SLACK_PREFIX = f"/{SLACK_TAG}"

JWT_TOKEN_PREFIX = "Token"  # noqa: S105
VERSION = "0.0.1"

config = Config(".env")

DEBUG: bool = config("DEBUG", cast=bool, default=False)

MAX_CONNECTIONS_COUNT: int = config("MAX_CONNECTIONS_COUNT", cast=int, default=10)
MIN_CONNECTIONS_COUNT: int = config("MIN_CONNECTIONS_COUNT", cast=int, default=10)

SECRET_KEY: Secret = config("SECRET_KEY", cast=Secret, default="AZOINvoinerOINV9243vOIN")

PROJECT_NAME: str = config("PROJECT_NAME", default="FastAPI Template Application")
ALLOWED_HOSTS: List[str] = config(
    "ALLOWED_HOSTS",
    cast=CommaSeparatedStrings,
    default="",
)

TAGS_METADATA = [
    {
        "name": SLACK_TAG,
        "description": "Endponts to manage Slack interactions and events. "
                       "These endpoints are to be accessed only by Slack.",
        "externalDocs": {
            "description": "Slack Events API",
            "url": "https://api.slack.com/events-api"
        }
    }
]

# LOGGING
# --------------------------------------------------------

LOGGING_LEVEL = logging.DEBUG if DEBUG else logging.INFO
LOGGING_PATH = "logs/"
LOGGING_MAX_BYTES = 1024 * 1024 * 5  # 5 megabytes
LOGGERS = [SLACK_TAG, "requests", "hooks"]
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        },
        "console": {
            "()": "uvicorn.logging.DefaultFormatter",  # colors the log output
            "format": "%(levelprefix)s %(message)s",
            "use_colors": None,
        }
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "console",
        }
    },
    "loggers": {}
}

# configure loggers with the default configuration
for handler in LOGGERS:
    LOGGING["loggers"].update({
        handler: {
            "handlers": ["console"],
            "level": "DEBUG",
            "propagate": False
        }
    })

# SLACK
# --------------------------------------------------------

SLACK_SIGNING_SECRET: str = config("SLACK_SIGNING_SECRET", cast=str, default="TEST")
SLACK_API_TOKEN: str = config("SLACK_API_TOKEN", cast=str, default="")
SLACK_DEFAULT_CHANNEL: str = config("SLACK_DEFAULT_CHANNEL", cast=str, default="general")
SLACK_BOT_ID: str = config("SLACK_BOT_ID", cast=str, default="")
SLACK_ADMIN_ID: str = config("SLACK_ADMIN_ID", cast=str, default="")
