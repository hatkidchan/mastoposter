from typing import List, Optional
from bs4 import BeautifulSoup, PageElement, Tag
from httpx import AsyncClient
from zlib import crc32
from mastoposter.integrations.base import BaseIntegration
from mastoposter.integrations.discord.types import (
    DiscordEmbed,
    DiscordEmbedAuthor,
    DiscordEmbedImage,
)
from mastoposter.types import Status


class DiscordIntegration(BaseIntegration):
    def __init__(self, webhook: str):
        self.webhook = webhook

    @staticmethod
    def md_escape(text: str) -> str:
        return (
            text.replace("\\", "\\\\")
            .replace("*", "\\*")
            .replace("[", "\\[")
            .replace("]", "\\]")
            .replace("_", "\\_")
            .replace("~", "\\~")
            .replace("|", "\\|")
            .replace("`", "\\`")
        )

    @classmethod
    def node_to_text(cls, el: PageElement) -> str:
        if isinstance(el, Tag):
            if el.name == "a":
                return "[%s](%s)" % (
                    cls.md_escape(str.join("", map(cls.node_to_text, el.children))),
                    el.attrs["href"],
                )
            elif el.name == "p":
                return str.join("", map(cls.node_to_text, el.children)) + "\n\n"
            elif el.name == "br":
                return "\n"
            return str.join("", map(cls.node_to_text, el.children))
        return cls.md_escape(str(el))

    async def execute_webhook(
        self,
        content: Optional[str] = None,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        embeds: Optional[List[DiscordEmbed]] = None,
    ) -> dict:
        async with AsyncClient() as c:
            json = {
                "content": content,
                "username": username,
                "avatar_url": avatar_url,
                "embeds": [embed.asdict() for embed in embeds]
                if embeds is not None
                else [],
            }
            return (
                await c.post(
                    self.webhook,
                    json=json,
                )
            ).json()

    async def post(self, status: Status) -> Optional[str]:
        source = status.reblog or status
        embeds: List[DiscordEmbed] = []

        text = self.node_to_text(BeautifulSoup(source.content, features="lxml"))
        if source.spoiler_text:
            text = f"{source.spoiler_text}\n||{text}||"

        if status.reblog is not None:
            title = f"@{status.account.acct} boosted from @{source.account.acct}"
        else:
            title = f"@{status.account.acct} posted"

        embeds.append(
            DiscordEmbed(
                title=title,
                description=text,
                url=status.link,
                timestamp=source.created_at,
                author=DiscordEmbedAuthor(
                    name=source.account.display_name,
                    url=source.account.url,
                    icon_url=source.account.avatar_static,
                ),
                color=crc32(source.account.id.encode("utf-8")) & 0xFFFFFF,
            )
        )

        for attachment in source.media_attachments:
            if attachment.type == "image":
                embeds.append(
                    DiscordEmbed(
                        url=status.link,
                        image=DiscordEmbedImage(
                            url=attachment.url,
                        ),
                    )
                )

        await self.execute_webhook(
            username=status.account.acct,
            avatar_url=status.account.avatar_static,
            embeds=embeds,
        )

        return None
