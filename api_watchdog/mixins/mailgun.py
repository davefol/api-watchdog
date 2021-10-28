import base64
import os
from typing import Optional
import urllib.parse
import urllib.request

class MailgunMixin:
    """
    Mixing that allows a class to send an email
    """
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
        data = urllib.parse.urlencode(
            {
                "from": self.from_address,
                "to": to,
                "subject": subject,
                "text": text,
            }
        ).encode("ascii")
        self._send_data(data)

    def send_html_email(self, to: str, subject: str, html: str):
        data = urllib.parse.urlencode(
            {
                "from": self.from_address,
                "to": to,
                "subject": subject,
                "html": html,
            }
        ).encode("ascii")
        self._send_data(data)

    def _send_data(self, data):
        request = urllib.request.Request(self.url, data=data)
        request.add_header("Content-Type", "application/x-www-form-urlencoded")
        encoded_token = base64.b64encode(
            ("api:" + self.token).encode("ascii")
        ).decode("ascii")
        request.add_header("Authorization", "Basic {}".format(encoded_token))
        response = urllib.request.urlopen(request)
        return response

