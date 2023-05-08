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
from typing import Literal, Set
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class MediaFilter(BaseFilter, filter_name="media"):
    def __init__(
        self,
        valid_media: Set[str],
        mode: Literal["include", "exclude", "only"],
    ):
        super().__init__()
        self.valid_media: Set[str] = valid_media
        self.mode = mode
        assert self.mode in ("include", "exclude", "only")

    @classmethod
    def from_section(cls, section: SectionProxy) -> "MediaFilter":
        return cls(
            valid_media=set(section["valid_media"].split()),
            mode=section.get("mode", "include"),  # type: ignore
        )

    def __call__(self, status: Status) -> bool:
        if not status.media_attachments:
            return False

        types: Set[str] = {a.type for a in status.media_attachments}

        if self.mode == "include":
            return len(types & self.valid_media) > 0
        elif self.mode == "exclude":
            return len(types & self.valid_media) == 0
        elif self.mode == "only":
            return len((types ^ self.valid_media) & types) == 0
        raise ValueError(f"{self.mode=} is not valid")

    def __repr__(self):
        return str.format(
            "Filter:{name}(mode={mode}, media={media})",
            name=self.filter_name,
            mode=self.mode,
            media=self.valid_media,
        )
