from datetime import datetime
from enum import Enum
from typing import Optional, Any, List

from pydantic import BaseModel, StrictStr, AnyUrl

from api_watchdog.integrations.trapi import TrapiMessage


class ValidationType(Enum):
    Trapi = "TRAPI"

VALIDATION_MAP = {ValidationType.Trapi: TrapiMessage}

class Expectation(BaseModel):
    selector: StrictStr
    value: Any
    validate: Optional[ValidationType]

class WatchdogTest(BaseModel):
    name: StrictStr
    target: AnyUrl
    validate_payload: Optional[ValidationType]
    payload: Any
    expectations: List[Expectation]

    @classmethod
    def parse_obj(cls, o):
        test = super(WatchdogTest, cls).parse_obj(o)
        if test.validate_payload is not None:
            breakpoint()
            try:
                test.payload = VALIDATION_MAP[test.validate_payload].parse_obj(
                    test.payload["message"]
                )
            except KeyError:
                raise ValueError(
                    f"Uknown validation type {test.validate_payload} for"
                    " payload"
                )
        return test

class WatchdogResult(BaseModel):
    test: WatchdogTest
    success: bool
    latency: float
    timestamp: datetime
    response: Any
