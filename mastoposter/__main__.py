#!/usr/bin/env python3
from asyncio import run
from configparser import ConfigParser, ExtendedInterpolation
from logging import DEBUG, Formatter, StreamHandler, getLogger
from sys import stdout
from mastoposter import execute_integrations, load_integrations_from
from mastoposter.integrations import FilteredIntegration
from mastoposter.sources import websocket_source
from typing import AsyncGenerator, Callable, List
from mastoposter.types import Account, Status
from httpx import Client

from mastoposter.utils import normalize_config


WSOCK_TEMPLATE = "wss://{instance}/api/v1/streaming"
VERIFY_CREDS_TEMPLATE = "https://{instance}/api/v1/accounts/verify_credentials"

logger = getLogger()


def init_logger(loglevel: int = DEBUG):
    stdout_handler = StreamHandler(stdout)
    stdout_handler.setLevel(DEBUG)
    formatter = Formatter("[%(asctime)s][%(levelname)5s:%(name)s] %(message)s")
    stdout_handler.setFormatter(formatter)
    logger.addHandler(stdout_handler)
    logger.setLevel(loglevel)


async def listen(
    source: Callable[..., AsyncGenerator[Status, None]],
    drains: List[FilteredIntegration],
    user: str,
    /,
    **kwargs,
):
    logger.info("Starting listening...")
    async for status in source(**kwargs):
        logger.debug("Got status: %r", status)
        if status.account.id != user:
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


def main(config_path: str):
    init_logger()
    conf = ConfigParser(interpolation=ExtendedInterpolation())
    conf.read(config_path)

    normalize_config(conf)

    modules: List[FilteredIntegration] = load_integrations_from(conf)

    logger.info("Loaded %d integrations", len(modules))

    user_id: str = conf["main"]["user"]
    if user_id == "auto":
        logger.info("config.main.user is set to auto, getting user ID")
        with Client() as c:
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
            list=conf["main"]["list"],
            access_token=conf["main"]["token"],
        )
    )


if __name__ == "__main__":
    from sys import argv

    main(argv[1])
