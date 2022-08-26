from asyncio import gather
from configparser import ConfigParser
from typing import List, Optional

from mastoposter.integrations.base import BaseIntegration
from mastoposter.integrations import DiscordIntegration, TelegramIntegration
from mastoposter.types import Status


def load_integrations_from(config: ConfigParser) -> List[BaseIntegration]:
    modules: List[BaseIntegration] = []
    for module_name in config.get("main", "modules").split():
        module = config[f"module/{module_name}"]
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
    return modules


async def execute_integrations(
    status: Status, sinks: List[BaseIntegration]
) -> List[Optional[str]]:
    return await gather(*[sink.post(status) for sink in sinks], return_exceptions=True)
