import concurrent.futures
import json
import logging
import time
from typing import Iterable, Iterator, Any
import requests

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
        """
        Run the watchdog tests found in the api-watchdog-translator-tests repo.

        note: the environment variable HTTPS_PROXY must be set in order for translator endpoints
        to be accessed properly

        :param test:
        :return:
        """
        method = test.method

        # init some flags for payload state
        body = None

        # if we have a test payload
        if test.payload:
            try:
                # pydantic .json() returns a string, need to make JSON
                body = json.loads(test.payload.json())
            except AttributeError:  # we got a plain python dict and not a pydantic model
                body = test.payload

        timer = Timer()

        with timer:
            try:
                if body is not None:
                    assert type(body) == dict, 'test.payload must be a dict.'
                    response = requests.request(method, url=test.target, json=body, timeout=120)
                # else we are just sending something simple on the url. the response should still be json
                else:
                    response = requests.request(method, url=test.target, timeout=120)

                # grab the status code for later
                status_code = response.status_code
                logging.info(f'{test.name}: {status_code}')
            except requests.Timeout as e:
                logging.error(f'{test.name} Timeout: {e}')
                response = None
                status_code = 408
            except requests.RequestException as e:
                logging.error(f'{test.name} Request Error: {e}')
                response = None
                status_code = 503
            except Exception as e:
                logging.error(f'{test.name} Exception: {e}')
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

        # grab the response in json format
        response_parsed = response.json()

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
