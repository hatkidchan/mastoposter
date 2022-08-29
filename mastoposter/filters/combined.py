from configparser import ConfigParser, SectionProxy
from typing import Callable, ClassVar, Dict, List
from functools import reduce
from mastoposter.filters.base import BaseFilter, FilterInstance
from mastoposter.types import Status


class CombinedFilter(BaseFilter, filter_name="combined"):
    OPERATORS: ClassVar[Dict[str, Callable]] = {
        "and": lambda a, b: a and b,
        "or": lambda a, b: a or b,
        "xor": lambda a, b: a ^ b,
    }

    def __init__(self, section: SectionProxy):
        self.filter_names = section.get("filters", "").split()
        self.operator = self.OPERATORS[section.get("operator", "and")]
        self._operator_name = section.get("operator", "and")
        self.filters: List[FilterInstance] = []

    def post_init(
        self, filters: Dict[str, FilterInstance], config: ConfigParser
    ):
        super().post_init(filters, config)
        self.filters = [
            self.new_instance(name, config["filter/" + name.lstrip("~!")])
            for name in self.filter_names
        ]

    def __call__(self, status: Status) -> bool:
        results = [fil.filter(status) ^ fil.inverse for fil in self.filters]
        if self.OPERATORS[self._operator_name] is not self.operator:
            self._operator_name = "N/A"
        return reduce(self.operator, results)

    def __repr__(self):
        return (
            f"Filter:combined(op={self._operator_name}, "
            f"filters={self.filters!r})"
        )
