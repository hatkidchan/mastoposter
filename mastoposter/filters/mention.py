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
