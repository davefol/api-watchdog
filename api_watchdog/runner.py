import concurrent.futures
import json
import time
from typing import Iterable, Iterator, Any, Optional
import urllib.request

import jq

from api_watchdog.core import (
    WatchdogTest,
    WatchdogResult,
    Expectation,
    ExpectationResult,
)
from api_watchdog.result_error import ResultError
from api_watchdog.validate import validate, ValidationError


class Timer:
    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, traceback):
        self.time = time.time() - self.start


class WatchdogRunner:
    def __init__(self, max_workers: int = 16):
        self.max_workers = max_workers

    def run_test(self, test: WatchdogTest) -> WatchdogResult:
        request = urllib.request.Request(test.target)
        request.add_header("Content-Type", "application/json; charset=utf-8")

        try:
            body = test.payload.json().encode("utf-8")
        except AttributeError:  # we got a plain python dict and not a pydantic model
            body = json.dumps(test.payload).encode("utf-8")

        request.add_header("Content-Length", str(len(body)))

        timer = Timer()
        with timer:
            response = urllib.request.urlopen(request, body)
        latency = timer.time

        status_code = response.getcode()
        if 400 >= status_code >= 599:
            expectation_results = [
                ExpectationResult(
                    expectation=expectation,
                    result=ResultError(status_code),
                    actual=None,
                )
                for expectation in test.expectations
            ]
            return WatchdogResult(
                test_name=test.name,
                target=test.target,
                success=False,
                latency=latency,
                timestamp=time.time(),
                payload=test.payload,
                response=None,
                results=expectation_results
            )

        response_data = response.read()
        response_data = response_data.decode(
            response.info().get_content_charset("utf-8")
        )

        response_parsed = json.loads(response_data)

        expectation_results = []
        for expectation in test.expectations:
            try:
                for e in jq.compile(expectation.selector).input(response_parsed):
                    # print(e)
                    expectation_error = self.resolve_expectation(expectation, e)
                    expectation_results.append(expectation_error)
            except ValueError:
                # jq internal error
                expectation_results.append(ExpectationResult(expectation=expectation, result="jq-error", actual=None))

        success = all([x.result == "success" for x in expectation_results])
        print(success)

        return WatchdogResult(
            test_name=test.name,
            target=test.target,
            success=success,
            latency=latency,
            timestamp=time.time(),
            payload=test.payload,
            response=response_parsed,
            results=expectation_results,
        )

    def run_tests(
        self, tests: Iterable[WatchdogTest]
    ) -> Iterator[WatchdogResult]:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            return executor.map(self.run_test, tests)

    @staticmethod
    def resolve_expectation(
        expectation: Expectation, value: Any
    ) -> ExpectationResult:
        try:
            validated_elem = validate(value, expectation.validation_type)
        except ValidationError:
            return ExpectationResult(
                expectation=expectation, result="validate", actual=value
            )

        if validated_elem == expectation.value:
            return ExpectationResult(
                expectation=expectation, result="success", actual=validated_elem
            )
        else:
            return ExpectationResult(
                expectation=expectation, result="value", actual=validated_elem
            )
