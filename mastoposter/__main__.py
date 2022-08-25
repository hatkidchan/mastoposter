#!/usr/bin/env python3
from asyncio import run
from configparser import ConfigParser
from mastoposter.integrations.discord import DiscordIntegration

from mastoposter.integrations.telegram import TelegramIntegration
from mastoposter.sources import websocket_source
from typing import Any, AsyncGenerator, Callable, Dict, List
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

        # TODO: add option/filter to handle that
        if status.visibility in ("direct", "private"):
            continue

        # TODO: find a better way to handle threads
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

    for section in conf.sections():
        _remove = set()
        for k, v in conf[section].items():
            normalized_key = k.replace(" ", "_").replace("-", "_")
            if k == normalized_key:
                continue
            conf[section][normalized_key] = v
            _remove.add(k)
        for k in _remove:
            del conf[section][k]

    modules: List[BaseIntegration] = []
    for module_name in conf.get("main", "modules").split():
        module = conf[f"module/{module_name}"]
        if module["type"] == "telegram":
            modules.append(
                TelegramIntegration(
                    token=module["token"],
                    chat_id=module["chat"],
                    show_post_link=module.getboolean("show_post_link", fallback=True),
                    show_boost_from=module.getboolean("show_boost_from", fallback=True),
                )
            )
        elif module["type"] == "discord":
            modules.append(DiscordIntegration(webhook=module["webhook"]))
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
