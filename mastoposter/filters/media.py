from configparser import SectionProxy
from typing import Set
from mastoposter.filters.base import BaseFilter
from mastoposter.types import Status


class MediaFilter(BaseFilter, filter_name="media"):
    def __init__(self, section: SectionProxy):
        super().__init__(section)
        self.valid_media: Set[str] = set(section.get("valid_media").split())
        self.mode = section.get("mode", "include")
        if self.mode not in ("include", "exclude", "only"):
            raise ValueError(f"{self.mode=} is not valid")

    def __call__(self, status: Status) -> bool:
        if not status.media_attachments:
            return False

        types: Set[str] = {a.type for a in status.media_attachments}

        if self.mode == "include":
            return len(types & self.valid_media) > 0
        elif self.mode == "exclude":
            return len(types & self.valid_media) == 0
        elif self.mode == "only":
            return len((types ^ self.valid_media) & types) == 0
        raise ValueError(f"{self.mode=} is not valid")
