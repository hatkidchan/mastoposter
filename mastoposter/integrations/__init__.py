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
from typing import List, NamedTuple
from mastoposter.filters.base import FilterInstance

from mastoposter.integrations.base import BaseIntegration
from .telegram import TelegramIntegration  # NOQA
from .discord import DiscordIntegration  # NOQA


class FilteredIntegration(NamedTuple):
    sink: BaseIntegration
    filters: List[FilterInstance]
