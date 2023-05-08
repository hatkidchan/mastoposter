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
from configparser import ConfigParser, SectionProxy
from typing import Callable, ClassVar, Dict, List, Sequence
from mastoposter.filters.base import BaseFilter, FilterInstance
from mastoposter.types import Status


class CombinedFilter(BaseFilter, filter_name="combined"):
    OPERATORS: ClassVar[Dict[str, Callable[[Sequence[bool]], bool]]] = {
        "all": lambda d: all(d),
        "any": lambda d: any(d),
        "single": lambda d: sum(d) == 1,
    }

    def __init__(self, filter_names: List[str], operator: str):
        self._filter_names = filter_names
        self._operator_name = operator
        self.operator = self.OPERATORS[self._operator_name]
        self.filters: List[FilterInstance] = []

    @classmethod
    def from_section(cls, section: SectionProxy) -> "CombinedFilter":
        return cls(
            filter_names=section["filters"].split(),
            operator=section.get("operator", "all"),
        )

    def post_init(
        self, filters: Dict[str, FilterInstance], config: ConfigParser
    ):
        super().post_init(filters, config)
        self.filters = [
            self.new_instance(name, config["filter/" + name.lstrip("~!")])
            for name in self._filter_names
        ]

    def __call__(self, post: Status) -> bool:
        if self.OPERATORS[self._operator_name] is not self.operator:
            self._operator_name = str(self.operator)
        return self.operator([f[1](post) ^ f[0] for f in self.filters])

    def __repr__(self):
        if self.filters:
            return (
                f"Filter:combined(op={self._operator_name}, "
                f"filters={self.filters!r})"
            )
        return (
            f"Filter:combined(op={self._operator_name}, "
            f"filters={self._filter_names!r}, loaded=False)"
        )
