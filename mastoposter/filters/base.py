from abc import ABC, abstractmethod
from typing import ClassVar, Dict, Type
from mastoposter.types import Status
from re import Pattern, compile as regexp


class BaseFilter(ABC):
    FILTER_REGISTRY: ClassVar[Dict[str, Type["BaseFilter"]]] = {}
    FILTER_NAME_REGEX: Pattern = regexp(r"^([a-z_]+)$")

    def __init__(self):
        pass

    @abstractmethod
    def __call__(self, status: Status) -> bool:
        raise NotImplementedError

    def __init_subclass__(cls, filter_name: str, **kwargs):
        super().__init_subclass__(**kwargs)
        if not cls.FILTER_NAME_REGEX.match(filter_name):
            raise ValueError(f"invalid {filter_name=!r}")
        if filter_name in cls.FILTER_REGISTRY:
            raise KeyError(f"{filter_name=!r} is already registered")
        cls.FILTER_REGISTRY[filter_name] = cls
