from json import loads
from typing import AsyncGenerator
from urllib.parse import urlencode

from mastoposter.types import Status


async def websocket_source(
    url: str, reconnect: bool = False, **params
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
        except WebSocketException:
            if not reconnect:
                raise
