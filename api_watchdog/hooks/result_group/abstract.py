from abc import ABC, abstractmethod

from api_watchdog.collect import WatchdogResultGroup


class ResultGroupHook(ABC):
    """Abstract class for handling post run result group processing."""

    @abstractmethod
    def __call__(self, result_group: WatchdogResultGroup):
        raise NotImplementedError
