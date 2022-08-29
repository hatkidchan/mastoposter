from typing import List

from mastoposter.types import Status
from .base import FilterInstance  # NOQA
from mastoposter.filters.boost import BoostFilter  # NOQA
from mastoposter.filters.combined import CombinedFilter  # NOQA
from mastoposter.filters.mention import MentionFilter  # NOQA
from mastoposter.filters.media import MediaFilter  # NOQA
from mastoposter.filters.text import TextFilter  # NOQA
from mastoposter.filters.spoiler import SpoilerFilter  # NOQA
from mastoposter.filters.visibility import VisibilityFilter  # NOQA


def run_filters(filters: List[FilterInstance], status: Status) -> bool:
    if not filters:
        return True
    return all((fil.filter(status) ^ fil.inverse for fil in filters))
