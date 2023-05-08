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
from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional


def _f(func: Callable, v: Optional[Any], *a, **kw) -> Any:
    return func(v, *a, **kw) if v is not None else None


__all__ = (
    "DiscordEmbed",
    "DiscordEmbedFooter",
    "DiscordEmbedImage",
    "DiscordEmbedThumbnail",
    "DiscordEmbedAuthor",
    "DiscordEmbedField",
)


@dataclass
class DiscordEmbedFooter:
    text: str
    icon_url: Optional[str]


@dataclass
class DiscordEmbedImage:
    url: str
    width: int = 0
    height: int = 0


@dataclass
class DiscordEmbedThumbnail:
    url: str


@dataclass
class DiscordEmbedAuthor:
    name: str
    url: Optional[str] = None
    icon_url: Optional[str] = None


@dataclass
class DiscordEmbedField:
    name: str
    value: str
    inline: Optional[bool]


@dataclass
class DiscordEmbed:
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    timestamp: Optional[datetime] = None
    color: Optional[int] = None
    footer: Optional[DiscordEmbedFooter] = None
    image: Optional[DiscordEmbedImage] = None
    thumbnail: Optional[DiscordEmbedThumbnail] = None
    author: Optional[DiscordEmbedAuthor] = None
    fields: Optional[List[DiscordEmbedField]] = None

    def asdict(self) -> Dict[str, Any]:
        return {
            "type": "rich",
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "timestamp": _f(
                datetime.isoformat, self.timestamp, "T", "seconds"
            ),
            "color": self.color,
            "footer": _f(asdict, self.footer),
            "image": _f(asdict, self.image),
            "thumbnail": _f(asdict, self.thumbnail),
            "author": _f(asdict, self.author),
            "fields": _f(lambda v: list(map(asdict, v)), self.fields),
        }
