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
from asyncio import exceptions, sleep
from json import loads
from logging import getLogger
from typing import AsyncGenerator
from urllib.parse import urlencode
from mastoposter.types import Status

logger = getLogger("sources")


async def websocket_source(
    url: str, reconnect: bool = False, reconnect_delay: float = 1.0, **params
) -> AsyncGenerator[Status, None]:
    from websockets.client import connect
    from websockets.exceptions import WebSocketException

    url = f"{url}?" + urlencode({"stream": "list", **params})
    while True:
        try:
            async with connect(url) as ws:
                while (msg := await ws.recv()) is not None:
                    event = loads(msg)
                    if "error" in event:
                        raise Exception(event["error"])
                    if event["event"] == "update":
                        yield Status.from_dict(loads(event["payload"]))
                    else:
                        logger.warn("unknown event type %r", event["event"])
                        logger.debug("data: %r", event)
        except (
            WebSocketException,
            TimeoutError,
            exceptions.TimeoutError,
            ConnectionError,
        ) as e:
            if not reconnect:
                raise
            else:
                logger.warn("%r caught, reconnecting", e)
                await sleep(reconnect_delay)
        else:
            logger.info(
                "WebSocket closed connection without any errors, "
                "but we're not done yet"
            )
            await sleep(reconnect_delay)
