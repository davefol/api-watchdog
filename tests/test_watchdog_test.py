import unittest

from api_watchdog.core import WatchdogTest
from api_watchdog.integrations.trapi import TrapiMessage

TRAPI_SKIP_MESSAGE = "TRAPI exentsion not installed"
try:
    import reasoner_pydantic

    TRAPI_ENABLED = True
except ImportError:
    TRAPI_ENABLED = False


class TestWatchdog(unittest.TestCase):
    @unittest.skipIf(not TRAPI_ENABLED, TRAPI_SKIP_MESSAGE)
    def test_instantiate_trapi_validated_payload(self):
        """
        Test that a WatchdogTest with a TRAPI validated payload can be
        instantiated
        """
        test = WatchdogTest(
            name="",
            target="http://test.com",
            validate_payload="TRAPI",
            payload=TrapiMessage(),
            expectation={},
        )
        self.assertEqual(test.name, "")
        self.assertEqual(test.target, "http://test.com")
        self.assertEqual(test.payload, TrapiMessage())
        self.assertEqual(test.validate_payload, "TRAPI")
        self.assertEqual(test.expectation, {})
        self.assertEqual(test.validate_expectation, None)

    @unittest.skipIf(not TRAPI_ENABLED, TRAPI_SKIP_MESSAGE)
    def test_parse_trapi_validate_payload_from_json(self):
        """
        Test parsing loading a WatchdogTest from json with TRAPI validated
        payload
        """
        test = WatchdogTest.parse_raw(
            """
            {
                "name": "",
                "target": "http://test.com",
                "validate_payload": "TRAPI",
                "payload": {},
                "expectation": {}
            }
        """
        )
        self.assertEqual(test.name, "")
        self.assertEqual(test.target, "http://test.com")
        self.assertEqual(test.payload, TrapiMessage())
        self.assertEqual(test.validate_payload, "TRAPI")
        self.assertEqual(test.expectation, {})
        self.assertEqual(test.validate_expectation, None)

    @unittest.skipIf(not TRAPI_ENABLED, TRAPI_SKIP_MESSAGE)
    def test_instantiate_trapi_validated_expectation(self):
        """
        Test that a WatchdogTest with a TRAPI validated payload can
        be instantiated
        """
        test = WatchdogTest(
            name="",
            target="http://test.com",
            payload={},
            validate_expectation="TRAPI",
            expectation=TrapiMessage(),
        )
        self.assertEqual(test.name, "")
        self.assertEqual(test.target, "http://test.com")
        self.assertEqual(test.payload, {})
        self.assertEqual(test.validate_payload, None)
        self.assertEqual(test.expectation, TrapiMessage())
        self.assertEqual(test.validate_expectation, "TRAPI")

    @unittest.skipIf(not TRAPI_ENABLED, TRAPI_SKIP_MESSAGE)
    def test_parse_trapi_validate_expectation_from_json(self):
        """
        Test parsing loading WatchdogTest from json with TRAPI validated
        expectation
        """
        test = WatchdogTest.parse_raw(
            """
            {
                "name": "",
                "target": "http://test.com",
                "validate_expectation": "TRAPI",
                "payload": {},
                "expectation": {}
            }
        """
        )
        self.assertEqual(test.name, "")
        self.assertEqual(test.target, "http://test.com")
        self.assertEqual(test.payload, {})
        self.assertEqual(test.validate_payload, None)
        self.assertEqual(test.expectation, TrapiMessage())
        self.assertEqual(test.validate_expectation, "TRAPI")

    def test_validate_expectation_unknown_raises_err(self):
        """
        Test that using an unknown validation type raises an error
        """
        with self.assertRaises(ValueError):
            WatchdogTest.parse_raw(
                """
                {
                    "name": "",
                    "target": "http://test.com",
                    "validate_expectation": "Exotic Type",
                    "payload": {},
                    "expectation: {},
                }
                """
            )

    def test_validate_payload_unknown_raises_err(self):
        """
        Test that using an unknown validation type raises an error
        """
        with self.assertRaises(ValueError):
            WatchdogTest.parse_raw(
                """
                {
                    "name": "",
                    "target": "http://test.com",
                    "validate_payload": "Exotic Type",
                    "payload": {},
                    "expectation: {},
                }
                """
            )


if __name__ == "__main__":
    unittest.main()
