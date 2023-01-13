import io
import logging
import os
from typing import Optional, Dict, Tuple, Literal, List

import requests

logger = logging.getLogger(__name__)

class MailgunMixin:
    """Mixin that allows a class to send an email."""

    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        from_address: Optional[str] = None,
    ):
        self.url = url or os.environ["MAILGUN_API_URL"]
        self.token = token or os.environ["MAILGUN_API_TOKEN"]
        self.from_address = from_address or os.environ["MAILGUN_FROM"]

    def send_text_email(self, to: str, subject: str, text: str):
        data = {
                "from": self.from_address,
                "to": to,
                "subject": subject,
                "text": text,
            }
        return self._send_data(data)

    def send_html_email(self, to: str, subject: str, html: str):
        data = {
                "from": self.from_address,
                "to": to,
                "subject": subject,
                "html": html,
            }
        return self._send_data(data)

    def _send_data(self, data):
        logger.info(f"Sending request to {self.url}")
        response = requests.post(
            self.url,
            auth=("api", self.token),
            data=data,
            timeout=60,
        )
        logger.info(f"Got response from {self.url}: {response.json()}")
        return response
