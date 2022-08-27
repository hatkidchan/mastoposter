from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class BoostFilter(BaseFilter, filter_name="boost"):
    def __call__(self, status: Status) -> bool:
        return status.reblog is not None
