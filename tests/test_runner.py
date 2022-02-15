import json
import unittest
from unittest.mock import patch, MagicMock

TRAPI_SKIP_MESSAGE = "TRAPI exentsion not installed"
try:
    import reasoner_pydantic

    TRAPI_ENABLED = True
except ImportError:
    TRAPI_ENABLED = False

from api_watchdog.core import WatchdogTest, Expectation
from api_watchdog.runner import WatchdogRunner
from api_watchdog.validate import ValidationType


class TestWatchdogRunner(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_run_tests(self, mock_urlopen):
        """
        Test run_tests returns correct success parameter for each test
        """

        def get_response_mock(req, body=None):
            mock = MagicMock()
            mock.getcode.return_value = 200

            def mocked_read():
                if body:
                    body_str = body.decode("utf-8")
                    if body_str:
                        data = json.loads(body_str)
                
                    return json.dumps(
                        {
                            "magic_number": 0xFEEDFACE ^ int(data["magic_number"]),
                        }
                    ).encode("utf-8")
                return json.dumps(
                    {
                        "empty_body": True,
                    }
                ).encode("utf-8")

            mock.read.side_effect = mocked_read
            mock.info.return_value.get_content_charset.return_value = "utf-8"
            return mock

        mock_urlopen.side_effect = get_response_mock

        tests = [
            WatchdogTest(
                name="Bad Coffee",
                target="http://test.com",
                payload={"magic_number": 0xBADC0FFEE},
                expectations=[
                    Expectation(selector=".magic_number", value=-1, validation_type=ValidationType.Int) # incorrect value
                ]
            ),
            WatchdogTest(
                name="Bad Food",
                target="http://test.com",
                payload={"magic_number": 0xBADF00D},
                expectations=[
                    Expectation(selector=".magic_number", value=0xFEEDFACE^0xBADF00D, validation_type=ValidationType.Int) # incorrect value
                ]
            ),
            WatchdogTest(
                name="Feed Face",
                target="http://test.com",
                payload={"magic_number": 0xFEEDFACE},
                expectations=[
                    Expectation(selector=".magic_number", value=0, validation_type=ValidationType.Int) # incorrect value
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
        
        print(results)

        self.assertFalse(results[0].success)
        self.assertTrue(results[1].success)
        self.assertTrue(results[2].success)
        self.assertTrue(results[3].success)

    @unittest.skipIf(not TRAPI_ENABLED, TRAPI_SKIP_MESSAGE)
    @patch("urllib.request.urlopen")
    def test_run_tests_trapi_validation(self, mock_urlopen):
        """
        Test run_tests returns correct success parameter for each test when
        there payload and expectation are TRAPI validated
        """

        def get_response_mock(req, body):
            mock = MagicMock()
            mock.getcode.return_value = 200

            def mocked_read():
                data = json.loads(body.decode("utf-8"))
                magic_number = list(data["query_graph"]["nodes"].keys())[0]
                magic_number = 0xFEEDFACE ^ int(magic_number, 16)
                return json.dumps(
                    {
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
                ).encode("utf-8")

            mock.read.side_effect = mocked_read
            mock.info.return_value.get_content_charset.return_value = "utf-8"
            return mock

        mock_urlopen.side_effect = get_response_mock

        tests = [
            WatchdogTest(
                name="Bad Coffee",
                target="http://test.com",
                payload=reasoner_pydantic.message.Message(
                    query_graph=reasoner_pydantic.QueryGraph(
                        nodes = {"BADC0FFEE": reasoner_pydantic.QNode()},
                        edges = {}
                    ),
                    knowledge_graph=reasoner_pydantic.KnowledgeGraph(
                        nodes={},
                        edges={}
                    )
                ),
                expectations = [
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
                                    score = -1
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
                        nodes = {"BADF00D": reasoner_pydantic.QNode()},
                        edges = {}
                    ),
                    knowledge_graph=reasoner_pydantic.KnowledgeGraph(
                        nodes={},
                        edges={}
                    )
                ),
                expectations = [
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
                                    score = 0xFEEDFACE ^ 0xBADF00D
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
                        nodes = {"FEEDFACE": reasoner_pydantic.QNode()},
                        edges = {}
                    ),
                    knowledge_graph=reasoner_pydantic.KnowledgeGraph(
                        nodes={},
                        edges={}
                    )
                ),
                expectations = [
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
                                    score = 0
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
