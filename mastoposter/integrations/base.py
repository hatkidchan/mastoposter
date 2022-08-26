from abc import ABC, abstractmethod
from typing import Optional

from mastoposter.types import Status


class BaseIntegration(ABC):
    def __init__(self):
        pass

    @abstractmethod
    async def post(self, status: Status) -> Optional[str]:
        raise NotImplemented
