import json
import logging
import typing

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from starlette.requests import Request
from starlette.responses import Response
from starlette.status import HTTP_200_OK

from app.core.config import SLACK_TAG
from app.models.slack.common import SlackAction, SlackChallenge, SlackCommand, SlackEnvelope
from app.slack.events.routes import event_mapping
from app.slack.hooks import actions, commands, emit
from app.slack.registry import R
from app.slack.verification import check_timeout, verify_signature

log = logging.getLogger(SLACK_TAG)

router = APIRouter()


@router.post(
    "/events",
    status_code=HTTP_200_OK,
    dependencies=[Depends(verify_signature), Depends(check_timeout)],
)
async def post_events(message: typing.Union[SlackEnvelope, SlackChallenge]):
    if isinstance(message, SlackChallenge):
        return message.challenge

    try:
        jsonable_payload = jsonable_encoder(message)
        log.debug(jsonable_payload)
        event = message.event["type"]
        if event in event_mapping:
            await event_mapping[message.event["type"]](jsonable_payload)
        else:
            log.warn("Unknown event type: %s" % event)
    except Exception as e:
        log.exception(e)
    return Response()


@router.post(
    "/actions",
    status_code=HTTP_200_OK,
    dependencies=[Depends(verify_signature), Depends(check_timeout)],
)
async def post_actions(request: Request) -> Response:
    form = await request.form()
    form_data = json.loads(form["payload"])

    # have the convenience of pydantic validation
    action = SlackAction(**form_data)
    _events = [action.type]
    if action.actions:
        _events.extend(_add_action_triggers(action))
    if action.callback_id:
        _events.append(f"{action.type}:{action.callback_id}")
    if action.view:
        view_callback_id = action.view.get("callback_id")
        if view_callback_id:
            _events.append(f"{action.type}:{view_callback_id}")

    for _event in _events:
        emit(actions, _event, payload=action)

    registered_handlers = set(R.callbacks.keys())
    registered_events = set(_events)
    handlers_to_call = registered_handlers.intersection(registered_events)
    if len(handlers_to_call) > 1:
        raise ValueError("Multiple response handlers found.")

    if handlers_to_call:
        handle = handlers_to_call.pop()
        response = R.handle(handle, action.dict())
        assert isinstance(
            response, Response
        ), "Please return a starlette.responses.Response"
        return response
    return Response()


def _add_action_triggers(action: SlackAction) -> list:
    gathered_events = [
        f"{action.type}:{triggered_action['action_id']}"
        for triggered_action in action.actions
        if "action_id" in triggered_action
    ]
    gathered_events.extend(
        [
            f"{action.type}:{triggered_action['name']}"
            for triggered_action in action.actions
            if "name" in triggered_action
        ]
    )
    gathered_events.extend(
        [
            f"{action.type}:{triggered_action['type']}"
            for triggered_action in action.actions
            if "type" in triggered_action
        ]
    )
    gathered_events.extend(
        [
            f"{action.type}:{triggered_action['name']}:{triggered_action['type']}"
            for triggered_action in action.actions
            if "name" in triggered_action and "type" in triggered_action
        ]
    )

    return gathered_events


@router.post(
    "/commands",
    status_code=HTTP_200_OK,
    dependencies=[Depends(verify_signature), Depends(check_timeout)],
)
async def post_commands(request: Request):
    form = await request.form()
    command = SlackCommand(**form)
    emit(commands, command.command.lstrip("/"), command)

    return Response()
