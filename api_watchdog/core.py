from typing import Optional, Union, Any, Dict

from pydantic import BaseModel, StrictStr, AnyUrl, Json

from api_watchdog.integrations.trapi import TrapiMessage

VALIDATION_MAP = {"TRAPI": TrapiMessage}


class WatchdogTest(BaseModel):
    name: StrictStr
    target: AnyUrl
    validate_payload: Optional[StrictStr]
    validate_expectation: Optional[StrictStr]
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
