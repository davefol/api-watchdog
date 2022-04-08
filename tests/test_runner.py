import unittest
from unittest.mock import patch, MagicMock

from api_watchdog.core import WatchdogTest, Expectation
from api_watchdog.runner import WatchdogRunner
from api_watchdog.validate import ValidationType

TRAPI_SKIP_MESSAGE = "TRAPI exentsion not installed"
try:
    import reasoner_pydantic

    TRAPI_ENABLED = True
except ImportError:
    TRAPI_ENABLED = False


class TestWatchdogRunner(unittest.TestCase):
    @patch("requests.request")
    def test_run_tests(self, mock_request):
        """Test run_tests returns correct success parameter for each test."""

        def get_response_mock(method, url=None, json=None, timeout=120):
            mock = MagicMock()
            mock.status_code = 200

            def mocked_read():
                nonlocal json
                if json:
                    return {
                        "magic_number": 0xFEEDFACE ^ int(json["magic_number"]),
                    }
                return {
                    "empty_body": True,
                }

            mock.json = mocked_read
            return mock

        mock_request.side_effect = get_response_mock

        tests = [
            WatchdogTest(
                name="Bad Coffee",
                target="http://test.com",
                payload={"magic_number": 0xBADC0FFEE},
                expectations=[
                    Expectation(selector=".magic_number", value=-1, validation_type=ValidationType.Int)  # incorrect value
                ]
            ),
            WatchdogTest(
                name="Bad Food",
                target="http://test.com",
                payload={"magic_number": 0xBADF00D},
                expectations=[
                    Expectation(selector=".magic_number", value=0xFEEDFACE ^ 0xBADF00D, validation_type=ValidationType.Int)  # incorrect value
                ]
            ),
            WatchdogTest(
                name="Feed Face",
                target="http://test.com",
                payload={"magic_number": 0xFEEDFACE},
                expectations=[
                    Expectation(selector=".magic_number", value=0, validation_type=ValidationType.Int)  # incorrect value
                ]
            ),
            WatchdogTest(
                name="Empty Face",
                target="http://test.com",
                payload={},
                expectations=[
                    Expectation(selector=".empty_body", value=True, validation_type=ValidationType.Int)
                ]
            ),
        ]

        runner = WatchdogRunner()
        results = sorted(runner.run_tests(tests), key=lambda x: x.test_name)

        self.assertFalse(results[0].success)
        self.assertTrue(results[1].success)
        self.assertTrue(results[2].success)
        self.assertTrue(results[3].success)

    @unittest.skipIf(not TRAPI_ENABLED, TRAPI_SKIP_MESSAGE)
    @patch("requests.request")
    def test_run_tests_trapi_validation(self, mock_request):
        """
        Test run_tests returns correct success parameter for each test when
        there payload and expectation are TRAPI validated
        """

        def get_response_mock(method, url=None, json=None, timeout=120):
            mock = MagicMock()
            mock.status_code = 200

            def mocked_read():
                nonlocal json
                magic_number = list(json["query_graph"]["nodes"].keys())[0]
                magic_number = 0xFEEDFACE ^ int(magic_number, 16)
                return {
                    "message": {
                        "results": [
                            {
                                "node_bindings": {
                                    "n0": [
                                        {
                                            "id": "MONDO:0005618"
                                        }
                                    ],
                                    "n1": [
                                        {
                                            "id": "MONDO:0024613"
                                        }
                                    ]
                                },
                                "edge_bindings": {},
                                "score": magic_number
                            }
                        ]
                    }
                }

            mock.json = mocked_read
            return mock

        mock_request.side_effect = get_response_mock

        tests = [
            WatchdogTest(
                name="Bad Coffee",
                target="http://test.com",
                payload=reasoner_pydantic.message.Message(
                    query_graph=reasoner_pydantic.QueryGraph(
                        nodes={"BADC0FFEE": reasoner_pydantic.QNode()},
                        edges={}
                    ),
                    knowledge_graph=reasoner_pydantic.KnowledgeGraph(
                        nodes={},
                        edges={}
                    )
                ),
                expectations=[
                    Expectation(
                        selector=".message.results[0].node_bindings.n0[0]",
                        validation_type=ValidationType.TrapiNodeBinding,
                        value={"id": "MONDO:0005618"}
                    ),
                    Expectation(
                        selector=".message.results[0].edge_bindings",
                        validation_type=ValidationType.Object,
                        value={}
                    ),
                    Expectation(
                        selector=".message.results[0].score",
                        validation_type=ValidationType.Int,
                        value=-1
                    ),
                    Expectation(
                        selector=".message",
                        validation_type=ValidationType.TrapiMessage,
                        value=reasoner_pydantic.message.Message(
                            results=[
                                reasoner_pydantic.Result(
                                    node_bindings={
                                        "n0": [
                                            {
                                                "id": "MONDO:0005618"
                                            }
                                        ],
                                        "n1": [
                                            {
                                                "id": "MONDO:0024613"
                                            }
                                        ]
                                    },
                                    edge_bindings={},
                                    score=-1
                                )
                            ]
                        )
                    )
                ]
            ),
            WatchdogTest(
                name="Bad Food",
                target="http://test.com",
                payload=reasoner_pydantic.message.Message(
                    query_graph=reasoner_pydantic.QueryGraph(
                        nodes={"BADF00D": reasoner_pydantic.QNode()},
                        edges={}
                    ),
                    knowledge_graph=reasoner_pydantic.KnowledgeGraph(
                        nodes={},
                        edges={}
                    )
                ),
                expectations=[
                    Expectation(
                        selector=".message.results[0].node_bindings.n0[0]",
                        validation_type=ValidationType.TrapiNodeBinding,
                        value={"id": "MONDO:0005618"}
                    ),
                    Expectation(
                        selector=".message.results[0].edge_bindings",
                        validation_type=ValidationType.Object,
                        value={}
                    ),
                    Expectation(
                        selector=".message.results[0].score",
                        validation_type=ValidationType.Int,
                        value=0xFEEDFACE ^ 0xBADF00D
                    ),
                    Expectation(
                        selector=".message",
                        validation_type=ValidationType.TrapiMessage,
                        value=reasoner_pydantic.message.Message(
                            results=[
                                reasoner_pydantic.Result(
                                    node_bindings={
                                        "n0": [
                                            {
                                                "id": "MONDO:0005618"
                                            }
                                        ],
                                        "n1": [
                                            {
                                                "id": "MONDO:0024613"
                                            }
                                        ]
                                    },
                                    edge_bindings={},
                                    score=0xFEEDFACE ^ 0xBADF00D
                                )
                            ]
                        )
                    )
                ]
            ),
            WatchdogTest(
                name="Feed Face",
                target="http://test.com",
                payload=reasoner_pydantic.message.Message(
                    query_graph=reasoner_pydantic.QueryGraph(
                        nodes={"FEEDFACE": reasoner_pydantic.QNode()},
                        edges={}
                    ),
                    knowledge_graph=reasoner_pydantic.KnowledgeGraph(
                        nodes={},
                        edges={}
                    )
                ),
                expectations=[
                    Expectation(
                        selector=".message.results[0].node_bindings.n0[0]",
                        validation_type=ValidationType.TrapiNodeBinding,
                        value={"id": "MONDO:0005618"}
                    ),
                    Expectation(
                        selector=".message.results[0].edge_bindings",
                        validation_type=ValidationType.Object,
                        value={}
                    ),
                    Expectation(
                        selector=".message.results[0].score",
                        validation_type=ValidationType.Int,
                        value=0
                    ),
                    Expectation(
                        selector=".message",
                        validation_type=ValidationType.TrapiMessage,
                        value=reasoner_pydantic.message.Message(
                            results=[
                                reasoner_pydantic.Result(
                                    node_bindings={
                                        "n0": [
                                            {
                                                "id": "MONDO:0005618"
                                            }
                                        ],
                                        "n1": [
                                            {
                                                "id": "MONDO:0024613"
                                            }
                                        ]
                                    },
                                    edge_bindings={},
                                    score=0
                                )
                            ]
                        )
                    )
                ]
            ),
        ]

        runner = WatchdogRunner()
        results = sorted(runner.run_tests(tests), key=lambda x: x.test_name)
        self.assertFalse(results[0].success)
        self.assertTrue(results[1].success)
        self.assertTrue(results[2].success)


if __name__ == "__main__":
    unittest.main()
