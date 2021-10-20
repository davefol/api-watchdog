import io
import os
from pathlib import Path
import json
import shutil
import unittest
from unittest.mock import patch, MagicMock

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
                "expectation": {"val": 2}
            }
            """
        )
        (self.base_path / "2.watchdog.json").write_text(
            """
            {
                "name": "2",
                "target": "http://a.com/b",
                "payload": {"val": 2},
                "expectation": {"val": 3}
            }
            """
        )
        (self.base_path / "3.watchdog.json").write_text(
            """
            {
                "name": "3",
                "target": "http://a.com/c",
                "payload": {"val": 3},
                "expectation": {"val": 4}
            }
            """
        )


    @patch("time.time", MagicMock(return_value=0.0))
    @patch("sys.stdout", new_callable=io.StringIO)
    @patch("urllib.request.urlopen")
    def test_discover_print_to_stdout(self, mock_urlopen, mock_stdout):
        """
        Test that discover finds finds and prints
        them to stdout
        """
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
        mocked_args.search_directory = self.base_path
        mocked_args.pattern = "*.watchdog.json"
        mocked_args.output_path = None

        discover(mocked_args)
        expectation = (
            f"{1:<20} Pass {0.0:<12.3f}\n"
            f"{2:<20} Pass {0.0:<12.3f}\n"
            f"{3:<20} Pass {0.0:<12.3f}\n"
        )
        self.assertEqual(expectation, mock_stdout.getvalue())

if __name__ == "__main__":
    unittest.main()
