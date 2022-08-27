from abc import ABC, abstractmethod
from configparser import SectionProxy
from typing import Optional

from mastoposter.types import Status


class BaseIntegration(ABC):
    def __init__(self, section: SectionProxy):
        pass

    @abstractmethod
    async def post(self, status: Status) -> Optional[str]:
        raise NotImplementedError
