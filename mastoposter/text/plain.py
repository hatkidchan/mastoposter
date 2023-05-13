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

from mastoposter.text import (
    nodes_process,
    register_converter,
    register_fmt_converter,
    node_process,
    STRIPE,
    BULLET,
)

from bs4.element import Tag
from html import escape


@register_converter("a", "plain")
def proc_tag_a_to_plain(tag: Tag):
    return "%s (%s)" % (
        nodes_process(tag.children, "plain"),
        escape(tag.attrs.get("href", "#")),
    )


register_fmt_converter("%s\n\n", "p", "plain")
register_fmt_converter("\n", "br", "plain")


@register_converter("blockquote", "plain")
def proc_tag_blockquote_to_plain(tag: Tag) -> str:
    return str.join(
        "\n",
        (
            STRIPE + " " + line
            for line in nodes_process(tag.children, "plain")
            .strip()
            .split("\n")
        ),
    )


@register_converter("ul", "plain")
def proc_tag_ul_to_plain(tag: Tag) -> str:
    return "\n" + str.join(
        "\n",
        (
            BULLET
            + " "
            + node_process(el, "plain").replace("\n", "\n   ").rstrip()
            for el in tag.children
        ),
    )


@register_converter("li", "plain")
def proc_tag_li_to_plain(tag: Tag) -> str:
    return "\n" + str.join(
        "\n",
        (
            "%d. %s"
            % (i, node_process(el, "plain").replace("\n", "\n   ").rstrip())
            for i, el in enumerate(tag.children, 1)
        ),
    )
