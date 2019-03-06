from abc import ABC, abstractmethod

from typing import List


class MetricNamer(ABC):
    @abstractmethod
    def __call__(self, scope) -> str:
        pass


class TimingClient(ABC):
    """ An abstract class detailing the client interface """
    @abstractmethod
    def timing(self, metric_name: str, timing: float, tags: List[str]):
        pass
