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
from dataclasses import dataclass, field, fields
from datetime import datetime
from typing import Any, Callable, Optional, List, Literal, TypeVar

from bs4 import BeautifulSoup

from mastoposter.utils import node_to_html, node_to_markdown, node_to_plaintext


def _date(val: str) -> datetime:
    return datetime.fromisoformat(val.rstrip("Z"))


T = TypeVar("T")


def _fnil(fn: Callable[[Any], T], val: Optional[Any]) -> Optional[T]:
    return None if val is None else fn(val)


def _date_or_none(val: Optional[str]) -> Optional[datetime]:
    return _fnil(_date, val)


def _int_or_none(val: Optional[str]) -> Optional[int]:
    return _fnil(int, val)


@dataclass
class Field:
    name: str
    value: str
    verified_at: Optional[datetime] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Field":
        return cls(
            name=data["name"],
            value=data["value"],
            verified_at=_date_or_none(data.get("verified_at")),
        )


@dataclass
class Emoji:
    shortcode: str
    url: str
    static_url: str
    visible_in_picker: bool
    category: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Emoji":
        return cls(
            **{f.name: data[f.name] for f in fields(cls) if f.name in data}
        )


@dataclass
class Account:
    id: str
    username: str
    acct: str
    url: str
    display_name: str
    note: str
    avatar: str
    avatar_static: str
    header: str
    header_static: str
    locked: bool
    emojis: List[Emoji]
    discoverable: bool
    created_at: datetime
    last_status_at: Optional[datetime]
    statuses_count: int
    followers_count: int
    following_count: int
    moved: Optional["Account"] = None
    fields: Optional[List[Field]] = None
    bot: Optional[bool] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Account":
        return cls(
            id=data["id"],
            username=data["username"],
            acct=data["acct"],
            url=data["url"],
            display_name=data["display_name"],
            note=data["note"],
            avatar=data["avatar"],
            avatar_static=data["avatar_static"],
            header=data["header"],
            header_static=data["header_static"],
            locked=data["locked"],
            emojis=list(map(Emoji.from_dict, data["emojis"])),
            discoverable=data.get("discoverable", False),
            created_at=_date(data["created_at"]),
            last_status_at=_date_or_none(data.get("last_status_at")),
            statuses_count=data["statuses_count"],
            followers_count=data["followers_count"],
            following_count=data["following_count"],
            moved=_fnil(Account.from_dict, data.get("moved")),
            fields=list(map(Field.from_dict, data.get("fields", []))),
            bot=bool(data.get("bot")),
        )

    @property
    def name(self) -> str:
        return self.display_name or self.username

    @property
    def name_emojiless(self) -> str:
        if not self.display_name:
            return self.username
        name = self.display_name
        for emoji in self.emojis:
            name = name.replace(":%s:" % emoji.shortcode, "")
        return name.strip() or self.username


@dataclass
class AttachmentMetaImage:
    @dataclass
    class Vec2F:
        x: float
        y: float

    @dataclass
    class AttachmentMetaImageDimensions:
        width: int
        height: int
        size: str
        aspect: float

    original: AttachmentMetaImageDimensions
    small: AttachmentMetaImageDimensions
    focus: Vec2F

    @classmethod
    def from_dict(cls, data: dict) -> "AttachmentMetaImage":
        return cls(
            **{f.name: data[f.name] for f in fields(cls) if f.name in data},
            original=cls.AttachmentMetaImageDimensions(**data["original"]),
            small=cls.AttachmentMetaImageDimensions(**data["small"]),
            focus=cls.Vec2F(**data["focus"]),
        )


@dataclass
class AttachmentMetaVideo:
    @dataclass
    class AttachmentMetaVideoOriginal:
        width: int
        height: int
        duration: float
        bitrate: int
        frame_rate: Optional[str]  # XXX Gargron wtf?

    @dataclass
    class AttachmentMetaVideoSmall:
        width: int
        height: int
        size: str
        aspect: float

    length: str
    duration: float
    fps: int
    size: str
    width: int
    height: int
    aspect: float
    audio_encode: str
    audio_bitrate: str  # XXX GARGROOOOONNNNNN!!!!!!!
    audio_channels: str  # XXX I HATE YOU
    original: AttachmentMetaVideoOriginal
    small: AttachmentMetaVideoSmall

    @classmethod
    def from_dict(cls, data: dict) -> "AttachmentMetaVideo":
        return cls(
            **data,
            original=cls.AttachmentMetaVideoOriginal(**data["original"]),
            small=cls.AttachmentMetaVideoSmall(**data["small"]),
        )


@dataclass
class Attachment:
    id: str
    type: Literal["unknown", "image", "gifv", "video", "audio"]
    url: str
    preview_url: str
    remote_url: Optional[str] = None
    preview_remote_url: Optional[str] = None
    meta: Optional[dict] = None
    description: Optional[str] = None
    blurhash: Optional[str] = None
    text_url: Optional[str] = None  # XXX: DEPRECATED

    @classmethod
    def from_dict(cls, data: dict) -> "Attachment":
        return cls(
            **{f.name: data[f.name] for f in fields(cls) if f.name in data}
        )


@dataclass
class Application:
    name: str
    website: Optional[str] = None
    vapid_key: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Application":
        return cls(
            **{f.name: data[f.name] for f in fields(cls) if f.name in data}
        )


@dataclass
class Mention:
    id: str
    username: str
    acct: str
    url: str

    @classmethod
    def from_dict(cls, data: dict) -> "Mention":
        return cls(
            **{f.name: data[f.name] for f in fields(cls) if f.name in data}
        )


@dataclass
class Tag:
    name: str
    url: str

    @classmethod
    def from_dict(cls, data: dict) -> "Tag":
        return cls(
            **{f.name: data[f.name] for f in fields(cls) if f.name in data}
        )


@dataclass
class Poll:
    @dataclass
    class PollOption:
        title: str
        votes_count: Optional[int] = None

    id: str
    expires_at: Optional[datetime]
    expired: bool
    multiple: bool
    votes_count: int
    voters_count: Optional[int] = None
    options: List[PollOption] = field(default_factory=list)
    emojis: List[Emoji] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: dict) -> "Poll":
        return cls(
            id=data["id"],
            expires_at=_date_or_none(data.get("expires_at")),
            expired=data["expired"],
            multiple=data["multiple"],
            votes_count=data["votes_count"],
            voters_count=_int_or_none(data.get("voters_count")),
            options=[cls.PollOption(**opt) for opt in data["options"]],
        )


@dataclass
class Status:
    id: str
    uri: str
    created_at: datetime
    account: Account
    content: str
    visibility: Literal["public", "unlisted", "private", "direct"]
    sensitive: bool
    spoiler_text: str
    media_attachments: List[Attachment]
    reblogs_count: int
    favourites_count: int
    replies_count: int
    mentions: List[Mention]
    tags: List[Tag]
    application: Optional[Application] = None
    url: Optional[str] = None
    in_reply_to_id: Optional[str] = None
    in_reply_to_account_id: Optional[str] = None
    reblog: Optional["Status"] = None
    poll: Optional[Poll] = None
    card: Optional[dict] = None
    language: Optional[str] = None
    text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Status":
        return cls(
            id=data["id"],
            uri=data["uri"],
            created_at=_date(data["created_at"]),
            account=Account.from_dict(data["account"]),
            content=data["content"],
            visibility=data["visibility"],
            sensitive=data["sensitive"],
            spoiler_text=data["spoiler_text"],
            media_attachments=list(
                map(Attachment.from_dict, data["media_attachments"])
            ),
            application=_fnil(Application.from_dict, data.get("application")),
            reblogs_count=data["reblogs_count"],
            favourites_count=data["favourites_count"],
            replies_count=data["replies_count"],
            url=data.get("url"),
            in_reply_to_id=data.get("in_reply_to_id"),
            in_reply_to_account_id=data.get("in_reply_to_account_id"),
            reblog=_fnil(Status.from_dict, data.get("reblog")),
            poll=_fnil(Poll.from_dict, data.get("poll")),
            card=data.get("card"),
            language=data.get("language"),
            text=data.get("text"),
            mentions=[Mention.from_dict(m) for m in data.get("mentions", [])],
            tags=[Tag.from_dict(m) for m in data.get("tags", [])],
        )

    @property
    def reblog_or_status(self) -> "Status":
        return self.reblog or self

    @property
    def link(self) -> str:
        return self.account.url + "/" + str(self.id)

    @property
    def content_flathtml(self) -> str:
        return node_to_html(
            BeautifulSoup(self.content, features="lxml")
        ).rstrip()

    @property
    def content_markdown(self) -> str:
        return node_to_markdown(
            BeautifulSoup(self.content, features="lxml")
        ).rstrip()

    @property
    def content_plaintext(self) -> str:
        return node_to_plaintext(
            BeautifulSoup(self.content, features="lxml")
        ).rstrip()
