#!/usr/bin/env python3
from asyncio import run
from configparser import ConfigParser
from mastoposter import execute_integrations, load_integrations_from
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

        # TODO: add option/filter to handle that
        if status.visibility in ("direct", "private"):
            continue

        # TODO: find a better way to handle threads
        if (
            status.in_reply_to_account_id is not None
            and status.in_reply_to_account_id != user
        ):
            continue

        await execute_integrations(status, drains)


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

    modules = load_integrations_from(conf)

    url = "wss://{}/api/v1/streaming".format(conf["main"]["instance"])
    run(
        listen(
            websocket_source,
            modules,
            conf["main"]["user"],
            url=url,
            reconnect=conf["main"].getboolean("auto_reconnect", False),
            list=conf["main"]["list"],
            access_token=conf["main"]["token"],
        )
    )


if __name__ == "__main__":
    from sys import argv

    main(argv[1])
