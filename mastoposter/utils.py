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

from configparser import ConfigParser
from logging import getLogger

logger = getLogger("utils")


def normalize_config(conf: ConfigParser):
    for section in conf.sections():
        _remove = set()
        for k, v in conf[section].items():
            normalized_key = k.replace(" ", "_").replace("-", "_")
            if k == normalized_key:
                continue
            logger.info(
                "moving %r.%r -> %r.%r", section, k, section, normalized_key
            )
            conf[section][normalized_key] = v
            _remove.add(k)
        for k in _remove:
            logger.info("removing key %r.%r", section, k)
            del conf[section][k]
