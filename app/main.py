from logging.config import dictConfig

import nest_asyncio

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from mangum import Mangum
from starlette.exceptions import HTTPException
from starlette.middleware.cors import CORSMiddleware

from app.api.exceptions import http_error_handler, http422_error_handler
from app.api.router import api_router
from app.core.config import LOGGING
from app.core.config import ALLOWED_HOSTS, API_PREFIX, DEBUG, PROJECT_NAME, SLACK_PREFIX, TAGS_METADATA, VERSION
from app.middleware import LambdaLoggerMiddleware
from app.slack.routes import router as slack_router


def get_application() -> FastAPI:
    application = FastAPI(
        title=PROJECT_NAME,
        debug=DEBUG,
        version=VERSION,
        root_path="/prod",
        openapi_tags=TAGS_METADATA
    )

    application.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_HOSTS or ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )

    application.add_middleware(LambdaLoggerMiddleware)

    dictConfig(LOGGING)

    # application.add_event_handler("startup", create_start_app_handler(application))
    # application.add_event_handler("shutdown", create_stop_app_handler(application))

    application.add_exception_handler(HTTPException, http_error_handler)
    application.add_exception_handler(RequestValidationError, http422_error_handler)

    application.include_router(api_router, prefix=API_PREFIX)
    application.include_router(slack_router, prefix=SLACK_PREFIX, tags=["slack"])

    return application


app = get_application()
nest_asyncio.apply()
handler = Mangum(app, lifespan="off", enable_lifespan=False)
