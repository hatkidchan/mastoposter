from asyncio import gather
from configparser import ConfigParser
from logging import getLogger
from typing import Dict, List, Optional
from mastoposter.filters import run_filters
from mastoposter.filters.base import BaseFilter, FilterInstance

from mastoposter.integrations import (
    DiscordIntegration,
    FilteredIntegration,
    TelegramIntegration,
)
from mastoposter.types import Status

logger = getLogger(__name__)


def load_integrations_from(config: ConfigParser) -> List[FilteredIntegration]:
    modules: List[FilteredIntegration] = []
    for module_name in config.get("main", "modules").split():
        mod = config[f"module/{module_name}"]
        logger.info(
            "Configuring %s integration (type=%s)", module_name, mod["type"]
        )

        filters: Dict[str, FilterInstance] = {}
        for filter_name in mod.get("filters", "").split():
            filter_basename = filter_name.lstrip("~!")

            logger.info(
                "Loading filter %s for integration %s",
                filter_basename,
                module_name,
            )

            filters[filter_basename] = BaseFilter.new_instance(
                filter_name, config[f"filter/{filter_basename}"]
            )

        for finst in list(filters.values()):
            logger.info("Running post-initialization hook for %r", finst)
            finst.filter.post_init(filters, config)

        # TODO: make a registry of integrations
        # INFO: mastoposter/integrations/base.py@__init__
        if mod["type"] == "telegram":
            modules.append(
                FilteredIntegration(
                    TelegramIntegration.from_section(mod),
                    list(filters.values()),
                )
            )
        elif mod["type"] == "discord":
            modules.append(
                FilteredIntegration(
                    DiscordIntegration.from_section(mod),
                    list(filters.values()),
                )
            )
        else:
            raise ValueError("Invalid module type %r" % mod["type"])
    return modules


async def execute_integrations(
    status: Status, sinks: List[FilteredIntegration]
) -> List[Optional[str]]:
    logger.info("Executing integrations...")
    return await gather(
        *[sink[0](status) for sink in sinks if run_filters(sink[1], status)],
        return_exceptions=True,
    )
