import copy
import io
import time
from typing import Optional, Callable, Set, List

from api_watchdog.collect import WatchdogResultGroup
from api_watchdog.mixins.mailgun import MailgunMixin
from api_watchdog.hooks.result_group.abstract import ResultGroupHook
from api_watchdog.formatters.result_group_html import html_from_result_group


def filter_result_group(
    result_group: WatchdogResultGroup, filter_fn: Callable
) -> WatchdogResultGroup:
    result_group = copy.deepcopy(result_group)

    def recursive_filter(
        result_group: WatchdogResultGroup, filter_fn: Callable
    ):
        result_group.results = list(filter(filter_fn, result_group.results))
        for group in sorted(result_group.groups, key=lambda g: g.name):
            recursive_filter(group, filter_fn)
        result_group.groups = list(
            filter(
                lambda g: len(g.results) > 0 or len(g.groups) > 0,
                result_group.groups,
            )
        )

    recursive_filter(result_group, filter_fn)
    return result_group


def email_receivers(result_group) -> List[str]:
    def recursive_receivers(result_group: WatchdogResultGroup) -> Set[str]:
        receivers = set()
        for result in result_group.results:
            if result.email_to:
                receivers.update(result.email_to)
        for group in result_group.groups:
            receivers.update(recursive_receivers(group))
        return receivers

    return sorted(recursive_receivers(result_group))


class ResultGroupHookMailgun(MailgunMixin, ResultGroupHook):
    def __init__(
        self,
        url: Optional[str] = None,
        token: Optional[str] = None,
        from_address: Optional[str] = None,
    ):
        MailgunMixin.__init__(self, url, token, from_address)
        ResultGroupHook.__init__(self)

    def __call__(self, result_group: WatchdogResultGroup):
        receivers = email_receivers(result_group)
        subject = "Watchdog Result Summary"
        result_group_bytes = io.BytesIO(result_group.json().encode("utf-8"))
        result_group_bytes.name = f"{int(time.time())}_results.json"
        for receiver in receivers:
            to = receiver
            filtered_result_group = filter_result_group(
                result_group, lambda r: receiver in (r.email_to or [])
            )
            self.send_html_email(
                to=to,
                subject=subject,
                html=html_from_result_group(filtered_result_group),
                attachments=[("attachment", result_group_bytes)]
            )
            result_group_bytes.seek(0)
