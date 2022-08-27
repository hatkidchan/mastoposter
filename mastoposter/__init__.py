from asyncio import gather
from configparser import ConfigParser
from typing import List, Optional

from mastoposter.integrations.base import BaseIntegration
from mastoposter.integrations import DiscordIntegration, TelegramIntegration
from mastoposter.types import Status


def load_integrations_from(config: ConfigParser) -> List[BaseIntegration]:
    modules: List[BaseIntegration] = []
    for module_name in config.get("main", "modules").split():
        mod = config[f"module/{module_name}"]
        if mod["type"] == "telegram":
            modules.append(TelegramIntegration(mod))
        elif mod["type"] == "discord":
            modules.append(DiscordIntegration(mod))
        else:
            raise ValueError("Invalid module type %r" % mod["type"])
    return modules


async def execute_integrations(
    status: Status, sinks: List[BaseIntegration]
) -> List[Optional[str]]:
    coros = [sink.post(status) for sink in sinks]
    return await gather(*coros, return_exceptions=True)
