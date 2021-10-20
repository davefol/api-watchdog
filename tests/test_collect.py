import unittest

from api_watchdog.collect import collect_results, WatchdogResultGroup
from api_watchdog.core import WatchdogResult, WatchdogTest


class TestCollect(unittest.TestCase):
    def test_collect_results_groupby_target(self):
        result_fragments = [
            ("1", "http://a.com/"),
            ("2", "http://a.com/b"),
            ("3", "http://a.com/b"),
            ("4", "http://a.com/c"),
            ("5", "http://a.com/d"),
        ]
        results = [
            WatchdogResult(
                test=WatchdogTest(
                    name=name, target=target, payload=None, expectation=None
                ),
                success=True,
                latency=0.0,
                timestamp=0.0,
                response=None,
            )
            for name, target in result_fragments
        ]
        result_group = collect_results(results)

        expectation = WatchdogResultGroup(
            name="<root>",
            results=[],
            groups=[
                WatchdogResultGroup(
                    name="http://a.com",
                    results=[
                        WatchdogResult(
                            test=WatchdogTest(
                                name="1",
                                target="http://a.com/",
                                payload=None,
                                expectation=None,
                            ),
                            success=True,
                            latency=0.0,
                            timestamp=0.0,
                            response=None,
                        )
                    ],
                    groups=[
                        WatchdogResultGroup(
                            name="http://a.com/b",
                            results=[
                                WatchdogResult(
                                    test=WatchdogTest(
                                        name="2",
                                        target="http://a.com/b",
                                        payload=None,
                                        expectation=None,
                                    ),
                                    success=True,
                                    latency=0.0,
                                    timestamp=0.0,
                                    response=None,
                                ),
                                WatchdogResult(
                                    test=WatchdogTest(
                                        name="3",
                                        target="http://a.com/b",
                                        payload=None,
                                        expectation=None,
                                    ),
                                    success=True,
                                    latency=0.0,
                                    timestamp=0.0,
                                    response=None,
                                ),
                            ],
                            groups=[],
                        ),
                        WatchdogResultGroup(
                            name="http://a.com/c",
                            results=[
                                WatchdogResult(
                                    test=WatchdogTest(
                                        name="4",
                                        target="http://a.com/c",
                                        payload=None,
                                        expectation=None,
                                    ),
                                    success=True,
                                    latency=0.0,
                                    timestamp=0.0,
                                    response=None,
                                )
                            ],
                            groups=[],
                        ),
                        WatchdogResultGroup(
                            name="http://a.com/d",
                            results=[
                                WatchdogResult(
                                    test=WatchdogTest(
                                        name="5",
                                        target="http://a.com/d",
                                        payload=None,
                                        expectation=None,
                                    ),
                                    success=True,
                                    latency=0.0,
                                    timestamp=0.0,
                                    response=None,
                                )
                            ],
                            groups=[],
                        ),
                    ],
                )
            ],
        )
        self.assertEqual(result_group, expectation)

    def test_collect_results_groupby_target_no_tld(self):
        result_fragments = [
            ("2", "http://a.com/b"),
            ("3", "http://a.com/b"),
            ("4", "http://a.com/c"),
            ("5", "http://a.com/d"),
        ]
        results = [
            WatchdogResult(
                test=WatchdogTest(
                    name=name, target=target, payload=None, expectation=None
                ),
                success=True,
                latency=0.0,
                timestamp=0.0,
                response=None,
            )
            for name, target in result_fragments
        ]
        result_group = collect_results(results)

        expectation = WatchdogResultGroup(
            name="<root>",
            results=[],
            groups=[
                WatchdogResultGroup(
                    name="http://a.com/b",
                    results=[
                        WatchdogResult(
                            test=WatchdogTest(
                                name="2",
                                target="http://a.com/b",
                                payload=None,
                                expectation=None,
                            ),
                            success=True,
                            latency=0.0,
                            timestamp=0.0,
                            response=None,
                        ),
                        WatchdogResult(
                            test=WatchdogTest(
                                name="3",
                                target="http://a.com/b",
                                payload=None,
                                expectation=None,
                            ),
                            success=True,
                            latency=0.0,
                            timestamp=0.0,
                            response=None,
                        ),
                    ],
                    groups=[],
                ),
                WatchdogResultGroup(
                    name="http://a.com/c",
                    results=[
                        WatchdogResult(
                            test=WatchdogTest(
                                name="4",
                                target="http://a.com/c",
                                payload=None,
                                expectation=None,
                            ),
                            success=True,
                            latency=0.0,
                            timestamp=0.0,
                            response=None,
                        )
                    ],
                    groups=[],
                ),
                WatchdogResultGroup(
                    name="http://a.com/d",
                    results=[
                        WatchdogResult(
                            test=WatchdogTest(
                                name="5",
                                target="http://a.com/d",
                                payload=None,
                                expectation=None,
                            ),
                            success=True,
                            latency=0.0,
                            timestamp=0.0,
                            response=None,
                        )
                    ],
                    groups=[],
                ),
            ],
        )
        self.assertEqual(result_group, expectation)


if __name__ == "__main__":
    unittest.main()
