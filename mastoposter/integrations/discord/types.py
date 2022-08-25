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
            "timestamp": _f(datetime.isoformat, self.timestamp, "T", "seconds"),
            "color": self.color,
            "footer": _f(asdict, self.footer),
            "image": _f(asdict, self.image),
            "thumbnail": _f(asdict, self.thumbnail),
            "author": _f(asdict, self.author),
            "fields": _f(lambda v: list(map(asdict, v)), self.fields),
        }
