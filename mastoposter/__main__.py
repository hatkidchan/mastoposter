#!/usr/bin/env python3
from asyncio import run
from configparser import ConfigParser, ExtendedInterpolation
from mastoposter import execute_integrations, load_integrations_from
from mastoposter.integrations import FilteredIntegration
from mastoposter.sources import websocket_source
from typing import AsyncGenerator, Callable, List
from mastoposter.types import Account, Status
from httpx import Client


WSOCK_TEMPLATE = "wss://{instance}/api/v1/streaming"
VERIFY_CREDS_TEMPLATE = "https://{instance}/api/v1/accounts/verify_credentials"


async def listen(
    source: Callable[..., AsyncGenerator[Status, None]],
    drains: List[FilteredIntegration],
    user: str,
    /,
    **kwargs,
):
    async for status in source(**kwargs):
        if status.account.id != user:
            continue

        # TODO: add option/filter to handle that
        if status.visibility in ("direct",):
            continue

        # TODO: find a better way to handle threads
        if (
            status.in_reply_to_account_id is not None
            and status.in_reply_to_account_id != user
        ):
            continue

        await execute_integrations(status, drains)


def main(config_path: str):
    conf = ConfigParser(interpolation=ExtendedInterpolation())
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

    modules: List[FilteredIntegration] = load_integrations_from(conf)

    user_id: str = conf["main"]["user"]
    if user_id == "auto":
        with Client() as c:
            rq = c.get(
                VERIFY_CREDS_TEMPLATE.format(**conf["main"]),
                params={"access_token": conf["main"]["token"]},
            )
            account = Account.from_dict(rq.json())
            user_id = account.id

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
