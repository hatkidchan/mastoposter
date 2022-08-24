from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Literal


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
            verified_at=(
                datetime.fromisoformat(data["verified_at"].rstrip("Z"))
                if data.get("verified_at") is not None
                else None
            ),
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
        return cls(**data)


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
    last_status_at: datetime
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
            discoverable=data["discoverable"],
            created_at=datetime.fromisoformat(data["created_at"].rstrip("Z")),
            last_status_at=datetime.fromisoformat(data["last_status_at"].rstrip("Z")),
            statuses_count=data["statuses_count"],
            followers_count=data["followers_count"],
            following_count=data["following_count"],
            moved=(
                Account.from_dict(data["moved"])
                if data.get("moved") is not None
                else None
            ),
            fields=list(map(Field.from_dict, data.get("fields", []))),
            bot=bool(data.get("bot")),
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
        return cls(**data)


@dataclass
class Application:
    name: str
    website: Optional[str] = None
    vapid_key: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Application":
        return cls(**data)


@dataclass
class Mention:
    id: str
    username: str
    acct: str
    url: str

    @classmethod
    def from_dict(cls, data: dict) -> "Mention":
        return cls(**data)


@dataclass
class Tag:
    name: str
    url: str

    @classmethod
    def from_dict(cls, data: dict) -> "Tag":
        return cls(**data)


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
    application: Optional[Application] = None
    url: Optional[str] = None
    in_reply_to_id: Optional[str] = None
    in_reply_to_account_id: Optional[str] = None
    reblog: Optional["Status"] = None
    poll: Optional[dict] = None
    card: Optional[dict] = None
    language: Optional[str] = None
    text: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "Status":
        return cls(
            id=data["id"],
            uri=data["uri"],
            created_at=datetime.fromisoformat(data["created_at"].rstrip("Z")),
            account=Account.from_dict(data["account"]),
            content=data["content"],
            visibility=data["visibility"],
            sensitive=data["sensitive"],
            spoiler_text=data["spoiler_text"],
            media_attachments=list(
                map(Attachment.from_dict, data["media_attachments"])
            ),
            application=(
                Application.from_dict(data["application"])
                if data.get("application") is not None
                else None
            ),
            reblogs_count=data["reblogs_count"],
            favourites_count=data["favourites_count"],
            replies_count=data["replies_count"],
            url=data.get("url"),
            in_reply_to_id=data.get("in_reply_to_id"),
            in_reply_to_account_id=data.get("in_reply_to_account_id"),
            reblog=(
                Status.from_dict(data["reblog"])
                if data.get("reblog") is not None
                else None
            ),
            poll=data.get("poll"),
            card=data.get("card"),
            language=data.get("language"),
            text=data.get("text"),
        )

    @property
    def link(self) -> str:
        return self.account.url + "/" + str(self.id)
