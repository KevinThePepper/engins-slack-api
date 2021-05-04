import datetime

from typing import Optional

from pydantic import BaseConfig, BaseModel


def convert_datetime_to_realworld(dt: datetime.datetime) -> str:
    return dt.replace(tzinfo=datetime.timezone.utc).isoformat().replace("+00:00", "Z")


def convert_field_to_camel_case(string: str) -> str:
    return "".join(
        word if index == 0 else word.capitalize()
        for index, word in enumerate(string.split("_"))
    )


class Model(BaseModel):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    class Config(BaseConfig):
        allow_population_by_field_name = True
        json_encoders = {datetime.datetime: convert_datetime_to_realworld}
        alias_generator = convert_field_to_camel_case


class BaseResponse(Model):
    ok: bool
    message: Optional[str]

    def __init__(self, ok: bool = True, message: str = "") -> None:
        super().__init__(ok=ok, message=message)
