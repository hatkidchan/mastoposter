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

logger = getLogger(__name__)


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
