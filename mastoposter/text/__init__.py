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
from typing import Callable, Iterable, Literal, Optional
from bs4.element import Tag, PageElement
from html import escape

VALID_OUTPUT_TYPES = Literal["plain", "html", "markdown"]
BULLET = "\u2022"
STRIPE = "\u258d"


def md_escape(text: str) -> str:
    return (
        text.replace("\\", "\\\\")
        .replace("*", "\\*")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("_", "\\_")
        .replace("~", "\\~")
        .replace("|", "\\|")
        .replace("`", "\\`")
    )


node_processors: dict[
    tuple[VALID_OUTPUT_TYPES, str],
    list[
        Callable[
            [
                Tag,
            ],
            Optional[str],
        ]
    ],
] = {}


def register_converter(tag: str, output_type: VALID_OUTPUT_TYPES = "plain"):
    def decorate(function):
        node_processors[output_type, tag].append(function)
        return function

    return decorate


def register_fmt_converter(
    format: str,
    tag: str,
    output_type: VALID_OUTPUT_TYPES = "plain",
    separator: str = "",
):
    def fmt_tag(el: Tag) -> str:
        if "%s" in format:
            return format % nodes_process(el.children, output_type, separator)
        return format

    register_converter(tag, output_type)(fmt_tag)


def node_process(el: PageElement, type_: VALID_OUTPUT_TYPES) -> str:
    if isinstance(el, Tag):
        for func in node_processors[type_, el.name]:
            result = func(el)  # XXX: could use walrus, but it's py3.8+ only
            if result:
                return result
    return escape(str(el))


def nodes_process(
    els: Iterable[PageElement],
    type_: VALID_OUTPUT_TYPES = "plain",
    separator: str = "",
) -> str:
    return str.join(separator, (node_process(el, type_) for el in els))


__all__ = ["node_process", "nodes_process", "md_escape", "BULLET", "STRIPE"]

import mastoposter.text.html  # noqa F401
import mastoposter.text.markdown  # noqa F401
import mastoposter.text.plain  # noqa F401
