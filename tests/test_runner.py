import json
import unittest
from unittest.mock import patch, MagicMock

TRAPI_SKIP_MESSAGE = "TRAPI exentsion not installed"
try:
    import reasoner_pydantic

    TRAPI_ENABLED = True
except ImportError:
    TRAPI_ENABLED = False

from api_watchdog.core import WatchdogTest
from api_watchdog.runner import WatchdogRunner


class TestWatchdogRunner(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_run_tests_no_validation(self, mock_urlopen):
        """
        Test run_tests returns correct success parameter for each test when
        there is no validation
        """

        def get_response_mock(req, body):
            mock = MagicMock()
            mock.getcode.return_value = 200

            def mocked_read():
                data = json.loads(body.decode("utf-8"))
                return json.dumps(
                    {"magic_number": 0xFEEDFACE ^ int(data["magic_number"])}
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
                expectation={"magic_number": -1},  # incorrrect value
            ),
            WatchdogTest(
                name="Bad Food",
                target="http://test.com",
                payload={"magic_number": 0xBADF00D},
                expectation={"magic_number": 0xFEEDFACE ^ 0xBADF00D},  # correct
            ),
            WatchdogTest(
                name="Feed Face",
                target="http://test.com",
                payload={"magic_number": 0xFEEDFACE},
                expectation={"magic_number": 0},  # correct
            ),
        ]

        runner = WatchdogRunner()
        results = sorted(runner.run_tests(tests), key=lambda x: x.test.name)
        self.assertFalse(results[0].success)
        self.assertTrue(results[1].success)
        self.assertTrue(results[2].success)

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
                        "results": [
                            {
                                "node_bindings": {},
                                "edge_bindings": {},
                                "score": magic_number
                            }
                        ]
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
                expectation=reasoner_pydantic.message.Message(
                    results=[
                        reasoner_pydantic.Result(
                            node_bindings={},
                            edge_bindings={},
                            score = -1
                        )
                    ]
                ),
                validate_payload="TRAPI",
                validate_expectation="TRAPI"
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
                expectation=reasoner_pydantic.message.Message(
                    results=[
                        reasoner_pydantic.Result(
                            node_bindings={},
                            edge_bindings={},
                            score = 0xFEEDFACE ^ 0xBADF00D
                        )
                    ]
                ),
                validate_payload="TRAPI",
                validate_expectation="TRAPI"
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
                expectation=reasoner_pydantic.message.Message(
                    results=[
                        reasoner_pydantic.Result(
                            node_bindings={},
                            edge_bindings={},
                            score = 0
                        )
                    ]
                ),
                validate_payload="TRAPI",
                validate_expectation="TRAPI"
            ),
        ]

        runner = WatchdogRunner()
        results = sorted(runner.run_tests(tests), key=lambda x: x.test.name)
        self.assertFalse(results[0].success)
        self.assertTrue(results[1].success)
        self.assertTrue(results[2].success)

if __name__ == "__main__":
    unittest.main()
