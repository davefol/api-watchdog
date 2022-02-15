from datetime import datetime
from enum import Enum
from typing import Any, List, Literal, Union, Optional

from api_watchdog.result_error import ResultError
from api_watchdog.validate import ValidationType
from api_watchdog.validate import validate as _validate

from pydantic import BaseModel, StrictStr, AnyUrl

class ExpectationLevel(Enum):
    CRITICAL = "critical"
    WARNING = "warning"
    INFO = "info"

class Expectation(BaseModel):
    selector: StrictStr
    value: Any
    validation_type: ValidationType
    level: ExpectationLevel = ExpectationLevel.CRITICAL

    def __init__(self, selector, value, validation_type, level=ExpectationLevel.CRITICAL):
        super().__init__(selector=selector, value=value, validation_type=validation_type, level=level)
        self.value = _validate(self.value, self.validation_type)


class ExpectationResult(BaseModel):
    expectation: Expectation
    result: Union[Literal["success", "value", "validate", "jq-error"], ResultError]
    actual: Any

class WatchdogTest(BaseModel):
    name: StrictStr
    target: AnyUrl
    method: Optional[StrictStr] = "POST"
    email_to: Optional[List[StrictStr]]
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
    email_to: Optional[List[StrictStr]]

