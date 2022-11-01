from abc import ABC, abstractmethod
from configparser import SectionProxy
from typing import Optional

from mastoposter.types import Status


class BaseIntegration(ABC):
    # TODO: make a registry of integrations
    def __init__(self):
        pass

    @classmethod
    def from_section(cls, section: SectionProxy) -> "BaseIntegration":
        raise NotImplementedError

    @abstractmethod
    async def __call__(self, status: Status) -> Optional[str]:
        raise NotImplementedError
