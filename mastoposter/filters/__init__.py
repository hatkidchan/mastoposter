from typing import List

from mastoposter.types import Status
from .base import BaseFilter  # NOQA
from mastoposter.filters.boost import BoostFilter  # NOQA
from mastoposter.filters.combined import CombinedFilter  # NOQA
from mastoposter.filters.mention import MentionFilter  # NOQA
from mastoposter.filters.media import MediaFilter  # NOQA
from mastoposter.filters.text import TextFilter  # NOQA
from mastoposter.filters.spoiler import SpoilerFilter  # NOQA


def run_filters(filters: List[BaseFilter], status: Status) -> bool:
    return all((fil(status) for fil in filters))
