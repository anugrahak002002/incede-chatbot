from typing import Literal
from typing_extensions import TypedDict


class botState(TypedDict):
    current_field: Literal["name", "phone", "email", "description", "done"]
    name:          str
    email:         str
    phone:         str
    description:   str
    user_input:    str
    bot_message:   str
    valid:         bool