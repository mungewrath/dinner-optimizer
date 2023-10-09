import datetime
from typing import Self


class Interaction:
    @classmethod
    def from_dynamo(cls, dynamo_entry) -> Self:
        ret = Interaction(
            role=dynamo_entry["M"]["role"]["S"],
            time=dynamo_entry["M"]["time"]["S"],
            text=dynamo_entry["M"]["text"]["S"],
            timestamp=dynamo_entry["M"]["timestamp"]["S"],
        )

        return ret

    def __init__(self, role: str, time: str, text: str, timestamp: str) -> None:
        self.role = role
        self.time = time
        self.text = text
        self.timestamp = timestamp

    def to_dynamo(self):
        if (
            self.role is None
            or self.time is None
            or self.text is None
            or self.timestamp is None
        ):
            raise ValueError(
                "Tried to create dynamo object from Interaction, but fields were not fully populated"
            )

        return {
            "M": {
                "role": {"S": self.role},
                "time": {"S": self.time},
                "text": {"S": self.text},
                "timestamp": {"S": self.timestamp},
            },
        }
