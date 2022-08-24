from abc import ABC, abstractmethod

from mastoreposter.types import Status


class BaseIntegration(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def post(self, status: Status) -> str:
        raise NotImplemented
