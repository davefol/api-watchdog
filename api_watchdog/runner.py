import concurrent.futures
import json
import time
from typing import Iterable, Iterator
import urllib.request

from api_watchdog.core import WatchdogTest, WatchdogResult


class Timer:
    def __init__(self):
        self.start = time.time()

    def __enter__(self):
        return self

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
        except AttributeError: # we got a plain python dict and not a pydantic model
            body = json.dumps(test.payload).encode("utf-8")

        request.add_header("Content-Length", str(len(body)))

        timer = Timer()
        with timer:
            response = urllib.request.urlopen(request, body)
        latency = timer.time

        response_data = response.read()
        response_data = response_data.decode(response.info().get_content_charset('utf-8'))

        try:
            response_data = type(test.expectation).parse_raw(response_data)
        except AttributeError: # expectation is a plain python dict and not a pydantic model
            response_data = json.loads(response_data)

        success = response_data == test.expectation

        return WatchdogResult(
            test=test, success=success, latency=latency, timestamp=time.time(), response=response_data
        )

    def run_tests(
        self, tests: Iterable[WatchdogTest]
    ) -> Iterator[WatchdogResult]:
        with concurrent.futures.ThreadPoolExecutor(
            max_workers=self.max_workers
        ) as executor:
            return executor.map(self.run_test, tests)
