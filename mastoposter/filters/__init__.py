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
from logging import getLogger
from typing import List

from mastoposter.types import Status
from .base import FilterInstance
from mastoposter.filters.boost import BoostFilter  # NOQA
from mastoposter.filters.combined import CombinedFilter  # NOQA
from mastoposter.filters.mention import MentionFilter  # NOQA
from mastoposter.filters.media import MediaFilter  # NOQA
from mastoposter.filters.text import TextFilter  # NOQA
from mastoposter.filters.spoiler import SpoilerFilter  # NOQA
from mastoposter.filters.visibility import VisibilityFilter  # NOQA

logger = getLogger("filters")


def run_filters(filters: List[FilterInstance], status: Status) -> bool:
    logger.debug("Running filters on %r", status.id)

    if not filters:
        logger.debug("No filters, returning True")
        return True

    results: List[bool] = []
    for fil in filters:
        result = fil.filter(status)
        logger.debug(
            "%r -> %r ^ %r -> %r",
            fil.filter,
            result,
            fil.inverse,
            result ^ fil.inverse,
        )
        results.append(result ^ fil.inverse)
    logger.debug("Result: %r", all(results))
    return all(results)
