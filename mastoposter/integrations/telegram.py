from configparser import SectionProxy
from dataclasses import dataclass
from typing import Any, List, Mapping, Optional
from httpx import AsyncClient
from jinja2 import Template
from mastoposter.integrations.base import BaseIntegration
from mastoposter.types import Attachment, Poll, Status
from emoji import emojize


@dataclass
class TGResponse:
    ok: bool
    params: dict
    result: Optional[Any] = None
    error: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict, params: dict) -> "TGResponse":
        return cls(
            ok=data["ok"],
            params=params,
            result=data.get("result"),
            error=data.get("description"),
        )


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
DEFAULT_TEMPLATE: str = """\
{% if status.reblog %}\
Boost from <a href="{{status.reblog.account.url}}">\
{{status.reblog.account.name}}</a>\
{% endif %}\
{% if status.reblog_or_status.spoiler_text %}\
{{status.reblog_or_status.spoiler_text}}
<tg-spoiler>{% endif %}{{ status.reblog_or_status.content_flathtml }}\
{% if status.reblog_or_status.spoiler_text %}</tg-spoiler>{% endif %}

<a href="{{status.link}}">Link to post</a>"""


class TelegramIntegration(BaseIntegration):
    def __init__(self, sect: SectionProxy):
        self.token = sect.get("token", "")
        self.chat_id = sect.get("chat", "")
        self.silent = sect.getboolean("silent", True)
        self.template: Template = Template(
            emojize(sect.get("template", DEFAULT_TEMPLATE))
        )

    async def _tg_request(self, method: str, **kwargs) -> TGResponse:
        url = API_URL.format(self.token, method)
        async with AsyncClient() as client:
            return TGResponse.from_dict(
                (await client.post(url, json=kwargs)).json(), kwargs
            )

    async def _post_plaintext(self, text: str) -> TGResponse:
        return await self._tg_request(
            "sendMessage",
            parse_mode="HTML",
            disable_notification=self.silent,
            disable_web_page_preview=True,
            chat_id=self.chat_id,
            text=text,
        )

    async def _post_media(self, text: str, media: Attachment) -> TGResponse:
        # Just to be safe
        if media.type not in MEDIA_MAPPING:
            return await self._post_plaintext(text)

        return await self._tg_request(
            "send%s" % MEDIA_MAPPING[media.type].title(),
            parse_mode="HTML",
            disable_notification=self.silent,
            disable_web_page_preview=True,
            chat_id=self.chat_id,
            caption=text,
            **{MEDIA_MAPPING[media.type]: media.url},
        )

    async def _post_mediagroup(
        self, text: str, media: List[Attachment]
    ) -> TGResponse:
        media_list: List[dict] = []
        allowed_medias = {"image", "gifv", "video", "audio", "unknown"}
        for attachment in media:
            if attachment.type not in allowed_medias:
                continue
            if attachment.type not in MEDIA_COMPATIBILITY:
                continue
            allowed_medias &= MEDIA_COMPATIBILITY[attachment.type]
            media_list.append(
                {
                    "type": MEDIA_MAPPING[attachment.type],
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
            disable_notification=self.silent,
            disable_web_page_preview=True,
            chat_id=self.chat_id,
            media=media_list,
        )

    async def _post_poll(
        self, poll: Poll, reply_to: Optional[str] = None
    ) -> TGResponse:
        return await self._tg_request(
            "sendPoll",
            disable_notification=self.silent,
            disable_web_page_preview=True,
            chat_id=self.chat_id,
            question=f"Poll:{poll.id}",
            reply_to_message_id=reply_to,
            allow_multiple_answers=poll.multiple,
            options=[opt.title for opt in poll.options],
        )

    async def __call__(self, status: Status) -> Optional[str]:
        source = status.reblog or status

        text = self.template.render({"status": status})

        ids = []

        if not source.media_attachments:
            if (res := await self._post_plaintext(text)).ok:
                if res.result:
                    ids.append(res.result["message_id"])

        elif len(source.media_attachments) == 1:
            if (
                res := await self._post_media(
                    text, source.media_attachments[0]
                )
            ).ok and res.result is not None:
                ids.append(res.result["message_id"])
        else:
            if (
                res := await self._post_mediagroup(
                    text, source.media_attachments
                )
            ).ok and res.result is not None:
                ids.append(res.result["message_id"])

        if source.poll:
            if (
                res := await self._post_poll(
                    source.poll, reply_to=ids[0] if ids else None
                )
            ).ok and res.result:
                ids.append(res.result["message_id"])

        return str.join(",", map(str, ids))

    def __repr__(self) -> str:
        return (
            "<TelegramIntegration "
            "chat_id={chat!r} "
            "template={template!r} "
            "silent={silent!r}>"
        ).format(chat=self.chat_id, silent=self.silent, template=self.template)
