from configparser import SectionProxy
from fnmatch import fnmatch
from typing import List
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class BoostFilter(BaseFilter, filter_name="boost"):
    def __init__(self, accounts: List[str]):
        super().__init__()
        self.list = accounts

    @classmethod
    def from_section(cls, section: SectionProxy) -> "BoostFilter":
        return cls(section["list"].split())

    @classmethod
    def check_account(cls, acct: str, mask: str) -> bool:
        return fnmatch(acct, mask)

    def __call__(self, status: Status) -> bool:
        if status.reblog is None:
            return False
        if not self.list:
            return True
        return any(
            [
                self.check_account("@" + status.reblog.account.acct, mask)
                for mask in self.list
            ]
        )

    def __repr__(self):
        if not self.list:
            return "Filter:boost(any)"
        return f"Filter:boost(from={self.list!r})"
