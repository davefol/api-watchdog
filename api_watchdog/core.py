from datetime import datetime
from typing import Any, List, Literal, Union

from api_watchdog.result_error import ResultError
from api_watchdog.validate import ValidationType
from api_watchdog.validate import validate as _validate

from pydantic import BaseModel, StrictStr, AnyUrl

class Expectation(BaseModel):
    selector: StrictStr
    value: Any
    validation_type: ValidationType

    def __init__(self, selector, value, validation_type):
        super().__init__(selector=selector, value=value, validation_type=validation_type)
        self.value = _validate(self.value, self.validation_type)


class ExpectationResult(BaseModel):
    expectation: Expectation
    result: Union[Literal["success", "value", "validate", "jq-error"], ResultError]
    actual: Any

class WatchdogTest(BaseModel):
    name: StrictStr
    target: AnyUrl
    payload: Any
    expectations: List[Expectation]

class WatchdogResult(BaseModel):
    test_name: StrictStr
    target: AnyUrl
    success: bool
    latency: float
    timestamp: datetime
    payload: Any
    response: Any
    results: List[ExpectationResult]

