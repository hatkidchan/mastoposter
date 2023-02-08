from configparser import SectionProxy
from re import Pattern, compile as regexp
from typing import Optional, Set

from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class TextFilter(BaseFilter, filter_name="content"):
    def __init__(
        self, regex: Optional[str] = None, tags: Optional[Set[str]] = None
    ):
        super().__init__()
        assert regex is not None or tags

        self.tags: Optional[Set[str]] = tags
        self.regexp: Optional[Pattern] = regexp(regex) if regex else None

    @classmethod
    def from_section(cls, section: SectionProxy) -> "TextFilter":
        if "regexp" in section and "tags" in section:
            raise AssertionError("you can't use both tags and regexp")
        elif "regexp" in section:
            return cls(regex=section["regexp"])
        elif "tags" in section:
            return cls(tags=set(section["tags"].split()))
        raise AssertionError("neither regexp or tags were set")

    def __call__(self, status: Status) -> bool:
        source = status.reblog or status
        if self.regexp is not None:
            return self.regexp.search(source.content_plaintext) is not None
        elif self.tags:
            return len(self.tags & {t.name.lower() for t in source.tags}) > 0
        else:
            raise ValueError("Neither regexp or tags were set. Why?")

    def __repr__(self):
        if self.regexp is not None:
            return str.format(
                "Filter:{name}(regexp={regex!r})",
                name=self.filter_name,
                regex=self.regexp.pattern,
            )
        elif self.tags:
            return str.format(
                "Filter:{name}(tags={tags!r})",
                name=self.filter_name,
                tags=self.tags,
            )
        return "Filter:{name}(invalid)".format(name=self.filter_name)
