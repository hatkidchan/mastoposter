from json import loads
from typing import AsyncGenerator
from urllib.parse import urlencode


from mastoposter.types import Status


async def websocket_source(url: str, **params) -> AsyncGenerator[Status, None]:
    from websockets.client import connect

    url = f"{url}?" + urlencode({"stream": "list", **params})
    async with connect(url) as ws:
        while (msg := await ws.recv()) != None:
            event = loads(msg)
            if "error" in event:
                raise Exception(event["error"])
            if event["event"] == "update":
                yield Status.from_dict(loads(event["payload"]))
