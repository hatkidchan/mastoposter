#!/usr/bin/env python3
from asyncio import run
from configparser import ConfigParser

from mastoposter.integrations.telegram import TelegramIntegration
from mastoposter.sources import websocket_source
from typing import AsyncGenerator, Callable, List
from mastoposter.integrations.base import BaseIntegration
from mastoposter.types import Status


async def listen(
    source: Callable[..., AsyncGenerator[Status, None]],
    drains: List[BaseIntegration],
    user: str,
    /,
    **kwargs,
):
    async for status in source(**kwargs):
        if status.account.id != user:
            continue
        print(status)
        if status.visibility == "direct":
            continue
        if (
            status.in_reply_to_account_id is not None
            and status.in_reply_to_account_id != user
        ):
            continue
        for drain in drains:
            await drain.post(status)


def main(config_path: str):
    conf = ConfigParser()
    conf.read(config_path)

    modules = []
    for module_name in conf.get("main", "modules").split():
        module = conf[f"module/{module_name}"]
        if module["type"] == "telegram":
            modules.append(
                TelegramIntegration(
                    token=module.get("token"),
                    chat_id=module.get("chat"),
                    show_post_link=module.getboolean("show-post-link", fallback=True),
                    show_boost_from=module.getboolean("show-boost-from", fallback=True),
                )
            )
        else:
            raise ValueError("Invalid module type %r" % module["type"])

    url = "wss://{}/api/v1/streaming".format(conf["main"]["instance"])
    run(
        listen(
            websocket_source,
            modules,
            conf["main"]["user"],
            url=url,
            list=conf["main"]["list"],
            access_token=conf["main"]["token"],
        )
    )


if __name__ == "__main__":
    from sys import argv

    main(argv[1])
