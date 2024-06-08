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

from bs4 import NavigableString
from mastoposter.text import (
    nodes_process,
    register_converter,
    register_fmt_converter,
    register_text_node_converter,
    node_process,
    STRIPE,
    BULLET,
)

from typing import Optional
from bs4.element import Tag
from html import escape


@register_text_node_converter("html")
def proc_text_node_to_html(txt: NavigableString) -> str:
    return escape(txt)


@register_converter("a", "html")
def proc_tag_a_to_html(tag: Tag):
    return '<a href="%s">%s</a>' % (
        escape(tag.attrs.get("href", "#")),
        nodes_process(tag.children, "html"),
    )


register_fmt_converter("%s\n\n", "p", "html")
register_fmt_converter("<i>%s</i>", "i", "html")
register_fmt_converter("<i>%s</i>", "em", "html")
register_fmt_converter("<b>%s</b>", "b", "html")
register_fmt_converter("<b>%s</b>", "strong", "html")
register_fmt_converter("<s>%s</s>", "s", "html")
register_fmt_converter("<s>%s</s>", "del", "html")
register_fmt_converter("<u>%s</u>", "u", "html")
register_fmt_converter("<u>%s</u>", "ins", "html")
register_fmt_converter("\n", "br", "html")
register_fmt_converter("\n<pre>%s</pre>\n", "pre", "html")
register_fmt_converter("<code>%s</code>", "code", "html")


@register_converter("span", "html")
def proc_tag_span_to_html(tag: Tag) -> Optional[str]:
    if "_mfm_blur_" in tag.attrs.get("class", ""):
        return '<span class="tg-spoiler">%s</span>' % nodes_process(
            tag.children, "html"
        )
    return None


@register_converter("blockquote", "html")
def proc_tag_blockquote_to_html(tag: Tag) -> str:
    return str.join(
        "\n",
        (
            STRIPE + " " + line
            for line in nodes_process(tag.children, "html").strip().split("\n")
        ),
    )


@register_converter("ul", "html")
def proc_tag_ul_to_html(tag: Tag) -> str:
    return "\n" + str.join(
        "\n",
        (
            BULLET
            + " "
            + node_process(el, "html").replace("\n", "\n   ").rstrip()
            for el in tag.children
        ),
    )


@register_converter("ol", "html")
def proc_tag_li_to_html(tag: Tag) -> str:
    return "\n" + str.join(
        "\n",
        (
            "%d. %s"
            % (i, node_process(el, "html").replace("\n", "\n   ").rstrip())
            for i, el in enumerate(tag.children, 1)
        ),
    )
