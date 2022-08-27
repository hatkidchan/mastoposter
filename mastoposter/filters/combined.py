from configparser import SectionProxy
from typing import Callable, ClassVar, Dict, List, NamedTuple
from functools import reduce
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class FilterType(NamedTuple):
    inverse: bool
    filter: BaseFilter


class CombinedFilter(BaseFilter, filter_name="combined"):
    OPERATORS: ClassVar[Dict[str, Callable]] = {
        "and": lambda a, b: a and b,
        "or": lambda a, b: a or b,
        "xor": lambda a, b: a ^ b,
    }

    def __init__(self, section: SectionProxy):
        self.filter_names = section.get("filters", "").split()
        self.operator = self.OPERATORS[section.get("operator", "and")]
        self.filters: List[FilterType] = []

    def post_init(self, filters: Dict[str, "BaseFilter"]):
        super().post_init(filters)
        for filter_name in self.filter_names:
            self.filters.append(
                FilterType(
                    filter_name[:1] in "~!",  # inverse
                    filters[filter_name.rstrip("!~")],
                )
            )

    def __call__(self, status: Status) -> bool:
        results = [fil.filter(status) ^ fil.inverse for fil in self.filters]
        return reduce(self.operator, results)
