from datetime import datetime
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, StrictStr, AnyUrl

from api_watchdog.integrations.trapi import TrapiMessage


class ValidationType(Enum):
    Trapi = "TRAPI"

VALIDATION_MAP = {ValidationType.Trapi: TrapiMessage}

class WatchdogTest(BaseModel):
    name: StrictStr
    target: AnyUrl
    validate_payload: Optional[ValidationType]
    validate_expectation: Optional[ValidationType]
    payload: Any
    expectation: Any

    @classmethod
    def parse_obj(cls, o):
        test = super(WatchdogTest, cls).parse_obj(o)
        if test.validate_payload is not None:
            try:
                test.payload = VALIDATION_MAP[test.validate_payload].parse_obj(
                    test.payload
                )
            except KeyError:
                raise ValueError(
                    f"Uknown validation type {test.validate_payload} for"
                    " payload"
                )
        if test.validate_expectation is not None:
            try:
                test.expectation = VALIDATION_MAP[
                    test.validate_expectation
                ].parse_obj(test.expectation)
            except KeyError:
                raise ValueError(
                    f"Unknown validation type {test.validate_expectation} for"
                    " expectation"
                )

        return test

class WatchdogResult(BaseModel):
    test: WatchdogTest
    success: bool
    latency: float
    timestamp: datetime
