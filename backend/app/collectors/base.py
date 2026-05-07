from abc import ABC, abstractmethod


class BaseCollector(ABC):
    name: str

    @abstractmethod
    def collect(self):
        raise NotImplementedError
