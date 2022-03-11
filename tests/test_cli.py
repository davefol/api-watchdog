import io
import os
from pathlib import Path
import json
import shutil
import unittest
from unittest.mock import patch, MagicMock, mock_open

from api_watchdog.cli import discover


class TestCli(unittest.TestCase):
    def setUp(self):

        self.base_path = Path(f"test_{os.getpid()}_tmp")
        os.mkdir(self.base_path)

        def cleanup():
            shutil.rmtree(self.base_path)
        self.addCleanup(cleanup)

        (self.base_path / "1.watchdog.json").write_text(
            """
            {
                "name": "1",
                "target": "http://a.com/",
                "payload": {"val": 1},
                "expectations": [
                    {
                        "selector": ".val",
                        "value": 2,
                        "validation_type": "int"
                    }
                ]
            }
            """
        )
        (self.base_path / "2.watchdog.json").write_text(
            """
            {
                "name": "2",
                "target": "http://a.com/b",
                "payload": {"val": 2},
                "expectations": [
                    {
                        "selector": ".val",
                        "value": 3,
                        "validation_type": "int"
                    }
                ]
            }
            """
        )
        (self.base_path / "3.watchdog.json").write_text(
            """
            {
                "name": "3",
                "target": "http://a.com/c",
                "payload": {"val": 3},
                "expectations": [
                    {
                        "selector": ".val",
                        "value": 4,
                        "validation_type": "int"
                    }
                ]
            }
            """
        )

    @patch("time.time", MagicMock(return_value=0.0))
    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("urllib.request.urlopen")
    def test_discover_print_to_stdout(self, mock_urlopen, mock_stdout):
        """Test that discover finds finds and prints them to stdout."""
        def get_response_mock(req, body):
            mock = MagicMock()
            mock.getcode.return_value = 200

            def mocked_read():
                data = json.loads(body.decode("utf-8"))
                return json.dumps(
                    {"val": data["val"] + 1}
                ).encode("utf-8")

            mock.read.side_effect = mocked_read
            mock.info.return_value.get_content_charset.return_value = "utf-8"
            return mock

        mock_urlopen.side_effect = get_response_mock
        mocked_args = MagicMock()
        vars(mocked_args)["search-directory"] = self.base_path
        mocked_args.pattern = "*.watchdog.json"
        mocked_args.output_path = None
        mocked_args.email = False

        discover(mocked_args)
        expectation = (
            f"{1:<20} Pass {0.0:<12.3f}\n"
            f"{2:<20} Pass {0.0:<12.3f}\n"
            f"{3:<20} Pass {0.0:<12.3f}\n"
        )
        self.assertEqual(expectation, mock_stdout.getvalue())

    @patch("time.time", MagicMock(return_value=0.0))
    @patch("builtins.open", new_callable=mock_open)
    @patch("urllib.request.urlopen")
    def test_discover_write_to_file(self, mock_urlopen, mock_stdout):
        """Test that discover finds finds and writes them to file."""
        def get_response_mock(req, body):
            mock = MagicMock()
            mock.getcode.return_value = 200

            def mocked_read():
                data = json.loads(body.decode("utf-8"))
                return json.dumps(
                    {"val": data["val"] + 1}
                ).encode("utf-8")

            mock.read.side_effect = mocked_read
            mock.info.return_value.get_content_charset.return_value = "utf-8"
            return mock


        mock_urlopen.side_effect = get_response_mock
        mocked_args = MagicMock()
        vars(mocked_args)["search-directory"] = self.base_path
        mocked_args.pattern = "*.watchdog.json"
        mocked_args.output_path = "some/random/path.json"
        mocked_args.email = False

        discover(mocked_args)

        expected = """
        {
          "name": "<root>",
          "results": [],
          "groups": [
            {
              "name": "http://a.com",
              "results": [
                {
                  "test_name": "1",
                  "target": "http://a.com/",
                  "success": true,
                  "latency": 0.0,
                  "timestamp": "1970-01-01T00:00:00+00:00",
                  "email_to": null,
                  "payload": {
                    "val": 1
                  },
                  "response": {
                    "val": 2
                  },
                  "results": [
                    {
                      "expectation": {
                        "selector": ".val",
                        "value": 2,
                        "validation_type": "int",
                        "level": "critical"
                      },
                      "result": "success",
                      "actual": 2
                    }
                  ]
                }
              ],
              "groups": [
                {
                  "name": "http://a.com/b",
                  "results": [
                    {
                      "test_name": "2",
                      "target": "http://a.com/b",
                      "success": true,
                      "latency": 0.0,
                      "timestamp": "1970-01-01T00:00:00+00:00",
                      "email_to": null,
                      "payload": {
                        "val": 2
                      },
                      "response": {
                        "val": 3
                      },
                      "results": [
                        {
                          "expectation": {
                            "selector": ".val",
                            "value": 3,
                            "validation_type": "int",
                            "level": "critical"
                          },
                          "result": "success",
                          "actual": 3
                        }
                      ]
                    }
                  ],
                  "groups": []
                },
                {
                  "name": "http://a.com/c",
                  "results": [
                    {
                      "test_name": "3",
                      "target": "http://a.com/c",
                      "success": true,
                      "latency": 0.0,
                      "timestamp": "1970-01-01T00:00:00+00:00",
                      "email_to": null,
                      "payload": {
                        "val": 3
                      },
                      "response": {
                        "val": 4
                      },
                      "results": [
                        {
                          "expectation": {
                            "selector": ".val",
                            "value": 4,
                            "validation_type": "int",
                            "level": "critical"
                          },
                          "result": "success",
                          "actual": 4
                        }
                      ]
                    }
                  ],
                  "groups": []
                }
              ]
            }
          ]
        }
        """
        mock_stdout.assert_called_once_with("some/random/path.json", "w")
        self.assertEqual(json.loads(mock_stdout().write.mock_calls[0][1][0]), json.loads(expected))


if __name__ == "__main__":
    unittest.main()
