from configparser import SectionProxy
from re import Pattern, compile as regexp
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class SpoilerFilter(BaseFilter, filter_name="spoiler"):
    def __init__(self, section: SectionProxy):
        super().__init__(section)
        self.regexp: Pattern = regexp(section["regexp"])

    def __call__(self, status: Status) -> bool:
        return self.regexp.match(status.spoiler_text) is not None
