"""
mastoposter - configurable reposter from Mastodon-compatible Fediverse servers
Copyright (C) 2022-2023 hatkidchan <hatkidchan@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.
"""
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
