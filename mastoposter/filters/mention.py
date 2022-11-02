from configparser import SectionProxy
from re import Pattern, compile as regexp
from typing import ClassVar, Set
from fnmatch import fnmatch
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class MentionFilter(BaseFilter, filter_name="mention"):
    MENTION_REGEX: ClassVar[Pattern] = regexp(r"@([^@]+)(@([^@]+))?")

    def __init__(self, accounts: Set[str]):
        super().__init__()
        self.accounts = accounts

    @classmethod
    def from_section(cls, section: SectionProxy) -> "MentionFilter":
        return cls(set(section.get("list", "").split()))

    @classmethod
    def check_account(cls, acct: str, mask: str) -> bool:
        return fnmatch("@" + acct, mask)

    def __call__(self, status: Status) -> bool:
        if not self.accounts and status.mentions:
            return True
        # XXX: make it better somehow. and faster. and stronger.
        return any(
            (
                any(
                    self.check_account(mention.acct, mask)
                    for mask in self.accounts
                )
                for mention in status.mentions
            )
        )

    def __repr__(self):
        return str.format(
            "Filter:{name}({list!r})",
            name=self.filter_name,
            list=self.accounts,
        )
