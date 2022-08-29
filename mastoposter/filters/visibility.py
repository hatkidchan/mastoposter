from configparser import SectionProxy
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class VisibilityFilter(BaseFilter, filter_name="visibility"):
    def __init__(self, section: SectionProxy):
        super().__init__(section)
        self.options = set(section["options"].split())

    def __call__(self, status: Status) -> bool:
        return status.visibility in self.options

    def __repr__(self):
        return str.format("Filter:{}({})", self.filter_name, self.options)
