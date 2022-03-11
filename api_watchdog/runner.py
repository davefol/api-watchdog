import concurrent.futures
import json
import time
from typing import Iterable, Iterator, Any
import urllib.request
import urllib.error

import jq

from api_watchdog.core import (
    WatchdogTest,
    WatchdogResult,
    Expectation,
    ExpectationResult,
    ExpectationLevel,
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
        method = test.method

        request = urllib.request.Request(test.target, method=method)
        request.add_header("Content-Type", "application/json; charset=utf-8")
        request.add_header("accept", "application/json")

        use_body = False
        body = None

        if test.payload:
            use_body = True
            try:
                body = test.payload.json().encode("utf-8")
            except AttributeError:  # we got a plain python dict and not a pydantic model
                body = json.dumps(test.payload).encode("utf-8")

            request.add_header("Content-Length", str(len(body)))

        # use the proxy if found
        if test.proxy is not None:
            # create a proxy handler using the proxy address found in the test
            proxy_handler = urllib.request.ProxyHandler({"http": test.proxy})

            # create a opener for this request
            opener = urllib.request.build_opener(proxy_handler)

            # install the opener that uses the proxy
            urllib.request.install_opener(opener)

        timer = Timer()

        with timer:
            try:
                if use_body:
                    response = urllib.request.urlopen(request, body)
                else:
                    response = urllib.request.urlopen(request)
                status_code = response.getcode()
            except (urllib.error.HTTPError, urllib.error.URLError) as e:
                response = None
                if isinstance(e, urllib.error.HTTPError):
                    status_code = e.code
                elif isinstance(e, urllib.error.URLError):
                    status_code = 503
            except:
                response = None
                status_code = 500

        latency = timer.time

        if 400 <= status_code <= 599:
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
                email_to=test.email_to,
                payload=test.payload,
                response=None,
                results=expectation_results,
            )

        assert response is not None
        response_data = response.read()
        response_data = response_data.decode(
            response.info().get_content_charset("utf-8")
        )

        response_parsed = json.loads(response_data)

        expectation_results = []
        for expectation in test.expectations:
            try:
                for e in jq.compile(expectation.selector).input(
                    response_parsed
                ):
                    expectation_error = self.resolve_expectation(expectation, e)
                    expectation_results.append(expectation_error)
            except ValueError:
                # jq internal error
                expectation_results.append(
                    ExpectationResult(
                        expectation=expectation, result="jq-error", actual=None
                    )
                )

        success = all(
            [
                (x.result == "success" and x.expectation.level == ExpectationLevel.CRITICAL)
                or (x.expectation.level != ExpectationLevel.CRITICAL)
                for x in expectation_results
            ]
        )

        result = WatchdogResult(
            test_name=test.name,
            target=test.target,
            success=success,
            latency=latency,
            timestamp=time.time(),
            email_to=test.email_to,
            payload=test.payload,
            response=response_parsed,
            results=expectation_results,
        )

        return result

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
