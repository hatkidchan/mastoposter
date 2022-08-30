from typing import List, NamedTuple
from mastoposter.filters.base import FilterInstance

from mastoposter.integrations.base import BaseIntegration
from .telegram import TelegramIntegration  # NOQA
from .discord import DiscordIntegration  # NOQA


class FilteredIntegration(NamedTuple):
    sink: BaseIntegration
    filters: List[FilterInstance]
