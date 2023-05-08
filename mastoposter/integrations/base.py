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
from configparser import SectionProxy
from typing import Optional

from mastoposter.types import Status


class BaseIntegration(ABC):
    # TODO: make a registry of integrations
    def __init__(self):
        pass

    @classmethod
    def from_section(cls, section: SectionProxy) -> "BaseIntegration":
        raise NotImplementedError

    @abstractmethod
    async def __call__(self, status: Status) -> Optional[str]:
        raise NotImplementedError
