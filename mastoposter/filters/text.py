from configparser import SectionProxy
from re import Pattern, compile as regexp
from typing import Optional, Set

from bs4 import BeautifulSoup, PageElement, Tag
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class TextFilter(BaseFilter, filter_name="content"):
    def __init__(self, section: SectionProxy):
        super().__init__(section)
        self.mode = section["mode"]
        self.tags: Set[str] = set()
        self.regexp: Optional[Pattern] = None

        if self.mode == "regexp":
            self.regexp = regexp(section["regexp"])
        elif self.mode in ("hashtag", "tag"):
            self.tags = set(section["tags"].split())
        else:
            raise ValueError(f"Invalid filter mode {self.mode}")

    @classmethod
    def node_to_text(cls, el: PageElement) -> str:
        if isinstance(el, Tag):
            if el.name == "br":
                return "\n"
            elif el.name == "p":
                return (
                    str.join("", map(cls.node_to_text, el.children)) + "\n\n"
                )
            return str.join("", map(cls.node_to_text, el.children))
        return str(el)

    @classmethod
    def html_to_plain(cls, html: str) -> str:
        soup = BeautifulSoup(html, "lxml")
        return cls.node_to_text(soup).rstrip()

    def __call__(self, status: Status) -> bool:
        source = status.reblog or status
        if self.regexp is not None:
            return (
                self.regexp.match(self.html_to_plain(source.content))
                is not None
            )
        elif self.tags:
            print(f"{self.tags=} {source.tags=}")
            return len(self.tags & {t.name for t in source.tags}) > 0
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
