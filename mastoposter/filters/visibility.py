from configparser import SectionProxy
from typing import Set
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class VisibilityFilter(BaseFilter, filter_name="visibility"):
    def __init__(self, options: Set[str]):
        super().__init__()
        self.options = options

    @classmethod
    def from_section(cls, section: SectionProxy) -> "BaseFilter":
        return cls(set(section["options"].split()))

    def __call__(self, status: Status) -> bool:
        return status.visibility in self.options

    def __repr__(self):
        return str.format("Filter:{}({})", self.filter_name, self.options)
