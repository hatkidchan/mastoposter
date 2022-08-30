from configparser import SectionProxy
from fnmatch import fnmatch
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class BoostFilter(BaseFilter, filter_name="boost"):
    def __init__(self, section: SectionProxy):
        super().__init__(section)
        self.list = section.get("list", "").split()

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
