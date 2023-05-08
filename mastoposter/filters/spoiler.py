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
