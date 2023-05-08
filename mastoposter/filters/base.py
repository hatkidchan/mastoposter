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
from abc import ABC, abstractmethod
from configparser import ConfigParser, SectionProxy
from typing import ClassVar, Dict, NamedTuple, Type
from mastoposter.types import Status
from re import Pattern, compile as regexp

UNUSED = lambda *_: None  # NOQA


class FilterInstance(NamedTuple):
    inverse: bool
    filter: "BaseFilter"

    def __repr__(self):
        if self.inverse:
            return f"~{self.filter!r}"
        return repr(self.filter)


class BaseFilter(ABC):
    FILTER_REGISTRY: ClassVar[Dict[str, Type["BaseFilter"]]] = {}
    FILTER_NAME_REGEX: ClassVar[Pattern] = regexp(r"^([a-z_]+)$")

    filter_name: ClassVar[str] = "_base"

    def __init__(self):
        pass

    def __init_subclass__(cls, filter_name: str, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.FILTER_NAME_REGEX.match(filter_name):
            raise ValueError(f"invalid {filter_name=!r}")
        if filter_name in cls.FILTER_REGISTRY:
            raise KeyError(f"{filter_name=!r} is already registered")
        cls.FILTER_REGISTRY[filter_name] = cls
        setattr(cls, "filter_name", filter_name)

    @abstractmethod
    def __call__(self, status: Status) -> bool:
        raise NotImplementedError

    def post_init(
        self, filters: Dict[str, FilterInstance], config: ConfigParser
    ):
        UNUSED(filters, config)

    def __repr__(self):
        return f"Filter:{self.filter_name}()"

    @classmethod
    def load_filter(cls, name: str, section: SectionProxy) -> "BaseFilter":
        if name not in cls.FILTER_REGISTRY:
            raise KeyError(f"no filter with name {name!r} was found")
        return cls.FILTER_REGISTRY[name].from_section(section)

    @classmethod
    def from_section(cls, section: SectionProxy) -> "BaseFilter":
        raise NotImplementedError

    @classmethod
    def new_instance(cls, name: str, section: SectionProxy) -> FilterInstance:
        return FilterInstance(
            inverse=name[:1] in "~!",
            filter=cls.load_filter(section["type"], section),
        )
