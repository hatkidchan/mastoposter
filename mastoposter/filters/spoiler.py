from configparser import SectionProxy
from re import Pattern, compile as regexp
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class SpoilerFilter(BaseFilter, filter_name="spoiler"):
    def __init__(self, regex: str = "^.*$"):
        super().__init__()
        self.regexp: Pattern = regexp(regex)

    @classmethod
    def from_section(cls, section: SectionProxy) -> "SpoilerFilter":
        return cls(section.get("regexp", section.get("regex", "^.*$")))

    def __call__(self, status: Status) -> bool:
        return self.regexp.match(status.spoiler_text) is not None

    def __repr__(self):
        return str.format(
            "Filter:{name}({regex!r})",
            name=self.filter_name,
            regex=self.regexp.pattern,
        )
