from configparser import SectionProxy
from dataclasses import dataclass
from logging import getLogger
from typing import Any, List, Mapping, Optional
from httpx import AsyncClient
from jinja2 import Template
from mastoposter.integrations.base import BaseIntegration
from mastoposter.types import Attachment, Poll, Status
from emoji import emojize


logger = getLogger("integrations.telegram")


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
MEDIA_SPOILER_SUPPORT: Mapping[str, bool] = {
    "image": True,
    "video": True,
    "gifv": True,
    "audio": False,
    "unknown": False,
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
    def __init__(
        self,
        token: str,
        chat_id: str,
        template: Optional[Template] = None,
        silent: bool = True,
    ):
        self.token = token
        self.chat_id = chat_id
        self.silent = silent

        if template is None:
            self.template = Template(emojize(DEFAULT_TEMPLATE))
        else:
            self.template = template

    @classmethod
    def from_section(cls, section: SectionProxy) -> "TelegramIntegration":
        return cls(
            token=section["token"],
            chat_id=section["chat"],
            silent=section.getboolean("silent", True),
            template=Template(
                emojize(section.get("template", DEFAULT_TEMPLATE))
            ),
        )

    async def _tg_request(self, method: str, **kwargs) -> TGResponse:
        url = API_URL.format(self.token, method)
        async with AsyncClient() as client:
            logger.debug("TG request: %s(%r)", method, kwargs)
            response = TGResponse.from_dict(
                (await client.post(url, json=kwargs)).json(), kwargs
            )
            if not response.ok:
                logger.error("TG error: %r", response.error)
                logger.error("parameters: %r", kwargs)
            else:
                logger.debug("Result: %r", response.result)
            return response

    async def _post_plaintext(self, text: str) -> TGResponse:
        logger.debug("Sending HTML message: %r", text)
        return await self._tg_request(
            "sendMessage",
            parse_mode="HTML",
            disable_notification=self.silent,
            disable_web_page_preview=True,
            chat_id=self.chat_id,
            text=text,
        )

    async def _post_media(
        self, text: str, media: Attachment, spoiler: bool = False
    ) -> TGResponse:
        # Just to be safe
        if media.type not in MEDIA_MAPPING:
            logger.warning(
                "Media %r has unknown type, falling back to plaintext", media
            )
            return await self._post_plaintext(text)

        return await self._tg_request(
            "send%s" % MEDIA_MAPPING[media.type].title(),
            parse_mode="HTML",
            disable_notification=self.silent,
            disable_web_page_preview=True,
            chat_id=self.chat_id,
            caption=text,
            **{MEDIA_MAPPING[media.type]: media.url},
            **(
                {"has_spoiler": spoiler}
                if MEDIA_SPOILER_SUPPORT.get(media.type, False)
                else {}
            ),
        )

    async def _post_mediagroup(
        self, text: str, media: List[Attachment], spoiler: bool = False
    ) -> TGResponse:
        logger.debug("Sendind media group: %r (text=%r)", media, text)
        media_list: List[dict] = []
        allowed_medias = {"image", "gifv", "video", "audio", "unknown"}
        for attachment in media:
            if attachment.type not in allowed_medias:
                continue
            if attachment.type not in MEDIA_COMPATIBILITY:
                logger.warning(
                    "attachment %r is not in %r",
                    attachment.type,
                    MEDIA_COMPATIBILITY,
                )
                continue
            allowed_medias &= MEDIA_COMPATIBILITY[attachment.type]
            media_list.append(
                {
                    "type": MEDIA_MAPPING[attachment.type],
                    "media": attachment.url,
                    **(
                        {"has_spoiler": spoiler}
                        if MEDIA_SPOILER_SUPPORT.get(attachment.type, False)
                        else {}
                    ),
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
        logger.debug("Sending poll: %r", poll)
        return await self._tg_request(
            "sendPoll",
            disable_notification=self.silent,
            disable_web_page_preview=True,
            chat_id=self.chat_id,
            question=f"Poll:{poll.id}",
            reply_to_message_id=reply_to,
            allows_multiple_answers=poll.multiple,
            options=[opt.title for opt in poll.options],
        )

    async def __call__(self, status: Status) -> Optional[str]:
        source = status.reblog or status

        has_spoiler = source.spoiler_text != ""
        text = self.template.render({"status": status})

        ids = []

        if not source.media_attachments:
            if (res := await self._post_plaintext(text)).ok:
                if res.result:
                    ids.append(res.result["message_id"])

        elif len(source.media_attachments) == 1:
            if (
                res := await self._post_media(
                    text, source.media_attachments[0], has_spoiler
                )
            ).ok and res.result is not None:
                ids.append(res.result["message_id"])
        else:
            if (
                res := await self._post_mediagroup(
                    text, source.media_attachments, has_spoiler
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
        bot_uid, key = self.token.split(":")
        return (
            "<TelegramIntegration "
            "chat_id={chat!r} "
            "template={template!r} "
            "token={bot_uid}:{key} "
            "silent={silent!r}>"
        ).format(
            chat=self.chat_id,
            silent=self.silent,
            template=self.template,
            bot_uid=bot_uid,
            key=str.join("", ("X" for _ in key)),
        )
