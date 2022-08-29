from configparser import SectionProxy
from re import Pattern, compile as regexp
from typing import ClassVar
from fnmatch import fnmatch
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class MentionFilter(BaseFilter, filter_name="mention"):
    MENTION_REGEX: ClassVar[Pattern] = regexp(r"@([^@]+)(@([^@]+))?")

    def __init__(self, section: SectionProxy):
        super().__init__(section)
        self.list = section.get("list", "").split()

    @classmethod
    def check_account(cls, acct: str, mask: str):
        return fnmatch(acct, mask)

    def __call__(self, status: Status) -> bool:
        if not self.list and status.mentions:
            return True
        return any(
            (
                any(
                    self.check_account(mention.acct, mask)
                    for mask in self.list
                )
                for mention in status.mentions
            )
        )

    def __repr__(self):
        return str.format(
            "Filter:{name}({list!r})", name=self.filter_name, list=self.list
        )
