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
from logging import getLogger
from typing import List, Optional
from httpx import AsyncClient, AsyncHTTPTransport
from zlib import crc32
from mastoposter.integrations.base import BaseIntegration
from mastoposter.integrations.discord.types import (
    DiscordEmbed,
    DiscordEmbedAuthor,
    DiscordEmbedImage,
)
from mastoposter.types import Status

logger = getLogger("integrations.discord")


class DiscordIntegration(BaseIntegration):
    def __init__(self, webhook: str, retries: int = 5):
        self.webhook = webhook
        self.retries = retries

    @classmethod
    def from_section(cls, section: SectionProxy) -> "DiscordIntegration":
        return cls(section["webhook"], section.getint("retries", 5))

    async def execute_webhook(
        self,
        content: Optional[str] = None,
        username: Optional[str] = None,
        avatar_url: Optional[str] = None,
        embeds: Optional[List[DiscordEmbed]] = None,
    ) -> dict:
        async with AsyncClient(
            transport=AsyncHTTPTransport(retries=self.retries)
        ) as c:
            json = {
                "content": content,
                "username": username,
                "avatar_url": avatar_url,
                "embeds": [embed.asdict() for embed in embeds]
                if embeds is not None
                else [],
            }

            logger.debug("Executing webhook with %r", json)

            result = (
                await c.post(
                    self.webhook,
                    json=json,
                )
            ).json()
            logger.debug("Result: %r", result)
            return result

    async def __call__(self, status: Status) -> Optional[str]:
        source = status.reblog or status
        embeds: List[DiscordEmbed] = []

        text = source.content_markdown
        if source.spoiler_text:
            text = f"{source.spoiler_text}\n||{text}||"

        if status.reblog is not None:
            title = (
                f"@{status.account.acct} boosted from @{source.account.acct}"
            )
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
            else:
                logger.warn(
                    "Unsupported attachment %r for Discord Embed",
                    attachment.type,
                )

        await self.execute_webhook(
            username=status.account.acct,
            avatar_url=status.account.avatar_static,
            embeds=embeds,
        )

        return None
