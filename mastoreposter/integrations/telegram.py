from dataclasses import dataclass
from html import escape
from typing import Any, List, Mapping, Optional, Union
from bs4 import BeautifulSoup, Tag, PageElement
from httpx import AsyncClient
from mastoreposter.integrations.base import BaseIntegration
from mastoreposter.types import Attachment, Status


@dataclass
class TGResponse:
    ok: bool
    params: dict
    result: Optional[Any] = None
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict, params: dict) -> "TGResponse":
        return cls(data["ok"], params, data.get("result"), data.get("error"))


class TelegramIntegration(BaseIntegration):
    API_URL: str = "https://api.telegram.org/bot{}/{}"
    MEDIA_COMPATIBILITY: Mapping[str, set] = {
        "image": {"image", "video"},
        "video": {"image", "video"},
        "gifv": {"gifv"},
        "audio": {"audio"},
        "unknown": {"unknown"},
    }
    MEDIA_MAPPING: Mapping[str, str] = {
        "image": "photo",
        "video": "video",
        "gifv": "animation",
        "audio": "audio",
        "unknown": "document",
    }

    def __init__(
        self,
        token: str,
        chat_id: Union[str, int],
        show_post_link: bool = True,
        show_boost_from: bool = True,
    ):
        self.token = token
        self.chat_id = chat_id
        self.show_post_link = show_post_link
        self.show_boost_from = show_boost_from

    async def _tg_request(self, method: str, **kwargs) -> TGResponse:
        url = self.API_URL.format(self.token, method)
        async with AsyncClient() as client:
            return TGResponse.from_dict(
                (await client.post(url, json=kwargs)).json(), kwargs
            )

    async def _post_plaintext(self, text: str) -> TGResponse:
        return await self._tg_request(
            "sendMessage",
            parse_mode="HTML",
            disable_notification=True,
            disable_web_page_preview=True,
            chat_id=self.chat_id,
            text=text,
        )

    async def _post_media(self, text: str, media: Attachment) -> TGResponse:
        # Just to be safe
        if media.type not in self.MEDIA_MAPPING:
            return await self._post_plaintext(text)

        return await self._tg_request(
            "send%s" % self.MEDIA_MAPPING[media.type].title(),
            parse_mode="HTML",
            disable_notification=True,
            disable_web_page_preview=True,
            chat_id=self.chat_id,
            caption=text,
            **{self.MEDIA_MAPPING[media.type]: media.preview_url},
        )

    async def _post_mediagroup(self, text: str, media: List[Attachment]) -> TGResponse:
        media_list: List[dict] = []
        allowed_medias = {"image", "gifv", "video", "audio", "unknown"}
        for attachment in media:
            if attachment.type not in allowed_medias:
                continue
            if attachment.type not in self.MEDIA_COMPATIBILITY:
                continue
            allowed_medias &= self.MEDIA_COMPATIBILITY[attachment.type]
            media_list.append(
                {
                    "type": self.MEDIA_MAPPING[attachment.type],
                    "media": attachment.url,
                }
            )
            if len(media_list) == 1:
                media_list[0].update(
                    {
                        "caption": text,
                        "parse_mode": "HTML",
                    }
                )

        return await self._tg_request(
            "sendMediaGroup",
            disable_notification=True,
            disable_web_page_preview=True,
            chat_id=self.chat_id,
            media=media_list,
        )

    @classmethod
    def node_to_text(cls, el: PageElement) -> str:
        if isinstance(el, Tag):
            if el.name == "a":
                return '<a href="{}">{}</a>'.format(
                    escape(el.attrs["href"]),
                    str.join("", map(cls.node_to_text, el.children)),
                )
            elif el.name == "p":
                return str.join("", map(cls.node_to_text, el.children)) + "\n\n"
            elif el.name == "br":
                return "\n"
            return str.join("", map(cls.node_to_text, el.children))
        return escape(str(el))

    async def post(self, status: Status) -> str:
        source = status.reblog or status
        text = self.node_to_text(BeautifulSoup(source.content, features="lxml"))

        if source.spoiler_text:
            text = "Spoiler: {cw}\n<tg-spoiler>{text}</tg-spoiler>".format(
                cw=source.spoiler_text, text=text
            )

        if self.show_post_link:
            text += '\n\n<a href="%s">Link to post</a>' % status.link

        if status.reblog and self.show_boost_from:
            text = (
                'Boosted post from <a href="{}">{}</a>'.format(
                    source.account.url, source.account.display_name
                )
                + text
            )

        if not source.media_attachments:
            msg = await self._post_plaintext(text)
        elif len(source.media_attachments) == 1:
            msg = await self._post_media(text, source.media_attachments[0])
        else:
            msg = await self._post_mediagroup(text, source.media_attachments)

        if not msg.ok:
            raise Exception(msg.error, msg.params)

        return ""

    def __repr__(self) -> str:
        return (
            "<TelegramIntegration "
            "chat_id={chat!r} "
            "show_post_link={show_post_link!r} "
            "show_boost_from={show_boost_from!r} "
        ).format(
            chat=self.chat_id,
            show_post_link=self.show_post_link,
            show_boost_from=self.show_boost_from,
        )
