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
from typing import Set
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class VisibilityFilter(BaseFilter, filter_name="visibility"):
    def __init__(self, options: Set[str]):
        super().__init__()
        self.options = options

    @classmethod
    def from_section(cls, section: SectionProxy) -> "BaseFilter":
        return cls(set(section["options"].split()))

    def __call__(self, status: Status) -> bool:
        return status.visibility in self.options

    def __repr__(self):
        return str.format("Filter:{}({})", self.filter_name, self.options)
