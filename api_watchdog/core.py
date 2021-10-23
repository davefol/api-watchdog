from datetime import datetime
from typing import Any, List, Literal

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
    result: Literal["success", "value", "validate"]
    actual: Any

class WatchdogTest(BaseModel):
    name: StrictStr
    target: AnyUrl
    payload: Any
    expectations: List[Expectation]

class WatchdogResult(BaseModel):
    test_name: StrictStr
    success: bool
    latency: float
    timestamp: datetime
    payload: Any
    response: Any
    results: List[ExpectationResult]

