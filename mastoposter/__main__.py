#!/usr/bin/env python3
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
from asyncio import run
from configparser import ConfigParser, ExtendedInterpolation
from logging import (
    INFO,
    Formatter,
    Logger,
    StreamHandler,
    getLevelName,
    getLogger,
)
from sys import argv, stdout
from mastoposter import execute_integrations, load_integrations_from
from mastoposter.integrations import FilteredIntegration
from mastoposter.sources import websocket_source
from typing import AsyncGenerator, Callable, List
from mastoposter.types import Account, Status
from httpx import Client, HTTPTransport

from mastoposter.utils import normalize_config


WSOCK_TEMPLATE = "wss://{instance}/api/v1/streaming"
VERIFY_CREDS_TEMPLATE = "https://{instance}/api/v1/accounts/verify_credentials"

logger = getLogger()


def init_logger(loglevel: int = INFO):
    stdout_handler = StreamHandler(stdout)
    stdout_handler.setLevel(loglevel)
    formatter = Formatter("[%(asctime)s][%(levelname)5s:%(name)s] %(message)s")
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    logger.setLevel(loglevel)
    for log in logger.manager.loggerDict.values():
        if isinstance(log, Logger):
            log.setLevel(loglevel)


async def listen(
    source: Callable[..., AsyncGenerator[Status, None]],
    drains: List[FilteredIntegration],
    user: str,
    /,
    **kwargs,
):
    logger.info("Starting listening...")
    async for status in source(**kwargs):
        logger.info("New status: %s", status.uri)
        logger.debug("Got status: %r", status)
        if status.account.id != user:
            logger.info(
                "Skipping status %s (account.id=%r != %r)",
                status.uri,
                status.account.id,
                user,
            )
            continue

        # TODO: add option/filter to handle that
        if status.visibility in ("direct",):
            logger.info(
                "Skipping post %s (status.visibility=%r)",
                status.uri,
                status.visibility,
            )
            continue

        # TODO: find a better way to handle threads
        if (
            status.in_reply_to_account_id is not None
            and status.in_reply_to_account_id != user
        ):
            logger.info(
                "Skipping post %s because it's a reply to another person",
                status.uri,
            )
            continue

        await execute_integrations(status, drains)


def main(config_path: str = argv[1]):
    conf = ConfigParser(interpolation=ExtendedInterpolation())
    conf.read(config_path)

    init_logger(getLevelName(conf["main"].get("loglevel", "INFO")))
    normalize_config(conf)

    modules: List[FilteredIntegration] = load_integrations_from(conf)
    retries: int = conf["main"].getint("http-retries", 5)

    logger.info("Loaded %d integrations", len(modules))

    user_id: str = conf["main"]["user"]
    if user_id == "auto":
        logger.info("config.main.user is set to auto, getting user ID")
        with Client(transport=HTTPTransport(retries=retries)) as c:
            rq = c.get(
                VERIFY_CREDS_TEMPLATE.format(**conf["main"]),
                params={"access_token": conf["main"]["token"]},
            )
            account = Account.from_dict(rq.json())
            user_id = account.id

    logger.info("account.id=%s", user_id)

    url = "wss://{}/api/v1/streaming".format(conf["main"]["instance"])

    run(
        listen(
            websocket_source,
            modules,
            user_id,
            url=url,
            reconnect=conf["main"].getboolean("auto_reconnect", False),
            reconnect_delay=conf["main"].getfloat("reconnect_delay", 1.0),
            list=conf["main"]["list"],
            access_token=conf["main"]["token"],
        )
    )


if __name__ == "__main__":
    main()
