from asyncio import gather
from configparser import ConfigParser
from typing import Dict, List, Optional
from mastoposter.filters import run_filters
from mastoposter.filters.base import BaseFilter, FilterInstance

from mastoposter.integrations import (
    DiscordIntegration,
    FilteredIntegration,
    TelegramIntegration,
)
from mastoposter.types import Status


def load_integrations_from(config: ConfigParser) -> List[FilteredIntegration]:
    modules: List[FilteredIntegration] = []
    for module_name in config.get("main", "modules").split():
        mod = config[f"module/{module_name}"]

        filters: Dict[str, FilterInstance] = {}
        for filter_name in mod.get("filters", "").split():
            filter_basename = filter_name.lstrip("~!")

            filters[filter_basename] = BaseFilter.new_instance(
                filter_name, config[f"filter/{filter_basename}"]
            )

        for finst in list(filters.values()):
            finst.filter.post_init(filters, config)

        if mod["type"] == "telegram":
            modules.append(
                FilteredIntegration(
                    TelegramIntegration(mod), list(filters.values())
                )
            )
        elif mod["type"] == "discord":
            modules.append(
                FilteredIntegration(
                    DiscordIntegration(mod), list(filters.values())
                )
            )
        else:
            raise ValueError("Invalid module type %r" % mod["type"])
    return modules


async def execute_integrations(
    status: Status, sinks: List[FilteredIntegration]
) -> List[Optional[str]]:
    return await gather(
        *[sink[0](status) for sink in sinks if run_filters(sink[1], status)],
        return_exceptions=True,
    )
